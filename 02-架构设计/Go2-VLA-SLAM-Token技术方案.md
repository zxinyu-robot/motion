# 面向 x86 VLN 的增量空间 Token 端边链路

——从 OctVox 增量序列化到 Go2 任务闭环

> 整理自技术讨论（2026-07-09）  
> 视角：SLAM 工程师落地（不依赖 AI 训练能力）  
> 平台：Unitree Go2 + Super-LIO/OctVox + x86 VLN（当前设计，实测状态见 `40-验证/`）  
> **当前工程排序**：见 `01-工作计划/ForkSpatialLink-实现方向_含AsyncShield对齐.md` §4.3。

---

## 1. 项目概览

### 1.1 痛点

现有 VLN/VLA 消费 SLAM 3D 几何时存在接口与执行断层：

- **数据接口断层**：SLAM 输出止步于 `/odom` + `/pointcloud`，x86 语义侧需重复解析或体素化；
- **时标断层**：语义推理与网络时延远慢于本地规划和安全控制；
- **证据断层**：空间版本、语义结果、执行终态和失败原因尚未形成可重放闭环。

### 1.2 方案一句话

提出 **SLAM-Token / Spatial Token 中间件**：将 Super-LIO/OctVox 的帧级增量先形成版本化 `VoxelTransaction`，再编码为 `TokenSequence v0.1`，经现有 IP 网络送至 x86；x86 Decoder 与可替换 VLN Adapter 产生粗粒度 waypoint/ActionGroup，回传后由当前 Nav2 2D 与固件安全链执行并返回终态。无损链路通过后，再做弱网单变量优化。

### 1.3 成果定位

| 项 | 内容 |
|----|------|
| 真机平台 | Unitree Go2（EDU + Orin） |
| 安全执行 | Unitree 固件 / estop 兜底；精度与触发行为以 `40-验证/` 为准 |
| 边端负载 | 【待补充实测】；VLA/VLN 不作为 Go2 P0 端侧进程 |
| 愿景 | 封装为可替换 Producer 与 VLN Adapter 的 SLAM-Token 模组候选 |

---

## 2. 当前目标架构

### 2.1 系统数据流

```
[边端 Go2 / Orin]
  Livox Mid-360 + IMU
       ↓
  Super-LIO + OctVox
       ↓
  帧级 VoxelTransaction / DeltaBlock
       ↓
  TokenSequence v0.1 Encoder
       ├─→ 现有 IP 数据面 → [x86]
       │                         ↓
       │                    Token Decoder
       │                         ↓
       │                可替换 VLN Adapter + VLN
       │                         ↓
       └─← Waypoint / ActionGroup + 来源版本 ←─┘
       ↓
  Nav2 2D（当前 P0；后续规划器须过 Gate）
       ↓
  /cmd_vel → go2_base
       ↓
  Unitree 固件避障 / estop 安全链
```

### 2.2 四级避障 / 规划分工

| 层级 | 执行方 | 频率 / 精度 | 角色 |
|------|--------|-------------|------|
| L1 固件级 | Unitree `go2_base` / estop | 以实测配置为准 | 最后安全兜底 |
| L2 规划级 | Nav2 2D（当前 P0） | 以 `40-验证/` 为准 | 本地轨迹与到达 |
| L3 演进规划 | ego / 3D planner（后续 Gate） | 【待补充】 | 纯探索、窄缝或 3D 场景 |
| L4 语义级 | x86 VLN | 【待补充实测】 | 输出 coarse waypoint/ActionGroup |

**原则**：VLN/VLA 永不直接发 `/cmd_vel`；L1/L2 不依赖 x86 语义链。

### 2.3 边端资源账（待实测）

| 模块 | 占用 |
|------|------|
| Super-LIO（含 OctVox） | 【待补充】CPU、帧耗时 |
| 事务聚合 + Token Encoder | 【待补充】CPU、内存、编码耗时 |
| 传输进程 | 【待补充】协议开销、队列和带宽 |
| Nav2 2D + 安全链 | 【待补充】CPU、规划频率 |

**【设计决策】** P0 不把 VLN/VLA 放到 Go2 端侧。资源收益和安全影响必须由同场景 Benchmark 证明，不再引用未回链的估算作为实测结论。

---

## 3. 关键技术模块

### 3.1 Super-LIO + OctVox

- **定位**：固态 LiDAR + IMU 紧耦合 LIO；内嵌 OctVox 哈希体素
- **优势 vs FAST-LIO2 + VoxBlox**：一次到位体素化；ARM 上约快 4.2×；增量 hook 更干净
- **Frame 对齐（必做）**：

```yaml
lidar_frame: "mid360"
body_frame: "base_link"   # 改掉默认 body
map_frame: "odom"         # 改掉默认 camera_init
```

- **注意**：Super-LIO 原生无回环；长走廊（>200m）会漂，需外挂回环或给体素加 confidence

### 3.2 双触发关键帧

```text
is_keyframe =
  (位移 > 0.3m 或 转角 > 15°)     // 运动触发
  OR (本帧新增/更新体素 > 200)    // 几何触发（OctVox diff）
  OR (指令变更)                   // 语义触发（可选）
  OR (距上次关键帧 > 2s)            // 兜底
```

**为何不全靠运动**：ego 探索时常「原地转圈看 / 贴墙走」，纯运动会漏「转一圈发现新路口」。

### 3.3 TokenSequence 与网络载荷边界

**【设计决策】** 四层对象必须分开，防止把“序列化”误写成“Token 语义”：

```text
VoxelTransaction：Producer 提交的版本化空间事实
TokenSequence：面向下游的稳定语义编码
Network Payload：Protobuf 等具体序列化与分片载荷
VLN Input：x86 Adapter 生成的模型专用输入
```

下列 message 仅为历史设计草案；T-003 冻结前不得作为已实现或公开 Spec：

```protobuf
message KeyFrame {
  uint64 timestamp_ns = 1;
  string robot_id = 2;
  // Super-LIO 位姿
  double odom_x = 3; double odom_y = 4; double odom_z = 5;
  double quat_w = 6; double quat_x = 7; double quat_y = 8; double quat_z = 9;
  // RGB-D（压缩）
  bytes rgb_jpeg = 10;      // 640x480, ~50KB
  bytes depth_png = 11;
  // OctVox 增量
  repeated VoxelDiff voxels = 12;
  // ego 状态
  string ego_mode = 13;     // exploring / tracking / hovering
  double target_x = 14; double target_y = 15;
  string instruction = 16;
}

message VoxelDiff {
  uint64 hash_key = 1;      // Morton / hash
  float cx = 2; float cy = 3; float cz = 4;
  uint8 intensity = 5;
  uint8 hit_count = 6;
}
```

**带宽参考**：历史估算约 100KB/帧 × 2Hz；实际 payload、协议开销和频率必须在 P0-B 实测，不得据此宣称 WiFi 下已满足实时性。

### 3.4 x86 VLN Adapter（两条候选路）

| 路子 | 做法 | 适用 |
|------|------|------|
| A 图像派（先跑通） | OctVox → 局部三视图投影 → 当伪 RGB / 第 4 通道进 ViT | 不改 VLA 主干 |
| B 稀疏体素派 | `(x,y,z,intensity)` → MinkowskiEncoder → token | 保留 Z 轴（钻桌底、台阶） |

**【设计决策】** P0 先选择一个最小 Adapter 跑通，不把模型输入格式写入 `TokenSequence`；A/B 的收益须按同一 Token 输入与任务场景对照。

### 3.5 回传与底层执行

```text
x86 VLN Adapter → 现有 IP 数据面 → Go2: waypoint/ActionGroup
  → 关联 map/session/version/timestamp
  → Nav2 2D（当前）
  → cmd_vel adapter
  → 固件避障 / estop 安全链
  → 终态与失败码回传
```

后续 ego/3D planner 只能通过适配器替换 Nav2 消费者，须保留相同下行契约、旧基线和回退路径。

### 3.6 LiDAR 选型备忘

| 型号 | 条件 | 备注 |
|------|------|------|
| Livox Mid-360 | EDU + 拓展坞 | 社区主流，VLA 多模态首选 |
| Unitree L1 | EDU + 拓展坞 | 官方去畸变 `/cloud_deskewed` |
| Livox XT16 | EDU + 拓展坞 | 更便宜 16 线替代 |

腿式必用去畸变点云，否则体素会「长毛」。

---

## 4. 与相关工作对比

### 4.1 VLA-for-Quadruped

| 维度 | NaVILA | MobileVLA-R1 | 本方案 |
|------|--------|--------------|--------|
| 平台 | Go2/H1 等 | Go2 | Go2 |
| VLA 输入 | RGB only | RGB + Depth + PTv3 点云 | RGB + OctVox hash token |
| 3D 表征 | height map（只给 loco） | 瞬时点云 / implicit 地图 | **显式增量体素** |
| 底层 | RL loco（Isaac Sim） | 本地 tracker + velocity | **当前 Nav2 2D + Unitree 安全链** |
| 边端 | Orin 跑 VLA（量化） | Orin，VLA 上云 ~10s/步 | **VLN 在 x86；边端给事务/Token + 本地执行** |
| 关键帧 | 未提 | 未提 | **运动+几何双触发** |

**MobileVLA-R1 要点（对标用）**

- 论文：arXiv 2511.17889；NaVILA 基座 + DepthAnything V2 + PTv3 + LLaMA3-8B LoRA
- 训练：Gemini 造 MobileVLA-CoT → SFT → GRPO（运动余弦 / 动作 / 格式三重奖励）
- 真机：L2 LiDAR + D435i；混合云；复杂指令 SR 约 86–91%
- 代码：https://github.com/AIGeeksGroup/MobileVLA-R1

**【待验证假设】** OctVox 增量与版本契约可减少重复处理并改善可追溯性；是否优于瞬时点云/implicit 表征，须由 P0-B～P0-D 对照，不能预先写成性能优势。

### 4.2 底层规划

| 维度 | Nav2 | EGO 原版 | SCAN-Planner | 本方案 |
|------|------|----------|--------------|--------|
| 原生 | 轮式 | 无人机 | Go2 已改 | Go2 |
| SLAM | 任意 | 任意 | FAST-LIO2 | **Super-LIO + OctVox** |
| 3D | 2D costmap | 可能「飞」 | projected A* 贴地 | 待改 kinodynamic |
| 兜底 | inflation | ESDF | yaw-aware | **Unitree 固件 / estop（实测为准）** |
| VLN 对接 | NavigateToPose | 无 | 无 | **waypoint/ActionGroup → 当前 Nav2 2D** |

**【事实】当前 P0 基线**：Go2 已测执行链为 Super-LIO + SHM 静态层至 Nav2 costmap + Nav2 2D（MPPI）；其真机到达仍未达标，详见 `40-验证/BENCH-P0-Go2-MotionSLAM-基线.md`。  
**【设计决策】演进路径**：纯探索 / 窄缝场景后续评估 ego（可参考 SCAN-Planner 的 yaw-aware 双圆柱 + projected A*）；3D/ego 规划不替代当前 P0 闭环验收，须在 Nav2 2D 到达与安全基线通过后，按单变量对照准入。

### 4.3 Related Work 叙述建议（三段）

1. **VLA-for-Quad**：NaVILA（RGB-only）→ MobileVLA-R1（PTv3 implicit）→ 本工作：显式增量体素 diff → token  
2. **底层规划**：Nav2 → EGO → SCAN-Planner → 本工作：Super-LIO 更快 + 上层 VLA + L1 固件兜底  
3. **边端分工**：TIC-VLA / TrackVLA 的 offload → 本工作：版本化增量空间 Token + x86 VLN Adapter + 本地安全执行

---

## 5. SLAM 工程师落地清单（不碰训练）

把 VLA 当成「特殊传感器融合节点」：只保证输入格式与坐标系正确。

### 5.1 任务清单

1. N4/N5 运动基线补证（可与上行开发并行）；
2. **P0-A**：从真实 OctVox 更新路径形成帧级事务、Recorder 与重放证据；
3. **P0-B**：实现 `TokenSequence v0.1` Encoder/Decoder，在干净网络完成 Go2→x86 首测；
4. **P0-C**：实现一个可替换 VLN Adapter，回传 waypoint/ActionGroup 并由 Nav2 2D + 安全链执行；
5. 回传终态、失败码与来源空间版本，形成固定场景闭环；
6. **P0-D**：无损闭环通过后逐轴注入弱网变量。

### 5.2 OctVox → VLA 可吃数据（Adapter）

**方案 A（推荐）**：局部高度图 / 占据栅格 → `sensor_msgs/Image`（假 RGB）  
**方案 B**：8 方向几何统计特征 → 小向量 / Protobuf（带宽极小）

高度图生成前建议用 odom 的 Roll/Pitch 把地面「摆平」，避免狗抬头导致地形倾斜。

### 5.3 分辨率建议

- OctVox：0.1–0.2m（约 Go2 腿宽量级）  
- 过细（0.05）：数据量大、结构不清；过粗（0.5）：丢椅子腿等细节  

### 5.4 Go2 必踩坑

1. App 切 **AI 模式**，否则躯干晃、图像糊、VLA 幻觉  
2. LiDAR 用去畸变话题  
3. 非全向：`vy=0`；Nav2 若用则锁 `vy_max: 0.0`  
4. 断网时切纯 L1+L2，不依赖 VLA  

---

## 6. 产品化：SLAM-Token 模组

### 6.1 产品缝隙

市面有 LiDAR + SLAM 模组（输出 odom/cloud），**没有**「SLAM runtime → 标准化 spatial token → 给 VLA」这一层。

### 6.2 三个切片

| 切片 | 形态 | 卖点 |
|------|------|------|
| A 边缘 Token 盒 | Orin NX + Super-LIO 改 + tokenizer | 输出 diff token，下游不用再体素化 |
| B Token + 局部规划 | A + ego | 无 VLA 也能探索；接 VLA 后升级语义 |
| C 协议 + SDK | `liboctvox_tokenizer` + Protobuf schema | 事实标准；杠杆最大、要快 |

### 6.3 壁垒（注意 IP）

- Super-LIO / OctVox 是开源（RA-L），**引擎本身不是自有 IP**  
- 真正壁垒：tokenizer 协议、双触发策略、下游 decoder / adapter 中间件  

### 6.4 阶梯

| 阶段 | 时间 | 目标 |
|------|------|------|
| L1 Demo | 当前 | Go2 闭环跑通 |
| L2 库剥离 | ~3 个月 | `liboctvox_tokenizer` + 标准 schema |
| L3 硬件盒 | ~6 个月 | Orin NX 盒送测 2–3 家 AMR |
| L4 规划一体 | ~12 个月 | 切片 B + 多底盘适配 |

---

## 7. 专利框架要点

### 7.1 定位

钉在 **「SLAM → VLA 的 token 化中间件 + 双触发关键帧 + 边云分工」**，避开「又写了一个 SLAM」。

### 7.2 发明名称（建议）

面向视觉-语言-动作模型的机器人 SLAM 数据序列化方法、装置及系统

### 7.3 独权骨架（方法）

1. 在线 SLAM 输出位姿 + **哈希结构增量体素地图**  
2. **运动 ∨ 体素变化量** 双条件判定关键帧  
3. 提取位姿、RGB-D、**仅变化体素条目**（哈希键、中心、命中、强度）  
4. 按协议序列化，无线发送至离线 VLA  
5. 接收粗粒度导航目标点，下发本地规划器 + 固件级避障执行  

### 7.4 规避三坑

| 坑 | 写法 |
|----|------|
| Super-LIO 开源 | 独权写「哈希增量体素」，不写 IESKF/OctVox 内部结构；说明书声明区别于 Super-LIO |
| 宇树 4cm | 写「对接外部固件级避障接口，阈值≤4cm」，不主张自有避障 IP |
| VLA 模型 | 写「可采用 NaVILA/MobileVLA-R1 等」，发明点是中间件不是 VLA |

### 7.5 可分案

1. 体素 → token 编码方法（三视图 / Minkowski / 语义统计）  
2. 端边协同 VLN 导航控制方法（coarse waypoint/ActionGroup + 可替换本地规划器 + 安全兜底）  

---

## 8. 汇报材料结构（可直接做 PPT）

1. **Executive Summary**：痛点 / 方案 / 成果 / 愿景  
2. **技术架构**：边云图 + 三级避障  
3. **核心创新**：增量体素 Token、双触发、时空解耦  
4. **竞品对比表**：NaVILA / MobileVLA-R1 / Ours  
5. **产品路径**：盒子 / 协议 / 客户（AMR、四足、科研）  
6. **IP 布局**：主专利 + 两分案 + 规避说明  
7. **Roadmap & Ask**：人力（1 名中间件开发）、专利费用、厂商对接  
8. **附录**：实机视频、带宽延迟数据、OctVox Diff 示意  

---

## 9. 下一步建议（按优先级）

1. **P0-A**：OctVox 帧级事务 + Recorder + 重放；
2. **P0-B**：TokenSequence v0.1 + Go2→x86 Encoder/Decoder 首测；
3. **P0-C**：x86 VLN Adapter → waypoint/ActionGroup → Nav2 2D/L1 → 结果回传；
4. **P0-D**：无损闭环后做 WeakNet 单变量扫描；
5. **并行**：回链 N4/N5/N6 与 bag/ATE、专利证据映射、GrAco bag 到位后的 Swarm Gate；NAV-2/NAV-4 仍待验证。

---

## 10. 参考链接

- MobileVLA-R1 代码：https://github.com/AIGeeksGroup/MobileVLA-R1  
- MobileVLA-R1 项目页：https://aigeeksgroup.github.io/MobileVLA-R1/  
- go2_ros2_toolbox（社区）：andy-zhuo-02 / go2_ros2_toolbox  
- InternNav Go2 部署：适合「最快说话→狗走」对照路径  

---

*文档版本：v1.0 | 整理日期：2026-07-09*
---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | ARCH-SLAM-TOKEN-001 |
| type | architecture |
| stage | design |
| status | in-progress |
| canonical | true |
| evidence_level | proposal |
| confidentiality | patent-sensitive |
| updated | 2026-07-22 |
| next | P0-A 接出 OctVox 帧级事务与 Recorder；P0-B 完成 Go2→x86 TokenSequence 干净网络首测 |
