# Super-LIO 作为 Go2 端侧首个 SLAM Producer

## 结论

**【事实】** Super-LIO（arXiv:2509.05723v2 / RA-L preprint）是开源滤波系 LIO：IESKF + **OctVox**（每体素最多 8 个子体素代表点）+ **HKNN**；Orin NX 上公开集场景均值约 **10.47 ms/帧**，相对 FAST-LIO2 约 **4.2×** 加速（论文 Table III / Fig.1）。  
**【事实】** 本仓 P0 已将其作为 Go2 单机基线前端（见 `BENCH-P0-Go2-MotionSLAM-基线.md`）。  
**【设计决策】** 下游只依赖 **PoseStream + 版本化增量哈希体素契约**；Super-LIO 可替换，不得成为 Token / Nav2 / Recorder 的直接耦合对象。  
**【推断】** 无原生回环 → 长走廊/大回环场景需 Swarm-SLAM 后端或其它外挂；地图 LRU/`EVICT` 不得解释为现实障碍 `REMOVE`。

## 适用条件

- Go2 + Mid-360（或同类固态 LiDAR）边端实时里程计与局部地图
- 需要可对标的边端耗时/CPU 参考（论文 Orin NX）
- 作为 Swarm-SLAM 等框架的**外置里程计**前端

## 不适用

- 单独解决多机一致性、弱网 Token、VLA 语义导航
- 把论文 RMSE / ms 填进 Benchmark「实测」列
- 专利独权写成「OctVox / IESKF / HKNN 内部结构」（引擎开源）
- 假设仓库 LICENSE 或正式 RA-L 卷期已核验（仍【待查证】）

## 关联

- 笔记：`04-文献阅读/notes/02-SLAM-定位-建图/2025-RAL-Super-LIO-阅读笔记.md`
- 架构：`02-架构设计/Go2端侧-可闭环易解释系统工程.md`；`02-架构设计/Go2-VLA-SLAM-Token技术方案.md` §3.1
- 验证：`40-验证/BENCH-P0-Go2-MotionSLAM-基线.md`
- 代码声明：https://github.com/Liansheng-Wang/Super-LIO.git
- 多机对接：`CAP-SLAM-SWARM-SLAM-GATE-001`（外置 odom）

## 验证 todo

- [ ] 本仓子模块 commit 与上游版本对照写入技术栈索引 / Benchmark
- [ ] N4/N5/N6 回链：到达距离 + bag/evo；实测列只填本机
- [ ] 确认 TF：`base_link` / `odom`（或项目约定帧）与论文默认帧差异
- [ ] LICENSE 与正式 DOI 回填笔记【待查证】项
---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | CAP-SLAM-SUPER-LIO-PRODUCER-001 |
| type | capability |
| stage | knowledge |
| status | in-progress |
| evidence_level | literature + partial measured（基线自检 ✅；真机到达 ❌） |
| sources | `04-文献阅读/notes/02-SLAM-定位-建图/2025-RAL-Super-LIO-阅读笔记.md`；`10-收集箱/papers/02-SLAM-定位-建图/2509.05723v2-Super-LIO.pdf`；`40-验证/BENCH-P0-Go2-MotionSLAM-基线.md` |
| applies_to | Go2 端侧 Producer、OctVox 地图边界、P0 Benchmark 参考列 |
| related_tasks | T-001, T-004 |
| updated | 2026-07-21 |
