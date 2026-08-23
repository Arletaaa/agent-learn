# System Prompt 设计方法论

---

**更新时间**：2026-08-22
**所属阶段**：阶段四 - 关键能力
**掌握程度**：🔵 理解

---

## 概念定义

System Prompt（系统提示）是 Agent / LLM 应用的"**底层配置**"，在对话开始前注入模型，定义模型的角色、行为准则、知识范围与输出约束。它是 Agent 的"人格 + 大脑 + 工作手册"。

一句话：**System Prompt = 给模型的"入职培训"，决定它是什么角色、按什么规则工作、输出什么格式。**

## 为什么在 Agent 时代特别重要

普通 LLM 应用中 System Prompt 只是"加一句设定"，但在 Agent 场景下，System Prompt 承担了三个普通对话没有的职责：

1. **工具使用说明书**：告诉模型有哪些工具、每个工具干什么、什么时候调用（工具选择策略）
2. **工作流规则**：规定 Agent 的思考顺序、决策边界、什么情况该停止、什么情况该放弃
3. **输出契约**：要求模型按结构化格式（JSON / 特定模板）输出，供下游程序解析

> 在 Agent 中，System Prompt 就是 Agent 的 **instructions**（OpenAI Agents SDK 中 `Agent(instructions=...)` 本质就是一个 System Prompt）。

## 设计方法：四要素框架

一套完整的 System Prompt 通常由四个部分构成：

```
┌─────────────────────────────────────────────────┐
│  1. 角色定位（Role）      你是谁，服务的对象是谁      │
│  2. 任务与目标（Task）    要完成什么，成功标准是什么   │
│  3. 约束与规则（Rules）   必须遵守什么，禁止做什么     │
│  4. 输出格式（Output）    以什么格式返回结果          │
└─────────────────────────────────────────────────┘
```

### 1. 角色定位

- 明确角色身份：`你是一个资深 Python 工程师`
- 明确服务对象和场景：`你正在为一家电商公司优化订单处理`
- 角色设定会影响模型的语气、专业程度和知识调用倾向

### 2. 任务与目标

- 描述要完成的任务（做什么）
- 明确成功标准（做到什么样算好）
- 必要时给出任务边界（什么范围之外的不做）

### 3. 约束与规则

- **行为规则**：先分析再行动、不确定就承认、不许编造事实
- **安全规则**：不执行危险操作、涉及敏感信息要警告（对应 Agent 的 Guardrail 理念）
- **工具使用规则**：什么时候必须调用工具，而不是凭记忆回答
- **否定式约束往往比肯定式更有效**：明确列出"不要做什么"

### 4. 输出格式

- 要求 JSON / Markdown / 特定模板
- 给出**示例**（比描述更有效）
- Agent 场景下常要求与工具调用的返回格式严格对齐

## 关键技术手段

### 1. Few-shot（少样本示例）

给模型 1~3 个输入输出的完整示例，远比"请你按照……的格式输出"有效：

```
输入: "巴黎天气如何？"
输出: {"city": "paris", "query_type": "weather", "needs_tool": true}

输入: "今天股票涨了吗？"
输出: {"city": null, "query_type": "stock", "needs_tool": true}
```

**要点**：示例要"典型 + 覆盖边界情况"，而不是随便给几个；示例中如果包含错误示范，要标注"这是反面例子"。

### 2. Chain-of-Thought（思维链）

让模型先"想清楚"再"说出来"（给出中间推理步骤），能显著提升复杂任务准确率：

- **做法**：在 System Prompt 中要求模型"一步一步思考"或在输出前先给出推理
- **注意**：需要可解释性时，把推理过程放入 `reasoning` 字段而不是直接暴露给用户
- **警惕**：不能为了强制 CoT 而牺牲输出结构化——最好把"推理"和"最终答案"分开两个字段

### 3. 分层设计

不要把所有规则塞进一个长长的 System Prompt，而是**分层**：

| 层级 | 内容 | 特点 |
|------|------|------|
| 全局层 | 通用安全规则、身份 | 所有对话共享 |
| 任务层 | 本次任务的目标与约束 | 每次任务单独注入 |
| 工具层 | 单个工具的说明书 | 随工具注册附带 |

### 4. 版本管理与迭代

- System Prompt 也要像代码一样版本化（v1 / v2 / ...）
- 用**评估集**（一组固定的测试用例）验证每次改动，防止"改好一个、改坏一片"
- 记录每次改动的影响（哪些场景变好了/变差了）

## 实际示例：一个客服 Agent 的 System Prompt

```
你是一个电商客服助手（Agent），负责解答用户关于订单、退款、物流的问题。

## 工作流程
1. 先判断用户问题类型
2. 涉及订单信息 → 必须调用 lookup_order 工具查询，不要凭记忆回答
3. 涉及退款政策 → 先查 policy 工具，再给结论
4. 超出权限（如投诉升级）→ 移交给人工专员

## 规则
- 不确定的信息必须说明"请以官方查询结果为准"
- 不要编造订单状态、退款金额等事实
- 用户情绪激动时，先共情再解决问题
- 禁止提供退货地址以外的任何敏感信息

## 输出格式
始终返回 JSON：
{
  "reply": "给用户的回复文本",
  "tool_used": "本次是否调用了工具（工具名或 null）",
  "needs_human": false
}
```

## 与其他概念的关系

- **前置概念**：[Message Role](./07-message-role.md)（System Prompt 就是 system 角色的内容）、[Function Calling](./05-function-calling.md)（System Prompt 中的工具使用规则与工具 schema 协同）、[Harness Engineering](./01-harness-engineering.md)（System Prompt 是 harness 给模型注入配置的载体）
- **后置概念**：RAG + Agent（System Prompt 决定检索结果的利用方式）、Agent 安全性（System Prompt 是防御 Prompt Injection 的第一道防线）、结构化输出与验证（System Prompt 是结构化输出的主要手段之一）
- **相关概念**：[OpenAI Agents SDK](./12-openai-agents-sdk.md)（instructions 即 System Prompt）、[ReAct 范式](./04-react-pattern.md)（System Prompt 常指导模型的 ReAct 循环）

## 常见误区

- **误区一："System Prompt 越长越好"**：过长会稀释关键指令、浪费 token、增加模型偏离的概率。原则是"信息密度高、只留必要规则"。
- **误区二："只要把规则写进去，模型就会遵守"**：模型对 Prompt 末尾的内容记忆更强，核心规则应放在开头和结尾；复杂的输出要求必须配 Few-shot 示例。
- **误区三："System Prompt 和 Fine-tuning 二选一"**：二者互补。System Prompt 负责"指挥行为"，Fine-tuning 负责"注入领域知识"。能用 Prompt 解决的优先用 Prompt（成本低、易迭代）。
- **误区四："写一次就固定不变"**：System Prompt 需要随模型版本升级、业务变化持续迭代，并配评估集验证。

## 参考资源

- [OpenAI Prompt Engineering 官方指南](https://platform.openai.com/docs/guides/prompt-engineering) — 官方最佳实践（含策略与战术）
- [Anthropic Prompt Engineering 文档](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) — Claude 提示工程指南
- [Prompt Engineering Guide](https://www.promptingguide.ai/zh) — 中文提示工程手册（Few-shot、CoT 等详解）
- [Chain-of-Thought Prompting 论文](https://arxiv.org/abs/2201.11903) — CoT 开创性工作
- [Anthropic 系统提示实践](https://www.anthropic.com/engineering/building-effective-agents) — Agent 构建中的系统提示实践
