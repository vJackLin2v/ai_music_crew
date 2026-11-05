#!/usr/bin/env python
r"""make_cover.py — 把一首歌的人声换成小鲸鱼的声音（分离 → 换声 → 混音 → 母带）。

设计原则：
  1) 每一步产物落盘、可单独重跑；换声参数要反复调，不能每次从头分离。
  2) 断点续跑：已有产物默认跳过，加 --force 重做。
  3) 混音比例不靠猜：人声/伴奏比例对齐到**原始混音**的实测值。
  4) 每个 stage 都写 report，出了问题能定位到哪一步。

用法：
  python make_cover.py all      --in song.mp3
  python make_cover.py all      --in song.mp3 --ref voice\xiaojingyu\reference-long.mp3 --steps 40
  python make_cover.py separate --in song.mp3 --work work\song
  python make_cover.py convert  --work work\song --ref ref.wav
  python make_cover.py mix      --work work\song
  python make_cover.py master   --work work\song
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent
PY = ROOT / ".svc" / "Scripts" / "python.exe"
SEEDVC = ROOT / "tools" / "seed-vc"
FFMPEG_DIR = Path(r"H:\tools\ffmpeg\ffmpeg-master-latest-win64-gpl\bin")
DEFAULT_REF = ROOT / "voice" / "xiaojingyu" / "reference-long.mp3"

SR = 44100
TARGET_LUFS = -14.0
TRUE_PEAK_CEIL = -1.0


# ---------------------------------------------------------------- helpers
def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# 模型仓库走本机代理：DSH 自己注入的 HTTP_PROXY(64402) 是它内部用的，
# 直接透传会让 huggingface_hub 连不上。用 Clash 的 7890 才算数。
# 换代理：设环境变量 MAKE_COVER_PROXY；置空字符串则直连。
PROXY = os.environ.get("MAKE_COVER_PROXY", "http://127.0.0.1:7890")


def env() -> dict:
    e = dict(os.environ)
    e.setdefault("HF_ENDPOINT", "https://huggingface.co")
    e["PATH"] = str(FFMPEG_DIR) + os.pathsep + e.get("PATH", "")
    e["PYTHONIOENCODING"] = "utf-8"
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        if PROXY:
            e[k] = PROXY
        else:
            e.pop(k, None)
    return e


def run(cmd: list, cwd: Path | None = None, label: str = "") -> None:
    log(f"{label or 'run'}: {' '.join(str(c) for c in cmd)}")
    r = subprocess.run([str(c) for c in cmd], cwd=str(cwd) if cwd else None, env=env())
    if r.returncode != 0:
        raise SystemExit(f"命令失败（exit {r.returncode}）：{label}")


def state_path(work: Path) -> Path:
    return work / "state.json"


def load_state(work: Path) -> dict:
    p = state_path(work)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def save_state(work: Path, st: dict) -> None:
    work.mkdir(parents=True, exist_ok=True)
    state_path(work).write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def read_audio(path: Path, sr: int = SR) -> np.ndarray:
    """读成立体声 (n, 2) float32，必要时重采样。"""
    data, file_sr = sf.read(str(path), always_2d=True, dtype="float32")
    if data.shape[1] == 1:
        data = np.repeat(data, 2, axis=1)
    elif data.shape[1] > 2:
        data = data[:, :2]
    if file_sr != sr:
        import soxr

        data = soxr.resample(data, file_sr, sr)
    return data.astype(np.float32)


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x)) + 1e-12))


def active_rms(x: np.ndarray, floor_db: float = -40.0) -> float:
    """只统计有声部分（去掉静音帧对电平判断的影响）。"""
    mono = x.mean(axis=1) if x.ndim > 1 else x
    win = int(SR * 0.05)
    n = len(mono) // win
    if n == 0:
        return rms(mono)
    frames = mono[: n * win].reshape(n, win)
    fr = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
    thr = 10 ** (floor_db / 20.0)
    voiced = fr[fr > thr]
    if voiced.size == 0:
        return rms(mono)
    return float(np.sqrt(np.mean(voiced ** 2)))


def db(x: float) -> float:
    return 20 * np.log10(max(x, 1e-9))


def peak_limit(x: np.ndarray, ceil_db: float = -1.0, block_ms: float = 8.0) -> np.ndarray:
    """真·限幅器：只在超过天花板的峰上压，不动整体响度。

    不要用 pedalboard.Limiter —— 实测它带自动补增益，会把 -14 LUFS 抬到 -10 LUFS 并削顶。
    """
    from scipy.ndimage import maximum_filter1d, uniform_filter1d

    ceil = 10 ** (ceil_db / 20.0)
    mono = np.max(np.abs(x), axis=1) if x.ndim > 1 else np.abs(x)
    k = max(1, int(SR * block_ms / 1000.0))
    env = maximum_filter1d(mono, size=k, mode="nearest")      # 前瞻包络
    gain = np.minimum(1.0, ceil / np.maximum(env, 1e-9))
    gain = uniform_filter1d(gain, size=k, mode="nearest")      # 平滑，避免咔哒
    gain = np.minimum(gain, np.minimum(1.0, ceil / np.maximum(mono, 1e-9)))
    if x.ndim > 1:
        return x * gain[:, None]
    return x * gain


# ---------------------------------------------------------------- 1. separate
def stage_separate(song: Path, work: Path, force: bool) -> None:
    """htdemucs_ft 两轨分离：人声 / 伴奏。"""
    work.mkdir(parents=True, exist_ok=True)
    vocals = work / "vocals.wav"
    inst = work / "inst.wav"
    if vocals.exists() and inst.exists() and not force:
        log(f"separate 已完成，跳过（{vocals.name} / {inst.name}）")
        return

    sep_dir = work / "demucs"
    run(
        [PY, "-m", "demucs", "-n", "htdemucs_ft", "--two-stems=vocals",
         "-o", str(sep_dir), str(song)],
        label="demucs htdemucs_ft",
    )
    stem_dir = sep_dir / "htdemucs_ft" / song.stem
    src_vocals = stem_dir / "vocals.wav"
    src_inst = stem_dir / "no_vocals.wav"
    if not src_vocals.exists():
        raise SystemExit(f"分离产物不存在：{src_vocals}")
    shutil.copy2(src_vocals, vocals)
    shutil.copy2(src_inst, inst)

    # 原始混音的人声/伴奏比例 —— 混音时用它，别自己猜
    v = read_audio(vocals)
    i = read_audio(inst)
    ratio = active_rms(v) / max(active_rms(i), 1e-9)
    save_state(work, {**load_state(work), "song": str(song), "orig_vocal_inst_ratio": ratio})
    log(f"separate 完成：人声/伴奏 原始比例 {db(ratio):+.2f} dB")


# ---------------------------------------------------------------- 2. convert
def stage_convert(work: Path, ref: Path, steps: int, force: bool,
                  ckpt: Path | None = None, cfg: Path | None = None,
                  svc_dir: str = "svc") -> Path:
    """Seed-VC 零样本歌声转换（保留音高/节奏，只换音色）。"""
    vocals = work / "vocals.wav"
    if not vocals.exists():
        raise SystemExit("缺少 vocals.wav，先跑 separate")
    out_dir = work / svc_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # 参考音：seed-vc 只用前 25 秒，切成 22 秒以内更稳
    ref_short = work / "ref22.wav"
    if force or not ref_short.exists():
        r = read_audio(ref)
        r = r[: int(SR * 22)]
        sf.write(str(ref_short), r, SR)
        log(f"参考音裁到 {len(r)/SR:.1f}s → {ref_short.name}")

    conv = next(iter(out_dir.glob("vc_*.wav")), None)
    if conv and not force:
        log(f"convert 已完成，跳过（{conv.name}）")
        return conv

    cmd = [PY, "inference.py",
           "--source", str(vocals),
           "--target", str(ref_short),
           "--output", str(out_dir),
           "--f0-condition", "True",       # 唱歌必须开
           "--diffusion-steps", str(steps),
           "--inference-cfg-rate", "0.7",
           "--semi-tone-shift", "0",
           "--fp16", "True"]
    if ckpt:
        cmd += ["--checkpoint", str(ckpt)]
    if cfg:
        cmd += ["--config", str(cfg)]
    run(cmd, cwd=SEEDVC, label="seed-vc svc")
    conv = next(iter(out_dir.glob("vc_*.wav")), None)
    if not conv:
        raise SystemExit("seed-vc 没有产出 vc_*.wav")
    save_state(work, {**load_state(work), "converted": str(conv), "steps": steps,
                       "ckpt": str(ckpt) if ckpt else "pretrained", "svc_dir": svc_dir})
    log(f"convert 完成：{conv.name}")
    return conv


# ---------------------------------------------------------------- 2.5 breath
def stage_breath(work: Path, gain_db: float = -13.0, force: bool = False) -> Path:
    """把换声丢掉的气息/气声补回来。

    Seed-VC 按 mel + 内容编码重建，**没音高的那部分（呼吸、气声、齿音尾巴）会被丢掉**，
    于是听感"太干净、不像人"。做法：从**源人声**里把「无音高 + 低能量 + 噪声性」的片段
    抠出来，叠回换声结果上 —— 呼吸本身几乎不含音色信息，所以不会串味。
    """
    import librosa

    if not gain_db:                       # 0 / None = 关闭
        log("breath 已关闭（--breath 0），跳过")
        return work / "vocals_breath.wav"   # 可能不存在，mix 会回落到原始换声结果

    out = work / "vocals_breath.wav"
    if out.exists() and not force:
        log("breath 已完成，跳过")
        return out

    st = load_state(work)
    conv_path = st.get("converted") or next(iter((work / "svc").glob("vc_*.wav")), None)
    if not conv_path:
        raise SystemExit("缺少换声产物，先跑 convert")

    src = read_audio(work / "vocals.wav", sr=SR).mean(axis=1)
    conv = read_audio(Path(conv_path), sr=SR).mean(axis=1)
    n = min(len(src), len(conv))
    src, conv = src[:n], conv[:n]

    hop, win = 512, 2048

    def frame_db(y):
        f = librosa.feature.rms(y=y, frame_length=win, hop_length=hop)[0]
        d = 20 * np.log10(np.maximum(f, 1e-8))
        return np.interp(np.arange(len(y)), np.arange(len(d)) * hop, d)

    # ① 噪声性：谱平坦度（呼吸是宽带噪声，音高成分平坦度低）
    flat_f = librosa.feature.spectral_flatness(y=src, n_fft=win, hop_length=hop)[0]
    flat = np.interp(np.arange(len(src)), np.arange(len(flat_f)) * hop, flat_f)

    src_db = frame_db(src)
    conv_db = frame_db(conv)
    peak_db = float(np.percentile(src_db, 99))
    med_conv = float(np.median(conv_db))

    # 换声结果在"气口"处几乎是静音，源人声那里却有一小段低能量噪声 —— 就是它
    mask = (conv_db < med_conv - 8) & (src_db > peak_db - 45) & (src_db < peak_db - 12)
    # 平坦度作为软门槛：太"tonal"的残响不要（librosa 的平坦度数值整体很低，阈值要跟着数据走）
    flat_thr = max(0.002, float(np.percentile(flat, 40)))
    mask &= (flat > flat_thr)

    # ⑤ 去掉过短的片段（齿音碎片），保留 ≥120ms 的气口
    m = mask.astype(np.float32)
    k = int(SR * 0.12)
    if m.any():
        from scipy.ndimage import minimum_filter1d, uniform_filter1d
        m = minimum_filter1d(m, size=max(1, k // 4))
        m = uniform_filter1d(m, size=max(1, k // 6))

    breath = src * m
    breath_rms = float(np.sqrt(np.mean(breath ** 2)))
    target_rms = float(np.sqrt(np.mean(conv ** 2))) * (10 ** (gain_db / 20))
    scale = target_rms / max(breath_rms, 1e-9) if breath_rms > 0 else 0.0

    from pedalboard import Pedalboard, HighpassFilter, LowpassFilter
    bp = Pedalboard([HighpassFilter(cutoff_frequency_hz=160), LowpassFilter(cutoff_frequency_hz=11000)])
    breath = bp(np.stack([breath * scale] * 2, axis=1).T, SR).T.mean(axis=1)

    merged = conv + breath
    peak = float(np.max(np.abs(merged)))
    if peak > 0.99:
        merged = merged * (0.99 / peak)
    stereo = np.stack([merged, merged], axis=1).astype(np.float32)
    sf.write(str(out), stereo, SR, subtype="FLOAT")

    pct = float(m.mean() * 100)
    log(f"breath 完成：气口占时长 {pct:.1f}%，气息增益 {gain_db:+.1f} dB")
    save_state(work, {**st, "breathed": str(out), "breath_pct": round(pct, 2)})
    return out


# ---------------------------------------------------------------- 3. mix
def stage_mix(work: Path, reverb: float, force: bool) -> Path:
    """把换声后的人声贴回伴奏：电平对齐原始比例 + EQ + 去齿音 + 混响。"""
    from pedalboard import (Compressor, HighpassFilter, HighShelfFilter,
                            LowShelfFilter, Pedalboard, Reverb)

    st = load_state(work)
    # 有补过气息的就用补过的，否则用原始换声结果
    conv_path = st.get("breathed") or st.get("converted")
    if not conv_path or not Path(conv_path).exists():
        cand = next(iter((work / st.get("svc_dir", "svc")).glob("vc_*.wav")), None)
        conv_path = str(cand) if cand else None
    if not conv_path:
        raise SystemExit("缺少换声产物，先跑 convert")

    out = work / "mixed.wav"
    if out.exists() and not force:
        log("mix 已完成，跳过")
        return out

    voc_new = read_audio(Path(conv_path))
    voc_src = read_audio(work / "vocals.wav")
    inst = read_audio(work / "inst.wav")

    n = max(len(voc_new), len(inst))
    def pad(x: np.ndarray) -> np.ndarray:
        if len(x) >= n:
            return x[:n]
        return np.pad(x, ((0, n - len(x)), (0, 0)))

    voc_new, voc_src, inst = pad(voc_new), pad(voc_src), pad(inst)

    # ① 电平和原始人声对齐（SVC 输出的响度和源人声不是一回事）
    gain = active_rms(voc_src) / max(active_rms(voc_new), 1e-9)
    voc_new = voc_new * gain
    log(f"人声电平对齐：{db(gain):+.2f} dB")

    # ② 人声处理链：高通去低频泥 + 压一点动态 + 削 7k 的齿音毛刺
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=90),
        Compressor(threshold_db=-18.0, ratio=2.5, attack_ms=8.0, release_ms=120.0),
        LowShelfFilter(cutoff_frequency_hz=250, gain_db=1.0),
        HighShelfFilter(cutoff_frequency_hz=7000, gain_db=-2.0),
    ])
    voc_proc = board(voc_new.T, SR).T

    # ③ 混响：换声输出是干的，原人声带房间感，不补会很"贴脸"
    if reverb > 0:
        rv = Pedalboard([Reverb(room_size=0.35, damping=0.5, wet_level=reverb,
                                dry_level=1.0 - reverb * 0.5, width=0.8)])
        voc_proc = rv(voc_proc.T, SR).T

    # ④ 比例：沿用原始混音的 人声/伴奏 实测比例
    ratio = float(st.get("orig_vocal_inst_ratio") or 0.35)
    inst_gain = 1.0
    voc_gain = (active_rms(inst) * ratio) / max(active_rms(voc_proc), 1e-9)
    mix = inst * inst_gain + voc_proc * voc_gain

    peak = float(np.max(np.abs(mix)))
    if peak > 0:
        mix = mix * (10 ** (-1.0 / 20) / peak)
    sf.write(str(out), mix.astype(np.float32), SR, subtype="FLOAT")
    save_state(work, {**st, "mixed": str(out), "vocal_gain_db": db(voc_gain), "reverb": reverb})
    log(f"mix 完成：{out.name}（峰值归一 -1 dBFS）")
    return out


# ---------------------------------------------------------------- 4. master
def stage_master(work: Path, out_dir: Path, force: bool) -> Path:
    """响度归一到 -14 LUFS，真峰值 ≤ -1 dBTP，导出 24bit WAV + 320k MP3。"""
    import pyloudnorm as pyln

    st = load_state(work)
    mixed = st.get("mixed") or str(work / "mixed.wav")
    if not Path(mixed).exists():
        raise SystemExit("缺少 mixed.wav，先跑 mix")

    out_dir.mkdir(parents=True, exist_ok=True)
    name = Path(st.get("song", "cover")).stem
    wav_out = out_dir / f"{name}_cover.wav"
    mp3_out = out_dir / f"{name}_cover.mp3"
    if wav_out.exists() and not force:
        log("master 已完成，跳过")
        return wav_out

    audio = read_audio(Path(mixed))
    meter = pyln.Meter(SR)
    loud0 = meter.integrated_loudness(audio)

    # 先补/减到目标响度，再限幅；限幅后重新校一次（限峰会吃掉一点点响度）
    audio = peak_limit(audio * (10 ** ((TARGET_LUFS - loud0) / 20)), TRUE_PEAK_CEIL)
    for _ in range(3):
        loud = meter.integrated_loudness(audio)
        if abs(loud - TARGET_LUFS) <= 0.3:
            break
        audio = peak_limit(audio * (10 ** ((TARGET_LUFS - loud) / 20)), TRUE_PEAK_CEIL)
    loud2 = meter.integrated_loudness(audio)
    log(f"响度：{loud0:.2f} LUFS → {loud2:.2f} LUFS（目标 {TARGET_LUFS}）")

    peak = float(np.max(np.abs(audio)))
    if peak > 10 ** (TRUE_PEAK_CEIL / 20):
        audio = audio * (10 ** (TRUE_PEAK_CEIL / 20) / peak)
    loud2 = meter.integrated_loudness(audio)

    sf.write(str(wav_out), audio.astype(np.float32), SR, subtype="PCM_24")
    run([FFMPEG_DIR / "ffmpeg.exe", "-y", "-i", str(wav_out), "-b:a", "320k", str(mp3_out)],
        label="ffmpeg mp3 320k")

    st.update({
        "mastered_wav": str(wav_out), "mastered_mp3": str(mp3_out),
        "lufs_before": round(float(loud0), 2), "lufs_after": round(float(loud2), 2),
        "peak_dbfs": round(db(peak), 2),
    })
    save_state(work, st)
    (out_dir / "report.json").write_text(
        json.dumps({k: v for k, v in st.items() if not k.startswith("_")},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"master 完成：{wav_out.name} / {mp3_out.name}（{loud2:.2f} LUFS）")
    return wav_out


# ---------------------------------------------------------------- 批量
def stage_batch(indir: Path, outroot: Path, ref: Path, steps: int, reverb: float,
                force: bool, limit: int | None = None, pattern: str = "*.mp3",
                breath_db: float = -13.0) -> list:
    """把一个目录里的歌全部走一遍。单首失败不影响后面的，最后出 batch-report.json。"""
    songs = [p for p in sorted(indir.rglob(pattern))
             if p.stat().st_size > 500_000]          # 跳过试听片段
    if limit:
        songs = songs[:limit]
    if not songs:
        raise SystemExit(f"{indir} 下没有找到 {pattern}")
    log(f"批量：{len(songs)} 首")
    results = []
    for i, song in enumerate(songs, 1):
        log(f"=== [{i}/{len(songs)}] {song.name}")
        work = ROOT / "work" / "batch" / song.stem
        out = outroot / song.stem
        try:
            stage_separate(song, work, force)
            stage_convert(work, ref, steps, force)
            stage_breath(work, breath_db, force)
            stage_mix(work, reverb, force)
            stage_master(work, out, force)
            results.append({"song": str(song), "ok": True, "out": str(out)})
        except SystemExit as e:
            log(f"!! 跳过 {song.name}: {e}")
            results.append({"song": str(song), "ok": False, "err": str(e)})
        except Exception as e:                       # noqa: BLE001
            log(f"!! 跳过 {song.name}: {e!r}")
            results.append({"song": str(song), "ok": False, "err": repr(e)})
    outroot.mkdir(parents=True, exist_ok=True)
    (outroot / "batch-report.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for r in results if r["ok"])
    log(f"批量结束：成功 {ok}/{len(results)} → {outroot}")
    return results


# ---------------------------------------------------------------- cli
def main() -> None:
    ap = argparse.ArgumentParser(description="Suno 曲 → 小鲸鱼人声替换 → 母带")
    ap.add_argument("stage", choices=["all", "separate", "convert", "breath", "mix", "master", "batch"])
    ap.add_argument("--in", dest="song", type=Path)
    ap.add_argument("--work", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--ref", type=Path, default=DEFAULT_REF)
    ap.add_argument("--steps", type=int, default=40, help="扩散步数，唱歌建议 30~50")
    ap.add_argument("--reverb", type=float, default=0.12, help="混响湿度 0~1")
    ap.add_argument("--breath", type=float, default=0.0,
                    help="气息补偿：0=关闭（默认，实测搬源人声的气口会带进 demucs 残留噪音）")
    ap.add_argument("--force", action="store_true", help="重做已有产物")
    ap.add_argument("--ckpt", type=Path, help="微调后的 DiT checkpoint（默认用官方预训练模型）")
    ap.add_argument("--cfg", type=Path, help="微调后的 config（配合 --ckpt）")
    ap.add_argument("--svc-dir", default="svc", help="换声产物的子目录名，便于 A/B 留档")
    ap.add_argument("--limit", type=int, help="批量模式最多处理几首")
    ap.add_argument("--pattern", default="*.mp3", help="批量模式的文件匹配")
    a = ap.parse_args()

    if a.stage == "batch":
        if not a.song:                      # --in 传目录
            raise SystemExit("batch 需要 --in <目录>")
        stage_batch(a.song.resolve(), (a.out or ROOT / "out" / "batch").resolve(),
                    a.ref, a.steps, a.reverb, a.force, a.limit, a.pattern, a.breath)
        return

    if a.stage in ("all", "separate"):
        if not a.song:
            raise SystemExit("separate/all 需要 --in <song.mp3>")
        song = a.song.resolve()
        work = (a.work or ROOT / "work" / song.stem).resolve()
    else:
        if not a.work:
            raise SystemExit("需要 --work <目录>")
        work = a.work.resolve()
        song = None

    out_dir = (a.out or ROOT / "out" / work.name).resolve()
    # seed-vc 的 inference.py 在 tools/seed-vc 下运行，相对路径会解析错地方，统一转绝对
    ckpt = a.ckpt.resolve() if a.ckpt else None
    cfg = a.cfg.resolve() if a.cfg else None

    t0 = time.time()
    if a.stage == "separate":
        stage_separate(song, work, a.force)
    elif a.stage == "convert":
        stage_convert(work, a.ref, a.steps, a.force, ckpt, cfg, a.svc_dir)
    elif a.stage == "breath":
        stage_breath(work, a.breath, a.force)
    elif a.stage == "mix":
        stage_mix(work, a.reverb, a.force)
    elif a.stage == "master":
        stage_master(work, out_dir, a.force)
    else:
        stage_separate(song, work, a.force)
        stage_convert(work, a.ref, a.steps, a.force)
        stage_breath(work, a.breath, a.force)
        stage_mix(work, a.reverb, a.force)
        stage_master(work, out_dir, a.force)
    log(f"完成，用时 {time.time() - t0:.1f}s → {out_dir}")


if __name__ == "__main__":
    main()
