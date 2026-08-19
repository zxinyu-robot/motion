# 论文 Demo：ISM-Stream  
## From Pixels to Local Worlds — 增量分层局部世界地图端边流式协同

> **定位**：基于本仓现有事实与 P0 主链的**论文 Demo / outline**，不是可投稿正文，也不是已实现系统说明书。  
> **保密**：`internal`。申请日前不写双触发伪码、完整 Token 字段定稿与权利要求级细节；对外仅可用架构概念与已 measured 基线数字。  
> **证据等级**：方法为 proposal；Go2 运动基线部分 measured；Token/分层传输/QoS 调度均为【待实验】。

---

## 0. 一句话

把端边主通道从「传图片」升级为「传版本化局部世界增量」，按网络质量分层加权传输，使端侧执行栈与边侧模型消费同一世界切片，为后续动作模型提供几何级底座。

---

## 1. 事实底座（只写已有证据）

### 1.1 已具备（【事实】）

| 项 | 状态 | 来源 |
|---|---|---|
| 验证载体 | Unitree Go2 EDU + Orin NX | `BENCH-P0-Go2-MotionSLAM-基线.md` |
| 几何前端 | Super-LIO（子模块登记）+ Mid-360 | 同上；`hosts.md` / 双边事实 |
| 本地执行 | 纯 Nav2 2D（MPPI）+ SHM costmap + `estop_go2` / Sport | 狗端测试记录；BENCH |
| 短距运动闭环 | N4 2 m 误差 0.253 m；N6 3 m 误差 0.283 m；N5 急停后 3 s 位移 0.011 m | Go2 `docs/测试记录.md`（至 2026-07-23） |
| 架构冻结 | Spatial Token 端边链路；VLN/VLA 不上狗；下行 ActionGroup | `ForkSpatialLink-实现方向…`；`Go2-VLA-SLAM-Token技术方案.md` |
| 端侧约束 | 版本化增量哈希体素契约；Producer 可替换 | `Go2端侧-可闭环易解释系统工程.md` |
| 弱网尺子 | 带宽/延迟/jitter/丢包/断连提纲已有 | `P1-WeakNet-Collab-指标提纲.md` |

### 1.2 尚未具备（【待补充】，Demo 要补的）

| 项 | 状态 |
|---|---|
| `VoxelTransaction` / `TokenSequence` 编解码 | 未接入真机（T-003） |
| 增量地图上行带宽/延迟实测 | 无 |
| 分层语义增量（L1） | 设计旁路，未实现 |
| QoS 加权调度 | 本 Demo 新增设计点，未实现 |
| ActionGroup 绑定 version 的闭环 | P0-C，未测 |
| bag 回传开发机、ATE/RPE | 部分缺 |
| NAV-2 / NAV-4 | 待复测 |
| SCAN-Planner hybrid | 有代码，无 PASS |

### 1.3 本 Demo 与现有论文线关系

| 既有线 | 关系 |
|---|---|
| P1 弱网协同世界模型 | 本 Demo 是**单机端边**可跑切片；多机是后续扩展 |
| P3 关键帧压缩 | 对照臂「传图」与「传增量」共用弱网实验床 |
| C 族 SLAM-Token 专利 | Demo 写 QoS/分层消融；独权细节不进正文。C0=分地图层封装；C2=按需补全与 WAM 交互；细调度主战场在本 Demo/A4 |

---

## 2. 问题与贡献（论文口径）

### 2.1 问题

端边具身协同若以 RGB 视频/图片为主通道，则：

1. 带宽随分辨率与帧率线性膨胀；  
2. 边侧模型与端侧执行器难以共享同一几何世界版本；  
3. 网络劣化时，像素流与控制意图更容易时空错位。

本项目已有端侧几何闭环能力，但**结构化局部世界增量尚未成为主通信载荷**。

### 2.2 三项贡献（Demo 级，不写成已验证）

1. **内容升级**：定义端→边主通道为版本化局部世界增量（几何层必选，语义层可选），替代「仅传图片」。  
2. **分层管理 / 传输 / 消费**：L0 几何、L1 语义（可选）、执行命令层分离；渲染 / 规划 / 执行按层订阅。  
3. **QoS 加权传输**：按网络质量调节各层配额，优先保住几何锚与版本连续，并以 `session/version/TTL` 约束远端动作，降低时空错位。

---

## 3. Demo 系统名与边界

| 项 | 内容 |
|---|---|
| 系统名 | **ISM-Stream**（Incremental Semantic/Spatial Map Streaming） |
| 平台 | Go2 + Orin NX（端）+ x86（边） |
| 主传感 | Mid-360 + IMU；头摄 RGB **可选辅通道** |
| 不做 | 跨楼 Elevator-LIO 切换验收、多机 merge、端侧大 VLM、3DGS 城市级渲染、NeuPAN/WAM 默认栈替换 |

**【设计决策】** 决策头（VLN / 世界状态查询 / 未来动作模型）一律经 **可替换 Adapter** 输出 `ActionGroup`，不直发 `/cmd_vel`。

---

## 4. 方法：分层局部世界

### 4.1 层定义

| 层 | 名称 | 内容 | 谁生产 | Demo 是否必做 |
|---|---|---|---|---|
| **L0** | Geometry | 哈希体素增量、位姿锚、`map/session/version` | 端侧 Super-LIO → 事务 | **必做** |
| **L1** | Semantic | 稀疏类别/置信度/freshness（旁路） | 端侧低频或边侧 RGB 反投 | 阶段 2 |
| **L2** | Instance | 开放词汇对象节点（可选） | **边侧** | 阶段 3 可选 |
| **Cmd** | Action | `ActionGroup` + 绑定 version/TTL | 边侧 Adapter | 阶段 2–3 |

事件语义沿用端侧宪章：`ADD / UPDATE / EVICT / RESET`；`EVICT≠REMOVE`。

### 4.2 四层对象分离（防概念混淆）

```text
VoxelTransaction   ← 端侧事实提交
TokenSequence      ← 稳定契约编码（Spatial Token）
Network Payload    ← 序列化/分片（Demo 期 Protobuf 可）
Downstream Input   ← Adapter 生成的模型输入（不写进 Token 本体）
```

### 4.3 最小契约字段（接口级，非冻结 Spec）

```text
WorldDelta {
  robot_id, map_id, session_id, seq
  base_version, commit_version
  timestamp_ns, frame_id
  world_T_base
  l0_diffs[]          // 几何增量
  l1_updates[]?       // 可选语义
}

ActionGroup {
  command_id, goal_point, prefer_yaw?
  map_id, session_id, base_version
  ttl_ms, timestamp_ns
}
```

**【保密】** 完整 schema、量化表、双触发阈值不在本文展开。

---

## 5. 分层传输与 QoS 加权

### 5.1 通道

| 通道 | 方向 | 载荷 | 角色 |
|---|---|---|---|
| M0 | 端→边 | L0 WorldDelta | **主通道** |
| M1 | 端→边 | L1 语义增量 | 辅 |
| M2 | 端→边 | 压缩 RGB / 少量视觉 token | **对照/可选** |
| D0 | 边→端 | ActionGroup | 下行意图 |
| D1 | 边→端 | 可选校正摘要 | 低频 |

### 5.2 QoS 档位与权重（可调参数）

网络观测：带宽、RTT、丢包、jitter（对齐 WeakNet 四轴）。

| 档位 | w_L0 | w_L1 | w_M2 | 行为 |
|---|---|---|---|---|
| Good | 0.55 | 0.30 | 0.15 | 全层可开 |
| Fair | 0.75 | 0.25 | 0.00 | 关视觉辅通道；语义降频 |
| Poor | 0.95 | 0.05 | 0.00 | 保几何+版本；语义极稀疏 |
| Dead | — | — | — | 停远端新动作；端侧本地 L0+安全链 |

硬门闩：

1. 缺合法 L0/version 时，禁止边侧下发新 ActionGroup；  
2. ActionGroup 过期或 session 不匹配 → 端侧拒绝；  
3. 权重调整有滞回，避免档位抖振造成版本风暴。

### 5.3 统一世界与时空对齐

```text
同一 map_id/session_id
+ 单调 commit_version
+ ActionGroup.base_version 对齐
+ TTL 随 RTT 收紧
⇒ 机器人执行与边侧模型消费同一世界切片
```

这是「为后续动作模型做几何级底座」的操作化定义：  
不是宣称已实现 World Model，而是保证**动作条件输入绑定可回放的几何版本**。

---

## 6. 分层消费

```text
                 ┌─ Render：L0+L1 可视化（可降频）
LayeredWorld ───┼─ Plan：L1/L2 + 任务文本 → ActionGroup
                 └─ Exec Bridge：带 version 的命令下行
端侧本地 Exec：Nav2/SCAN + Sport/estop（不依赖渲染频率）
```

| 消费者 | 订阅 | 失败策略 |
|---|---|---|
| 渲染 | L0+L1 | 降帧不影响执行 |
| 规划 | 世界切片 + 任务 | 无把握则不下发或降级 |
| 执行 | 本地 L0 + 合法 ActionGroup | 过期拒绝；断网本地安全 |

---

## 7. 实验协议（Demo）

### 7.1 对照臂

| 臂 | 上行 | 目的 |
|---|---|---|
| A0 | 传图片/视频 | 像素基线 |
| A1 | 仅 L0 增量 | 证明可不传图同步局部世界 |
| A2 | L0+L1 | 语义分层附加 |
| A3 | A2 + QoS 加权 | 弱网下一致性与任务 |

### 7.2 场景

| ID | 场景 | 依赖事实 |
|---|---|---|
| S1 | 室内短距语义/航点到达 | 复用 N4/N6 级运动能力 |
| S2 | 限带宽 / 加延迟 / 丢包 | WeakNet 提纲 |
| S3 | 渲染降频时执行仍稳定 | 消费解耦展示 |

### 7.3 指标（实测列一律待填）

| 维 | 指标 | 现状 |
|---|---|---|
| 通信 | 上行带宽、端→边可见延迟、MB/success | 【待实验】 |
| 一致性 | version 对齐率、过期 Action 拒绝率、version lag | 【待实验】 |
| 任务 | SR、到达误差、碰撞/急停次数 | 运动基线有数字；语义任务【待实验】 |
| 解耦 | 渲染降频下控制频率/到达变化 | 【待实验】 |
| 资源 | Orin CPU%、编码耗时 | 【待实验】 |

已可引用的运动基线（非本 Demo 通信结论）：

- N4：0.253 m；N6：0.283 m；N5：0.011 m（见 BENCH）

---

## 8. 分阶段落地（贴 P0-A～P0-D）

| 阶段 | 工程内容 | 对应主链 | Demo 产出 |
|---|---|---|---|
| D1 | VoxelTransaction + Recorder + 边侧解码显示 | P0-A/B | A0 vs A1 带宽图 |
| D2 | ActionGroup + version/TTL 执行闭环 | P0-C | S1 任务表 |
| D3 | L1 语义旁路 + 渲染订阅 | 扩展 | A2 可视化 |
| D4 | QoS 加权 + WeakNet 单变量 | P0-D | A3 曲线 |
| D5 | （可选）实例层 / 决策头替换 | Adapter 插件 | 消融 |

**【设计决策】** D1–D2 未过前，不并行上跨楼、多机、端侧大模型。

---

## 9. 系统架构图（论文用）

```text
[Go2 / Orin]
 Mid-360 + IMU
      → Super-LIO (Producer)
      → VoxelTransaction (L0)
      → (+ optional L1)
      → QoS Mux → TokenSequence / WorldDelta
      → 本地 Nav2/SCAN + Safety
      ← ActionGroup(version, TTL)

        │ WiFi / 现有 IP（载体可替换）
        ▼

[x86 Edge]
 Decoder → LayeredWorldState
      ├─ Render Consumer
      ├─ Plan / VLN / WM-Query Adapter
      └─ Command with version binding
```

---

## 10. Related Work 写法（安全版）

分三条轴，不写“首次”：

1. **通信内容压缩**：关键帧/特征/嵌入传输（相对传整图）；  
2. **分层地图表示**：几何–语义–拓扑分离与增量更新；  
3. **弱网具身导航**：几何底座 + 本地安全降级。

差异句（建议）：

> 本文以版本化局部世界增量为主通道，将几何层与可选语义层分离传输，并在网络质量约束下加权调度；远端决策经版本绑定的 ActionGroup 回端执行，从而使机器人与上层模型对齐同一世界切片。完整协议字段与触发策略受专利分流，正文仅报告系统抽象与实验协议。

---

## 11. 标题与摘要草案

### 标题候选

1. *From Pixels to Local Worlds: QoS-Aware Layered Map Streaming for Edge–Robot Collaboration*  
2. *Incremental Layered Spatial Map Streaming under Weak Networks*（更贴 P0-D）

### 摘要草案

端边机器人协同常以图像流传递环境信息，导致带宽压力大，并难以保证远端模型与端侧执行器共享同一几何世界版本。本文给出一个面向四足平台的增量分层局部世界地图流式 Demo：端侧由 LiDAR-inertial 前端生成版本化几何增量（可选附加语义增量），按网络质量对各层分配传输权重；边侧重建可查询的分层世界状态，分别供渲染、规划与命令生成消费；下行动作携带会话与版本约束，由端侧本地规划与安全链执行。我们将在真实 Go2 短距运动基线之上，对照传图与传世界增量，并在可控带宽/延迟/丢包条件下评估通信开销、版本对齐与任务可用性。  
**【待补充】** 效果句待 D1–D4 实验后填入真实数字。

---

## 12. 风险与非目标

| 风险 | 处理 |
|---|---|
| 把 Demo 写成已实现 Token | 文中全程标 proposal / 待实验 |
| 专利未 filed 泄露独权 | 不写双触发伪码与完整字段 |
| 范围膨胀到跨楼/多机/3DGS | 明确非目标 |
| 用「世界模型」夸张表述 | 对外用「局部世界状态 / 几何底座」 |
| 运动基线数字冒充通信结论 | 分列引用 |

---

## 13. 下一步（工程）

1. T-003：最小 L0 WorldDelta 编解码 + Recorder；  
2. 同场景 A0/A1 带宽对照（可先 bag 回放）；  
3. P0-C：ActionGroup + version/TTL；  
4. 再开 QoS 加权与 WeakNet 扫参；  
5. 专利 C 族交底推进与论文展开以申请日为界分流。

---

## 文档元数据

| 字段 | 值 |
|---|---|
| id | PAPER-DEMO-ISM-STREAM-001 |
| type | paper |
| stage | outline |
| status | in-progress |
| priority | P0 支撑产出 |
| confidentiality | internal |
| evidence_level | proposal（方法）；部分运动基线 measured |
| knowledge_refs | CAP-SLAM-SUPER-LIO-PRODUCER-001；CAP-EVAL-VLN-REAL-001；CAP-EXEC-ASYNC-SHIELD-ALIGN-001 |
| patent_refs | C族-SLAM-Token；专利族谱映射 |
| benchmark_refs | BENCH-P0-Go2-MotionSLAM；P1-WeakNet-Collab-指标提纲 |
| related_docs | `02-架构设计/Go2-VLA-SLAM-Token技术方案.md`；`Go2端侧-可闭环易解释系统工程.md`；`ForkSpatialLink-实现方向_含AsyncShield对齐.md`；`motion_ws/docs/双边事实-motion与Go2-2026-07-27.md` |
| updated | 2026-07-30 |
| next | D1：实现/回放最小 L0 增量通道并出 A0 vs A1 带宽草图；同步 C 族交底不泄露独权细节 |
