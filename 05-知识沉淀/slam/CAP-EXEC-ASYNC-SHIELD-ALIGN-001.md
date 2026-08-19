# 异步云端 VLA 边端执行对齐（借鉴 AsyncShield）

## 结论

**【事实】** AsyncShield（arXiv:2604.24086）主张：在云端 VLA + 边端运动 + 网络/推理延迟下，用边端位姿缓冲做 **SE(2) 白盒时滞对齐**，并以 CMDP/RL adapter 在子目标跟踪与 LiDAR 硬约束间权衡，输出统一 Local Sub-goal。  
**【推断】** 对 motion：**上行仍靠 SLAM-Token；下行在 ActionGroup/waypoint 与本地规划之间插入「时滞对齐」插件位**。P0 只借鉴白盒对齐 + WeakNet 延迟轴；RL shield 为他人方法，标 P1 可选，不写入自有独权。

## 适用条件

- 云端/边侧 VLA 出 coarse waypoint 或 ActionGroup(`point`, `prefer-yaw`)
- 端侧有可靠频率的位姿（如 Super-LIO odom）与时间戳
- 需要评测：注入 RTT / 推理延迟后的 SR、CR、意图恢复误差

## 不适用

- 替代 KeyFrame / VoxelDiff 带宽问题（见 CAP-SLAM-KEYFRAME-DUAL-TRIGGER-001）
- 替代 Swarm-SLAM 多机回环（见 CAP-SLAM-SWARM-SLAM-GATE-001）
- 宣称 PPO-Lagrangian / CMDP 为 motion 自有专利点
- 在 Token/端边无损闭环与 WeakNet 基线未完成前，不优先做完整 RL shield

## 关联

- 笔记：`04-文献阅读/notes/01-具身智能-VLA-VLN/2026-arXiv-AsyncShield-阅读笔记.md`
- 方向：`01-工作计划/ForkSpatialLink-实现方向_含AsyncShield对齐.md`
- 验证：`40-验证/P1-WeakNet-Collab-指标提纲.md`
- 技术方案：`02-架构设计/Go2-VLA-SLAM-Token技术方案.md` §2.2 四级规划

## 验证 todo

- [ ] PDF 入 `10-收集箱/papers/01-具身智能-VLA-VLN/`
- [ ] WeakNet 轴 A 填写 latency/jitter 注入方法
- [ ] 设计白盒 SE(2) 对齐接口草案（对接 ActionGroup / Local Sub-goal）
- [ ] （P1）评估是否需要 RL shield 或规则替代

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | CAP-EXEC-ASYNC-SHIELD-ALIGN-001 |
| type | capability |
| stage | analysis |
| status | draft |
| canonical | true |
| evidence_level | proposal |
| updated | 2026-07-20 |
| next | PDF 精读后更新实验声称核校；挂 T-017 |
