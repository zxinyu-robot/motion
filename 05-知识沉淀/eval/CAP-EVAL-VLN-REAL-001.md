# 真机 VLN 评测口径（SSR + CR）

## 结论

真机语言导航不能只报距离阈值下的 **SR**。必须同时报告：

1. **SSR（Strict Success Rate）**：停点距目标 ≤ 阈值 **且** 语义位置正确（`sem_i=1`）
2. **CR（Collision Rate）**：episode 级碰撞率；碰撞即终止并计失败相关安全指标
3. 可选 **OSR**：轨迹曾进入成功半径但最终未正确停止 → 诊断「不会停」

**【事实】** 同济综述 arXiv:2607.09792 真机实验：层级配置 SR 51%→SSR 37%；RGB-only 单体 CR 51% vs 层级 CR 7%。差距部分来自全景/LiDAR/SLAM 栈，不能简单归因「架构 alone」。

## 适用条件

- Go2 / 轮式等实体平台做 VLN 或 waypoint 闭环评测
- 需要与仿真 R2R-CE 数字对话时，补真机安全与语义停
- WeakNet Collaborative Bench：在通信轴之外叠加任务轴（SR/SSR/CR）

## 不适用

- 纯定位 ATE/RPE 回归（用 evo 即可）
- 未涉及语言目标的纯点到点导航（可只用 SR/Arrival；语义停可选）

## 关联

- 笔记：`04-文献阅读/notes/01-具身智能-VLA-VLN/2026-arXiv-EmbodiedVLN-Survey-阅读笔记.md`
- 验证：`40-验证/P0-Benchmark-模板.md`、`40-验证/P1-WeakNet-Collab-指标提纲.md`
- 架构：SLAM 几何底座 → coarse waypoint；不替代 L3 VLN 模型选型

## 验证 todo

- [ ] P0 首组实测填写 SR / SSR / CR（语义标注协议先定 1 页）
- [ ] P1 WeakNet：同一任务脚本下扫丢包/RTT，观察 SSR/CR 变化

---

## 文档元数据


| 字段             | 值                                                                                      |
| -------------- | -------------------------------------------------------------------------------------- |
| id             | CAP-EVAL-VLN-REAL-001                                                                  |
| type           | capability                                                                             |
| stage          | knowledge                                                                              |
| status         | done                                                                                   |
| evidence_level | proposal                                                                               |
| sources        | `04-文献阅读/notes/01-具身智能-VLA-VLN/2026-arXiv-EmbodiedVLN-Survey-阅读笔记.md`；arXiv:2607.09792 |
| applies_to     | 真机 VLN/waypoint 评测、WeakNet Bench 任务轴                                                   |
| updated        | 2026-07-16                                                                             |


