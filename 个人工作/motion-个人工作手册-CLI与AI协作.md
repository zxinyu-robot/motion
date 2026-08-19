# motion 个人工作手册：CLI 流程与 AI 协作

> 从 motion 统筹仓提炼的**个人操作层**摘要：开工顺序、AI 约束、Cursor 用法、常用 CLI、文献与文档流水线。  
> 动态状态不在此复制，以 `ProjectState.md` 为准；实现细节以 `motion_ws/` 为准。

---

## 1. 三秒定位：三个仓库各干什么

| 路径 | 角色 | 你在这里做什么 |
|------|------|----------------|
| `motion/` | 统筹文档仓 | 规划、设计、文献、验证、专利/论文 meta |
| `../motion_ws/` | P0 工程实现 | Docker Gate、Go2 SSH、子图接收、colcon |
| `../RGB_ws/` | v1 边侧语义网关 | 9877/9878/9879、Gazebo corridor、StreamVLN 支路 |

**【事实】** 同级目录布局（来源：`01-工作计划/技术栈索引.md`）：

```text
/home/ubuntu/Downloads/
├── motion/      # 统筹文档仓（本手册所在）
├── motion_ws/   # 实现：Swarm Gate / 子图 / Go2 脚本
└── RGB_ws/      # v1 边侧语义 + 仿真
```

Go2 真机 SLAM/Nav2 主栈在远端 `~/MotionSLAM_ws`（SSH `go2-edge-0`），不在本机 `motion_ws` 内。

---

## 2. 每次开工：先读什么

### 2.1 固定顺序（AI 与人类相同）

1. `ProjectState.md` — 当前阶段、active WIP（上限 3）、任务队列
2. `00-指导AI/prompt.md` — 七条铁律、统筹仓边界
3. 按需：`00-指导AI/项目宪章-无人协同系统工程.md`（架构取舍、验证、对外表述）
4. 按需：`WORKFLOW.md`（阶段 Gate、文档元数据、向下沉淀）

### 2.2 按任务下钻（不要一次加载全部 L2）

| 任务类型 | 额外 `@` |
|----------|----------|
| 文献阅读 | `04-文献阅读/文献阅读prompt.md` + PDF/笔记 |
| 架构/协议 | `02-架构设计/Go2-VLA-SLAM-Token技术方案.md` 等 L2 |
| 代码/工程 | `03-技术分析/` 笔记 + `motion_ws` 对应目录 |
| 验证/Benchmark | `40-验证/` 对应 BENCH 文档 |
| 专利/论文 | `06-产出/专利/专利族谱映射.md`（先专利后论文） |

### 2.3 文献任务开场 `@` 清单（强制精简）

来自 `00-指导AI/Harness三周实践-文献闭环.md`：

1. `@ProjectState.md`
2. `@00-指导AI/prompt.md`
3. `@04-文献阅读/文献阅读prompt.md`
4. `@10-收集箱/papers/<域>/<文件>.pdf`（或已有笔记）
5. 对照材料之一：如 `@02-架构设计/Go2-VLA-SLAM-Token技术方案.md`

---

## 3. AI 协作铁律（七条速查）

来源：`00-指导AI/prompt.md`、`.cursor/rules/motion-core.mdc`

| # | 铁律 | 操作含义 |
|---|------|----------|
| 1 | 不能编 | 版本/路径/调用链必须有文件证据；无则标【待补充】 |
| 2 | 不能只看表面 | 声明的依赖、目录名 ≠ 真实使用；回源码验证 |
| 3 | 区分标注 | 【事实】【推断】【设计决策】【待补充】 |
| 4 | 扫非标准目录 | 含 `config/`、`.env*`、`.cursorignore`；统筹仓不含 `src/` |
| 5 | 统筹与实现分离 | 不得把 `motion_ws` 环境当统筹层全局事实 |
| 6 | 先专利后论文 | `patent.stage < filed` 时不得写完整方法进待投稿论文 |
| 7 | 独立核校 | 人类输入是待核验命题；找反证；重大变更走 Gate |

**保密**：`confidentiality: patent-sensitive` 文档不得建议公开到可检索渠道。

---

## 4. 研发流水线（文档怎么流）

来源：`WORKFLOW.md`

```text
10-收集箱 (input)
    → 03-技术分析 / 04-文献阅读 (analysis)
    → 02-架构设计 / 01-工作计划 (design)
    → ../motion_ws/ (implementation)
    → 40-验证 (validation)
    → 05-知识沉淀 (knowledge)
    → 06-产出 (patents → papers / influence)
         └─ 验证结论、失败模式回流 input / design
```

### 4.1 活跃任务最低字段

进入 `ProjectState.md` 的 todo/active 项，须在 canonical 文档或执行卡中可定位：

- `problem` — 已证实的问题
- `downstream_artifact` — 下一层实现/Benchmark（不能只写「继续研究」）
- `acceptance` — 3–7 条可勾选验收
- `evidence_target` — commit / log / bag / 指标
- `output_route` — CAP / 专利 / 论文 / 归档

**WIP 上限**：同时 active 的 P0 设计主题最多 **3 个**（以 `ProjectState.md` 为准）。

### 4.2 文献闭环六步

1. PDF → `10-收集箱/papers/<域编号>/`
2. 笔记 → `04-文献阅读/notes/<同域>/*-阅读笔记.md`
3. 能力卡 → `05-知识沉淀/<主题>/CAP-*.md`（或写明无需 CAP）
4. 影响架构 → 更新 L2 + `ProjectState.md`
5. 可专利 → `06-产出/专利/`（申请前保密）
6. 可论文 → `06-产出/论文/`（**申请日后**）

笔记命名：`<年>-<会或来源>-<简称>-阅读笔记.md`；**禁止**落在 `notes/` 根目录。

### 4.3 文档元数据（文末表）

活跃文档正文以 `#` 开头；元数据放文末「## 文档元数据」：

| 字段 | 示例值 |
|------|--------|
| id | UNIQUE-ID |
| type | architecture / analysis / paper / patent / capability / benchmark / plan |
| stage | input / analysis / design / validation / knowledge / output |
| status | todo / in-progress / done / archived |
| evidence_level | idea / proposal / prototype / measured / production |
| confidentiality | public / internal / patent-sensitive |
| updated | YYYY-MM-DD |
| next | 下一步动作 |

批量迁移脚本：`.cursor/scripts/restore_and_footer_metadata.py`

---

## 5. Cursor 协作

### 5.1 阶段规则（`.cursor/rules/`）

| 阶段 | 目录 | Rule 文件 |
|------|------|-----------|
| 全局 | — | `motion-core.mdc`（alwaysApply） |
| 计划 | `01-工作计划/` | `work-planning.mdc` |
| 文献 | `04-文献阅读/` | `paper-analysis.mdc` |
| 代码分析 | `03-技术分析/` | `code-analysis.mdc` |
| 架构 | `02-架构设计/` | `architecture-design.mdc` |
| 验证 | `40-验证/` | `benchmark-validation.mdc` |
| 产出 | `06-产出/` | `output-general.mdc` / `paper-draft.mdc` / `patent-disclosure.mdc` |

### 5.2 模型分工（一句话）

来源：`00-指导AI/Cursor-Pro+模型选型与项目分析策略.md`

```text
Composer 干活，Grok 跑长程，Sonnet 精读顶会，Terra 常规推理，Sol 系统排障，
Fable 架构决策，Kimi 读中文，GLM 写汇报，DeepSeek 推算法。
```

| 场景 | 推荐模型 | 模式 |
|------|----------|------|
| 日常改代码、整理文档 | Composer 2.5 | Agent |
| 深读工程、批量分析 | Grok 4.5 | Agent |
| 读论文、解释设计 | Grok / Sonnet / Kimi | Ask |
| Docker/CUDA/CMake 排障 | GPT-5.6 Sol | Agent |
| 架构 trade-off | Fable 5 / Sonnet 5 | Ask |
| 中文汇报 | GLM 5.2 | Ask |

**预算**：Pro+ 关闭按需付费；Fable/Sol 仅关键节点；长分析尽量**同会话续聊**省 token。

### 5.3 Ask vs Agent

| 模式 | 适合 | 典型任务 |
|------|------|----------|
| **Ask** | 只读、解释、评审 | 读论文、架构评审、回答问题 |
| **Agent** | 可改文件、跑命令 | 实现、批量重构、环境排障、脚本执行 |

### 5.4 四步分析流程（工程/文献通用）

1. **项目地图**（Composer）：目录、入口、数据流、阅读顺序
2. **关键链路**（Grok）：追调用链，对照 L2 方案核验
3. **架构评审**（Fable/Sonnet）：trade-off、风险、改进优先级
4. **中文产出**（GLM）：汇报 / executive summary

### 5.5 可复制 Prompt 片段

**项目地图**：

```text
请分析 @<项目目录> 的整体结构：
1. 顶层目录职责  2. 主入口与数据流  3. mermaid 模块关系
4. 推荐阅读顺序及每条链路目的
输出 markdown 笔记格式。
```

**关键链路**：

```text
基于 @<已有笔记> 和 @<源码目录>，追踪 <功能> 完整调用链；
对照 @<技术方案.md> 列不一致处与改进建议。
```

**文献四章**（详见 `04-文献阅读/文献阅读prompt.md`）：

1. 该文献是什么  
2. 作者/课题组  
3. 与本项目关系（借鉴矩阵 + 立即跟进/调研/存档）  
4. 主要设计参考参数指标  

---

## 6. AI 标准工作流（接代码前）

来源：`00-指导AI/prompt.md`、`我+AI如何去完成工程项目？.md`

1. **建立项目认知**（先读再写）：技术栈、目录、对外接口、调用链、配置位置、命名约定  
2. **深度扫描 → ProjectInfo.md**（实现仓适用）：结构、依赖、架构一致性、链路、异常/配置模式；**重点是可信而非完整**  
3. **TDD**：先定输入输出与验收，再实现  
4. **编码提交**：遵守 Git 规范（见 §7.2）；未完成处打 `TODO`/`NOTE`/`BUG`  
5. **产出前自检**：铁律清单 + 专利/保密边界（`prompt.md` §4）

---

## 7. CLI 命令速查

### 7.1 motion 统筹仓

```bash
cd /home/ubuntu/Downloads/motion

# PDF 提取可翻译文本（Comment Translate 旁路）
./10-收集箱/papers/extract-pdf-text.sh <file.pdf>
# → 同目录生成 <file>.txt

# 文档元数据批量修复（front-matter → 文末表）
python3 .cursor/scripts/restore_and_footer_metadata.py
```

### 7.2 Git（Jetson / 多实验迭代习惯）

来源：`00-指导AI/项目开发规范准则/项目开发规范准则.md`

```bash
git checkout -b dev_test
git pull --rebase                    # 每次开发前

git add <paths>
git commit -m "fix: adjust multipoint mission logic"   # 小步提交

# 前缀：feat | fix | refactor | docs
```

**禁止**：在 `master` 直接开发；`git push -f`（除非明确需要）；版本控制 `build/`、`devel/`。  
**凭据**：GitHub/Gitee token 用环境变量，**禁止**写入文档或提交到库。

```bash
git log --oneline
git reset --hard HEAD~1              # 回退（谨慎）
git checkout <commit> -- <file>      # 恢复单文件
git tag flight_time && git push origin --tags
```

### 7.3 motion_ws — Swarm-SLAM GrAco Gate

来源：`../motion_ws/README.md`

```bash
cd /home/ubuntu/Downloads/motion_ws

# 0) 数据：Graco ground-01/02/03 → data/Graco_Ground/Graco-{0,1,2}/
./scripts/check-data.sh

# 1a) 宿主机 ROS 2（Jazzy 或 Humble）
source /opt/ros/jazzy/setup.bash
./scripts/bootstrap-swarm-slam-host.sh
./scripts/check-host-env.sh
GATE_MODE=host ./scripts/run-graco-gate.sh

# 1b) 或 Docker（无需宿主机 ROS）
GATE_MODE=docker ./scripts/run-graco-gate.sh

# 2) 检查输出 → 结论写入 motion/40-验证/BENCH-P0-SwarmSLAM-GrAco-Gate.md
./scripts/check-gate-output.sh
./scripts/gate-docker-smoke.sh          # 无 bag 冒烟
```

### 7.4 motion_ws — Go2 真机

```bash
cd /home/ubuntu/Downloads/motion_ws

./scripts/ssh-go2.sh probe              # 只读探测
./scripts/ssh-go2.sh                    # 登录 go2-edge-0
./scripts/sync-to-go2.sh                # platforms/go2/ → 远端 staging
./scripts/pull-go2-benchmark.sh         # 拉 git + 测试记录 → logs/
```

主机登记：`motion_ws/hosts.md`（dev-host / go2-edge-0；Go2 通常 `192.168.110.61`）。

### 7.5 motion_ws — 子图接收 + Foxglove

```bash
cd /home/ubuntu/Downloads/motion_ws

# 1) 开发机收子图（防火墙放行 TCP 9876）
./scripts/start_submap_receiver.sh --port 9876

# 2) Foxglove（另开终端）
./scripts/start_submap_foxglove.sh
# Studio → ws://127.0.0.1:8765；3D: /submap/stitched, frame=world

# 3) 重拼（滤地/天花 + 0.25m 体素）
./scripts/restitch_submaps.sh
```

产出目录：`logs/submaps_recv/`（`submap_*.pcd` + `stitched.pcd`）。  
狗端采集在 Go2 `~/MotionSLAM_ws` 执行，非本机 `motion_ws`。

### 7.6 RGB_ws

v1 语义双路与 Gazebo：见 `../RGB_ws/docs/v1-motion体系对齐说明.md`；与 `motion_ws` 端口分工见该文档。

---

## 8. 代码与注释规范（摘要）

来源：`00-指导AI/项目开发规范准则/项目开发规范准则.md`

| 项 | 约定 |
|----|------|
| 注释 | Google Style；重要函数写清参数、返回值、功能、示例 |
| 命名 | 接口字段：大驼峰 / 小驼峰 |
| 文档 | Python → mkdocs + material；C++ → Doxygen |
| Todo 标签 | `TODO` / `BUG` / `FIXME` / `HACK` / `NOTE` / `TAG` / `DONE` / `TEST` / `UPDATE` |
| Git 分支 | `master`（稳定）、`dev`（测试）、`feature/*`（新功能） |

---

## 9. 独立核校（生成轮 → 核校轮）

设计与验证的关键结论建议分两轮：

**生成轮**：AI/人产出方案或分析  
**核校轮**：检查来源、证据等级、反例、范围、保密、验收、回退

证据优先级：**实测/bag/日志 > 可复现实验 > 源码配置 > 架构决策 > 规划愿景**

---

## 10. 源文档索引（细节下钻）

| 主题 | Canonical 路径 |
|------|----------------|
| 项目状态 | `ProjectState.md` |
| AI 铁律全文 | `00-指导AI/prompt.md` |
| 研发流水线 | `WORKFLOW.md` |
| 系统工程宪章 | `00-指导AI/项目宪章-无人协同系统工程.md` |
| Cursor 模型与 Prompt | `00-指导AI/Cursor-Pro+模型选型与项目分析策略.md` |
| 文献 Prompt | `04-文献阅读/文献阅读prompt.md` |
| Harness 文献闭环 | `00-指导AI/Harness三周实践-文献闭环.md` |
| 技术栈与路径 | `01-工作计划/技术栈索引.md` |
| motion_ws CLI | `../motion_ws/README.md` |
| 宿主机 ROS Gate | `../motion_ws/docs/宿主机ROS2-Gate路径.md` |
| 专利/论文分流 | `06-产出/专利/专利族谱映射.md` |

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | PERSONAL-WORK-HANDBOOK-001 |
| type | plan |
| stage | knowledge |
| status | done |
| canonical | true |
| evidence_level | proposal |
| confidentiality | internal |
| updated | 2026-08-13 |
| next | 随 `prompt.md` / `WORKFLOW.md` / `motion_ws/README.md` 变更时同步摘要；Zotero 导入流程可另开子文档 |
