# 开发笔记

## 设计思路

项目延续"对比学习"的思路——同一个任务两种实现，差异只在编排层。

## 核心发现

### 1. 手写图 = 显式控制流

```python
graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")
```

每一步都看得见：谁调用谁、条件怎么判断、数据怎么传。适合需要精细控制的场景（如条件复杂的多分支 Agent）。

### 2. create_react_agent = 隐式标准循环

```python
agent = create_react_agent(llm, tools, checkpointer=memory)
```

底层就是上面的 3 节点图。适合标准 ReAct Agent 场景——省掉样板代码，专注 Prompt 和工具设计。

### 3. Checkpointer = 自动记忆管理

不用手动拼接 messages 列表了。同一个 `thread_id` 就是同一个对话，历史自动保留。这解决了项目一/三中手动管理上下文的痛点。

### 4. 流式输出 = 节点级粒度

```python
for event in app.stream(input, config):
    for node_name, output in event.items():
        # 每个节点完成时触发一次
```

比 callback 直观，适合做进度展示（"AI 正在搜索..."→"AI 正在思考..."）。

## 对比感受

| 维度 | 手写 StateGraph | create_react_agent |
|------|----------------|--------------------|
| 代码量 | ~80 行 | ~5 行 |
| 灵活性 | 完全可控 | 受限于规范 |
| 学习价值 | 理解底层 | 快速上手 |
| 生产推荐 | 自定义 Agent | 标准 ReAct Agent |

## 后续延伸

- 用 LangGraph 实现 Plan-and-Execute 图（项目四的策略对比）
- 用 Subgraph 实现多 Agent 协作
- 添加 interrupt 实现 Human-in-the-Loop
