# 双触发关键帧 + 体素 Diff 序列化

## 结论

边端 SLAM 输出通过 **运动触发 ∨ 几何（体素 diff）触发** 筛选关键帧，序列化为轻量 Token（目标 ~200KB/s 量级），供弱网上传与网关 VLA 消费。这是 SLAM-Token 产品主专利核心。

## 适用条件

- 增量体素地图（OctVox 等可替换前端）
- 弱网 WiFi / 网关架构

## 验证 todo

- [ ] 实测关键帧大小与频率 → `40-验证/P0-Benchmark-模板.md`
- [ ] 冻结 schema v0.1
---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | CAP-SLAM-KEYFRAME-DUAL-TRIGGER-001 |
| type | capability |
| stage | knowledge |
| status | in-progress |
| evidence_level | proposal |
| sources | `02-架构设计/Go2-VLA-SLAM-Token技术方案.md` |
| applies_to | 边端 Go2、SLAM-Token 中间件 |
| patent_refs | PAT-SLAM-TOKEN-MAIN |
| paper_refs | PAPER-P3-001 |
| updated | 2026-07-10 |
