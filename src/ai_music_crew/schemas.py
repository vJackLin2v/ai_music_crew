"""核心数据结构 —— 定义 Agent 之间传递的强类型对象。"""

from pydantic import BaseModel, Field


class SongBrief(BaseModel):
    """音乐导演产出的歌曲创作简报"""
    title_suggestion: str = Field(
        ..., description="歌曲标题建议，如 '夜色释怀'"
    )
    theme: str = Field(
        ..., description="核心主题，一句话概括这首歌要讲什么"
    )
    mood_keywords: list[str] = Field(
        ..., description="情绪关键词列表，如 ['孤独', '释怀', '安静']"
    )
    bpm_range: str = Field(
        ..., description="推荐 BPM 范围，如 '65-78'"
    )
    key_suggestion: str = Field(
        ..., description="推荐调式，如 'G大调' 或 'A小调'"
    )
    style_direction: str = Field(
        ..., description="风格方向，如 '独立民谣/氛围流行'"
    )
    vocal_advice: str = Field(
        ..., description="人声建议，如 '气声为主，副歌可转真声'"
    )
    lyric_imagery_keywords: list[str] = Field(
        ..., description="歌词意象关键词，如 ['街灯', '影子', '便利店', '月光']"
    )
    avoid_directions: list[str] = Field(
        ..., description="需要避免的方向，如 ['不要直白抒情', '避免强鼓点']"
    )
    arrangement_tips: str | None = Field(
        default=None, description="编曲建议，可选"
    )


class Lyrics(BaseModel):
    """作词人产出的歌词"""
    verse_1: str = Field(
        ..., description="主歌 Verse 1，4-8行，负责建立场景和叙事"
    )
    chorus: str = Field(
        ..., description="副歌 Chorus，4-6行，情绪释放和记忆点"
    )
    verse_2: str = Field(
        ..., description="主歌 Verse 2，4-8行，推进故事或增加回忆/矛盾"
    )
    bridge: str | None = Field(
        default=None, description="桥段 Bridge，2-6行，情绪转折或顿悟，可选"
    )
    outro: str | None = Field(
        default=None, description="尾奏歌词，1-2行淡出，可选"
    )
    creation_notes: str = Field(
        ..., description="创作说明，解释歌词如何回应用户需求"
    )
    rhyme_rate: int | None = Field(
        default=None, description="押韵率（百分比，如果使用韵脚分析工具检查过）"
    )

class ArrangementPlan(BaseModel):
    """编曲人产出的编曲方案"""
    instruments: list[str] = Field(
        ..., description="使用的主要乐器列表，如 ['钢琴', '大提琴', '二胡', '铃鼓']"
    )
    structure_timeline: str = Field(
        ...,
        description=(
            "按时间线描述每个段落的编曲安排。"
            "格式示例：'前奏(0:00-0:25) 钢琴独奏引入 → "
            "主歌A(0:25-0:55) 加入大提琴铺底，钢琴分解和弦 → "
            "副歌(0:55-1:25) 全编制进入，鼓组轻入，弦乐铺满'"
        ),
    )
    dynamics_plan: str = Field(
        ...,
        description=(
            "音量/情绪动态规划。描述整首歌的强弱起伏，"
            "如 '前奏 pp → 主歌 p → 副歌 mf → 桥段 mp → 最后副歌 f → 尾奏 pp'"
        ),
    )
    mixing_notes: str = Field(
        ...,
        description=(
            "混音建议。包括：各乐器在声场中的位置（左右声道分布）、"
            "主次关系（人声在前/乐器在后）、重点频段处理建议"
        ),
    )
    sfx_suggestions: str | None = Field(
        default=None,
        description="环境音效建议，如 '桥段加入旧木板咯吱声' 或 '尾奏加入渐远的脚步声'",
    )
    total_duration: str = Field(
        ..., description="预计总时长，如 '3分45秒'"
    )

class MelodyNote(BaseModel):
    """单个旋律音符"""
    pitch: str = Field(..., description="音高，如 'G4', 'A4', 或 'rest'（休止）")
    duration: float = Field(..., description="时值，四分音符为 1.0，八分音符为 0.5")
    syllable: str = Field(..., description="对应的歌词字，休止符留空")

class MelodyOutput(BaseModel):
    """旋律设计师产出的旋律 + 和弦"""
    chord_progression: dict = Field(
        ...,
        description="和弦进行，如 {'verse': ['G','D','Em','C'], 'chorus': ['Em','C','G','D']}"
    )
    melody: dict = Field(
        ...,
        description=(
            "按歌词段落组织的旋律音符。格式: "
            "{'verse_1': [{'pitch':'G4','duration':0.5,'syllable':'街'}, ...], "
            "'chorus': [...], 'verse_2': [...], 'bridge': [...] | null, 'outro': [...] | null}"
        ),
    )


class ReviewReport(BaseModel):
    """审核人产出的审核报告"""
    verdict: str = Field(
        ..., description="审核判决，只能是 '通过' 或 '需要修改'"
    )
    strengths: list[str] = Field(
        ..., description="符合用户需求的地方，至少列出 3 条"
    )
    issues: list[str] = Field(
        ..., description="存在的问题，如果判决为'通过'可以为空列表"
    )
    suggestions: list[str] = Field(
        ..., description="具体修改建议，如果判决为'通过'可以为空列表"
    )
    next_direction: str = Field(
        ..., description="下一版可以强化的方向，一句话概括"
    )
    score: int | None = Field(
        default=None, description="综合评分 1-10，可选"
    )
