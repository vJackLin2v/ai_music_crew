"""快速测试旋律 Agent —— 输出 MIDI + MP3 + PDF。"""

import json
import re

from tests.test_helpers import (
    load_round_context,
    build_melody_prompt,
    call_and_render_melody,
)


def test_melody():
    ctx = load_round_context()
    if "error" in ctx:
        print(f"[ERR] {ctx['error']}\n请先运行一次 crewai run 生成上下文")
        return

    agents = ctx["agents"]
    params = ctx["params"]
    key = params.get("key", "G大调")
    bpm = params.get("bpm", "65-78")
    title = params.get("title", "测试歌曲")

    brief = next((v for k, v in agents.items() if "创作简报" in k or "导演" in k), "")
    lyrics = next((v for k, v in agents.items() if "歌词" in k or "作词" in k), "")

    if not brief or not lyrics:
        print("[ERR] 无法提取简报或歌词，请先运行一次 crewai run")
        return

    prompt = build_melody_prompt(brief, lyrics, key, bpm)
    # 从 round 文件提取歌词 JSON（用于规则引擎）
    lyrics_json = _extract_lyrics_json_from_context(ctx)
    call_and_render_melody("melody", prompt, key, bpm, title, lyrics_json)


def _extract_lyrics_json_from_context(ctx: dict) -> str:
    """从 round 文件提取的上下文中还原歌词 JSON。"""
    agents = ctx.get("agents", {})
    lyrics_text = next((v for k, v in agents.items() if "歌词" in k or "作词" in k), "")

    # 用正则从 Markdown 中提取各段歌词
    result = {}
    for section in ["verse_1", "verse_2", "chorus", "bridge", "outro"]:
        # 匹配 **Verse 1（主歌）**\n歌词内容\n\n
        patterns = [
            rf"\*\*{section}[^*]*\*\*\s*\n(.+?)(?=\n\n\*\*|\n\n\*|\Z)",
            rf"\*\*{section.replace('_',' ').title()}[^*]*\*\*\s*\n(.+?)(?=\n\n\*\*|\n\n\*|\Z)",
        ]
        found = None
        for p in patterns:
            m = re.search(p, lyrics_text, re.DOTALL)
            if m:
                found = m.group(1).strip()
                break
        if found:
            result[section] = found
    return json.dumps(result, ensure_ascii=False) if result else "{}"

    print("\n[OK] 完成。MIDI/MP3/PDF 在 output/agent_tests/ 下")


if __name__ == "__main__":
    test_melody()
