import json
from pathlib import Path

SKILLS_DIR = Path(__file__).parent

def list_skills() -> list[dict]:
    skills = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if d.is_dir() and (d / "skill.json").exists():
            with open(d / "skill.json", encoding="utf-8") as f:
                data = json.load(f)
            skills.append({"id": d.name, "name": data.get("name", d.name)})
    return skills

def load_skill(skill_id: str) -> dict | None:
    skill_dir = SKILLS_DIR / skill_id
    if not skill_dir.is_dir():
        return None
    json_path = skill_dir / "skill.json"
    if not json_path.exists():
        return None
    
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    
    prompts = data.get("agent_prompts", {})
    labels = {
        "music_director": "音乐导演",
        "lyricist": "作词人",
        "arranger": "编曲人",
    }

    sections = []
    for key, label in labels.items():
        if key in prompts:
            sections.append(f"## {label}\n{prompts[key]}")

    knowledge_files = data.get("knowledge_files", [])
    knowledge_text = ""
    for kf in knowledge_files:
        kf_path = skill_dir / kf
        if kf_path.exists():
            content = kf_path.read_text(encoding="utf-8").strip()
            if content:
                knowledge_text += f"\n\n# 专属参考知识\n\n{content}"
    
    full_prompt = "\n\n".join(sections)
    if knowledge_text:
        full_prompt += knowledge_text

    return {
        "skill_name": data.get("name", skill_id),
        "skill_prompt": full_prompt,
        "suno_override": data.get("suno_style", ""),
    }
        
def auto_detect_skill(topic: str) -> str | None:
    patterns = {
        "jay_chou": ["周杰伦", "jay", "方文山", "七里香", "晴天", "东风破", "稻香", "夜曲"],
        "gufeng": ["古风", "凄美", "虞兮", "虞姬", "侠客", "江湖", "长安", "洛阳", "铜钱", "战鼓", "红笺"],
    }
    for skill_id, words in patterns.items():
        if any(w.lower() in topic.lower() for w in words):
            return skill_id
    return None