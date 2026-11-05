"""快速测试作词人 Agent prompt。"""

from tests.test_helpers import load_round_context, build_writer_prompt, call_agent


def test_writer():
    ctx = load_round_context()
    if "error" in ctx:
        print(f"[ERR] {ctx['error']}\n请先运行一次 crewai run 生成上下文")
        return

    agents = ctx["agents"]
    params = ctx["params"]

    brief = next((v for k, v in agents.items() if "创作简报" in k or "导演" in k), "")
    if not brief:
        print("[ERR] 无法提取简报")
        return

    topic = f"一首{params.get('key','G大调')}的{params.get('title','歌')}"
    prompt = build_writer_prompt(brief, topic)
    call_agent("writer", prompt)

    print("\n[OK] 完成。结果在 output/agent_tests/ 下")


if __name__ == "__main__":
    test_writer()
