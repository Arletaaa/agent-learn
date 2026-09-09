# Agent Skills（技能封装）

---

**更新时间**：2026-08-23
**所属阶段**：阶段四 - 关键能力
**掌握程度**：🔵 理解

---

## 概念定义

Skill = 把**可复用的任务工作流**封装成结构化指令文件（`SKILL.md` + 可选辅助文件），Agent 在任务匹配时**按名称加载**，获得该任务的完整操作指引。类比：给 Agent 的"**岗位说明书 / 操作手册**"——平时不占地方，需要时翻开照做。

## 核心要点

1. **结构**：`SKILL.md`（YAML frontmatter：`name` + `description`；正文：步骤 / 规则 / 示例）+ 辅助文件（模板、checklist、参考文档、脚本）
2. **触发机制**：`description` 是语义索引——Agent 根据任务判断"该加载哪个 Skill"
3. **按需加载**：不加载就不占上下文（**省 token**），加载后才注入指令
4. **价值**：复用性、输出一致性、上下文节约、团队共享（skills 目录 / registry）
5. **与 Prompt 的区别**：Prompt 是对话上下文里的一段文本，每次都在；Skill 是独立文件包，按需装载、可版本管理、可多人共享

## 工作原理 / 架构

### 目录结构

```
skills/
└── my-skill/
    ├── SKILL.md          # 技能主文件（必需）
    ├── templates/        # 输出模板（可选）
    └── references/       # 参考文档（可选）
```

### SKILL.md 示例

```markdown
---
name: meeting-notes
description: 当用户需要把会议记录整理成结构化纪要时使用。
  适用于：会议录音转写文本、散乱笔记。
  不适用于：写周报、写邮件。
---

# 会议纪要整理

## 步骤
1. 阅读原始材料，提取：主题、决定、行动项（负责人+截止日期）
2. 按模板输出，缺失信息标注 [待确认]
3. 行动项单独成表

## 输出模板
| 主题 | 决定 | 行动项（负责人/截止） |
```

### 加载流程

```
用户任务
   ↓
Agent 语义匹配各 Skill 的 description
   ├─ 命中 → 读取 SKILL.md → 按指引执行
   └─ 未命中 → 不加载，按常规方式处理（省 token）
```

## Skill vs MCP（两者互补，不是替代）

| 维度 | Skill | MCP |
|------|------|-----|
| 回答的问题 | **怎么做**（流程 / 指令知识） | **能做什么**（工具能力接入） |
| 形态 | 指令文件包（SKILL.md） | Client-Server 协议 + 工具 |
| 加载时机 | 任务匹配时按需加载 | 运行时常驻连接 |
| 类比 | 操作手册 | 工具箱 |

**互补关系**：Skill 告诉 Agent 用哪个 MCP 工具、什么顺序、什么格式；MCP 提供工具本身。呼应 `15-rag-agent.md` 的 Skills-guided retrieval——Skill 定义检索流程（用哪个索引、怎么构造查询、引用格式），检索工具（MCP/API）提供执行能力。

> 注：MCP 已在阶段二系统学过（`02-mcp-protocol.md`，project-02-mcp-server，🟢 掌握），此处仅做对照复习。

## 制作一个 Skill 的步骤

1. **选题**：高频、流程稳定、可标准化的任务（写周报、整理会议纪要、代码审查清单……）
2. **写 SKILL.md**：frontmatter（`name` 小写短横线 + `description` 精确描述何时用/何时不用）+ 正文（目标 / 步骤 / 规则 / 示例 / 输出格式）
3. **加辅助文件**：模板、checklist、参考文档
4. **测试迭代**：在真实任务上让 Agent 加载执行——观察是否被正确触发、是否按流程走、输出质量如何
5. **存放与共享**：`skills/<name>/SKILL.md` 目录结构；可发布到 registry 供团队共享

## 常见误区

- **误区一：`description` 随便写** → 触发不准：写太泛，无关任务也加载，浪费 token；写太窄，该用时加载不到。description 是 Skill 的"索引"，要写清楚"何时用 / 何时不用"
- **误区二：Skill 做得越大越全越好** → 加载开销大、指令互相干扰。一个 Skill 只做一件事
- **误区三：把 Skill 当 Prompt 写** → 只写步骤不写"触发条件、判断标准、反例"，Agent 不知道该何时用、用对没有
- **误区四：认为 Skill 会取代 MCP** → 两者互补：Skill 管流程知识，MCP 管工具能力

## 参考资源

- 官方文档：[Claude.ai - Creating custom skills](https://claude.com/docs/skills/how-to)
- 官方博客：[Anthropic - Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- 官方仓库：[anthropics/skills](https://github.com/anthropics/skills)（官方 Skill 集合与规范）
- 相关：[Introducing Agent Skills | Claude](https://claude.com/blog/skills)
