# 项目八：OpenAI Agents SDK —— 客服 Handoff 系统

---

**开始日期**：2026-08-15
**完成日期**：2026-08-15
**状态**：✅ 已完成
**所属阶段**：阶段三 - 主流框架

---

## 项目目标

用 OpenAI Agents SDK 构建一个**客服 Handoff 系统**：

1. 入口客服 Agent（support）—— 识别用户意图
2. 账单专员 Agent（billing）—— 处理退款/账单
3. 技术专员 Agent（tech）—— 处理技术问题

核心体验：**Handoff 委托机制** —— 客服遇到专业问题时，把对话控制权整体移交给对应专家。

## 技术栈

- 框架：OpenAI Agents SDK（`openai-agents`）
- LLM：DeepSeek Chat（兼容端点）

## 核心功能

1. 多 Agent + Handoff 路由
2. function_tool 工具定义
3. Session 多轮对话
4. Guardrail 输入护栏演示

## 运行方式

```bash
# 安装依赖
pip install openai-agents

# 设置 API Key
set DEEPSEEK_API_KEY=sk-xxx

# 运行
python support_agent.py
```

## 相关资源

- 概念文档：[12 - OpenAI Agents SDK](../../concepts/12-openai-agents-sdk.md)
- 官方文档：https://openai.github.io/openai-agents-python/
