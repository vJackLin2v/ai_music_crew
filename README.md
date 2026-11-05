# AI Music Crew

基于 [CrewAI](https://crewai.com) Flow 的 **AI 音乐创作流水线**：从选题到可直接投喂 Suno 的成品提示词，中间由多个 Agent 分工完成作词、编曲、审核与产出整理。

## 流水线

```
选题 / 热歌榜
   ↓  brief（歌名 + 曲风线索）
作词 Crew      → 歌词（verse / chorus / bridge / outro）
编曲 Crew      → 乐器配置 + 结构时间线 + 时长
审核 Crew      → verdict 通过/打回（未通过则带反馈重跑，最多 3 轮）
产出 Crew      → Suno Style Prompt + 结构化 post.md
```

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `src/ai_music_crew/main.py` | 主 Flow（状态机 + JSON 解析兜底 + 报告落盘） |
| `src/ai_music_crew/crews/production_crew/` | 作词 / 编曲 / 审核 Crew 的 agents 与 tasks 配置 |
| `src/ai_music_crew/crews/output_crew/` | Suno 提示词产出 Crew |
| `src/ai_music_crew/tools/` | 押韵分析、节奏与情绪分析等本地工具 |
| `skills/` | 风格技能包（古风、周杰伦），`skill.json` + 语料 |
| `knowledge/` | 作词 / 编曲 / 曲式知识库 |
| `hotlist/` | 热歌榜抓取结果（`YYYY-MM-DD.json`） |
| `tools/` | 抓榜、Suno 半自动提交、换声/混音、MV 合成等运维脚本 |
| `app.py` | Streamlit 前端（可选，交互式跑 Flow 并预览产出） |
| `tests/` | 解析器与工具单元测试 |

## 快速开始

需要 Python 3.10–3.13 与 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync                      # 安装依赖
copy .env.example .env       # 填入 OPENAI_API_KEY 等密钥
crewai run                   # 跑 Flow（Windows 下可用 run.ps1 绕过 Defender 对 uv trampoline 的拦截）
uv run streamlit run app.py  # 或走 Web 界面
```

产出写在 `output/<时间戳>_<歌名>/post.md`。

## 说明

仓库只包含代码与文档。模型权重、虚拟环境、生成音频与素材（`tools/seed-vc`、`.musicenv`、`.svc`、`voice`、`assets`、`fonts` 等）不纳入版本管理，见 `.gitignore`。
