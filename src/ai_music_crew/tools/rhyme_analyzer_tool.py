"""中文韵脚分析工具 —— 分析歌词的押韵情况并给出改进建议。"""
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# 近似韵母分组——中文里这些韵母在歌词创作中被认为是"可以押的"
# 例如 an/ian/uan/üan 在实际演唱中听感相似
RHYME_GROUPS: dict[str, set[str]] = {
    "an":  {"an", "ian", "uan", "üan"},
    "ang": {"ang", "iang", "uang"},
    "ao":  {"ao", "iao"},
    "en":  {"en", "in", "un", "ün"},
    "eng": {"eng", "ing", "ong", "iong"},
    "e":   {"e", "ie", "üe", "ue"},
    "a":   {"a", "ia", "ua"},
    "ou":  {"ou", "iu"},
    "i":   {"i", "ei", "ui"},
    "u":   {"u"},
}

def _get_final(char: str) -> str:
    """获取一个汉字的韵母，失败时返回空字符串"""
    try:
        from pypinyin import Style, pinyin
        result = pinyin(char, style=Style.FINALS)
        if result and result[0]:
            return result[0][0].lower()
    except Exception:
        pass
    return ""

def _is_rhyme_match(final1: str, final2: str, strict: bool) -> bool:
    """判断两个韵母是否匹配（押韵）"""
    if not final1 or not final2:
        return False
    if strict:
        return final1 == final2
    # 宽松模式，检查是否是同一个韵母组
    for group in RHYME_GROUPS.values():
        if final1 in group and final2 in group:
            return True
    return final1 == final2

class RhymeAnalysisInput(BaseModel):
    """韵脚分析工具的输入结构"""
    lyrics: str = Field(
        ...,
        description="需要分析的完整中文歌词文本，可包含多行、标点和空行",
    )
    strict_mode: bool = Field(
        default=False,
        description="是否启用严格模式。False=宽松模式（近似韵母算押韵），True=韵母必须完全相同",
    )

class RhymeAnalyzerTool(BaseTool):
    name: str = "RhymeAnalyzer"
    description: str = (
        "分析中文歌词的韵脚分布。输入歌词文本，返回每行末字的韵母、"
        "押韵率统计和改进建议。在写完歌词后使用此工具检查韵脚质量。"
    )
    args_schema: Type[BaseModel] = RhymeAnalysisInput

    def _run(self, lyrics: str, strict_mode: bool = False) -> str:
        """执行韵脚分析。"""
        if not lyrics or not lyrics.split():
            return "⚠️ 歌词文本为空，无法分析。"

        # 1.提取有效行（过滤空行和纯标点行）
        raw_lines = lyrics.strip().split("\n")
        lines: list[str] = []
        for line in raw_lines:
            stripped = line.strip()
            if stripped and any("\u4e00" <= ch <= "\u9fff" for ch in stripped):
                lines.append(stripped)
        
        if len(lines) < 2:
            return f"⚠️ 检测到 {len(lines)} 个有效行，至少需要 2 行才能分析韵脚（需要包含中文歌词）。"
        
        # 2.逐行提取末字和韵母
        line_analysis: list[dict] = []
        for i, line in enumerate(lines, 1):
            # 找到最后一个字
            last_char = ""
            for ch in reversed(line):
                if "\u4e00" <= ch <= "\u9fff":
                    last_char = ch
                    break
            final = _get_final(last_char) if last_char else ""
            line_analysis.append({
                "line_num": i,
                "text": line,
                "last_char": last_char,
                "final": final or "？",
            })
        
        # 3.统计韵脚分布
        # 找出出现最多的韵母组作为”主韵“
        final_counts: dict[str, int] = {}
        for item in line_analysis:
            f = item["final"]
            if f and f != "？":
                final_counts[f] = final_counts.get(f, 0) + 1
        
        # 4.计算押韵率
        rhyme_pairs = 0
        total_pairs = len(lines) - 1
        for i in range(total_pairs):
            f1 = line_analysis[i]["final"]
            f2 = line_analysis[i + 1]["final"]
            if _is_rhyme_match(f1, f2, strict_mode):
                rhyme_pairs += 1
        
        rhyme_rate = (rhyme_pairs / total_pairs * 100) if total_pairs > 0 else 0

        # 5. 构建输出报告
        mode_label = "严格模式（韵母必须完全相同）" if strict_mode else "宽松模式（近韵母可算押韵）"

        output = "# 中文歌词韵脚分析\n\n"
        output += f"分析模式: {mode_label}\n"
        output += f"有效行数: {len(lines)}\n"
        output += f"相邻押韵对数: {rhyme_pairs}/{total_pairs}\n"
        output += f"押韵率: {rhyme_rate:.0f}%\n\n"

        output += "## 逐行分析\n\n"
        output += "| 行号 | 末字 | 韵母 | 歌词 |\n"
        output += "|------|------|------|------|\n"
        for item in line_analysis:
            text_preview = item["text"][:30] + ("..." if len(item["text"]) > 30 else "")
            output += f"| {item['line_num']} | {item['last_char']} | {item['final']} | {text_preview} |\n"

        output += "\n## 韵脚统计\n\n"
        if final_counts:
            sorted_finals = sorted(final_counts.items(), key=lambda x: x[1], reverse=True)
            for final, count in sorted_finals:
                output += f"- 韵母 `{final}`：出现 {count} 次\n"
            main_final = sorted_finals[0][0]
            output += f"\n主韵: `{main_final}`\n"
        else:
            output += "未能识别出有效韵母。\n"

        # 6. 给出建议
        output += "\n## 改进建议\n\n"
        if rhyme_rate >= 70:
            output += "✅ 押韵率良好！歌词有清晰的韵脚脉络，适合演唱。\n"
            output += "可以考虑在桥段或过渡句中刻意换韵，增加听觉变化。\n"
        elif rhyme_rate >= 40:
            output += "⚠️ 押韵率中等。建议：\n"
            output += f"- 尝试让更多行使用主韵 `{main_final if final_counts else '?'}` 结尾\n"
            output += "- 或者采取 AABB 押韵结构（第1-2行押韵，第3-4行换韵）\n"
        else:
            output += "🔴 押韵率较低。建议：\n"
            output += "- 确定一个主韵母（如 `ang` 或 `an`），至少 60% 的行尾字使用它\n"
            output += "- 在保持词意的前提下，替换末字为同韵母的字\n"
            output += "- 或者采用偶数行押韵的结构（只要求第2、4、6...行押韵）\n"

        return output
        