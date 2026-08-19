# Kimera-Multi 作为多机稠密协同对标（非 P0 底座）

## 结论

**【事实】** Kimera-Multi（IEEE T-RO 2022 accepted；arXiv:2106.14386v2）是 **全分布式 P2P** 的多机度量-语义稠密 SLAM：Kimera 本地 VIO/mesh + 分布式地点识别 + **D-GNC/RBCD** 鲁棒位姿图 + 本地 mesh 校正。  
**【事实】** 通信可拆为 PR / GV / DPGO；例：Medfield 总载荷 **65.9 MB**，相对中心化传图量级（2113 MB）显著更省；文称相对传关键点中心化最高约 **70%** 降幅（Vicon Room 2）。  
**【设计决策】** motion P0 **不**以 Kimera-Multi 替换 Swarm-SLAM；本品用作拓扑对照、鲁棒后端思想与 WeakNet **通信量记账模板**。  
**【推断】** 产品「网关金字塔」可吸收其「通信可用时触发协同」与「先一致轨迹再纠地图」，但传感与地图表示仍走 Super-LIO + 增量体素契约。

## 适用条件

- Reading Group / 相关工作：P2P 稠密 vs 网关增量
- WeakNet Bench：按模块记账通信量（识别 / 几何验证 / 后端）
- 研究外点机间回环与分布式初始化失败模式

## 不适用

- 作为 Go2 P0 默认 C-SLAM 产品底座
- 用视觉 Kimera-VIO 替换已定的 Super-LIO Producer
- 把 Table I/V 数字填进本仓 Benchmark 实测列
- 在未核仓库 LICENSE 前主张特定开源许可【待查证】

## 关联

- 笔记：`04-文献阅读/notes/03-多机协同-Swarm/2022-TRO-Kimera-Multi-阅读笔记.md`
- 对照：`CAP-SLAM-SWARM-SLAM-GATE-001`；Swarm-SLAM 阅读笔记
- 外链索引：`03-技术分析/联网外部参考资料索引.md` §3.2（代码 URL）
- 任务：T-012（Reading Group）；T-010（WeakNet 指标可吸收三分账）
- 规划：主规划统一 Swarm-SLAM，COVINS/双栈已否决

## 验证 todo

- [ ] T-012：用本 CAP + Swarm CAP 完成一次「拓扑差」讨论并记结论
- [ ] （可选）WeakNet 提纲增加 PR/GV/后端通信量列
- [ ] 核验 GitHub LICENSE 与 T-RO 卷期 DOI，回填笔记【待查证】
---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | CAP-SLAM-KIMERA-MULTI-REF-001 |
| type | capability |
| stage | knowledge |
| status | done |
| evidence_level | literature |
| sources | `04-文献阅读/notes/03-多机协同-Swarm/2022-TRO-Kimera-Multi-阅读笔记.md`；`10-收集箱/papers/03-多机协同-Swarm/2106.14386v2-Kimera-Multi.pdf` |
| applies_to | 多机对标、分布式鲁棒 PGO、WeakNet 通信记账、Reading Group |
| related_tasks | T-001, T-012, T-010 |
| updated | 2026-07-21 |
