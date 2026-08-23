# 开发笔记

## 设计思路

三种策略统一使用相同的 `call_llm()` 底层函数，差异只在编排逻辑上。这样可以公平对比 Token 消耗。

## 关键实现

### ReAct

- 循环：while 步数 < 上限 → LLM(Thought+Action) → 执行工具 → Observation → 下一轮
- 终止：LLM 返回 Finish Action 或达到步数上限

### Plan-and-Execute

- 第 1 次 LLM 调用：生成步骤计划（JSON 格式）
- 按计划顺序执行工具
- 第 2 次 LLM 调用：基于所有步骤结果综合生成最终答案

### Reflexion

- Actor 使用 ReAct 执行任务
- Evaluator LLM 判断结果是否 PASS/FAIL
- 如果 FAIL，Reflection LLM 分析原因并生成改进建议
- Actor 带着反思重新执行（最多 3 次）

## 经验总结

1. **Token 消耗**：Reflexion >> ReAct > Plan-and-Execute，差距可达 3~5 倍
2. **输出质量**：Reflexion 在需要多步推理的任务上质量最好，因为能自我纠错
3. **响应速度**：Plan-and-Execute 最快（仅 2 次 LLM 调用），ReAct 中等，Reflexion 最慢
4. **适用场景匹配**：不要盲目用复杂的策略，务实的 ReAct 能解决 80% 的问题

## 潜在改进

- 添加 ReWOO 实现以对比并行执行的效率
- 使用真实的 Tavily 搜索工具替代模拟工具
- 增加多任务基准测试（而非单一案例）
