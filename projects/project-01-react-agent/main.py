"""
从零手写 ReAct Agent
不依赖任何 Agent 框架，使用 DeepSeek API 驱动
"""
import re
import os
import requests


class ReActAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        self.max_steps = 10

        self.tools = {
            "search": self._search,
            "calculator": self._calculator,
        }

    def _search(self, query):
        knowledge = {
            "react": "ReAct 是 Yao 等人于 2022 年提出的框架，全称 Reasoning + Acting，让 LLM 以交替方式生成推理轨迹和任务操作，是 Agent Loop 的核心范式。",
            "mcp": "MCP（Model Context Protocol）是 Anthropic 发布的开放协议，为 AI 模型与外部工具之间提供标准化的 Client-Server 接口。",
            "deepseek": "DeepSeek 是中国公司深度求索推出的大语言模型，API 兼容 OpenAI 格式，支持 chat 和 reasoning 两种模型。",
            "langchain": "LangChain 是目前最成熟的 LLM 应用开发框架，提供 Chain（固定流程）和 Agent（动态决策）两种模式。",
            "北京": "北京市常住人口约 2184 万（2023 年），面积 16410 平方公里。",
            "python": "Python 由 Guido van Rossum 于 1991 年首次发布，是最流行的编程语言之一。",
        }
        for key, value in knowledge.items():
            if key in query.lower():
                return value
        return f"搜索 '{query}'：未找到相关信息。"

    def _calculator(self, expression):
        try:
            allowed = {"abs": abs, "round": round, "min": min, "max": max,
                       "pow": pow, "int": int, "float": float}
            result = eval(expression, {"__builtins__": allowed}, {})
            return f"计算结果：{expression} = {result}"
        except Exception as e:
            return f"计算错误：{e}"

    def _system_prompt(self):
        return """你是一个能够使用工具的 AI Agent，通过 ReAct 范式工作：

可用工具：
- search(query): 搜索知识库，参数 query 为搜索关键词
- calculator(expression): 执行数学计算，参数 expression 为数学表达式

请严格按照以下格式回复，每一步都必须包含 Thought：

Question: 用户的问题
Thought: 我当前的分析和推理
Action: 要使用的工具名称（search 或 calculator）
Action Input: 工具的参数

当你确认已经得到最终答案时：
Thought: 我现在已经获取了所有需要的信息
Final Answer: 最终答案（用中文回答）"""

    def _call_llm(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _parse_output(self, text):
        thought = re.search(r"Thought:\s*(.+?)(?:\n\s*(?:Action|Final)|$)", text, re.DOTALL)
        action = re.search(r"Action:\s*(.+?)(?:\n|$)", text)
        action_input = re.search(r"Action Input:\s*(.+)", text)
        final = re.search(r"Final Answer:\s*(.+)", text, re.DOTALL)

        return {
            "thought": thought.group(1).strip() if thought else None,
            "action": action.group(1).strip() if action else None,
            "action_input": action_input.group(1).strip() if action_input else None,
            "final_answer": final.group(1).strip() if final else None,
        }

    def run(self, question):
        messages = [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": f"Question: {question}"},
        ]

        for step in range(self.max_steps):
            print(f"\n{'=' * 60}")
            print(f"  Step {step + 1}")
            print(f"{'=' * 60}")

            raw = self._call_llm(messages)
            parsed = self._parse_output(raw)

            print(f"\n  [LLM 响应]")
            print(f"  {raw}")

            if parsed["final_answer"]:
                print(f"\n{'=' * 60}")
                print(f"  ✅ 最终答案: {parsed['final_answer']}")
                print(f"{'=' * 60}")
                return parsed["final_answer"]

            thought = parsed["thought"]
            action = parsed["action"]
            action_input = parsed["action_input"]

            if not action:
                print(f"\n  ⚠️  LLM 未正确调用工具")
                return raw

            tool = self.tools.get(action.strip().lower())
            if tool is None:
                observation = f"错误：未知工具 '{action}'，可用工具：search, calculator"
            else:
                observation = tool(action_input)
                print(f"\n  🔧 Tool: {action}({action_input})")
                print(f"  👁  Result: {observation}")

            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"Observation: {observation}"})

        return "已达到最大执行步数，未得出最终答案。"


if __name__ == "__main__":
    agent = ReActAgent()
    if not agent.api_key:
        print("请设置环境变量 DEEPSEEK_API_KEY")
        exit(1)

    print("=" * 60)
    print("  ReAct Agent (DeepSeek)")
    print("  可用工具: search, calculator")
    print("  输入 'quit' 退出")
    print("=" * 60)

    while True:
        try:
            question = input("\n📝 请输入问题: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue

        agent.run(question)
