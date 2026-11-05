"""Agent 测试工具 —— 加载上下文、构造 prompt、调用 LLM、渲染音频。"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

_llm_instance = None


def _get_llm() -> LLM:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLM(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
            temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
        )
    return _llm_instance


# ============================================================
# 上下文加载
# ============================================================

def find_latest_run() -> Path | None:
    """找最近修改过的歌曲运行目录（跳过 agent_tests）。"""
    output_dir = Path("output")
    dirs = [
        d for d in output_dir.iterdir()
        if d.is_dir() and d.name != "agent_tests"
    ]
    if not dirs:
        return None
    # 按修改时间排序，最新的在前
    dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return dirs[0]


def load_round_context() -> dict:
    """加载最近一次运行的输出，返回 {agents, params, run_dir}。"""
    run_dir = find_latest_run()
    if not run_dir:
        return {"error": "没有找到历史运行目录"}

    round_files = sorted(run_dir.glob("round_*.md"))
    if not round_files:
        return {"error": "没有找到 round 文件"}

    content = round_files[0].read_text(encoding="utf-8")
    sections = re.split(r"\n## ", content)

    agents = {}
    for s in sections:
        s = s.strip()
        lines = s.split("\n", 1)
        name = lines[0].strip()
        body = lines[1] if len(lines) > 1 else ""
        agents[name] = body

    params = _extract_params(agents)
    params["run_dir"] = str(run_dir)
    return {"agents": agents, "params": params, "run_dir": str(run_dir)}


def _extract_params(agents: dict) -> dict:
    """从简报 section 提取 BPM、调式、标题。"""
    brief = next(
        (v for k, v in agents.items() if "创作简报" in k or "导演" in k), ""
    )
    params = {"bpm": "65-78", "key": "G大调", "title": "测试歌曲"}
    for field, pattern in [
        ("bpm", r"BPM 范围.*?(\d+[-~]\d+)"),
        ("key", r"调式建议.*?([A-G](?:#|b)?[^|\n]{0,10})"),
        ("title", r"标题建议.*?([^|\n]{2,20})"),
    ]:
        m = re.search(pattern, brief)
        if m:
            params[field] = m.group(1).strip().rstrip("|").strip()
    return params


# ============================================================
# Prompt 构建器（和实际 Agent 看到的 prompt 对齐）
# ============================================================

def build_planner_prompt(topic: str, feedback: str = "") -> str:
    fb = f"\n\n以下是上一轮审核的反馈意见，请针对性调整：\n---\n{feedback}\n---\n" if feedback else ""
    return (
        f"根据用户的音乐创作需求：{topic}.{fb}\n\n"
        "生成一份歌曲创作简报。用户可能不懂乐理，把自然语言需求翻译成创作方向。\n\n"
        "输出纯 JSON，格式：\n"
        '{"title_suggestion":"歌名","theme":"核心主题","mood_keywords":["情绪1","情绪2","情绪3"],'
        '"bpm_range":"65-78","key_suggestion":"G大调","style_direction":"民谣/氛围流行",'
        '"vocal_advice":"人声建议","lyric_imagery_keywords":["意象1","意象2"],'
        '"avoid_directions":["避免1","避免2"],"arrangement_tips":"编曲建议"}'
    )


def build_writer_prompt(brief_text: str, topic: str, feedback: str = "") -> str:
    fb = f"\n\n以下是上一轮审核的反馈意见，请针对性修改：\n---\n{feedback}\n---\n" if feedback else ""
    return (
        f"根据歌曲创作简报，为 {topic} 创作中文歌词。{fb}\n\n"
        f"创作简报：\n{brief_text[:1200]}\n\n"
        "歌词需要有主歌和副歌。主歌叙事铺垫，副歌情绪释放。不要写成诗歌赏析或口号。\n\n"
        "输出纯 JSON，格式：\n"
        '{"verse_1":"主歌Verse 1","chorus":"副歌Chorus","verse_2":"主歌Verse 2",'
        '"bridge":null,"outro":null,"creation_notes":"创作说明","rhyme_rate":85}'
    )


def build_arranger_prompt(brief_text: str, lyrics_text: str, topic: str, feedback: str = "") -> str:
    fb = f"\n\n以下是上一轮审核的反馈意见，请针对性调整：\n---\n{feedback}\n---\n" if feedback else ""
    return (
        f"根据歌曲创作简报和歌词，为 {topic} 设计一份编曲方案。{fb}\n\n"
        f"创作简报：\n{brief_text[:600]}\n\n"
        f"歌词：\n{lyrics_text[:600]}\n\n"
        "需要考虑乐器选择、段落编排、动态层次、混音建议。留白也是一种编排。\n\n"
        "输出纯 JSON，格式：\n"
        '{"instruments":["乐器1","乐器2"],"structure_timeline":"按时间线描述每个段落的编曲安排",'
        '"dynamics_plan":"强弱动态规划","mixing_notes":"混音建议",'
        '"sfx_suggestions":null,"total_duration":"预计时长"}'
    )


def build_melody_prompt(
    brief_text: str, lyrics_text: str, key: str, bpm: str, feedback: str = ""
) -> str:
    fb = f"\n\n以下是上一轮审核的反馈意见，请针对性调整：\n---\n{feedback}\n---\n" if feedback else ""
    return f"""你是 Suno AI 提示词专家。根据简报、歌词生成 Suno 提示词。

调式: {key} | BPM: {bpm}{fb}

简报:
{brief_text[:800]}

歌词:
{lyrics_text[:800]}

输出纯 JSON：
{{
  "suno_style_prompt": "英文音乐描述（30-60词），含风格+情绪+乐器+BPM",
  "suno_lyrics": "[Verse 1]\\n歌词...\\n\\n[Chorus]\\n副歌..."
}}

Style Prompt 用英文写，具体不笼统，含 BPM 和乐器。
歌词用 Suno 格式标记段落。
只要 JSON，不要代码块，不要解释"""


# ============================================================
# LLM 调用 + 保存
# ============================================================

def call_agent(name: str, prompt: str, save: bool = True) -> str:
    """调用 LLM，打印结果摘要，返回原始输出。"""
    llm = _get_llm()
    print(f"\n{'='*60}")
    print(f"[TEST] {name}")
    print(f"{'='*60}")
    print(f"Prompt 长度: {len(prompt)} 字符\n")

    try:
        resp = llm.call(messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        print(f"[FAIL] LLM call: {e}")
        return ""

    print(resp[:2000])
    print(f"\n... {len(resp)} 字符")

    if save:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path("output") / "agent_tests"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{name}_{ts}.txt"
        out_path.write_text(
            f"=== PROMPT ===\n{prompt}\n\n=== RESPONSE ===\n{resp}",
            encoding="utf-8",
        )
        print(f"[OK] Saved: {out_path}")

    return resp


def call_and_render_melody(name: str, prompt: str, key: str, bpm: str, title: str, lyrics_json: str = "{}") -> str:
    """调用 LLM 生成 Suno 提示词 → 保存到 agent_tests 目录。"""
    resp = call_agent(name, prompt, save=True)

    data = _parse_json(resp)
    if not data or "suno_style_prompt" not in data:
        print("[FAIL] Can't parse Suno prompt")
        return resp

    out_dir = Path("output") / "agent_tests"
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suno_path = out_dir / f"suno_{ts}.txt"
    with open(suno_path, "w", encoding="utf-8") as f:
        f.write(f"# Suno Style Prompt\n{data.get('suno_style_prompt', '')}\n\n")
        f.write(f"# Suno Lyrics\n{data.get('suno_lyrics', '')}\n")
    print(f"[OK] Suno prompt saved: {suno_path}")
    return resp


def _parse_json(raw: str) -> dict | None:
    """从 LLM 输出提取 JSON。"""
    if not raw:
        return None
    # 直接解析
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass
    # 提取代码块
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    return None
