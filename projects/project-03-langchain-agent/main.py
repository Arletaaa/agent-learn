"""
项目三：LangChain Agent + 真实搜索
对比项目一（手写 ReAct Agent），感受 Function Calling 和框架的力量

依赖安装：
  pip install langchain-openai langgraph tavily-python

运行：
  set DEEPSEEK_API_KEY=sk-xxx
  set TAVILY_API_KEY=tvly-xxx
  python main.py
"""
import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import sys

# 修复 Windows 中文终端编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def create_deepseek_llm():
    """用 DeepSeek API 创建 LLM（走 OpenAI 兼容接口）"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("请设置环境变量 DEEPSEEK_API_KEY")

    return ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        temperature=0,
    )


def create_search_tool():
    """创建真实 Web 搜索工具"""
    tavily_key = os.environ.get("TAVILY_API_KEY")

    if tavily_key:
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
            search_api = TavilySearchAPIWrapper(tavily_api_key=tavily_key)
            print("✅ 使用 Tavily 搜索（AI 优化）\n")
            return TavilySearchResults(api_wrapper=search_api, max_results=3)
        except ImportError:
            print("⚠️  Tavily 未安装，回退到 DuckDuckGo")

    # DuckDuckGo 搜索（免费，不需要 API Key）
    from langchain_community.tools import DuckDuckGoSearchRun
    print("✅ 使用 DuckDuckGo 搜索（免费）\n")
    return DuckDuckGoSearchRun()


def main():
    print("=" * 60)
    print("  LangChain ReAct Agent (DeepSeek + Web Search)")
    print("=" * 60)

    # 1. 创建 LLM
    llm = create_deepseek_llm()

    # 2. 创建工具
    search = create_search_tool()
    tools = [search]

    # 3. 创建 Agent（这就是框架帮你做的事——一行代码代替你的 159 行）
    agent = create_react_agent(model=llm, tools=tools)

    print("\n使用说明：")
    print("  - 输入问题让 Agent 自动搜索 + 回答")
    print("  - 输入 'quit' 退出")
    print("  - 观察 LLM 返回的 tool_calls（JSON），对比手写版的正则解析")
    print()

    while True:
        try:
            question = input("\n📝 请输入问题: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue

        # 4. 运行 Agent（invoke 自动处理循环、工具调用、结果汇总）
        print(f"\n{'=' * 60}")
        print("  Agent 开始工作...")
        print(f"{'=' * 60}\n")

        result = agent.invoke(
            {"messages": [("user", question)]},
            config={"recursion_limit": 10},  # 最多 10 步
        )

        # 5. 打印所有中间步骤（观察 Agent 的思考过程）
        for msg in result["messages"]:
            # 跳过 System Prompt
            if hasattr(msg, "type") and msg.type == "system":
                continue

            role = getattr(msg, "type", "unknown")

            if role == "human":
                print(f"👤 你: {msg.content}")

            elif role == "ai":
                # AI 消息可能包含 content（文本回答）和 tool_calls（工具调用）
                if hasattr(msg, "content") and msg.content:
                    print(f"🤖 AI: {msg.content}")

                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"🔧 调用工具: {tc['name']}({tc['args']})")
                        print(f"   ↑ 这就是 Function Calling —— 精确的 JSON")

            elif role == "tool":
                # 工具返回结果（Observation）
                tool_name = getattr(msg, "name", "unknown")
                print(f"👁  搜索结果 ({tool_name}): {str(msg.content)[:200]}...")

            print()

        print(f"{'=' * 60}")
        print("  Agent 工作完成")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
