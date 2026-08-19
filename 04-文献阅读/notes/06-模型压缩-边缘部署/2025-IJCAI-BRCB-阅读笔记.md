# 2025-IJCAI-BRCB 阅读笔记

## 1. 该文献是什么？

- **标题**：Boost Embodied AI Models with Robust Compression Boundary
- **作者**：Chong Yu, Tao Chen, Zhongxue Gan（复旦大学）
- **Venue**：IJCAI-25
- **问题**：具身 AI 模型在边缘部署需压缩，但压缩后还要抵抗雨/雪/夜/对抗等真实扰动
- **方法**：**BRCB** — 将权重分为 corruption-stable / corruption-sensitive 双路径；敏感路径加 **BRCB Gate** 突破稠密模型鲁棒上界
- **验证**：BEVFormer/BEVFusion（自动驾驶）、**OpenVLA**（机器人）；默认 INT8

## 2. 作者课题组信息

- **单位**：复旦大学 工程与应用技术研究院 / 信息科学与工程学院
- **通讯作者**：Tao Chen、Zhongxue Gan
- **方向【推断】**：视觉 Transformer 压缩、具身鲁棒部署（GPUSQ-ViT、UVC 等前作）
- **脉络【推断】**：延续课题组「压缩 + 鲁棒」线；与余翀团队合作切入点（主规划 §7.3）
- **资助**：上海市自然科学基金、国家重点研发计划等（论文 Acknowledgements）

## 3. 与本项目的关系分析

| 文献内容 | 本项目模块 | 可借鉴？ | 优先级 | 备注 |
|----------|-----------|----------|--------|------|
| OpenVLA INT8 压缩仍保持泛化 | 网关 VLA 推理 | 是 | 列入调研 | VLA 不上狗，PC 端可参考 |
| 视觉扰动鲁棒压缩 | 边端感知 | 间接 | 列入调研 | 与弱网 Token 正交 |
| SLAM-Token / 体素协议 | 中间件 | 否 | 仅存档 | 论文未涉及 |
| 与余翀 BRCB 合作 | 学术线 P1 | 是 | 列入调研 | 论文点①合作切口 |

**一句话结论**：BRCB 不直接支撑 SLAM-Token 中间件，但对 **网关侧 VLA 模型压缩与鲁棒部署** 有参考价值。

## 4. 主要设计参考参数指标

| 参数 | 数值 | 对标意义 |
|------|------|----------|
| 压缩格式 | INT8 | 网关部署精度底线 |
| BEVFusion 雨 mAP | BRCB 优于 baseline 与稠密模型 | 鲁棒压缩可行 |
| OpenVLA Visual 成功率 | 89.1% vs FP32 87.0% | VLA 压缩不降泛化 |
| Orin 加速 | 1.66×–2.55× | 边缘部署预期 |
| 扰动类型 | 雨/雪/夜/对抗 | 本项目需额外测弱网/丢包 |

## 附：next actions

- [ ] 能力卡已写入 `05-知识沉淀/deployment/CAP-DEPLOY-BRCB-001.md`
- [ ] 与余翀团队 BRCB 复现对齐主规划 M5 时间线
- [ ] **不**将 BRCB 细节写入待申请专利的 SLAM-Token 独权（正交技术）
---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | NOTE-2025-IJCAI-BRCB |
| type | paper-analysis |
| stage | analysis |
| status | done |
| paper | Boost Embodied AI Models with Robust Compression Boundary |
| venue | IJCAI-25 |
| priority | 列入调研 |
| reader_model | Composer |
| related_capability | CAP-DEPLOY-BRCB-001 |
| updated | 2026-07-10 |
