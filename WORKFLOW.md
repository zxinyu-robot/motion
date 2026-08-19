# Robot Engineering OS 工作流

> 任何东西只能按：**输入 → 分析 → 设计 → 实现(外部栈) → 验证 → 沉淀 → 产出** 流动。

---

## 状态机

```text
10-收集箱 (input)
    ↓
03-技术分析 / 04-文献阅读 (analysis)
    ↓
02-架构设计 / 01-工作计划 (design)
    ↓
../motion_ws/ (implementation)  ← 代码不在本仓
    ↓
40-验证 (validation)
    ↓
05-知识沉淀 (knowledge)
    ↓
06-产出 (patents → papers / influence / spec)
    └──────── 验证结论、失败模式与新问题回流到 input / design
```

---

## 文件元数据（文末「文档元数据」表）

**正文以标题 `#` 开头**；元数据放在文末，避免 YAML front-matter 块影响阅读。

每份活跃文档建议包含：

```markdown
# 文档标题

> 简介（可选）

……正文……

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | UNIQUE-ID |
| type | architecture / analysis / paper / patent / capability / benchmark / plan |
| stage | input / analysis / design / validation / knowledge / output |
| status | todo / in-progress / done / archived |
| canonical | true / false |
| evidence_level | idea / proposal / prototype / measured / production |
| confidentiality | public / internal / patent-sensitive |
| updated | YYYY-MM-DD |
| next | 下一步动作 |
```

列表型字段（`related`、`sources`、`patent_refs` 等）可在表后另起 `**字段名**` 列表。批量迁移脚本：`.cursor/scripts/restore_and_footer_metadata.py`。

### 活跃任务的向下沉淀字段

进入 `ProjectState.md` 的 `active/todo` 项，不要求把下列字段全部塞入状态表，但必须在对应 canonical 文档或执行卡中可定位：

| 字段 | 含义 |
|---|---|
| `problem` | 已被证实的问题；没有证据时标【待补充】 |
| `downstream_artifact` | 下一层实现任务、文件或 Benchmark，不得只写“继续研究” |
| `acceptance` | 3–7 条可勾选验收条件 |
| `evidence_target` | 预期 commit、日志、bag、指标或失败码 |
| `output_route` | CAP / 专利 / 论文 / 影响力 / 仅归档 |
| `expiry/review` | 复盘点；到期无下层工件则降为 `parking/archived` |

**【设计决策】** 缺少 `downstream_artifact + acceptance` 的输入只能停留在 input/analysis，不得通过新增多份规划文档制造“已推进”的假象。

---

## 阶段与 Cursor 规则

| 阶段 | 目录 | Cursor Rule | 主力模型 |
|------|------|-------------|----------|
| 指导 | `00-指导AI/` | `motion-core.mdc` | — |
| 工作计划 | `01-工作计划/` | `work-planning.mdc` | Composer / Grok |
| 文献分析 | `04-文献阅读/` | `paper-analysis.mdc` | Grok / Sonnet |
| 代码分析 | `03-技术分析/` | `code-analysis.mdc` | Grok |
| 架构设计 | `02-架构设计/` | `architecture-design.mdc` | Fable / Sonnet |
| 验证 | `40-验证/` | `benchmark-validation.mdc` | Composer / Sol |
| 产出（通用） | `06-产出/` | `output-general.mdc` | — |
| 论文产出 | `06-产出/论文/` | `paper-draft.mdc` | Sonnet |
| 专利产出 | `06-产出/专利/` | `patent-disclosure.mdc` | Composer / Sonnet |

---

## 阶段 Gate 与变更准入

| 阶段 | 最低入口 | 退出条件 | 必需回链 |
|---|---|---|---|
| input | 原始资料、需求或问题已归档 | 来源、保密级别与待核验项明确 | `10-收集箱/` 或需求记录 |
| analysis | 输入可定位 | 结论区分【事实】【推断】【待补充】；列出反证、风险、适用边界与相关工作差异 | 阅读笔记 / L3 分析 / 相关工作矩阵 |
| design | 已确认的问题与分析结论 | 模块边界、接口/状态、故障降级、验证指标和回退路径明确 | L2/L1 canonical 文档 |
| implementation | 已冻结的最小设计与验收项 | 实现版本、配置和复现步骤可定位；变更不超出设计边界 | `motion_ws` commit/文档 |
| validation | 可复现构建或测试条件 | 原始日志/bag/指标与结论回链；未通过项保持可见 | `40-验证/` |
| knowledge | 已验证或明确边界的结论 | 可复用结论、适用范围和证据等级固化 | `05-知识沉淀/` |
| output | 已完成专利/保密审查的材料 | 形成“问题—相关工作—设计/假设—闭环实验—数据对照—受限结论”论证链；表述不超出证据等级；可公开范围明确 | `06-产出/` + benchmark/阅读笔记回链 |

### 向下沉淀 Gate 与 WIP 限制

“阶段完成”不是同一段内容被复制到下一目录，而是发生以下工件转换：

```text
愿景/输入 → 可检验问题
规划条目 → 有验收条件的实现任务
架构设计 → schema / adapter / 场景 / Benchmark
实现结果 → commit / log / bag / 失败码
验证裁决 → CAP / 规则 / 专利证据 / 论文图表来源
```

- 同时 active 的 P0 设计主题最多 **3 个**；超出时必须先完成、降级或归档旧项。
- 新输入先判断是对现有 P0 的补强、替代、正交还是后续，不得自动升级为平行主线。
- 已有 canonical 的主题只追加差异、反证与下游任务；其他文档只保留用途、差异和链接。
- 连续一个复盘周期没有实现或验证工件的 active 规划，降为 `parking`，停止继续润色。
- 验证失败同样进入失败模式库并回写 design；不得以新建上层方案绕过失败。

当前 P0 的 3 个 active 主题以 `ProjectState.md` 为准，建议限制为：单机运动基线、OctVox→Token→x86 VLN 主链、主链通过后的 WeakNet Gate。

### 新技术与重大变更 Gate

任何新算法、模型、协议、中间件或关键架构替换，在进入主线前必须记录：

1. 已被证实的问题、现有基线和预期收益；
2. 模块边界、状态所有权、新增耦合与故障模式；
3. 隔离式原型或适配层方案；
4. 对照场景、指标、通过阈值和失败回退方式；
5. 许可证、专利与保密风险。

结论不完整时，技术仅可停留在 input/analysis 或旁路原型；不得升级为 P0 主线承诺。架构变更保持旧基线、单变量调整、同场景复测，禁止同时替换多个关键栈后直接归因。

### 独立核校

设计和验证的关键结论采用“生成轮 → 核校轮”。核校轮检查来源、证据等级、反例、范围、保密、验收条件和回退路径；发现冲突时按“原始实测/bag/日志 > 可复现实验 > 源码配置 > 架构决策 > 规划愿景”报告，不以润色替代核验。

---

## 铁律：先专利后论文

同一技术点若 `patent.stage < filed`，不得写入 `paper.stage < submit` 的完整方法细节。见 `00-指导AI/prompt.md` 铁律六。

---

## 闭环验收（单篇文献示例）

1. PDF → `10-收集箱/papers/`
2. 分析笔记 → `04-文献阅读/*-阅读笔记.md`
3. 能力卡 → `05-知识沉淀/<主题>/CAP-*.md`
4. 若影响架构 → 更新 L2 + `ProjectState.md` 任务
5. 若可专利 → `06-产出/专利/` 交底书（申请前保密）
6. 若可论文 → `06-产出/论文/`（申请日后）
