"""
项目八：OpenAI Agents SDK —— 客服 Handoff 系统

多 Agent + Handoff 委托：
  - support（客服入口） — 识别意图，移交给专家
  - billing（账单专员） — 处理退款/账单
  - tech（技术专员）   — 处理技术问题

核心机制：
  1. Handoff：控制权整体移交（带走上下文）
  2. function_tool：装饰器自动生成工具 schema
  3. Session：多轮对话记忆
  4. Guardrail：输入护栏

依赖安装：
  pip install openai-agents

运行：
  set DEEPSEEK_API_KEY=sk-xxx
  python support_agent.py
"""
import asyncio
import os
import sys

from agents import Agent, Runner, handoff, function_tool
from agents import Session, InputGuardrail, GuardrailFunctionOutput
from pydantic import BaseModel

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def setup_env():
    """DeepSeek 走 OpenAI 兼容端点，需切换到 Chat Completions 接口"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com/v1"
    # 让 SDK 使用 Chat Completions 而非 Responses API
    os.environ.setdefault("OPENAI_CHAT_COMPLETIONS", "1")
    return api_key


# ═══════════════════════════════════════════════════════
#  工具定义（function_tool 装饰器）
# ═══════════════════════════════════════════════════════

@function_tool
def lookup_order(order_id: str) -> str:
    """根据订单号查询订单状态"""
    return f"订单 {order_id}：已发货，预计 3 天内送达。"


@function_tool
def check_refund_policy(item: str) -> str:
    """查询某类商品的退款政策"""
    return f"{item} 支持 7 天无理由退款，需保留原包装。"


# ═══════════════════════════════════════════════════════
#  专业 Agent 定义
# ═══════════════════════════════════════════════════════

billing_agent = Agent(
    name="账单专员",
    instructions=(
        "你是账单专员，专门处理退款、发票、账单疑问。\n"
        "使用工具查询订单和退款政策，给出准确答复。"
    ),
    tools=[lookup_order, check_refund_policy],
)

tech_agent = Agent(
    name="技术专员",
    instructions=(
        "你是技术专员，处理产品使用、Bug、兼容性等技术问题。\n"
        "给出清晰的技术解答和排查步骤。"
    ),
)

# ═══════════════════════════════════════════════════════
#  入口客服 Agent（含 Handoff）
# ═══════════════════════════════════════════════════════

support_agent = Agent(
    name="客服",
    instructions=(
        "你是客服入口，首先判断用户问题的类型：\n"
        "1. 退款、账单、发票 → 移交给账单专员\n"
        "2. 技术使用、Bug → 移交给技术专员\n"
        "3. 其他简单问题 → 自己回答\n"
        "请用 friendly 的语气接待用户。"
    ),
    handoffs=[billing_agent, tech_agent],
)


# ═══════════════════════════════════════════════════════
#  Guardrail 演示（输入护栏）
# ═══════════════════════════════════════════════════════

class AbuseCheck(BaseModel):
    is_abusive: bool
    reasoning: str


@InputGuardrail
async def refuse_abuse(ctx, agent, input) -> GuardrailFunctionOutput:
    """简单规则：检测明显的辱骂关键词"""
    abusive_words = ["傻逼", "白痴", "混蛋", "滚"]
    is_abusive = any(w in str(input) for w in abusive_words)
    return GuardrailFunctionOutput(
        output_info=AbuseCheck(is_abusive=is_abusive, reasoning="关键词检测"),
        tripwire_triggered=is_abusive,
    )


guarded_support = Agent(
    name="客服（带护栏）",
    instructions=support_agent.instructions,
    handoffs=support_agent.handoffs,
    tools=support_agent.tools,
    input_guardrails=[refuse_abuse],
)


# ═══════════════════════════════════════════════════════
#  演示：Handoff 委托
# ═══════════════════════════════════════════════════════

async def demo_handoff():
    print("=" * 60)
    print("  演示一：Handoff 委托（客服 → 专家）")
    print("=" * 60)

    questions = [
        "我的订单 ABC123 能退款吗？",
        "你们的 App 在我的手机上打不开，怎么办？",
        "你好呀！",
    ]

    for q in questions:
        print(f"\n  👤 用户: {q}")
        result = await Runner.run(support_agent, q)
        print(f"  🤖 处理 Agent: {result.last_agent.name}")
        print(f"  💬 回复: {result.final_output}")


# ═══════════════════════════════════════════════════════
#  演示：Session 多轮对话
# ═══════════════════════════════════════════════════════

async def demo_session():
    print("\n" + "=" * 60)
    print("  演示二：Session 多轮对话记忆")
    print("=" * 60)

    session = Session()
    agent = support_agent

    q1 = "我想问一下退款政策"
    q2 = "那电子产品呢？"  # 依赖上一轮的上下文

    print(f"\n  👤 用户: {q1}")
    r1 = await Runner.run(agent, q1, session=session)
    print(f"  💬 回复: {r1.final_output}")

    print(f"\n  👤 用户: {q2}")
    r2 = await Runner.run(agent, q2, session=session)
    print(f"  💬 回复: {r2.final_output}")
    print("  ↑ 注意：第二问没有重提'退款政策'，Session 自动记住了上下文")


# ═══════════════════════════════════════════════════════
#  演示：Guardrail 护栏
# ═══════════════════════════════════════════════════════

async def demo_guardrail():
    print("\n" + "=" * 60)
    print("  演示三：Guardrail 输入护栏")
    print("=" * 60)

    print(f"\n  👤 用户: 你的产品是垃圾，白痴才会买")
    try:
        result = await Runner.run(guarded_support, "你的产品是垃圾，白痴才会买")
        print(f"  💬 回复: {result.final_output}")
    except Exception as e:
        print(f"  🛡️  护栏拦截：检测到辱骂内容，拒绝响应")
        print(f"  （异常类型: {type(e).__name__}）")


# ═══════════════════════════════════════════════════════
#  主程序
# ═══════════════════════════════════════════════════════

async def main():
    setup_env()

    print("=" * 60)
    print("  OpenAI Agents SDK 客服系统")
    print("=" * 60)
    print("\n架构：")
    print("  客服入口 → [Handoff] → 账单专员")
    print("           → [Handoff] → 技术专员")
    print("  特性：function_tool / Session / Guardrail")

    await demo_handoff()
    await demo_session()
    await demo_guardrail()

    print("\n" + "=" * 60)
    print("  总结")
    print("=" * 60)
    print("""
  OpenAI Agents SDK 的核心原语：
    - Agent      : name + instructions + tools
    - Handoff    : 控制权整体移交（客服 → 专家）
    - Guardrail  : 输入/输出护栏
    - Session    : 多轮对话记忆
    - Runner     : asyncio 运行时

  对比已学的四个框架：
    - LangGraph  : 最灵活（图），代码最多
    - CrewAI     : 角色流水线，最直观
    - AutoGen    : 自由对话 + 代码执行
    - OpenAI SDK : 最简洁，Handoff + 免费 Tracing
  """)


if __name__ == "__main__":
    asyncio.run(main())
