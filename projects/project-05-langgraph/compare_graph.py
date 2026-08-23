"""
项目五：LangGraph Agent 手写图 vs 预制库对比

两种方式实现同一搜问答 Agent：
  1. 手写 StateGraph  — 理解底层节点/边/条件机制
  2. create_react_agent — 感受框架带来的效率提升

依赖安装：
  pip install langgraph langchain-openai langchain-community

运行：
  set DEEPSEEK_API_KEY=sk-xxx
  set TAVILY_API_KEY=tvly-xxx
  python compare_graph.py
"""
import os
import sys

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def create_llm():
    """创建 DeepSeek LLM（OpenAI 兼容接口）"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com",
        temperature=0,
    )


def create_search_tool():
    """创建 Web 搜索工具（Tavily 优先，fallback 到 DuckDuckGo）"""
    tavily_key = os.environ.get("TAVILY_API_KEY")
    if tavily_key:
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            print("工具: Tavily Search (AI 优化)")
            return TavilySearchResults(max_results=2)
        except ImportError:
            pass
    from langchain_community.tools import DuckDuckGoSearchRun
    print("工具: DuckDuckGo Search (免费)")
    return DuckDuckGoSearchRun()


# ═══════════════════════════════════════════════════════════
#  方式一：手写 StateGraph（手动定义节点/边/条件）
# ═══════════════════════════════════════════════════════════

def build_manual_agent(llm, tools):
    """手写 StateGraph Agent 的完整构建过程"""
    tool_node = ToolNode(tools)
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: MessagesState):
        """Agent 节点：LLM 推理，决定调用工具还是直接回答"""
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def should_call_tools(state: MessagesState) -> str:
        """条件边：最后一条消息是否包含 tool_calls"""
        last_msg = state["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            return "tools"
        return "__end__"

    # 构建图
    graph = StateGraph(MessagesState)

    # 添加节点
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    # 添加边
    graph.add_edge(START, "agent")                              # 入口 → agent
    graph.add_conditional_edges("agent", should_call_tools)     # agent 有条件跳出
    graph.add_edge("tools", "agent")                            # 工具 → 回到 agent

    return graph


# ═══════════════════════════════════════════════════════════
#  方式二：create_react_agent（一行代码）
# ═══════════════════════════════════════════════════════════

def build_prebuilt_agent(llm, tools, checkpointer):
    """预制 ReAct Agent —— 底层就是个 StateGraph"""
    return create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=checkpointer,
    )


# ═══════════════════════════════════════════════════════════
#  多轮对话测试
# ═══════════════════════════════════════════════════════════

def test_multi_turn(app, thread_name):
    """测试多轮对话——同一 thread_id 共享记忆"""
    config = {"configurable": {"thread_id": thread_name}}

    questions = [
        "LangGraph 是什么？用一句话说明。",
        "它和 LangChain 的 Chain 最大的区别是什么？",
    ]

    for q in questions:
        print(f"\n  👤 用户: {q}")
        result = app.invoke({"messages": [HumanMessage(content=q)]}, config)
        last_msg = result["messages"][-1]
        print(f"  🤖 AI: {last_msg.content[:150]}...")


def test_streaming(app, thread_name):
    """测试流式输出——观察节点执行顺序"""
    config = {"configurable": {"thread_id": thread_name}}
    question = "今天北京天气怎么样？"

    print(f"\n  👤 用户: {question}")
    print(f"  ┌─ 流式输出（节点级）─┐")

    for event in app.stream(
        {"messages": [HumanMessage(content=question)]}, config
    ):
        for node_name, output in event.items():
            msgs = output.get("messages", [])
            for m in msgs:
                if hasattr(m, "tool_calls") and m.tool_calls:
                    for tc in m.tool_calls:
                        print(f"  │ [{node_name}] 🔧 调用: {tc['name']}({tc.get('args', {})})")
                elif hasattr(m, "content") and m.content:
                    preview = m.content[:80].replace("\n", " ")
                    print(f"  │ [{node_name}] 💬 {preview}")

    print(f"  └─────────────────────┘")


# ═══════════════════════════════════════════════════════════
#  主程序
# ═══════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  LangGraph 手写 vs 预制 Agent 对比")
    print("=" * 60)

    llm = create_llm()
    tools = [create_search_tool()]
    checkpointer = MemorySaver()

    # ── 方式一：手写图 ──
    print("\n" + "─" * 60)
    print("  方式一：手写 StateGraph")
    print("─" * 60)
    print("  图结构: START → agent → [conditional] → tools → agent (循环)")
    print("  关键点: 你手动定义了 agent_node, tool_node, should_call_tools")

    manual_graph = build_manual_agent(llm, tools)
    manual_app = manual_graph.compile(checkpointer=checkpointer)
    test_multi_turn(manual_app, "manual-session")

    # ── 方式二：预制 Agent ──
    print("\n" + "─" * 60)
    print("  方式二：create_react_agent（预制）")
    print("─" * 60)
    print("  关键点: 一行代码 = 上面的全部节点/边定义")

    prebuilt_app = build_prebuilt_agent(llm, tools, checkpointer)
    test_multi_turn(prebuilt_app, "prebuilt-session")

    # ── 流式输出对比 ──
    print("\n" + "─" * 60)
    print("  流式输出对比（使用预制 Agent）")
    print("─" * 60)
    test_streaming(prebuilt_app, "stream-session")

    # ── 总结 ──
    print("\n" + "=" * 60)
    print("  总结")
    print("=" * 60)
    print("""
  两种方式的内核是完全一样的：

      手工图         预制 library
      ──────         ────────────
  StateGraph  ←→  create_react_agent
  add_node    ←→  (内置 agent + tools 节点)
  add_edge    ←→  (内置 START→agent 边)
  conditional ←→  (内置 should_continue)
  compile     ←→  自动编译

  LangGraph 让你选择：
    - 想理解机制？手写图
    - 想快速迭代？用预制库
    - 都不是二选一——你可以从预制开始，
      需要自定义时再拆解成手写图
  """)


if __name__ == "__main__":
    main()
