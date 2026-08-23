# 开发笔记

## 设计思路

模拟一个真实的技术调研团队流水线：研究员收集信息，分析师做对比推理，写作者格式化输出。

刻意选择了一个简单但不琐碎的主题（LangGraph vs CrewAI 对比），让每个 Agent 都有实质工作可做。

## 关键实现

### Agent 定义

```python
Agent(role="...", goal="...", backstory="...", tools=[...], llm=llm)
```

三个属性的作用：
- `role` → 前半句 System Prompt
- `goal` → 后半句 System Prompt
- `backstory` → 补充上下文，让角色更立体

CrewAI 内部将这三者拼接成完整的 System Prompt，注入到 LLM 调用中。

### Task 依赖

```python
task2 = Task(..., context=[task1])
```

CrewAI 自动把 task1 的输出作为 task2 的上下文注入 Prompt。不需要手动拼接字符串。

### Sequential vs Hierarchical

本次使用 Sequential（顺序执行）。如果改用 Hierarchical，CrewAI 会自动生成一个 Manager Agent，让它根据 Agent 的 role 动态分配任务。顺序执行的好处是可预测、可调试。

## 遇到问题

1. **CrewAI v0.x API 变化**：旧版用 `agent=agent`，新版本可能改名。需确认安装版本。
2. **DeepSeek 兼容性**：CrewAI 默认用 OpenAI 的 LLM 接口，走 langchain_openai 的 ChatOpenAI 适配 DeepSeek 没问题。

## 对比感受

相比 LangGraph 的手写图，CrewAI 的"角色扮演+任务分配"更贴近人类对团队协作的直觉：
- 你不用想"图的结构是什么样的"
- 你只需想"我需要什么角色、他们分别做什么、结果怎么传递"

代价是灵活性——如果任务不是线性的流水线，CrewAI 就力不从心了。

## 后续延伸

- 用 Hierarchical Process 让 Manager 自动分配任务
- 给 Agent 添加真实工具（爬虫、代码执行器）
- 与 LangGraph 组合：CrewAI 管理高层角色，LangGraph 管理底层循环
