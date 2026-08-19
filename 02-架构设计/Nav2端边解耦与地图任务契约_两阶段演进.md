# Nav2 端边解耦与地图任务契约：两阶段演进

> **定位**：先复用当前 Go2 本地 Nav2 完整栈完成建图、地图上送和 x86 地图维护，再以对照实验推进边侧全局规划与端侧局部执行解耦。  
> **当前状态**：架构候选，不替换已冻结的 P0 Token→VLN→Nav2 闭环。  
> **实现草案**：`../../motion_ws/docs/端边全局规划解耦与地图任务契约设计.md`。  
> **保密**：`patent-sensitive`；地图版本、任务版本和安全降级的完整组合不得在申请前作为公开 Spec。

---

## 1. 事实基线与问题

### 1.1 当前已有能力

**【事实】** 当前 Go2 基线已经具备：

- Super-LIO + SHM 静态层至 Nav2 costmap；
- Nav2 栈自检通过；
- `ComputePathToPose` 干跑通过；
- Nav2 2D（MPPI）与 Unitree Sport / 固件 / `estop_go2` 安全链。

证据见 `40-验证/BENCH-P0-Go2-MotionSLAM-基线.md`。

**【事实】** 纯 Nav2 的 2 m 与 3 m 真机到达、以及行走中急停已有通过记录（N4 误差 0.253 m；N6 误差 0.283 m；N5 急停后 3 s 位移 0.011 m）。因此当前准确口径是“纯 Nav2 短距离单机运动与安全基线已通过，但静态障碍、WiFi 中断、ATE/RPE 与端边 Token 链路仍待验证”；SCAN-Planner hybrid 尚无对应 PASS 记录。

### 1.2 当前主要缺口

**【设计判断】** 当前不应先拆 Nav2，而应先补地图链路：

1. 可重复执行的区域扫描/巡检路线；
2. 地图快照、会话、坐标系和版本定义；
3. Go2 地图上送 x86；
4. x86 侧大地图持久化、回放、查询和增量维护；
5. 地图质量、长距离漂移和跨会话一致性证据。

这里“用 Nav2 扫图”的准确含义是：**Nav2 执行覆盖/巡检路线，Super-LIO/OctVox 负责定位和建图**。Nav2 本身不是建图器。

## 2. 两阶段总览

```text
阶段一：保留 Go2 本地 Nav2 完整栈

Super-LIO / OctVox 建图
  → 本地 Nav2 执行扫描/巡检路线
  → 地图快照 + VoxelTransaction / Recorder
  → 干净网络传至 x86
  → x86 MapStateStore 维护大地图
  → 回放、查询、版本连续性与地图质量验证

阶段二：在阶段一地图底座上拆分 Nav2

x86 MapSnapshot
  → 边侧 Global Planner
  → 带地图版本的 GlobalPathManifest
  → Go2 PathBridge
  → 本地 Nav2 Controller + Local Costmap + BT
  → cmd_vel → 固件 / estop
  → 执行状态 / ReplanRequest 回传
```

## 3. 阶段一：先把地图工作推下去

### 3.1 架构边界

阶段一不移动 Nav2 Planner、Controller 或 BT 的部署位置：

```text
Go2
├─ Super-LIO / OctVox
├─ 当前 Nav2 完整栈
├─ Local Costmap
├─ Sport / 固件 / estop
├─ Map Recorder / Exporter
└─ VoxelTransaction Producer

x86
├─ Map Receiver
├─ Recorder / Replay
├─ Static Map Importer
├─ MapStateStore
└─ Map Query / Visualization
```

**【设计决策】** x86 在本阶段只维护、检查和服务地图，不参与在线全局路径决策。这样可将地图问题与规划解耦问题分开归因。

### 3.2 地图数据分层

```text
Local Mapping State
  = Go2 当前 SLAM 会话内的在线状态

Map Snapshot
  = 可冻结、导出、校验和回放的地图快照

VoxelTransaction
  = 快照之间的版本化增量事实

x86 Large Map
  = 先验静态层 ⊕ 经验证的在线增量层
```

**【设计决策】** “传到 x86”分两步验证：

1. **快照基线**：先用文件/离线包证明地图可导出、导入、定位和查询；
2. **在线增量**：再用 `VoxelTransaction → TokenSequence → x86 Decoder` 维护版本连续的在线层。

这样避免在地图格式、坐标系和一致性尚未确认时，把问题全部归因到实时通信。

### 3.3 大地图不等于地图拼接成功

**【风险】** x86 保存更多体素或更大范围数据，不会自动解决：

- 长距离累计漂移；
- 回环与全局一致性；
- `map/odom` 坐标关系；
- 跨会话重定位；
- 动态障碍污染；
- `EVICT` 被误认为现实空间清除。

因此“大地图维护完成”必须由地图质量与回放证据定义，不能只以文件更大或显示范围更广作为验收。

### 3.4 阶段一 Gate

| Gate | downstream_artifact | acceptance | evidence_target |
|------|---------------------|------------|-----------------|
| M0 运动基线 | 当前 Nav2 完整栈复测 | N4 2 m 到达、N5 停栈通过 | bag、终态、到达误差、安全日志 |
| M1 扫描建图 | 固定区域扫描路线 + 地图快照 | 可重复完成；坐标系明确；快照可重载 | 路线、bag、地图包、导出日志 |
| M2 x86 离线地图 | Importer + MapStateStore + Viewer/Query | 同一快照导入一致；可回放与区域查询 | hash/统计、查询结果、回放日志 |
| M3 在线增量 | Go2 Producer/Recorder + x86 Receiver | 版本连续；GAP/RESET 可识别；快照与重放终态一致 | 事务日志、版本断点、CPU/带宽 |
| M4 地图质量 | 地图 Benchmark | 漂移、覆盖、重复区域一致性有量化结果 | ATE/RPE、覆盖率、重叠误差 |

阶段一只在干净网络完成 M3 后，才进入延迟、jitter、丢包和断连测试。

## 4. 阶段二：Nav2 全局规划解耦

### 4.1 目标职责

```text
x86 边侧
├─ MapStateStore
├─ immutable MapSnapshot
├─ Global Planner
├─ MissionStore
└─ ReplanCoordinator

Go2 端侧
├─ PathBridge
├─ Nav2 Controller
├─ Local Costmap
├─ BT Recovery
└─ Sport / L1 / estop
```

三类数据必须分开：

| 契约 | 回答的问题 | 方向 |
|------|------------|------|
| Map Contract / `VoxelTransaction` | 世界发生了什么 | Go2 → x86 |
| Mission Contract / `GlobalPathManifest` | 准备走哪条路线 | x86 → Go2 |
| Execution Contract / 状态与重规划请求 | 实际怎么走、结果如何 | 双向 |

`cmd_vel` 始终由 Go2 本地产生，边侧不得直接控制高频运动。

### 4.2 适配 Gate

阶段二必须同时保留“当前本地 Nav2 完整栈”作为 A/B 对照与回退路径。

| Gate | 验收 |
|------|------|
| D0 接口核验 | 以真实 Nav2 配置与源码确认外部 Path、取消、抢占、lifecycle 和 BT 接口 |
| D1 静态图路径 | x86 在冻结 MapSnapshot 上规划，Go2 可校验并跟踪路径 |
| D2 版本契约 | 路径关联 `map/session/version/valid_until`；过期或会话不一致会拒绝 |
| D3 重规划 | 本地恢复失败产生稳定原因码；边侧重新规划；不会绕过本地安全链 |
| D4 通信 | 先无损，再分别注入 latency、jitter、丢包、断连和恢复 |
| D5 A/B Benchmark | 与本地完整 Nav2 对比 SR、路径代价、时延、通信、CPU、恢复与安全 |

### 4.3 回退

出现以下任一情况时，回退到阶段一的本地完整 Nav2：

- 边侧地图版本出现 GAP 且无法恢复；
- Manifest 过期、坐标系不可转换或 session 不匹配；
- 网络断连超过任务允许时限；
- 边侧规划收益不足以覆盖通信和系统复杂度；
- 本地 Controller/BT 接口无法稳定接收外部路径；
- 弱网下安全指标劣于本地基线。

## 5. 与当前 P0 和后续演进的关系

| 层级 | 工作 | 状态 |
|------|------|------|
| 当前并行基线 | N4/N5/N6 已有纯 Nav2 通过记录；bag/evo、NAV-2/NAV-4 待补 | P0-C 证据回链前置 |
| P0-A/B | 地图事务、Recorder、TokenSequence、x86 解码 | 与阶段一 M2/M3 对齐 |
| P0-C | waypoint/ActionGroup → 当前本地 Nav2 完整栈 | 保持不变 |
| P0-D | 无损闭环后 WeakNet 单变量 | 先测试当前架构 |
| P0.5/P1 | 边侧 Global Planner + PathBridge | 阶段二，通过 D0–D5 后再升级 |
| 后续 | Traversability、Active Mapping、Planning-aware SLAM | 复用 x86 地图底座，另过 Gate |

**【设计决策】** 地图底座是 Nav2 解耦和后续空间表征演进的共同前置；不因阶段二设计存在，就提前改变当前 P0-C。

## 6. 专利与披露边界

- C 族仍聚焦版本化增量空间 Token、端边协同、下行版本关联与安全降级；
- A 族地图运行时、World Model 和弱网边界以 `06-产出/专利/专利族谱映射.md` 为准；
- 实现草案中的完整字段、状态机和版本组合按 `patent-sensitive` 管理；
- 阶段一形成地图证据，阶段二形成通信与规划解耦证据；证据进入交底前不得直接扩写为论文完整方法。

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | ARCH-NAV2-EDGE-DECOUPLING-001 |
| type | architecture |
| stage | design |
| status | in-progress |
| canonical | false |
| evidence_level | proposal |
| confidentiality | patent-sensitive |
| updated | 2026-07-22 |
| next | 先执行 M0～M2；M3 对齐 P0-A/B；完成地图质量证据后启动 D0 |

**sources**

- `40-验证/BENCH-P0-Go2-MotionSLAM-基线.md`
- `02-架构设计/Go2端侧-可闭环易解释系统工程.md`
- `02-架构设计/Go2-VLA-SLAM-Token技术方案.md`
- `motion_ws/docs/端边全局规划解耦与地图任务契约设计.md`
