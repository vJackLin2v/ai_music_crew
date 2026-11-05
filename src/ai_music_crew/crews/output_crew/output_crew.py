import os

from crewai import Agent, Crew, LLM, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

# 创建知识源
music_theory_knowledge= TextFileKnowledgeSource(
    file_paths=["music_theory.txt"]    
)

@CrewBase
class OutputCrew:
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
    def suno_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["suno_designer"],
            llm=self._llm(),
            knowledge_sources=[music_theory_knowledge],
        )

    @agent
    def reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["reviewer"],  # type: ignore[index]
            llm=self._llm(),
        )

    @task
    def melody_task(self) -> Task:
        return Task(
            config=self.tasks_config["melody_task"],
            context=[],
        )

    @task
    def editing_task(self) -> Task:
        return Task(
            config=self.tasks_config["editing_task"],  # type: ignore[index]
            context=[self.melody_task()],
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
