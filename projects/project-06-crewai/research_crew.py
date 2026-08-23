"""
项目六：CrewAI 多 Agent 协作 —— 技术调研流水线

三人团队模拟真实工作流：
  1. 研究员（Researcher）  — 搜索信息
  2. 分析师（Analyst）     — 对比分析
  3. 写作者（Writer）      — 整理为 Markdown 报告

依赖安装：
  pip install crewai crewai-tools langchain-openai langchain-community

运行：
  set DEEPSEEK_API_KEY=sk-xxx
  python research_crew.py
"""
import os
import sys

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def create_llm():
    """DeepSeek LLM"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com",
        temperature=0.3,
    )


def main():
    llm = create_llm()
    search_tool = DuckDuckGoSearchRun()

    # ═════════════════════════════════════════════════════
    #  定义三个 Agent
    # ═════════════════════════════════════════════════════

    researcher = Agent(
        role="资深技术研究员",
        goal="搜索并收集 LangGraph 和 CrewAI 两个 AI Agent 框架的最新信息，"
             "包括各自的核心特点、适用场景、优势劣势",
        backstory="你拥有十年技术调研经验，擅长从多个来源交叉验证信息，"
                  "不放过任何一个重要细节。",
        tools=[search_tool],
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    analyst = Agent(
        role="技术对比分析师",
        goal="基于研究员的数据，从架构设计、学习曲线、灵活性、适用场景"
             "四个维度系统对比 LangGraph 和 CrewAI",
        backstory="你是资深架构师出身，擅长做技术选型对比分析，"
                  "习惯于用表格和结构化方式来呈现对比结果。",
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    writer = Agent(
        role="技术文档写作者",
        goal="将分析结果整理为一份清晰、专业的 Markdown 技术选型报告，"
             "包含对比表格和最终推荐结论",
        backstory="你擅长将复杂技术分析转化为易读的文档，"
                  "注重排版美观和逻辑清晰。",
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    # ═════════════════════════════════════════════════════
    #  定义三个 Task（用 context 传递依赖）
    # ═════════════════════════════════════════════════════

    research_task = Task(
        description=(
            "搜索 LangGraph 和 CrewAI 的最新资料，包括：\n"
            "1. 各自的架构设计理念\n"
            "2. 核心特性的对比（谁更适合什么场景）\n"
            "3. 社区活跃度和学习资源\n"
            "用结构化的方式整理信息。"
        ),
        expected_output=(
            "一份结构化的调研摘要，包含 LangGraph 和 CrewAI "
            "各自的核心特点、适用场景和关键差异点"
        ),
        agent=researcher,
    )

    analysis_task = Task(
        description=(
            "基于研究员的调研结果，从以下四个维度做系统对比：\n"
            "1. 架构设计（图编排 vs 角色扮演）\n"
            "2. 学习曲线（上手难度）\n"
            "3. 灵活性（自定义程度）\n"
            "4. 适用场景（各自最适合什么样的项目）\n"
            "输出一个结构化的对比分析。"
        ),
        expected_output=(
            "包含四个维度详细对比的分析文档，每个维度有明确的结论"
        ),
        agent=analyst,
        context=[research_task],  # ← 关键：依赖研究员的结果
    )

    writing_task = Task(
        description=(
            "基于分析结果，生成一份完整的 Markdown 技术选型报告，要求：\n"
            "1. 开头简述两个框架\n"
            "2. 一个对比表格（至少 6 行 x 3 列）\n"
            "3. 场景推荐（什么情况下选 LangGraph，什么情况下选 CrewAI）\n"
            "4. 最终推荐结论"
        ),
        expected_output=(
            "一份完整的 Markdown 技术选型报告，包含对比表格和推荐结论"
        ),
        agent=writer,
        context=[analysis_task],
    )

    # ═════════════════════════════════════════════════════
    #  组建 Crew 并执行
    # ═════════════════════════════════════════════════════

    print("=" * 60)
    print("  CrewAI 技术调研团队")
    print("=" * 60)
    print(f"\n团队组成：{researcher.role} → {analyst.role} → {writer.role}")
    print(f"协作模式：Sequential（顺序流水线）")
    print(f"研究课题：LangGraph vs CrewAI 技术选型对比")
    print(f"\n{'─' * 60}")

    crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=[research_task, analysis_task, writing_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    # ── 输出最终报告 ──
    print("\n" + "=" * 60)
    print("  最终报告")
    print("=" * 60)
    print(result)

    # ── 可选：保存到文件 ──
    output_path = "report.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(result))
    print(f"\n报告已保存到 {output_path}")


if __name__ == "__main__":
    main()
