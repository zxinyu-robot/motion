# 40-验证（Validation）

本仓**不存放可编译代码**；此处只存验证结果、指标、报告，并**回链** `motion_ws` 的 commit/tag。

## 必填回链字段

- `stack`: motion_ws
- `commit`: 每个实例必填；以对应 BENCH 为准，README 不写死
- `bag` / `dataset`: 【待补充】
- `date`: 实测日期

## 模板与实例

| 文件 | 说明 |
|------|------|
| `P0-Benchmark-模板.md` | P0-A～P0-C 字段模板；不保存实例实测值 |
| `BENCH-P0-Go2-MotionSLAM-基线.md` | Go2 真机首组 measured（T-004） |
| `BENCH-P0-SwarmSLAM-GrAco-Gate.md` | Swarm Gate（T-008，bag 0/3 阻塞） |
| `P1-WeakNet-Collab-指标提纲.md` | P0-C 无损闭环后的 P0-D 弱网增量尺子（四轴） |

当前工程排序：`01-工作计划/ForkSpatialLink-实现方向_含AsyncShield对齐.md` §4.3。
