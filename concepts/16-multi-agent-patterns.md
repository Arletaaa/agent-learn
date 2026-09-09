# Multi-Agent 协作模式

---

**更新时间**：2026-08-23
**所属阶段**：阶段四 - 关键能力
**掌握程度**：🔵 理解

---

## 概念定义

Multi-Agent 协作是指把一个大任务**拆解为多个子任务**，由多个各司其职的 LLM Agent 通过**顺序 / 并行 / 辩论 / 层级**等协作机制共同完成。本质是"**分而治之 + 专业化**"：每个 Agent 专职、小上下文、单一角色，再用协作机制组合结果。

## 核心要点

1. **存在动机**：单 Agent 有五个边界——上下文窗口有限、角色单一、工具集耦合、串行瓶颈、缺乏第二意见
2. **四种模式**：顺序（流水线）、并行（扇出 + 汇总）、辩论（互审迭代）、层级（主管 + 工人）
3. **核心代价**：token 成本非线性增长、协调开销、错误传播、系统复杂度
4. **选型维度**：拓扑 × 通信方式 × 决策权（静态/动态）× 终止条件

## 工作原理 / 架构

### 为什么需要多 Agent（单 Agent 的边界）

| 边界 | 说明 |
|------|------|
| 上下文窗口有限 | 任务越长、工具返回越多，上下文越拥挤，Agent 越"糊涂"（衔接 token 爆炸问题） |
| 角色单一 | 一个 System Prompt 只能承载一种角色/职责，多角色塞进一个 Prompt 会互相干扰 |
| 工具集耦合 | 工具越多，模型选错工具的概率越高（Function Calling 候选空间变大） |
| 串行瓶颈 | 单循环只能做完一件事再做下一件，无法并行 |
| 缺乏第二意见 | 单 Agent 一次性输出，推理错误难自纠（自反思是弱监督） |

### 四种协作模式

#### 模式一：顺序（Sequential / Pipeline）

- **机制**：Agent A 的输出作为 Agent B 的输入，依次传递，一条链
- **典型**：CrewAI Sequential Process；RAG 的"检索→生成"本质也是顺序
- **适用**：任务有天然先后依赖（调研→分析→写作）
- **优点**：实现最简单、流程可预测、每步可单独调试
- **代价**：总延迟 = 各步之和；无反馈回路，上游错则下游跟着错；单点故障中断全链

#### 模式二：并行（Parallel / Fan-out）

- **机制**：任务拆成多个独立子任务，多个 Agent 同时处理，由汇总者（Aggregator）合并结果
- **典型**：多路检索 + 多角色分析；LangGraph 的 fan-out / fan-in 分支
- **适用**：子任务彼此独立、需要多视角/多来源覆盖、对延迟敏感
- **优点**：吞吐高、延迟只取最慢者；视角互补
- **代价**：结果合并难（冲突怎么裁决？）；汇总 Agent 本身成为新瓶颈；子任务必须真独立，否则重复劳动

#### 模式三：辩论（Debate / Critique）

- **机制**：多个 Agent 就同一问题各自作答，再互相审阅、质疑、修正，多轮迭代收敛
- **典型**：Multi-Agent Debate（Du et al., 2023，数学/事实性任务上两三轮辩论显著提升正确率）；S2-MAD（NAACL 2025，省 token）；Confidence-Guided Adaptive Debate（ICML 2026，按置信度决定辩论轮次）
- **适用**：事实性、推理、决策类任务；需要自我修正的场景
- **优点**：多视角对抗能纠错，推理类任务有实证提升
- **代价**：token 成本成倍（每轮每个 Agent 重读对方观点）；可能陷入重复争论不收敛；必须设定终止条件（轮次上限 / 共识判定）

#### 模式四：层级（Hierarchical / Supervisor）

- **机制**：主管（Orchestrator/Supervisor）负责理解任务、拆解、分派、回收、汇总；下属 Worker 各自执行并回报。主管可动态决定下一步派给谁
- **典型**：Anthropic 多智能体研究系统（Orchestrator-Worker）；LangGraph Supervisor；OpenAI Agents SDK Handoff；CrewAI Hierarchical Process
- **适用**：复杂、目标不明确、需要动态规划的任务
- **优点**：弹性好（加 Worker 即扩展）；主管隔离复杂度；可混合其他模式（主管下面套并行/顺序）
- **代价**：主管是单点——判断错则全系统错；主管上下文会膨胀（要汇总所有子任务结果）；多一层调用多一层延迟和成本

### 编排维度（选型时看什么）

- **拓扑**：链（顺序）/ 扇出（并行）/ 环（辩论）/ 树（层级）——决定 Agent 之间"谁连谁"
- **通信方式**：
  - 共享状态：LangGraph StateGraph，Agent 读写同一状态（显式、可 Checkpoint）
  - 消息传递：AutoGen GroupChat，Agent 互相发消息（对话式，隐式状态在对话历史里）
  - 工具调用：把"调用另一个 Agent"做成一个 tool（如 `research_agent(query)`），主 Agent 决策何时调（低耦合）
  - Handoff：OpenAI Agents SDK，Agent 主动把控制权交给另一个 Agent（控制权转移，类似电话转接）
- **决策权**：静态（拓扑写死，如 CrewAI Sequential）vs 动态（主管/LLM 决定下一步，如 LangGraph Supervisor、OpenAI Handoff）
- **终止条件**：轮次上限 / 达成共识 / 主管判定完成

### 已学框架对照表

| 框架（已学） | 对应模式 | 关键机制 |
|------|------|------|
| CrewAI（project-06） | 顺序 / 层级 | Process = sequential / hierarchical，Task 依赖 |
| AutoGen（project-07） | 辩论 / 对话 | GroupChat + Speaker 选择 + max_round |
| LangGraph（project-05） | 任意拓扑 | StateGraph 节点/边自由编排；官方 Supervisor 库 |
| OpenAI Agents SDK（project-08） | 层级（Handoff） | Agent 间 handoff 委托 + Guardrail |
| Anthropic 工程实践 | 层级（Orchestrator-Worker） | 主管拆任务、Worker 并行、主管汇总 |

## 代码示例

### 顺序模式（纯函数版，无框架依赖）

```python
def agent_research(topic: str) -> str:
    """Agent A：调研"""
    return f"【调研】{topic} 的核心概念：{topic} 是一种……（检索结果）"

def agent_analyze(report: str) -> str:
    """Agent B：分析"""
    return f"【分析】基于调研，关键结论是……（推理结果）"

def agent_write(analysis: str) -> str:
    """Agent C：写作"""
    return f"【成稿】{analysis} 整理为最终报告"

# 顺序模式 = 一条链：A → B → C
pipeline = [agent_research, agent_analyze, agent_write]
result = "多模态模型"
for step in pipeline:
    result = step(result)
print(result)
```

### 层级模式（主管分派，工具调用式通信）

```python
WORKERS = {
    "research": lambda q: f"检索结果：{q}",
    "calculator": lambda e: eval(e),  # 仅示意
    "writer": lambda notes: f"报告：{notes}",
}

def supervisor(task: str):
    """主管：拆解 → 分派 → 汇总（示意循环）"""
    plan = ["research", "calculator", "writer"]  # 真实场景由 LLM 动态生成
    notes = []
    for step in plan:
        notes.append(WORKERS[step](task))
    return " | ".join(notes)  # 主管汇总

print(supervisor("计算 2+2 并写成报告"))
```

## 与其他概念的关系

- 前置概念：ReAct 范式（单 Agent 循环）、Function Calling / Tool Use、Planning 策略、System Prompt 设计
- 相关概念：LangGraph（任意拓扑）、CrewAI（顺序/层级）、AutoGen（对话/辩论）、OpenAI Agents SDK（Handoff）
- 后置概念：Multi-Agent 安全性设计、Human-in-the-Loop、Agent 可观测性

## 常见误区

- **误区一："Agent 越多越聪明"**：多 Agent 是"用更多 token 和协调换能力"，简单任务上单 Agent + 好工具通常更快、更便宜、更稳
- **误区二："四种模式非此即彼"**：生产系统几乎都是混合——主管模式里套并行，辩论里加主管裁决
- **误区三："多 Agent 就能解决长上下文"**：拆任务能缓解，但每个 Agent 仍有自己的上下文上限，任务粒度没拆好照样爆
- **误区四："多 Agent = 并发加速"**：只有并行模式提速；顺序 / 辩论 / 层级通常比单 Agent 更慢（延迟更高）

## 参考资源

- 官方文档：[Anthropic - Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)（多 Agent 系统章节）、[LangGraph Multi-Agent 文档](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)、[LangGraph Supervisor 库](https://github.com/langchain-ai/langgraph-supervisor)、[CrewAI Processes 文档](https://docs.crewai.com/en/concepts/processes)
- 推荐教程：[Anthropic - How We Built Our Multi-Agent Research System](https://www.anthropic.com/engineering/built-multi-agent-research-system)（Orchestrator-Worker 生产实践拆解）
- 相关论文：[Multiagent Debate（Du et al., 2023）](https://arxiv.org/abs/2305.14325)、[S2-MAD（NAACL 2025）](https://aclanthology.org/2025.naacl-long.475/)、[Confidence-Guided Adaptive Debate（ICML 2026）](https://icml.cc/virtual/2026/poster/60593)
