"""
项目七：AutoGen 代码 Agent —— 自我验证的编程助手

双 Agent 对话协作：
  - assistant（程序员） — 写代码、解释
  - user_proxy（执行器） — 运行代码、反馈结果

核心机制：代码执行闭环 —— 写代码 → 执行 → 报错反馈 → 修正 → 再执行

依赖安装：
  pip install pyautogen

运行：
  set DEEPSEEK_API_KEY=sk-xxx
  python code_agent.py
"""
import os
import sys

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def create_config():
    """DeepSeek LLM 配置（AutoGen 用 config_list 格式）"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    return {
        "config_list": [
            {
                "model": "deepseek-chat",
                "api_key": api_key,
                "base_url": "https://api.deepseek.com/v1",
            }
        ],
        "temperature": 0,
    }


def demo_two_agent():
    """演示一：双 Agent 代码执行闭环"""
    print("=" * 60)
    print("  演示一：双 Agent 代码执行闭环")
    print("=" * 60)

    config = create_config()

    assistant = AssistantAgent(
        name="assistant",
        system_message=(
            "你是一名资深的 Python 工程师。\n"
            "当用户提出需求时：\n"
            "1. 写出完整可运行的 Python 代码（用 ```python 代码块包裹）\n"
            "2. 代码运行后，根据执行结果验证或修正\n"
            "3. 任务完成后，回复 'TERMINATE' 结束对话"
        ),
        llm_config=config,
    )

    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",            # 全自动，不打断
        max_consecutive_auto_reply=5,        # 最多自动回复 5 轮
        code_execution_config={
            "use_docker": False,             # 本地执行，不用 Docker
            "work_dir": "workspace",          # 代码执行目录
        },
    )

    print("\n任务：写一个函数计算斐波那契数列前 10 项，并运行验证\n")
    print("-" * 60)

    user_proxy.initiate_chat(
        assistant,
        message="写一个函数，计算斐波那契数列前 10 项，并运行验证结果是否正确。",
    )

    print("-" * 60)
    print("对话结束（代码已自动执行并验证）")


def demo_group_chat():
    """演示二：GroupChat 多角色协作"""
    print("\n" + "=" * 60)
    print("  演示二：GroupChat 多角色协作（程序员 + 评审）")
    print("=" * 60)

    config = create_config()

    coder = AssistantAgent(
        name="coder",
        system_message="你是程序员，负责写代码。写完后说 'TERMINATE'。",
        llm_config=config,
    )

    reviewer = AssistantAgent(
        name="reviewer",
        system_message="你是代码评审，审查代码质量，指出问题。确认没问题后说 'TERMINATE'。",
        llm_config=config,
    )

    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        code_execution_config={"use_docker": False, "work_dir": "workspace"},
    )

    groupchat = GroupChat(
        agents=[user_proxy, coder, reviewer],
        messages=[],
        max_round=8,
    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=config,   # Manager 用 LLM 决定每轮谁发言
    )

    print("\n任务：写一个冒泡排序函数，评审代码质量\n")
    print("-" * 60)

    user_proxy.initiate_chat(
        manager,
        message="写一个冒泡排序函数，并请评审代码质量。",
    )

    print("-" * 60)
    print("群聊结束")


def main():
    print("=" * 60)
    print("  AutoGen 代码 Agent 实战")
    print("=" * 60)
    print("\n说明：")
    print("  - 演示一：双 Agent 对话（程序员写代码 → 执行器运行 → 自动修正）")
    print("  - 演示二：GroupChat 群聊（程序员 + 评审 多角色协作）")
    print()

    # 演示一
    demo_two_agent()

    # 演示二
    demo_group_chat()

    print("\n" + "=" * 60)
    print("  总结")
    print("=" * 60)
    print("""
  AutoGen 的核心特点：
    - 对话式协作：Agent 自由发言，而非固定流水线
    - 代码执行闭环：写代码 → 执行 → 报错反馈 → 自动修正
    - GroupChat：多 Agent 群聊，Manager 决定发言顺序

  对比之前学的框架：
    - LangGraph：显式图（最精确，最可控）
    - CrewAI：流水线（角色分工，顺序执行）
    - AutoGen：对话（最自由，涌现协作）
  """)


if __name__ == "__main__":
    main()
