"""快速测试编曲人 Agent prompt。"""

from tests.test_helpers import load_round_context, build_arranger_prompt, call_agent


def test_arranger():
    ctx = load_round_context()
    if "error" in ctx:
        print(f"[ERR] {ctx['error']}\n请先运行一次 crewai run 生成上下文")
        return

    agents = ctx["agents"]
    params = ctx["params"]

    brief = next((v for k, v in agents.items() if "创作简报" in k or "导演" in k), "")
    lyrics = next((v for k, v in agents.items() if "歌词" in k or "作词" in k), "")

    if not brief or not lyrics:
        print("[ERR] 无法提取简报或歌词")
        return

    topic = params.get("title", "测试歌曲")
    prompt = build_arranger_prompt(brief, lyrics, topic)
    call_agent("arranger", prompt)

    print("\n[OK] 完成。结果在 output/agent_tests/ 下")


if __name__ == "__main__":
    test_arranger()
