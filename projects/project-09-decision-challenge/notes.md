# 开发笔记：project-09-decision-challenge

**开始日期**：2026-08-23

## 项目缘起

- 学完 Agent Skills（`17-agent-skills.md`）后，用户在引导问题 S-Q4 提出：想做一个"做决策时不让 LLM 偏向讨好自己"的 Skill
- 该现象在学界称 **sycophancy（谄媚/迎合）**，已有专门研究
- 用户找到一份三阶段提示词参考，本项目核心工作 = 把这份提示词**结构化为规范的 SKILL.md**

## 设计思路

1. **保留用户参考文本的骨架**：三阶段（最强反方 → 最强正方 → 中立裁判）设计质量很高，SKILL.md 主体保留其原意与措辞
2. **按 Skill 规范补全**：
   - frontmatter：`name`（decision-challenge）+ `description`（何时用 / 何时不用——不适用于纯事实查询、琐碎选择、情绪倾诉）
   - 硬性规则：禁奉承开头、事实/观点/推测标注、置信度、证据不足明说、裁决权只归第三阶段
   - 输出模板：结构化 Markdown，便于审查与前后对比
   - 输入确认：用户未说明倾向时先询问（没有"靶子"的质询是无的放矢）
3. **渐进式披露**：SKILL.md 只留核心规则，完整实战示例放 `references/worked-examples.md`

## 与今日所学关联

- **三阶段 ≈ 单 Agent 内模拟"多角色辩论"**：反方 / 正方 / 裁判 ≈ `16-multi-agent-patterns.md` 的辩论模式（Debate）
- 好处：不用真的启动 3 个 Agent（省 token、无协调开销），把辩论**折叠进一次结构化输出**——这正是 Skill 的价值：流程知识不依赖框架
- 为什么角色切换能对抗谄媚：它强制模型在给出结论前先**构造反对证据**（类似 ReAct 的 Thought 先行 + 结构化约束）

## 迭代记录

- **v1（2026-08-23）**：从用户参考文本结构化，创建 SKILL.md + 项目骨架
- **首测（2026-08-23）**：真实决策案例（HD490 Pro vs HD660S2 听 ACG）跑通三阶段
  - 反谄媚 ✅（用户：没有讨好/没有故意唱反调）
  - 反方在用户论证的"错误前提"上反驳（660S2"不适合人声"与主流听感相悖），而非顺着倾向
  - 用户反馈：输出偏长 → 触发 v2
- **v2（2026-08-23）**：首测后迭代，改动：
  - 硬性规则新增 **7 长度约束**（总输出 ≤ 600 字，每条要点一句话，禁止散文）
  - 硬性规则新增 **8 裁决落地**（必须给条件性结论 + 反转条件，点名缺失信息，禁止"取决于你自己"式敷衍）
  - 输出模板压缩：反方 ≤ 5 条、正方 ≤ 3 条、裁判固定 4 行
- **待办**：用 v2 复测一次，验证长度约束是否生效、裁决是否仍诚实
- **对比实验（2026-08-23）**：同一决策（HD490 Pro vs HD660S2）跑有 Skill vs 无 Skill，完整数据见 `test/comparison.md`
  - 成本：首次 ≈7.8×（大头是 SKILL.md 加载 ≈1036 token，占 72%）；同会话摊销后 ≈1.9×；输出 2.6×
  - 质量：无 Skill 顺着倾向、强化错误前提（"你的判断有道理…暖糊不适合 ACG"）；有 Skill 反驳论证前提、标注不确定（中）、点名未知变量、给反转条件
  - **核心结论**：两版本知识无差，差异在"敢不敢反驳 + 是否诚实标注不确定"→ 反谄媚本质是**输出约束问题**，不是模型聪明度问题
  - ✅ 附带完成 v2 复测：输出 462 字符 < 600 字约束生效；裁决点名缺失信息（曲库构成）+ 反转条件
- **v3 + 发布（2026-08-23）**：
  - v3 完善点：`description` 增加触发关键词（倾向/纠结/该不该/买不买/换不换/选 A 还是 B）；新增硬性规则 ⑨ 决策权归用户；正文开头加定位句"不是来赞同的，也不是来唱反调的"；`worked-examples.md` 补全完整实战示例（含无 Skill 朴素回答对比）
  - 打包独立仓库 `G:\MyProjects\agent-skills`（MIT License），结构 `skills/decision-challenge/`（SKILL.md + references/）
  - 推送 GitHub：https://github.com/Arletaaa/agent-skills （Public）
  - 待办：skills.sh 注册（GitHub 验证后跟进）；在 Claude Code 环境实测触发
- **skills.sh 注册（2026-08-23，进行中）**：
  - ✅ 前提已满足：仓库 Public + MIT LICENSE + `SKILL.md` frontmatter（name/description）+ 标准目录结构
  - ✅ 结构被官方 CLI 验证：`npx skills add https://github.com/Arletaaa/agent-skills --list` → "Found 1 skill"（可被正确解析/安装）
  - ⚠️ CLI 无 publish 命令 → 注册在 skills.sh **官网**完成（提交仓库 URL）
  - ✅ **注册成功**：用户在官网提交仓库 URL → 生成包页 `https://skills.sh/p/EE6VG4LgAtdDOPop`
  - ✅ **安装验证通过**：`npx skills add https://skills.sh/p/EE6VG4LgAtdDOPop -g -y` →
    - 安装到 `~\.agents\skills\decision-challenge`（SKILL.md + references/，2 files）
    - universal 分发：Codex / GitHub Copilot / OpenCode / Amp / Antigravity +12 等 16+ agents；symlink → Claude Code
    - 唯一警告：PromptScript 不支持全局安装（小众 agent，无影响）
  - ✅ **本环境实测加载成功**：技能出现在会话技能目录，`skill` 工具读取 `C:\Users\33466\.agents\skills\decision-challenge\SKILL.md` 内容完整 = v3
  - 安全提醒（CLI 提示）："Review skills before use; they run with full agent permissions"——第三方安装技能前需审查
  - 遗留：Claude Code 内真实决策触发测试（用户侧可选）
