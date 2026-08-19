# motion 项目状态（单一事实源）

> 本文件是统筹仓的**当前状态看板**。AI 开工前先读此文件 + `00-指导AI/prompt.md`。  
> 更新日期：2026-07-31（C0/C2 交底按「分地图层 + 按需补全 + QoS 降从属」改实；申请日须先于开源协议）

---

## 1. 当前阶段


| 项          | 状态                                                                            | 证据                                           |
| ---------- | ----------------------------------------------------------------------------- | -------------------------------------------- |
| 统筹仓阶段      | **方案 + 文档成熟，工程 Gate 环境就绪；Go2 单机基线已回链部分事实，bag/ATE 与专项场景仍待齐** | `swarmslam-gate` Docker ✅；`motion_ws/docs/宿主机ROS2-Gate路径.md`；`motion_ws/docs/双边事实-motion与Go2-2026-07-27.md` |
| 系统工程宪章 | **proposal**：以闭环、可解释、可验证、可靠、低耦合和持续演进定义项目；AI 采用独立核校 | `00-指导AI/项目宪章-无人协同系统工程.md` |
| 数据飞轮 | **proposal**：新输入→假设→设计→实现→Gate→CAP→专利/论文；运行证据反向回流；缺下层工件的规划不升级 | `WORKFLOW.md`；`02-架构设计/数据飞轮-实施清单与架构.md` |
| 2026 P0 主链 | 运动基线并行补证；P0-A OctVox 事务 → P0-B TokenSequence/x86 解码 → P0-C VLN/执行闭环 → P0-D WeakNet 单变量测试 | `01-工作计划/ForkSpatialLink-实现方向_含AsyncShield对齐.md` §4.3 |
| 并行证据线 | Swarm-SLAM GrAco/Gazebo Gate 在 bag 到位后继续，不阻塞单机 Token→VLN 主链 | `40-验证/BENCH-P0-SwarmSLAM-GrAco-Gate.md` |
| 协议状态       | **草案**（前端无关 `KeyFrame + SpatialChunk/VoxelDiff`，Demo 期 Protobuf，未冻结）          | `02-架构设计/Go2-VLA-SLAM-Token技术方案.md`          |
| Go2 端侧约束   | **proposal**：以版本化增量哈希体素、可追溯事件链和可重放验证实现闭环；当前 Super-LIO 为首个 Producer | `02-架构设计/Go2端侧-可闭环易解释系统工程.md` |
| 实现方向       | **面向 VLN 的增量空间 Token 端边链路**已冻结；执行按 P0-A～P0-D，AsyncShield 为 P0.5 插件位 | `01-工作计划/ForkSpatialLink-实现方向_含AsyncShield对齐.md` |
| 产品体系与统一口径 | **proposal**：P0 软件内核 → Go2 垂直 SKU → 通用硬件模组 / 开发运维控制面 / 协议生态 → 多机网关；后续形态不占当前 WIP | `01-工作计划/ForkSpatialLink-实现方向_含AsyncShield对齐.md` §2.3～§2.5（矩阵、七句话、现在/未来架构图） |
| 单机闭环       | **【measured】** 纯 Nav2 真机 2 m / 3 m 到达 ✅，行走中急停 ✅；静态纸箱绕行、WiFi 中断仍待复测；SCAN-Planner hybrid 未验收 | Go2 `~/MotionSLAM_ws/docs/测试记录.md`；`motion_ws/docs/双边事实-motion与Go2-2026-07-27.md` |
| 学术生态位计划    | **已落盘，执行中**（50/30/20；季度复盘）                                                    | `职业路线规划/学术生态位与三年行动计划.md`                     |

### 当前 active WIP（上限 3）

1. **运动基线**：回链 Go2 N4/N5/N6 的 commit、bag/evo，并补 NAV-2/NAV-4；
2. **Token 主链**：P0-A～P0-C，当前先做 OctVox 帧级事务与 Go2→x86 编解码；
3. **WeakNet Gate**：仅维护指标与注入准备，P0-C 无损闭环通过后才能首扫。

GrAco/Swarm 为 bag 驱动的并行证据线；AsyncShield、3D 规划、异构机体、Harness VLA 与 6G 不占当前 active P0 WIP。

---

## 2. 待拍板事项（P0）

- [ ] **ROS 2 双环境兼容**：仿真/主机候选 Jazzy + Ubuntu 24.04，实体机器人候选 Humble + Ubuntu 22.04 → 以构建、通信和闭环测试确认
- [ ] **Swarm-SLAM 准入**：完成 GrAco bag 与 Gazebo 双 Go2 对比，按回环、任务成功、资源和弱网恢复决定是否纳入真机 P0
- [ ] **仓库可见性**：motion 是否公开可检索 → 影响专利披露策略 ； 否不能公开
- [ ] **专利族谱统一**：C 族初步方案已落盘；仍待代理人确认母案/分案与 A 族边界 → `06-产出/专利/专利族谱映射.md`
- [ ] **单机证据回链**：已确认 Go2 `2abc6e4` 与 N4/N5/N6 结果；仍补 bag 回传、ATE/RPE，并同步 P0 Benchmark

---

## 3. 流水线任务队列（`status: todo`）


| ID    | stage      | 任务                                                   | next                                                 |
| ----- | ---------- | ---------------------------------------------------- | ---------------------------------------------------- |
| T-001 | input      | ✅ MapAPI PDF 已入 `papers/04`；LECES 仅 DOI 占位（IEEE closed，无 OA） | 人工补 LECES PDF 后开笔记；或扫 Go2 `MotionSLAM_ws` 传输痕迹 |
| T-002 | analysis   | 完成 BRCB 阅读笔记                                         | ✅ → CAP-DEPLOY-BRCB-001                              |
| T-016 | analysis   | ✅ Swarm-SLAM 阅读笔记 + CAP                               | → `04-文献阅读/notes/03-多机协同-Swarm/2024-arXiv-Swarm-SLAM-阅读笔记.md`；`CAP-SLAM-SWARM-SLAM-GATE-001` |
| T-003 | design→implementation | P0-A/B：帧级 VoxelTransaction + TokenSequence **v0.1** + x86 Decoder | downstream：`motion_ws` Encoder/Decoder + Recorder；acceptance：版本连续、可回放、干净网络可解码 → `40-验证/` |
| T-004 | validation | 回链 Go2 单机基线并填写 P0 Benchmark 首组数据                     | N4/N5/N6 狗端记录 ✅；next：更新 Benchmark 的 commit/指标，回传 bag/evo，补 NAV-2/NAV-4 |
| T-008 | validation | Swarm-SLAM 仿真 Gate（M1 GrAco bag）                        | Docker ✅ + 冒烟 ✅；**阻塞** bag 0/3 → `motion_ws/docs/T-008-GrAco-下载清单.md` |
| T-005 | output     | C 族 SLAM-Token 专利交底                               | **核心+卫星交底齐**：C-b（A+B）/ C-c（AccessTicket）/ C-h（多机 OCC）md+svg ✅；见 `C族/专利逻辑关系_一页讲清_C族.md`；待 docx/png + 交费顺序；卡点：申请人法律信息 |
| T-006 | output     | 论文 P1 开题 outline                                     | 申请日后展开；单机端边 Demo 已落盘 → `06-产出/论文/P0-ISM-Stream增量分层世界地图Demo/` |
| T-007 | analysis   | SuperMap + ITU-T Y.3663 外部对标写入 L3                    | ✅ → `03-技术分析/外部技术与标准对标_SuperMap与ITU-T_Y3663.md`      |
| T-009 | analysis   | 仙工/留形/眸深/motion 竞品与生态对标落盘 L3                         | ✅ → `03-技术分析/竞品与生态对标_仙工-留形-眸深-motion及相关厂商.md`        |
| T-010 | validation | WeakNet Collaborative Bench（P0-D）              | ✅ 四轴提纲；**阻塞于 P0-C 无损闭环**；next：选注入工具后逐轴首扫  |
| T-011 | output     | 首次内部分享 + 月度 PPT 落盘                                   | 素材之一：`06-产出/影响力/ONEPAGER-2026-EmbodiedVLN-Survey.md` |
| T-012 | analysis   | Reading Group 首轮（Swarm 论文 → 产品化讨论）                   | 材料：Swarm-SLAM + Kimera-Multi 笔记/CAP；讨论拓扑差（P2P vs 网关金字塔） |
| T-013 | output     | 目标导师清单 + 首封脱敏交流邮件                                    | WeakNet Bench 提纲完成后；见 `职业路线规划/` §8                   |
| T-014 | analysis   | EmbodiedVLN Survey 笔记 + Reading Group 第二期（VLN 真机）    | ✅ 笔记/CAP/ONEPAGER；待宣讲                                |
| T-015 | design     | Harness 三件套：L4 笔记 + 缺口清单 + 文献闭环三周实践           | ✅ W1–W3 完成（Swarm 打样 + venue/LICENSE 失败固化）；见三周实践进度表 |
| T-017 | design     | AsyncShield 对标：白盒时滞对齐接口草案 + WeakNet 延迟轴     | 笔记/CAP ✅；P0.5 插件位，不阻塞 P0-A～P0-D；RL shield=P1 |
| T-018 | design     | ForkSpatialLink 定位、依据与 P0-A～P0-D 冻结                 | ✅ → `01-工作计划/ForkSpatialLink-实现方向_含AsyncShield对齐.md` §2/§4 |
| T-019 | design | 系统工程宪章与阶段 Gate 落地 | 宪章 / AI 核校 / WORKFLOW ✅；next：以已通过的 N4/N5/N6 为运动样板，继续回链 bag/ATE、增量事务与弱网证据 |
| T-020 | design | 双向数据飞轮与向下沉淀 Gate | 文档/WORKFLOW ✅ → next：以 T-003 执行首个“规划→实现→验证→CAP→专利”样板 |
| T-021 | analysis | 社交导航 POMDP+ESN+PPO「绕行/停等」支线落盘 | ✅ parking → `03-技术分析/社交导航_ESN-PPO-绕行停等支线.md`；POMDP 仅作形式化框架，ESN 仅作可替换时序编码器；门闩后先做常速度/MLP/LSTM(或 GRU)/ESN 对照 |
| T-022 | analysis | C 族专利拥挤度/FTO 侦察索引（红黄绿）落盘 L3 | ✅ → `03-技术分析/专利拥挤度与技术空白_分层地图增量与端边契约.md`；next：拍板 Ca 降薄 vs 改交 C-b；代理人南湖/NNG 特征表 |


---

## 4. 保密与披露

- **专利敏感**：完整交底书、双触发伪码、未申请独权细节 → `confidentiality: patent-sensitive`
- **申请前禁止**：公开完整 Spec v1.0、顶会投稿含未申请方法、可检索仓库全文公开
- **可先公开**：架构概念、竞品对比、不含独权细节的 executive summary

---

## 5. 目录导航（短目录入口）

> **【事实】本表即 AGENTS 式短目录**：AI 先读本文件 + `00-指导AI/prompt.md`，再按路径下钻；**不**另建巨型 `AGENTS.md`。  
> Harness 缺口与三周实践：`00-指导AI/motion-Harness缺口清单.md`、`00-指导AI/Harness三周实践-文献闭环.md`。
> **Go2 端侧工作额外必读**：`02-架构设计/Go2端侧-可闭环易解释系统工程.md`（闭环、事件语义、证据与验收约束）。
> **项目定义、架构取舍、新技术、验证或对外表述额外必读**：`00-指导AI/项目宪章-无人协同系统工程.md`。  
> **数据采集、Benchmark、失败归因、沉淀与论文素材**：`02-架构设计/数据飞轮-实施清单与架构.md`。


| 阶段      | 目录                                                       |
| ------- | -------------------------------------------------------- |
| L0 指导   | `00-指导AI/`                                               |
| L1 计划   | `01-工作计划/`                                               |
| L2 设计   | `02-架构设计/`                                               |
| L3 分析   | `03-技术分析/`                                               |
| L4 文献   | `04-文献阅读/`                                               |
| L5 沉淀   | `05-知识沉淀/`                                               |
| L6 产出   | `06-产出/`（含 `影响力/` 白皮书/PPT）                               |
| 验证      | `40-验证/`                                                 |
| 收集      | `10-收集箱/`                                                |
| 专利草稿库   | `06-产出/专利/`（`A族/` + `C族/` + 族谱）；仓根 `专利/` 仅重定向指针 |
| 个人学习/职业 | `职业路线规划/`（**canonical 个人计划**）、`个人工作/`（CLI 与 AI 协作手册）、`学习计划/`、`SALM学习/`（非产品 WBS） |


---

## 6. 证据等级说明


| evidence_level | 含义                         |
| -------------- | -------------------------- |
| idea           | 讨论/愿景                      |
| proposal       | 架构文档已定稿表述                  |
| prototype      | 有代码或 demo，未量化              |
| measured       | 有 benchmark / bag / evo 数据 |
| production     | 可交付客户或送测                   |


当前多数 L2 文档为 **proposal**，尚未普遍达到 **measured**。