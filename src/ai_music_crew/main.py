#!/usr/bin/env python
from pathlib import Path
import json
import re
from datetime import datetime
from pydantic import BaseModel

from crewai.flow import Flow, listen, start, router

from ai_music_crew.crews.production_crew.production_crew import ProductionCrew
from ai_music_crew.crews.output_crew.output_crew import OutputCrew

from skills import load_skill, auto_detect_skill


class SongState(BaseModel):
    topic: str = ""
    feedback: str = ""
    round: int = 0
    max_rounds: int = 3
    song_title: str = ""
    is_instrumental: bool = False
    instrumental_hint: str = ""
    # 各 Crew 的产出
    brief_raw: str = ""
    lyrics_raw: str = ""
    arrangement_raw: str = ""
    suno_raw: str = ""
    editor_raw: str = ""
    skill_prompt: str = ""
    suno_override: str = ""

def _parse_json(raw_text: str) -> dict | None:
    """尝试从 LLM 原始输出中提取 JSON。"""
    if not raw_text:
        return None

    # 清理：去掉 BOM、首尾空白、零宽字符
    text = raw_text.strip().lstrip("﻿​‌‍⁠")

    strategies = [
        # 1. 直接解析
        lambda t: json.loads(t),
        # 2. 去掉 markdown 代码块包裹
        lambda t: json.loads(m.group(1).strip())
        if (m := re.search(r"```(?:json)?\s*\n?(.*?)\n?```", t, re.DOTALL))
        else None,
        # 3. 括号计数提取
        _extract_braced_json,
        # 4. 修复常见 JSON 错误后再解析
        lambda t: _repair_and_parse(t),
    ]

    for strategy in strategies:
        try:
            result = strategy(text)
            if result is not None and isinstance(result, dict):
                return result
        except (json.JSONDecodeError, TypeError, ValueError):
            continue

    return None

def _extract_braced_json(text: str) -> dict | None:
    """从文本中用括号计数提取 JSON 对象。"""
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
                return json.loads(text[start:i + 1])
    return None

def _repair_and_parse(text: str) -> dict | None:
    """修复 LLM 常见 JSON 错误后解析。"""
    # 1. 替换中文引号
    fixed = text.replace("“", '"').replace("”", '"')
    # 2. 去掉尾随逗号（如 {"a": 1,}）
    fixed = re.sub(r",(\s*[}\]])", r"\1", fixed)
    # 3. 再次尝试括号提取
    extracted = _extract_braced_json(fixed)
    if extracted:
        return extracted
    return None

class SongFlow(Flow[SongState]):

    @start()
    def plan(self, trigger: dict = None):
        if trigger:
            self.state.topic = trigger.get("topic", "AI Agents")
            print(f"Using trigger payload: {trigger}")
        else:
            self.state.topic = "我想写一首中文歌, 类似《虞兮叹》, 要有金句，有故事感，画面感，令人感动。但不要抄袭！时长限制在2分半-3分钟。"
            # self.state.topic = "我想要一首纯音乐，让人感觉回到了小时候的夏天。"

        # 检测TOPIC中是否触发Skill关键词
        skill_id = auto_detect_skill(self.state.topic)
        skill = load_skill(skill_id) if skill_id else None
        if skill:
            print(f"[Flow] 检测到风格: {skill['skill_name']}")
            self.state.skill_prompt = skill["skill_prompt"]
            self.state.suno_override = skill["suno_override"]
        else:
            self.state.skill_prompt = ""
            self.state.suno_override = ""
        
        # 检测是否需要歌词（排除否定表达：不要/不想/无需/不是 纯音乐等）
        neg = re.search(r"(不要|不想|无需|不是|非|别|不)\s*(纯音乐|纯器乐|instrumental|无歌词|无人声)", self.state.topic)
        self.state.is_instrumental = not bool(neg) and any(
            w in self.state.topic for w in ["纯音乐", "instrumental", "无歌词", "无人声", "纯器乐"]
        )
        self.state.instrumental_hint = "用户要的是纯音乐/无人声，直接输出所有歌词字段为 null。" if self.state.is_instrumental else ""

        self.state.round = 0
        self.state.feedback = ""
        self.state.max_rounds = 3
        print(f"[Flow] Topic: {self.state.topic}")
        if self.state.is_instrumental: print("[Flow] 纯音乐模式")

    @listen(plan)
    def produce_and_review(self):
        while self.state.round < self.state.max_rounds:
            self.state.round += 1
            print(f"\n{'='*50}")
            print(f"[Flow] 第 {self.state.round}/{self.state.max_rounds} 轮")
            print(f"{'='*50}")

            print("[Flow] >>> ProductionCrew 开始")
            result_production = (
                ProductionCrew().crew().kickoff(inputs={
                    "topic": self.state.topic,
                    "feedback": self.state.feedback,
                    "instrumental_hint": self.state.instrumental_hint,
                    "skill_prompt": self.state.skill_prompt
                })
            )
            # 存下本轮的歌词和编曲（以备通过后使用）
            self._capture_production(result_production)
            print(
                f"[Flow] <<< ProductionCrew 完成 | "
                f"title={self.state.song_title}, "
                f"brief={bool(self.state.brief_raw)}, "
                f"lyrics={bool(self.state.lyrics_raw)}, "
                f"arr={bool(self.state.arrangement_raw)}"
            )

            ctx = json.dumps({
                "brief": _parse_json(self.state.brief_raw),
                "lyrics": _parse_json(self.state.lyrics_raw),
                "arrangement": _parse_json(self.state.arrangement_raw),
            }, ensure_ascii=False) if self.state.brief_raw else ""

            print("[Flow] >>> ReviewCrew 开始")
            
            suno_hint = f"风格参考: {self.state.suno_override}" if self.state.suno_override else ""
            result_output = OutputCrew().crew().kickoff(inputs={
                "topic": self.state.topic,
                "feedback": ctx,
                "instrumental_hint": self.state.instrumental_hint,
                "suno_override_hint": suno_hint,
            })
            self._capture_review(result_output)

            # ── 判断审核结果 ──
            if self._is_approved():
                print("[Flow] ✅ 审核通过")
                break
            else:
                print(f"[Flow] ⚠️ 第 {self.state.round} 轮未通过，准备下一轮")
                self.state.feedback = self.state.editor_raw
        else:
            print(f"[Flow] ⏰ 达到最大轮次 {self.state.max_rounds}")

    @router(produce_and_review)
    def final_check(self):
        if self.state.round >= self.state.max_rounds:
            return "FORCE_SAVE"
        return "CLEAN_SAVE"
    
    @listen("CLEAN_SAVE")
    def save(self):
        self._write_report()
    
    @listen("FORCE_SAVE")
    def save_forced(self):
        self._write_report(forced=True)
    
    def _capture_production(self, result):
        """从 ProductionCrew 结果提取简报、歌词、编曲。"""
        for t in result.tasks_output:
            data = _parse_json(t.raw)
            if not data:
                continue
            if "title_suggestion" in data:
                self.state.brief_raw = t.raw
                self.state.song_title = data.get("title_suggestion", "未命名")
            elif "verse_1" in data:
                self.state.lyrics_raw = t.raw
            elif "instruments" in data:
                self.state.arrangement_raw = t.raw

    def _capture_review(self, result):
        """从 ReviewCrew 结果提取 Suno 提示词和审核报告。"""
        for t in result.tasks_output:
            data = _parse_json(t.raw)
            if not data:
                continue
            if "suno_style_prompt" in data:
                self.state.suno_raw = t.raw
            elif "verdict" in data:
                self.state.editor_raw = t.raw
    
    def _is_approved(self) -> bool:
        data = _parse_json(self.state.editor_raw) if self.state.editor_raw else None
        if data and "通过" in data.get("verdict", ""):
            return True
        # 兜底：字符串匹配
        return "总体判断：通过" in (self.state.editor_raw or "")
    
    def _write_report(self, forced: bool = False):
        """写 post.md + Suno 提示词（和之前一样）"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = re.sub(r'[\\/:*?"<>|]', "_", self.state.song_title or "未命名")
        d = Path("output") / f"{ts}_{safe}"
        d.mkdir(parents=True, exist_ok=True)

        brief = _parse_json(self.state.brief_raw) or {}
        lyrics = _parse_json(self.state.lyrics_raw) or {}
        arr = _parse_json(self.state.arrangement_raw) or {}
        suno = _parse_json(self.state.suno_raw) or {}

        tag = "（强制保存）" if forced else ""
        with open(d / "post.md", "w", encoding="utf-8") as f:
            f.write(f"# {self.state.song_title or '未命名'} {tag}\n\n")
            f.write(f"> 用户需求：{self.state.topic}\n\n---\n\n")

            if lyrics:
                f.write("## 🎤 歌词\n\n")
                for k in ["verse_1","chorus","verse_2","bridge","outro"]:
                    if lyrics.get(k): f.write(f"**{k}**\n\n{lyrics[k]}\n\n")

            if arr:
                f.write("## 🎹 编曲\n\n")
                f.write(f"乐器: {', '.join(arr.get('instruments',[]))}\n\n")
                f.write(f"{arr.get('structure_timeline','')}\n\n")
                f.write(f"**时长**: {arr.get('total_duration','')}\n\n")

            if suno:
                sp = suno.get("suno_style_prompt","")
                sl = (suno.get("suno_lyrics") or "").replace("\\n","\n")
                f.write("---\n\n## 🎵 Suno\n\n")
                f.write(f"**Style Prompt**:\n{sp}\n\n")
                if sl: f.write(f"**歌词**:\n{sl}\n\n")

            f.write(f"---\n\n*共 {self.state.round} 轮*\n")
        print(f"[Flow] Report saved: {d / 'post.md'}")

def kickoff():
    SongFlow().kickoff()

if __name__ == "__main__":
    kickoff()
