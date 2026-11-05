"""AI Music Crew - Streamlit 前端"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# 确保项目路径在 sys.path 中（streamlit run 从项目根目录执行）
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_music_crew.crews.production_crew.production_crew import ProductionCrew
from ai_music_crew.crews.output_crew.output_crew import OutputCrew
from skills import list_skills, load_skill, auto_detect_skill


# ═══════════════════════════════════════
# 工具函数（从 main.py 复制，避免循环 import）
# ═══════════════════════════════════════

def _parse_json(raw: str) -> dict | None:
    if not raw:
        return None
    text = raw.strip().lstrip("﻿​‌‍")
    for s in [
        lambda t: json.loads(t),
        lambda t: json.loads(m.group(1).strip())
        if (m := re.search(r"```(?:json)?\s*\n?(.*?)\n?```", t, re.DOTALL))
        else None,
    ]:
        try:
            r = s(text)
            if isinstance(r, dict):
                return r
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def _show_brief(data: dict):
    """展示导演简报。"""
    st.markdown(f"**{data.get('title_suggestion', '')}**")
    st.markdown(f"*{data.get('theme', '')}*")
    st.divider()
    items = [
        ("BPM", data.get("bpm_range", "")),
        ("调式", data.get("key_suggestion", "")),
        ("风格", data.get("style_direction", "")),
        ("情绪", ", ".join(data.get("mood_keywords", []))),
        ("人声", data.get("vocal_advice", "")),
        ("意象", ", ".join(data.get("lyric_imagery_keywords", []))),
    ]
    for label, val in items:
        if val:
            st.markdown(f"- **{label}**: {val}")


def _show_lyrics(data: dict):
    """展示歌词。"""
    for key, label in [
        ("verse_1", "主歌 1"), ("chorus", "副歌"),
        ("verse_2", "主歌 2"), ("bridge", "桥段"), ("outro", "尾奏"),
    ]:
        val = data.get(key)
        if val:
            st.markdown(f"**{label}**")
            st.markdown(val)
            st.markdown("")
    if data.get("creation_notes"):
        st.caption(f"*{data['creation_notes']}*")


def _show_arrangement(data: dict):
    """展示编曲方案。"""
    st.markdown(f"**乐器**: {', '.join(data.get('instruments', []))}")
    timeline = data.get("structure_timeline", "")
    if timeline:
        st.markdown("**段落时间线**")
        st.markdown(timeline)
    dynamics = data.get("dynamics_plan", "")
    if dynamics:
        st.markdown(f"**动态**: {dynamics}")
    st.markdown(f"**时长**: {data.get('total_duration', 'N/A')}")


def _render_cached_results():
    """从 session_state 渲染上一次运行的结果。"""
    st.header(st.session_state.get("last_title", "未命名"))
    st.caption(
        f"共 {st.session_state.get('last_rounds', '?')} 轮创作完成 · "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )

    lyrics = st.session_state.get("last_lyrics", {})
    arr = st.session_state.get("last_arr", {})
    suno = st.session_state.get("last_suno", {})
    editor = st.session_state.get("last_editor", {})

    if lyrics and lyrics.get("verse_1"):
        st.divider()
        st.header("🎤 歌词")
        cols = st.columns(2)
        with cols[0]:
            if lyrics.get("verse_1"):
                st.subheader("主歌 1")
                st.markdown(lyrics["verse_1"])
            if lyrics.get("verse_2"):
                st.subheader("主歌 2")
                st.markdown(lyrics["verse_2"])
        with cols[1]:
            if lyrics.get("chorus"):
                st.subheader("副歌")
                st.markdown(lyrics["chorus"])
            if lyrics.get("bridge"):
                st.subheader("桥段")
                st.markdown(lyrics["bridge"])

    if arr:
        st.divider()
        st.header("🎹 编曲方案")
        st.markdown(f"**乐器**: {', '.join(arr.get('instruments', []))}")
        st.markdown(arr.get("structure_timeline", ""))
        st.caption(f"**时长**: {arr.get('total_duration', 'N/A')}")

    if suno:
        st.divider()
        st.header("🎵 Suno 提示词")
        st.code(suno.get("suno_style_prompt", ""), language=None)
        sl = (suno.get("suno_lyrics") or "").replace("\\n", "\n")
        if sl:
            st.text_area("歌词", sl, height=200, key="cached_suno_lyrics")

    if editor:
        with st.expander("📋 审核评分"):
            overall = editor.get("overall_score", editor.get("score", "?"))
            st.caption(f"总评分: {overall}/10")
            for key, label in [
                ("brief", "创作简报"), ("lyrics", "歌词"),
                ("arrangement", "编曲方案"), ("suno", "Suno提示词"),
            ]:
                c = editor.get(key, {})
                if isinstance(c, dict):
                    icon = "✅" if c.get("score", 0) >= 8 else "⚠️"
                    st.write(f"{icon} **{label}**: {c.get('score','?')}/10 {c.get('verdict','')}")


# ═══════════════════════════════════════
# Streamlit 界面
# ═══════════════════════════════════════

st.set_page_config(page_title="AI Music Crew", page_icon="🎵", layout="wide")

# session_state 初始化
for key in ["running", "stop_requested"]:
    if key not in st.session_state:
        st.session_state[key] = False

st.title("🎵 AI Music Crew")
st.caption("多智能体协作 · AI 音乐创作 | Powered by CrewAI + DeepSeek")

# ── 输入区 ──
col_input, col_config = st.columns([3, 2])

with col_input:
    topic = st.text_area(
        "歌曲主题",
        value="我想写一首周杰伦风格的情歌，要有记忆点，不要抄袭！时长限制在2分半-3分钟。",
        height=100,
        placeholder="描述你想要的歌曲：风格、情绪、故事...",
    )

with col_config:
    skills = list_skills()
    skill_options = ["自动检测"] + [s["name"] for s in skills]
    skill_idx = st.selectbox(
        "风格 Skill", range(len(skill_options)),
        format_func=lambda i: skill_options[i],
    )

    col1, col2 = st.columns(2)
    with col1:
        max_rounds = st.slider("最大轮次", 1, 5, 3)
    with col2:
        is_instrumental = st.checkbox("纯音乐模式")

    running = st.session_state.running
    btn_label = "⏹️ 停止创作" if running else "🚀 开始创作"
    generate = st.button(
        btn_label, type="primary" if not running else "secondary",
        use_container_width=True,
    )

    # 停止按钮逻辑
    if generate and running:
        st.session_state.stop_requested = True
        st.session_state.running = False
        st.rerun()

    start_requested = generate and not running

    if start_requested and not running:
        st.session_state.running = True
        st.rerun()

# ── 进度 + 结果区 ──
placeholder = st.empty()

if start_requested or st.session_state.running:
    # ── 确定 Skill ──
    if skill_idx > 0:
        skill_id = skills[skill_idx - 1]["id"]
    else:
        skill_id = auto_detect_skill(topic)

    skill = load_skill(skill_id) if skill_id else None
    skill_prompt = skill["skill_prompt"] if skill else ""
    suno_override = skill["suno_override"] if skill else ""
    instrumental_hint = (
        "用户要的是纯音乐/无人声，直接输出所有歌词字段为 null。"
        if is_instrumental else ""
    )

    # ── 状态变量 ──
    brief_raw = lyrics_raw = arr_raw = suno_raw = editor_raw = ""
    song_title = "未命名"
    feedback = ""
    round_reports = []  # 存每轮完整产出

    # 标记开始运行
    st.session_state.running = True
    st.session_state.stop_requested = False

    # ── 反馈循环 ──
    for rnd in range(1, max_rounds + 1):
        if st.session_state.stop_requested:
            st.warning("⏹️ 用户手动终止")
            break
        progress_text = f"第 {rnd}/{max_rounds} 轮"
        progress_bar = st.progress(rnd / max_rounds, progress_text)

        rnd_report = {"round": rnd, "production": [], "review": []}

        # ── Production ──
        with st.expander(f"🎬 {progress_text} · 生产阶段", expanded=(rnd == 1)):
            p_col1, p_col2, p_col3 = st.tabs(["导演简报", "歌词", "编曲方案"])

            prod = (
                ProductionCrew().crew().kickoff(inputs={
                    "topic": topic,
                    "feedback": feedback,
                    "instrumental_hint": instrumental_hint,
                    "skill_prompt": skill_prompt,
                })
            )

            # 提取并展示每个 Agent 产出
            for t in prod.tasks_output:
                data = _parse_json(t.raw)
                if not data:
                    continue

                if "title_suggestion" in data:
                    brief_raw = t.raw
                    song_title = data.get("title_suggestion", "未命名")
                    rnd_report["production"].append({"agent": "导演", "data": data})
                    with p_col1:
                        _show_brief(data)

                elif "verse_1" in data:
                    lyrics_raw = t.raw
                    rnd_report["production"].append({"agent": "作词人", "data": data})
                    with p_col2:
                        _show_lyrics(data)

                elif "instruments" in data:
                    arr_raw = t.raw
                    rnd_report["production"].append({"agent": "编曲人", "data": data})
                    with p_col3:
                        _show_arrangement(data)

        # ── Review ──
        with st.expander(f"🔍 {progress_text} · 审核阶段", expanded=(rnd == 1)):
            r_tab1, r_tab2 = st.tabs(["🎵 Suno 提示词", "📋 审核报告"])

            ctx = json.dumps({
                "brief": _parse_json(brief_raw),
                "lyrics": _parse_json(lyrics_raw),
                "arrangement": _parse_json(arr_raw),
            }, ensure_ascii=False) if brief_raw else ""

            suno_hint = f"风格参考: {suno_override}" if suno_override else ""

            review = (
                OutputCrew().crew().kickoff(inputs={
                    "topic": topic,
                    "feedback": ctx,
                    "instrumental_hint": instrumental_hint,
                    "suno_override_hint": suno_hint,
                })
            )

            # 提取并展示
            for t in review.tasks_output:
                data = _parse_json(t.raw)
                if not data:
                    continue

                if "suno_style_prompt" in data:
                    suno_raw = t.raw
                    rnd_report["review"].append({"agent": "Suno设计师", "data": data})
                    with r_tab1:
                        st.caption("**Style Prompt**")
                        st.code(data.get("suno_style_prompt", ""), language=None)
                        sl = (data.get("suno_lyrics") or "").replace("\\n", "\n")
                        if sl:
                            st.text_area(
                                "歌词（可全选 Ctrl+A 复制）", sl, height=200,
                                key=f"suno_lyrics_r{rnd}",
                            )

                elif "brief" in data and isinstance(data.get("brief"), dict):
                    # 新版分组件审核格式（含评分）
                    editor_raw = t.raw
                    rnd_report["review"].append({"agent": "审核人", "data": data})
                    with r_tab2:
                        overall = data.get("overall_score", data.get("score", "?"))
                        st.caption(f"总评分: {overall}/10")
                        labels = {
                            "brief": "创作简报", "lyrics": "歌词",
                            "arrangement": "编曲方案", "suno": "Suno提示词",
                        }
                        for key, label in labels.items():
                            comp = data.get(key, {})
                            if not isinstance(comp, dict):
                                continue
                            s = comp.get("score", "?")
                            v = comp.get("verdict", "?")
                            icon = "✅" if "通过" in v else "⚠️"
                            st.markdown(f"**{icon} {label}** ({s}/10): {v}")
                            issues = comp.get("issues", [])
                            if issues:
                                for iss in issues:
                                    st.write(f"  - {iss}")

        round_reports.append(rnd_report)

        # 判断：所有组件 score >= 8 才算通过
        editor_data = _parse_json(editor_raw) if editor_raw else None
        approved = False
        if editor_data:
            if "brief" in editor_data and isinstance(editor_data.get("brief"), dict):
                components = ["brief", "lyrics", "arrangement", "suno"]
                approved = all(
                    editor_data.get(c, {}).get("score", 0) >= 8
                    for c in components
                )
            else:
                approved = "通过" in editor_data.get("verdict", "")
        approved = approved or "总体判断：通过" in (editor_raw or "")

        if approved:
            st.success(f"✅ {progress_text} · 审核通过！")
            break
        else:
            # 构造分组件反馈，通过的标注"保持原样"
            labels = {
                "brief": "创作简报", "lyrics": "歌词",
                "arrangement": "编曲方案", "suno": "Suno提示词",
            }
            fb_lines = []
            for key, label in labels.items():
                comp = (editor_data or {}).get(key, {})
                if isinstance(comp, dict):
                    v = comp.get("verdict", "需要修改")
                    issues = comp.get("issues", [])
                    if "通过" in v:
                        fb_lines.append(f"✅ [{label}] 已通过，保持原样。")
                    else:
                        fb_lines.append(
                            f"⚠️ [{label}] 需要修改：{'；'.join(issues) if issues else '细节优化'}"
                        )
            feedback = "\n".join(fb_lines) if fb_lines else editor_raw

            st.warning(f"⚠️ {progress_text} · 需要修改，进入下一轮")
            with st.expander("查看分项反馈"):
                st.markdown(feedback)
    else:
        st.warning(f"⏰ 达到最大轮次 {max_rounds}，保存当前版本")

    # ── 页脚 ──
    st.divider()
    st.caption(
        f"《{song_title}》 · 共 {rnd} 轮创作完成 · "
        f"{datetime.now().strftime('%H:%M:%S')}"
        f"{' · Skill: ' + skill['skill_name'] if skill else ''}"
    )
    # 存结果到 session_state，rerun 后还能看到
    st.session_state.last_brief = _parse_json(brief_raw) or {}
    st.session_state.last_lyrics = _parse_json(lyrics_raw) or {}
    st.session_state.last_arr = _parse_json(arr_raw) or {}
    st.session_state.last_suno = _parse_json(suno_raw) or {}
    st.session_state.last_editor = _parse_json(editor_raw) or {}
    st.session_state.last_rounds = rnd
    st.session_state.last_title = song_title
    st.session_state.show_results = True
    st.session_state.running = False
    st.rerun()

elif st.session_state.get("show_results"):
    # ── 显示上次运行结果（rerun 后持久化）──
    with placeholder.container():
        _render_cached_results()

else:
    # ── 初始状态：使用说明 ──
    with placeholder.container():
        st.markdown("""
        ## 👈 配置歌曲主题，点击「开始创作」

        ### 工作流程
        1. **音乐导演** 分析需求 → 创作简报（情绪、调式、BPM、风格）
        2. **作词人** 根据简报写中文歌词（Verse + Chorus + Bridge）
        3. **编曲人** 设计编曲方案（乐器、动态、结构）
        4. **旋律设计师** 生成 Suno AI 提示词
        5. **审核人** 审查所有产出 → 不通过则回到第1步

        ### 可选 Skill（风格专家）
        """)

        skill_cols = st.columns(len(list_skills()) if list_skills() else 1)
        for i, s in enumerate(list_skills()):
            with skill_cols[i]:
                with st.container(border=True):
                    st.subheader(s["name"])
                    st.caption(f"`{s['id']}`")

        st.info("💡 **提示**: 在主题中包含「周杰伦」「古风」等关键词，系统会自动检测并匹配 Skill。")
