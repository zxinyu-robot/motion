# L2 架构设计

| 文件 | 用途 |
|------|------|
| `数据飞轮-实施清单与架构.md` | **数据飞轮 canonical**：上层输入向实现/验证沉淀，运行证据向 CAP/专利/论文回流 |
| `Go2端侧-可闭环易解释系统工程.md` | **Go2 P0 canonical**：端侧闭环、事件语义、证据与验收；上位原则见 `00-指导AI/项目宪章-无人协同系统工程.md` |
| `Go2-VLA-SLAM-Token技术方案.md` | **Token 链路 canonical**：事务→TokenSequence→x86 VLN Adapter→本地执行 |
| `Nav2端边解耦与地图任务契约_两阶段演进.md` | **架构候选**：先保留本地 Nav2 完成建图/x86 地图维护，再验证边全局—端局部解耦 |
| `空间表征与规划耦合_架构演进.md` | **架构演进 canonical**：统一空间表征、Traversability、主动建图与规划耦合边界 |
| `Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md` | 知识体系与候选运输层；不重复定义当前 P0 |
| `SLAM-Token弱网中间件-汇报材料.md` | internal 汇报素材，非 canonical；申请前不得公开完整方法 |
| `大疆上云API参考-ActionGroup与Folder分层.md` | P0.5/P1 任务编排参考 |
| `行为树调度架构_BehaviorTree设计.md` | P1 调度设计 |
