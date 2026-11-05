import os

from crewai import Agent, Crew, LLM, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from ai_music_crew.tools import tempo_mood_tool, RhymeAnalyzerTool

from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

# 创建知识源
music_theory_knowledge= TextFileKnowledgeSource(
    file_paths=["music_theory.txt"]    
)
lyrics_tips_knowledge = TextFileKnowledgeSource(
    file_paths=["chinese_lyrics_tips.txt"]
)
song_structure_knowledge = TextFileKnowledgeSource(
    file_paths=["song_structure.txt"]
)
arrangement_tips_knowledge = TextFileKnowledgeSource(
    file_paths=["arrangement_tips.txt"]
)

@CrewBase
class ProductionCrew:
    agents: list[BaseAgent]
    tasks: list[Task]
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def _llm(self) -> LLM:
        return LLM(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
            temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
        )

    @agent
    def music_director(self) -> Agent:
        return Agent(
            config=self.agents_config["music_director"],  # type: ignore[index]
            llm=self._llm(),
            tools=[tempo_mood_tool],
            knowledge_sources=[music_theory_knowledge, song_structure_knowledge]
        )

    @agent
    def lyricist(self) -> Agent:
        return Agent(
            config=self.agents_config["lyricist"],  # type: ignore[index]
            llm=self._llm(),
            tools=[RhymeAnalyzerTool()],
            knowledge_sources=[lyrics_tips_knowledge],
        )
    
    @agent
    def arranger(self) -> Agent:
        return Agent(
            config=self.agents_config["arranger"],
            llm=self._llm(),
            knowledge_sources=[arrangement_tips_knowledge, music_theory_knowledge],
        )
    
    @task
    def planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["planning_task"],  # type: ignore[index]
        )

    @task
    def writing_task(self) -> Task:
        return Task(
            config=self.tasks_config["writing_task"],  # type: ignore[index]
            context=[self.planning_task()],
        )

    @task
    def arrangement_task(self) -> Task:
        return Task(
            config=self.tasks_config["arrangement_task"],
            context=[self.planning_task(), self.writing_task()],
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            embedder={
                "provider": "onnx",
            }
        )
