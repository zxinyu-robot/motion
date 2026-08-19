# 具身模型鲁棒 INT8 压缩（BRCB 思路）

## 结论

在网关/PC 侧部署 VLA 类模型时，可采用 **稳定/敏感权重分流 + 门控训练**，在 INT8 压缩下同时保持干净场景精度，并在雨/雪/夜等扰动下**不低于甚至超过** FP32 稠密模型。与 SLAM-Token 协议层**正交**。

## 适用条件

- 推理在 x86/Orin 网关，非边端狗载大模型
- 视觉输入存在真实世界退化
- 需要和余翀组合作复现 BRCB

## 不适用

- SLAM-Token 带宽/关键帧问题（应用双触发+体素 diff 能力卡）
- 弱网丢包/时延（应用通信层能力卡）

## 关联

- 论文 P1 合作切口
- 主规划 §7.3 BRCB
- 专利：不直接并入 SLAM-Token 主专利

## 验证 todo

- [ ] 在目标 VLA 权重上复现 INT8+BRCB 流程
- [ ] 记录 Orin 延迟与成功率 → `40-验证/`
---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | CAP-DEPLOY-BRCB-001 |
| type | capability |
| stage | knowledge |
| status | done |
| evidence_level | proposal |
| sources | `04-文献阅读/2025-IJCAI-BRCB-阅读笔记.md` |
| applies_to | 网关 VLA 推理、OpenVLA 类模型部署 |
| updated | 2026-07-10 |
