"""快速测试音乐导演 Agent prompt。"""

from tests.test_helpers import build_planner_prompt, call_agent


def test_planner():
    topic = "我想写一首中文歌，适合夜晚散步听。有点孤独，但最后是释怀。不要太吵，歌词要有画面感。"

    prompt = build_planner_prompt(topic)
    call_agent("planner", prompt)

    print("\n[OK] 完成。结果在 output/agent_tests/ 下")


if __name__ == "__main__":
    test_planner()
