"""情绪坐标工具 —— 把情绪词映射到二维空间，推荐音乐参数。"""

from crewai.tools import tool

# ============================================================
# 情绪坐标表: 词 → (能量 0~1, 效价 -1~1)
#   能量: 0=极静, 1=极动
#   效价: -1=极负面, 0=中性, 1=极正面
# ============================================================


EMOTION_COORDS: dict[str, tuple[float, float]] = {
    # ---- A 区: 高能量 + 正面 ----
    "热血": (0.85, 0.80),
    "希望": (0.75, 0.90),
    "喜悦": (0.80, 0.85),
    "力量": (0.90, 0.50),
    "激动": (0.95, 0.60),
    "欢快": (0.70, 0.80),
    "振奋": (0.80, 0.70),
    "期待": (0.55, 0.65),

    # ---- B 区: 低能量 + 正面 ----
    "释怀": (0.30, 0.50),
    "温暖": (0.35, 0.70),
    "治愈": (0.40, 0.75),
    "内省": (0.25, 0.20),
    "宁静": (0.10, 0.60),
    "平静": (0.15, 0.40),
    "回忆": (0.30, 0.10),
    "思念": (0.35, -0.10),
    "放松": (0.12, 0.55),
    "浪漫": (0.40, 0.80),

    # ---- C 区: 低能量 + 负面 ----
    "孤独":   (0.15, -0.70),
    "忧郁":   (0.20, -0.60),
    "寂寞":   (0.20, -0.55),
    "伤感":   (0.25, -0.50),
    "悲伤":   (0.15, -0.80),
    "难过":   (0.20, -0.65),
    "麻木":   (0.10, -0.30),
    "迷惘":   (0.20, -0.40),
    "空虚":   (0.10, -0.50),
    "失落":   (0.15, -0.55),
    "凄凉":   (0.18, -0.75),
    "遗憾":   (0.22, -0.45),
    "无奈":   (0.25, -0.35),
    "忧伤":   (0.18, -0.70),

    # ---- D 区: 高能量 + 负面 ----
    "愤怒": (0.90, -0.60),
    "绝望": (0.80, -0.90),
    "撕裂": (0.85, -0.70),
    "挣扎": (0.70, -0.50),
    "紧张": (0.60, -0.40),
    "焦虑": (0.65, -0.55),

    # ---- 原点附近 ----
    "安静": (0.10, 0.30),
    "淡然": (0.20, 0.25),
    "好奇": (0.45, 0.40),
    "自由": (0.50, 0.55),
}


# ============================================================
# 别名映射: 变体词 → 坐标表中的主词
# ============================================================
EMOTION_ALIASES: dict[str, str] = {
    # 孤独的变体
    "孤单": "孤独", "独自": "孤独", "一个人": "孤独", "独处": "孤独",

    # 忧郁的变体
    "消沉": "忧郁", "惆怅": "忧郁", "黯然": "忧郁", "心碎": "悲伤",

    # 释怀的变体
    "放下": "释怀", "看透": "释怀", "解脱": "释怀", "豁达": "释怀",

    # 热血/力量的变体
    "澎湃": "热血", "激昂": "热血", "冲动": "热血",
    "勇气": "力量", "坚毅": "力量", "果敢": "力量",

    # 温暖的变体
    "温馨": "温暖", "温情": "温暖", "暖意": "温暖",

    # 宁静的变体
    "安详": "平静", "静谧": "宁静", "平和": "平静",

    # 回忆的变体
    "怀念": "回忆", "回首": "回忆", "怀旧": "回忆", "追忆": "回忆",

    # 治愈的变体
    "疗愈": "治愈", "治愈系": "治愈",

    # 伤感的变体
    "感伤": "伤感", "伤心": "难过",

    # 其他
    "绝望感": "绝望", "无助": "绝望",
    "烦躁": "愤怒", "暴怒": "愤怒", "暴躁": "愤怒",
    "沮丧": "难过", "失落感": "失落",
    "茫然": "迷惘", "迷失": "迷惘", "彷徨": "迷惘",
    "虚无": "空虚", "空洞": "空虚",
    "闲适": "放松", "悠然": "放松",
    "开心": "喜悦", "快乐": "喜悦",
    "微醺": "迷惘", "沉醉": "内省",
    "悲凉": "凄凉", "凄美": "凄凉",
    "悔恨": "遗憾", "惋惜": "遗憾",
    "不甘": "无奈", "认命": "无奈",
    "压抑": "忧伤",
}

def _find_coord(keyword: str) -> tuple[tuple[float, float], str] | None:
    """对单个关键词，按四层策略找它的坐标。

    返回 （（energy, valence）, matched_label） 或None。
    matched_label 是最终匹配到的情绪词名，用于输出报告。
    """
    # 第1层: 直接匹配
    if keyword in EMOTION_COORDS:
        return (EMOTION_COORDS[keyword], keyword)

    # 第2层: 别名匹配
    if keyword in EMOTION_ALIASES:
        resolved = EMOTION_ALIASES[keyword]
        if resolved in EMOTION_COORDS:
            return (EMOTION_COORDS[resolved], f"{keyword}→{resolved}")

    # 第3层: 无法匹配——标记为未识别，LLM 下次会从工具描述里的词表中挑选
    return None

def _describe_quadrant(e: float, v: float) -> str:
    """根据坐标返回象限名。"""
    if e < 0.35:
        return "C区（低能量-负面）" if v < -0.15 else "B区（低能量-正面）"
    else:
        return "D区（高能量-负面）" if v < 0.2 else "A区（高能量-正面）"


def _recommend(e: float, v: float) -> str:
    """根据坐标生成音乐参数建议。"""
    # 象限边界不硬切，用坐标连续插值
    # BPM: 能量主导
    #  base = 低能量 50, 高能量 150
    bpm_low = int(50 + e * 100)
    bpm_high = int(70 + e * 80)
    # 微调用效价: 正面微调快一点，负面微调慢一点
    valence_shift = int(v * 10)
    bpm_low += valence_shift
    bpm_high += valence_shift

    # 调式: 效价主导
    if v > 0.15:
        key_advice = "大调或五声音阶（明亮）"
    elif v < -0.15:
        key_advice = "小调（忧伤底色）。可尝试借大调和弦进行走小调旋律，增加张力"
    else:
        key_advice = "大小调均可，或采用平行大小调切换"

    # 编曲密度: 能量主导
    if e < 0.25:
        arrangement = "极简编曲，1-2件乐器主导（推荐：钢琴独奏 或 木吉他+人声），大量留白和长音"
    elif e < 0.5:
        arrangement = "中等编曲，钢琴/木吉他 + 弦乐铺底 + 轻打击乐（沙锤/铃鼓），副歌可加贝斯和轻鼓组"
    elif e < 0.75:
        arrangement = "饱满编曲，全编制（鼓+贝斯+吉他/钢琴+弦乐），副歌加入铜管或合成器增加厚度"
    else:
        arrangement = "高密度编曲，重型鼓组+失真吉他+合成器Pad，持续强拍推进"

    # 核心乐器
    instruments = _pick_instruments(e, v)

    return (
        f"综合建议:\n"
        f"  坐标位置: ({e:.2f}, {v:.2f}) — {_describe_quadrant(e, v)}\n"
        f"  BPM 范围: {max(40, bpm_low)} - {min(160, bpm_high)}\n"
        f"  调式建议: {key_advice}\n"
        f"  核心乐器: {instruments}\n"
        f"  编曲策略: {arrangement}"
    )

def _pick_instruments(e: float, v: float) -> str:
    """根据坐标推荐乐器组合。"""
    if e < 0.3:
        if v < -0.3:
            return "钢琴 + 大提琴 + 弦乐（低音区），避免高音乐器"
        elif v < 0.3:
            return "钢琴 + 尼龙弦吉他 + 中提琴，温暖但不燥"
        else:
            return "木吉他 + 钢琴 + 轻弦乐 + 少量铃鼓"
    elif e < 0.6:
        if v < 0:
            return "电钢琴 + 贝斯 + 弦乐 + 轻鼓组，暗色调"
        else:
            return "钢琴/木吉他 + 贝斯 + 弦乐四重奏 + 铃鼓/沙锤"
    else:
        if v < 0:
            return "失真电吉他 + 重型鼓组 + 贝斯 + 合成器"
        else:
            return "电吉他 + 架子鼓 + 贝斯 + 铜管/合成器"


def _format_single_analysis(keyword: str, coord: tuple[float, float], label: str) -> str:
    """格式化单个关键词的分析行。"""
    e, v = coord
    return f"  • {keyword} → ({e:.2f}, {v:.2f}) [{label}]"

def _build_tool_description() -> str:
    """根据 EMOTION_COORDS 自动生成包含可用词表的工具描述。"""
    # 按象限分组
    groups: dict[str, list[str]] = {"A": [], "B": [], "C": [], "D": [], "O": []}
    for word, (e, v) in EMOTION_COORDS.items():
        if e >= 0.35 and v >= 0.2:
            groups["A"].append(word)
        elif e < 0.35 and v >= -0.15:
            groups["B"].append(word)
        elif e < 0.35 and v < -0.15:
            groups["C"].append(word)
        elif e >= 0.35 and v < 0.2:
            groups["D"].append(word)
        else:
            groups["O"].append(word)

    labels = {
        "A": "高能正面", "B": "低能正面",
        "C": "低能负面", "D": "高能负面", "O": "中性",
    }

    parts = [
        "根据中文情绪关键词分析情绪空间坐标，推荐BPM、调式和编曲方向。",
        "传入逗号或空格分隔的情绪词，工具会逐一映射到(能量,效价)二维坐标后给出音乐参数建议。",
        "",
        "支持的情绪词（请优先从中挑选，不要自己编造）：",
    ]
    for group_key in ["A", "B", "C", "D", "O"]:
        if groups[group_key]:
            parts.append(f"  {labels[group_key]}: {' '.join(sorted(groups[group_key]))}")

    return "\n".join(parts)


@tool("TempoMoodTool")
def tempo_mood_tool(mood_keywords: str) -> str:
    """根据中文情绪关键词分析情绪空间坐标，推荐BPM、调式和编曲方向。

    传入逗号或空格分隔的情绪词，工具会逐一映射到(能量,效价)二维坐标后给出音乐参数建议。

    支持的情绪词（请优先从中挑选，不要自己编造）：
    高能正面: 热血 希望 喜悦 力量 激动 欢快 振奋 期待
    低能正面: 释怀 温暖 治愈 内省 宁静 平静 回忆 思念 放松 浪漫
    低能负面: 孤独 忧郁 寂寞 伤感 悲伤 难过 麻木 迷惘 空虚 失落 凄凉 遗憾 无奈 忧伤
    高能负面: 愤怒 绝望 撕裂 挣扎 紧张 焦虑
    中性: 安静 淡然 好奇 自由
    """
    if not mood_keywords or not mood_keywords.strip():
        return (
            "⚠️ 未提供情绪关键词。\n"
            + _recommend(0.35, 0.0)
        )

    # 拆分关键词（支持逗号、中文逗号、空格分隔）
    raw = mood_keywords.replace("，", ",").replace("、", ",").replace(" ", ",")
    keywords = [kw.strip() for kw in raw.split(",") if kw.strip()]

    if not keywords:
        return (
            "⚠️ 无法解析情绪关键词。\n"
            + _recommend(0.35, 0.0)
        )

    # 逐词分析
    coords: list[tuple[float, float]] = []
    analyses: list[str] = []
    unmatched: list[str] = []

    for kw in keywords:
        result = _find_coord(kw)
        if result:
            coord, label = result
            coords.append(coord)
            analyses.append(_format_single_analysis(kw, coord, label))
        else:
            unmatched.append(kw)

    # 有匹配到的词 → 用平均坐标
    if coords:
        avg_e = sum(c[0] for c in coords) / len(coords)
        avg_v = sum(c[1] for c in coords) / len(coords)
    else:
        avg_e, avg_v = 0.35, 0.0  # 默认中性

    # 构建输出
    output = "# 🎭 情绪坐标分析\n\n"
    output += f"输入情绪: {', '.join(keywords)}\n\n"

    if coords:
        output += "## 逐一映射\n"
        output += "\n".join(analyses) + "\n\n"

        # 混合坐标
        output += f"## 混合坐标: ({avg_e:.2f}, {avg_v:.2f}) — {_describe_quadrant(avg_e, avg_v)}\n\n"

    if unmatched:
        output += f"## ⚠️ 未识别: {', '.join(unmatched)}\n"
        output += "(这些词已从平均坐标中排除，不影响整体建议)\n\n"

    output += _recommend(avg_e, avg_v)

    return output


# 用自动生成的描述替换硬编码 docstring，确保词表和 EMOTION_COORDS 始终同步
tempo_mood_tool.description = _build_tool_description()