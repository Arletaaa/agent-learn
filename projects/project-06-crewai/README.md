# 项目六：CrewAI 多 Agent 协作 —— 技术调研流水线

---

**开始日期**：2026-08-05
**完成日期**：2026-08-05
**状态**：✅ 已完成
**所属阶段**：阶段三 - 主流框架

---

## 项目目标

用 CrewAI 构建一个**三人技术调研团队**，模拟真实工作流程：

1. **研究员** — 搜索并收集信息
2. **分析师** — 基于信息做对比分析
3. **写作者** — 将分析结果整理为 Markdown 报告

通过这个流水线，理解 CrewAI 的 Agent → Task → Crew 三层模型，以及 Sequential Process 的执行机制。

## 技术栈

- 框架：CrewAI（0.x 最新版）
- LLM：DeepSeek Chat（通过 langchain_openai 适配）
- 工具：DuckDuckGo 搜索

## 核心功能

1. 三个不同角色的 Agent（各有独立 System Prompt）
2. Sequential 流水线：研究员 → 分析师 → 写作者
3. Task 依赖传递（context）
4. 观察每个 Agent 的 Verbose 输出日志

## 运行方式

```bash
# 安装依赖
pip install crewai crewai-tools langchain-openai langchain-community

# 设置 API Key
set DEEPSEEK_API_KEY=sk-xxx

# 运行
python research_crew.py
```

## 相关资源

- 概念文档：[10 - CrewAI 多 Agent 协作](../../concepts/10-crewai-multi-agent.md)
- CrewAI 官方文档：https://docs.crewai.com/
