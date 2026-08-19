# Swarm-SLAM 作为 P0 多机协同底座

## 结论

**【事实】** motion 主规划已选定 **Swarm-SLAM**（ROS 2、多传感、开源）为统一 C-SLAM 框架，替代 COVINS-G 双栈。  
**【事实】** 论文提供预算约束下的 **spectral 机间回环排序**、去中心邻居管理，以及 GrAco 等数据集与 3 机 ad-hoc 真机量级（约 95 MB 总通信 / 475 m）。  
**【推断】** 产品「本体→网关」金字塔可将网关固定为高频邻居/优化节点，不必照搬纯 P2P rendezvous；弱网关键帧策略可借鉴其**预算选点**思想，与 SLAM-Token 协议层正交互补。

## 适用条件

- P0：Go2 激光线；仿真 Gate（GrAco bag → Gazebo 双机）
- 外置里程计（如 Super-LIO）+ Swarm 前端回环/后端优化
- 需要开源、可改、ROS 2 集成路径

## 不适用

- 单独解决 VLA/VLN 或体素 Token 带宽问题（见 CAP-SLAM-KEYFRAME-DUAL-TRIGGER-001）
- 假设官方已支持本机 Jazzy 而不经编译验证
- 把论文 ATE 数字直接当作 Go2 真机验收值

## 关联

- 笔记：`04-文献阅读/notes/03-多机协同-Swarm/2024-arXiv-Swarm-SLAM-阅读笔记.md`
- 对标：`CAP-SLAM-KIMERA-MULTI-REF-001`（P2P 稠密 mesh / D-GNC；非替换底座）
- 任务：`ProjectState.md` T-008（仿真 Gate）、T-012（Reading Group）
- 规划：`01-工作计划/多机器人协同_详细技术与科研规划.md` §3.2–3.4
- 专利：不把 Swarm-SLAM 公开方法写入自有独权；自有差异在 Token/网关调度（申请前保密）

## 验证 todo

- [ ] GrAco bag 三机回环与参考系收敛 → 记录于 `40-验证/`
- [ ] Gazebo 双 Go2 + 选定 LIO + Swarm-SLAM 在线建图
- [ ] 填写通信量 / 优化耗时 / 是否纳入真机 P0（T-008 结论）
- [ ] LICENSE 与 Jazzy 构建路径回链 `技术栈索引.md`
---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | CAP-SLAM-SWARM-SLAM-GATE-001 |
| type | capability |
| stage | knowledge |
| status | in-progress |
| evidence_level | literature |
| sources | `04-文献阅读/notes/03-多机协同-Swarm/2024-arXiv-Swarm-SLAM-阅读笔记.md`；`10-收集箱/papers/03-多机协同-Swarm/2301.06230v3-Swarm-SLAM.pdf` |
| applies_to | P0 多机协同、Swarm-SLAM Gate、弱网回环预算思想 |
| related_tasks | T-008, T-012 |
| updated | 2026-07-17 |
