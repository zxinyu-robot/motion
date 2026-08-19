# Cursor Pro+ 模型选型与项目分析策略

> 适用方案：Pro+（$60/月，含 $70 API 用量 + 第一方模型大额度池）  
> 硬件环境：RTX 5070（12GB VRAM）+ 32GB 系统内存  
> 参考文档：[Cursor 模型与价格](https://cursor.com/cn/docs/models-and-pricing)  
> 更新日期：2026-07-16（含 OpenCode Zen BYOK 便宜试模型）

---

## 0. 一句话总纲

```
Composer 干活，Grok 跑长程，Grok 读英文论文，Terra 做常规推理，Sol 专攻系统疑难，
Fable 负责架构决策，Kimi 读中文，Sonnet 精读顶会，GLM 写汇报，DeepSeek 推算法，
Qwen-VL 做视觉，Cursor Tab 管补全，本地 Ollama 管隐私与实验。
```

**核心原则**：专业的事交给专业模型；日常走第一方池省额度，API 池留给关键时刻；国内模型补中文理解与低成本推理；本地模型补隐私与 VLN 视觉实验。

**预算铁律**：严格控制在 $60/月内，**关闭按需付费**，避免 API 池耗尽后产生额外账单。

---

## 1. Pro+ 用量结构

Pro+ 有两个**独立**的用量池，每月计费周期重置：

| 用量池 | 包含模型 | 特点 |
|--------|----------|------|
| **第一方模型池** | Auto、Composer 2.5、Grok 4.5 | 额度充裕，日常大量使用几乎不心疼 |
| **API 用量池** | Claude、GPT、Gemini、GLM、Kimi 等 | Pro+ 每月含 **$70**，按各模型 API 单价扣减 |

额外说明：

- **Cursor Tab 补全**：Pro+ 包含无限 Tab，始终使用 Cursor 内置模型，**无法被 Ollama 或 BYOK 替换**。
- **BYOK（自带 API Key）**：DeepSeek、Qwen 等通过 OpenAI 兼容接口接入时，走独立账户，**不消耗 Pro+ 的 $70**；但 Override Base URL 会影响 Cursor 内置模型路由，需手动开关。
- **本地 Ollama**：完全免费，仅支持 Chat/实验，Agent 工具链无官方保障。

---

## 2. 海外模型选型策略

### 2.1 分层使用与月占比

| 场景 | 推荐模型 | 用量池 | 月占比 | 说明 |
|------|----------|--------|--------|------|
| 日常改代码 | **Composer 2.5** | 第一方 | ~50% | 写脚本、重构、跑测试、整理文档 |
| 长 Agent / 深读工程 | **Grok 4.5** | 第一方 | ~20% | 自主读完整个工程、批量修改、长流水线 |
| 中等复杂推理 | **GPT-5.6 Terra** | API | ~10% | 常规多步 Agent；能用 Composer/Grok 完成时不必额外消耗 |
| 系统级硬核 Debug | **GPT-5.6 Sol** | API | ~8% | Docker/CUDA/EGL/CMake/Habitat-Sim 等环境排障 |
| 架构与关键决策 | **Claude Fable 5** | API | ~2% | VLN 总体架构、PPO 框架设计、跨模块重构，一个月 2–3 次 |

### 2.2 关键模型定位

#### Composer 2.5（默认，第一方池）
- Cursor 自研，针对 agentic 编程优化，速度快、成本低。
- 适合：日常实现、单/多文件修改、测试、文档整理。

#### Grok 4.5（长程，第一方池）
- Cursor 与 SpaceXAI 联合训练，专为长时间编码和知识工作设计。
- 适合：完整工程阅读、跨文件调用链追踪、批量资料分析。
- 注意：训练数据意外包含较早 Cursor 代码快照，CursorBench 得分可能受益。

#### GPT-5.6 Terra（常规推理，API 池）
- OpenAI 官方中档型号，价格约为 Sol 的一半（$2.5/$15 per 1M）。
- 适合：需要稳定推理但难度不及 Sol 的多步任务。

#### GPT-5.6 Sol（系统疑难，API 池）
- OpenAI 官方旗舰，$5/$30 per 1M，需开启 Max Mode。
- 适合：Ubuntu 24.04 Docker EGL 报错、Habitat-Sim CMake 依赖缺失、CUDA 编译链断裂等硬核排障。
- **修正**：91.9% 是 OpenAI 自报的 **Sol Ultra 四智能体并行配置**在 Terminal-Bench 2.1 上的成绩，普通 Sol 为 88.8%；不能等同于 Cursor 中普通 Sol 的实际表现。"Ultra Mode" 是 OpenAI 多智能体配置，不等同于 Cursor 的 Max Mode。

#### Claude Fable 5（架构决策，API 池）
- Anthropic 官方，$10/$50 per 1M，CursorBench 当前最高。
- 适合：从零规划多模态 3D 碰撞 + PPO 导航框架、理清多文件联动逻辑、最终技术评审。
- **极贵**：一次长会话可能吃掉 $5–10 API 额度，仅限关键节点。

### 2.3 明确避开的坑

| 选项 | 原因 |
|------|------|
| **Opus 4.7 fast mode**（$30/$150） | 极贵，Fable 5 在架构场景已足够 |
| **滥用 Max 模式** | 按 API 费率计费，消耗速度快很多 |
| **频繁新开对话** | 同一会话续聊可利用 cache read（输入价 10%），新开对话重复付全价 |
| **Fable 5 当日常默认** | 一次长会话可能吃掉大量 API 额度 |
| **Ollama 替代 Cursor Tab** | Tab 始终使用 Cursor 内置模型，Ollama 无法替换 |

### 2.4 参考定价（节选）

| 模型 | Input | Output | 用量池 | 备注 |
|------|-------|--------|--------|------|
| Composer 2.5 | $0.5/M | $2.5/M | 第一方 | 专为 agentic 编程优化 |
| Grok 4.5 | $2/M | $6/M | 第一方 | 适合长任务 |
| GPT-5.6 Terra | $2.5/M | $15/M | API | 中档推理 |
| GPT-5.6 Sol | $5/M | $30/M | API | 旗舰，需 Max Mode |
| Claude Fable 5 | $10/M | $50/M | API | 最贵，架构专用 |
| Claude Sonnet 5 | $2/M | $10/M | API | 促销至 2026-08-31，英文论文精读首选 |
| Gemini 3.5 Flash | $1.5/M | $9/M | API | 超长 PDF / 附录多的论文 |
| Kimi K2.7 Code | $0.95/M | $4/M | API | 中文阅读，默认隐藏需手动开启 |
| GLM 5.2 | $1.4/M | $4.4/M | API | 中文汇报，默认隐藏需手动开启 |
| Auto | $1.25/M | $6/M | 第一方 | 自动选型 |

---

## 3. 国内模型选型策略

国内模型价值不在替代 Composer/Sol，而在三件事上补位：**中文理解**、**便宜推理**、**本地视觉**。

### 3.1 三种接入方式

| 方式 | 代表模型 | 是否吃 Pro+ 额度 | 稳定性 |
|------|----------|------------------|--------|
| **Cursor 官方 API 池** | GLM 5.2、Kimi K2.7 Code | 吃 $70 API 池 | 最稳 |
| **BYOK + OpenAI 兼容接口** | DeepSeek、Qwen、MiniMax | 走独立 key，不走 Pro+ | 有坑（Base URL 冲突） |
| **OpenCode Zen BYOK** | GLM、Kimi、DeepSeek、MiMo（见 §3.5） | 走 Zen 账户余额，不走 Pro+ | 仅 `chat/completions` 类模型可用 |
| **本地 Ollama** | Qwen2.5-Coder、DeepSeek-R1、Qwen2.5-VL | 完全免费 | 仅 Chat/实验 |

### 3.2 国内模型分工

| 模型 | 接入方式 | 适合场景 | 不适合 |
|------|----------|----------|--------|
| **Kimi K2.7 Code** | Cursor API 池 | 读中文 VLN 论文、国内开源文档、中文注释密集的 ROS 代码 | 替代 Composer 日常改代码 |
| **GLM 5.2** | Cursor API 池 | 中文汇报材料、技术方案文档、executive summary | 硬核 Linux/CUDA 调试 |
| **DeepSeek V3/R1** | BYOK 或本地 Ollama | PPO 奖励函数、几何推导、复杂算法逻辑（极便宜） | 长程多文件 Agent |
| **Qwen2.5-Coder** | 本地 Ollama | 离线编码问答、单文件 debug | 替代 Cursor Tab |
| **Qwen2.5-VL** | 本地 Ollama | VLN 多模态验证（仿真器 RGB + 导航指令） | 云端 Agent 任务 |
| **小米 MiMo V2.5** | OpenCode Zen BYOK（`mimo-v2.5-free`） | 免费试模型、中文推理 | 替代 Composer 日常改代码 |

### 3.3 国内模型月占比（在 API 池内）

| 模型 | 月占比 | 典型任务 |
|------|--------|----------|
| Kimi K2.7 Code | ~10% | 中文论文/文档阅读、项目分析 |
| GLM 5.2 | ~3% | 写汇报、方案文档 |
| DeepSeek（BYOK，独立账户） | 不限 | 大量推理实验，不消耗 Pro+ |

### 3.4 文献阅读分工（中英文论文）

VLN 调研会同时遇到 arXiv/顶会英文论文和国内中文资料，**按语言分流，不要混用 Kimi 读英文**。

#### 英文论文（arXiv、CVPR、ICRA、NeurIPS 等）

| 阅读深度 | 推荐模型 | 用量池 | 说明 |
|----------|----------|--------|------|
| **批量速读 / 文献综述** | **Grok 4.5** | 第一方 | 默认首选；长上下文、不易半途而废，适合一次读 3–5 篇提炼方法对比 |
| **单篇精读 / 方法拆解** | **Claude Sonnet 5** | API | 促销价 $2/$10，擅长公式、实验设计、ablation 表解读；一个月精读 5–10 篇 landmark 论文 |
| **超长 PDF（附录多）** | **Gemini 3.5 Flash** | API | $1.5/$9，上下文窗口大，适合塞入完整 PDF + supplementary |
| **顶会论文 → 架构决策** | **Claude Fable 5** | API | 仅当论文方法直接影响你的 PPO/VLN 框架设计时启用，一个月 1–2 篇 |

**不推荐用 Kimi 读英文论文**：Kimi 优势在中文长文档，英文技术论文的方法论提炼和术语精度不如 Grok/Sonnet。

#### 中文论文 / 国内技术资料

| 阅读深度 | 推荐模型 | 用量池 | 说明 |
|----------|----------|--------|------|
| 中文论文、国内开源文档 | **Kimi K2.7 Code** | API | 中文语境理解更准确 |
| 中文资料 + 代码对照 | Kimi 读文档 + Grok 4.5 追代码 | API + 第一方 | 先 Kimi 提炼，再 Grok 对照实现 |

#### 英文论文推荐三步流程

```
1. Grok 4.5 批量速读    →  输出「方法表 + 实验对比 + 局限」结构化笔记
2. Sonnet 5 精读 2–3 篇  →  拆解核心公式/损失函数，对照你的 VLA-SLAM-Token 方案
3. Fable 5（偶尔）       →  判断「这篇论文的方法是否值得引入我们的架构」
```

#### 英文论文月占比（在整体 API 池内）

| 模型 | 月占比 | 典型任务 |
|------|--------|----------|
| Grok 4.5（英文论文速读） | 含在第一方 ~20% | 文献综述、Related Work 整理 |
| Sonnet 5（英文论文精读） | ~8% | landmark 论文方法拆解、跨论文对比 |
| Gemini 3.5 Flash | ~2% | 超长附录 PDF |
| Fable 5（论文驱动架构） | 含在 ~2% | 顶会方法直接影响设计时 |

### 3.5 OpenCode Zen BYOK（便宜试模型）

> **用途**：不消耗 Pro+ 的 $70 API 池，用 Zen 账户按量付费或免费模型做大量试验。  
> **官方文档**：[OpenCode Zen](https://open-code.ai/zh/docs/zen) · 模型列表 API：`https://opencode.ai/zen/v1/models`（2026-07-16 已核实）

#### 3.5.1 一次性配置（Cursor Settings → Models）

| 步骤 | 操作 |
|------|------|
| 1 | 打开 [opencode.ai/auth](https://opencode.ai/auth) → 登录 → 添加账单 → **Create API Key** |
| 2 | Cursor → **Settings → Models → API Keys** |
| 3 | 开启 **OpenAI API Key**，粘贴 Zen API Key |
| 4 | 开启 **Override OpenAI Base URL**，填 `https://opencode.ai/zen/v1` |
| 5 | 在 **Add Custom Model** 中逐个添加下表 Model ID（**必须完全一致**） |

**⚠️ 端点限制**：Zen 的 GPT（`/responses`）和 Claude（`/messages`）**不能**用 Cursor OpenAI BYOK。只添加 `chat/completions` 类模型。

#### 3.5.2 推荐模型清单（便宜试模型）

| 显示名（自定） | Model ID | Zen 定价（$/1M） | 适合试什么 |
|----------------|----------|------------------|------------|
| MiMo V2.5 Free | `mimo-v2.5-free` | **免费** | 首选试水；中文问答、轻量推理 |
| DeepSeek V4 Flash Free | `deepseek-v4-flash-free` | **免费** | 算法推导、代码逻辑 |
| DeepSeek V4 Flash | `deepseek-v4-flash` | $0.14 / $0.28 | 付费版，质量略好 |
| Kimi K2.5 | `kimi-k2.5` | $0.60 / $3.00 | 中文长文档阅读 |
| Kimi K2.7 Code | `kimi-k2.7-code` | $0.95 / $4.00 | 中文代码 + 文档对照 |
| GLM 5.2 | `glm-5.2` | $1.40 / $4.40 | 中文汇报草稿 |
| GLM 5 | `glm-5` | $1.00 / $3.20 | 更便宜的 GLM 备选 |

**建议起步组合**：先加 `mimo-v2.5-free` + `deepseek-v4-flash-free`，确认通了再加 Kimi/GLM。

#### 3.5.3 验证是否配置成功

1. 模型选择器选 `mimo-v2.5-free`（或你添加的自定义名）
2. 用 **Ask 模式**（Ctrl+L）发：

```
回复：Zen BYOK 测试成功，当前模型 ID 是？
```

3. 若返回 401/403 → 检查 API Key 和账单；404 → 检查 Model ID 拼写

#### 3.5.4 使用边界

| 可以做 | 不建议做 |
|--------|----------|
| Ask 模式读文档、试 prompt、中文资料整理 | 替代 Composer 2.5 做复杂 Agent 改代码 |
| 大量廉价推理实验（不碰 Pro+ 额度） | 开 Max 模式（Zen BYOK 无此概念，但上下文仍计费） |
| 对比 Kimi vs GLM vs DeepSeek 回答质量 | 指望完整工具链与 Cursor Agent 同等稳定 |

#### 3.5.5 切回 Composer/Grok 的开关纪律

```
用 Zen 模型时：  Override Base URL = ON  （https://opencode.ai/zen/v1）
用 Composer/Grok：Override Base URL = OFF
```

不关 Override 会导致内置模型请求也打到 Zen，出现莫名 404/鉴权失败。

#### 3.5.6 与 Pro+ 内置模型的分工

| 任务 | 用谁 | 计费 |
|------|------|------|
| 日常改代码、Agent | Composer 2.5 / Grok 4.5 | Pro+ 第一方池 |
| 便宜试 prompt、中文阅读草稿 | Zen `mimo-v2.5-free` / `deepseek-v4-flash-free` | Zen 免费额度 |
| 中文汇报定稿 | Pro+ 内置 GLM 5.2 或 Zen `glm-5.2` | 看哪边更便宜/更稳 |
| 英文论文 | Grok 4.5 / Sonnet 5 | Pro+ 池，不走 Zen |

---

## 4. 本地 Ollama 策略（RTX 5070，12GB VRAM）

> **注意**：本机为 **12GB 显存 + 32GB 系统内存**，不是 32GB 显存。模型必须塞进 12GB VRAM 才能保持可用速度。

### 4.1 推荐模型与显存占用

| 场景 | 模型 | 显存占用 | 与仿真器共存 |
|------|------|----------|--------------|
| 日常离线编码 | `qwen2.5-coder:7b` | ~4.7GB | ✅ 可以 |
| 复杂单文件 debug | `qwen2.5-coder:14b` | ~9GB | ❌ 独占 |
| 算法推理（按需） | `deepseek-r1:14b` | ~9GB | ❌ 独占 |
| VLN 多模态验证 | `qwen2.5vl:7b` | ~6GB | ⚠️ 勉强 |

### 4.2 Ollama 环境变量（systemd 配置）

`.bashrc` 对 systemd 服务不生效，正确做法：

```bash
sudo systemctl edit ollama.service
```

```ini
[Service]
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_KEEP_ALIVE=5m"
```

然后 `sudo systemctl restart ollama`。跑仿真前手动 `ollama stop <模型名>` 释放显存。

### 4.3 Cursor 接入 Ollama 的限制

- Cursor 请求经云端中转，**不能直接用 `localhost`**，需 Cloudflare Tunnel / ngrok 暴露 HTTPS 端点。
- 仅支持 Chat（Ctrl+L）和 Inline Edit（Ctrl+K），**不能替代 Tab 补全和完整 Agent**。
- API Key 填 `ollama`，Base URL 填 `https://<隧道地址>/v1`。

---

## 5. VLN 项目专项工作流

以 motion 项目（nav_pipline、VLA-SLAM-Token、弱网中间件等）为例：

### 5.1 四阶段模型映射

| 阶段 | 任务 | 推荐模型 | 用量池 |
|------|------|----------|--------|
| **阶段 1**：纯文本导航逻辑 | 写导航代码、推 PPO 算法 | Composer 2.5 + DeepSeek-R1（本地） | 第一方 + 免费 |
| **阶段 2a**：读英文 VLN 论文 | arXiv/顶会论文综述与精读 | Grok 4.5 + Sonnet 5 | 第一方 + API |
| **阶段 2b**：读中文资料 | 国内论文、中文文档 | Kimi K2.7 Code | API |
| **阶段 2c**：深读工程代码 | 追 nav_pipline 调用链 | Grok 4.5 | 第一方 |
| **阶段 3**：多模态视觉实验 | 仿真器 RGB + 导航指令验证 | Qwen2.5-VL（本地 Ollama） | 免费 |
| **阶段 4**：架构决策 / 写汇报 | PPO 框架设计、对外材料 | Fable 5 + GLM 5.2 | API |

### 5.2 推荐四步分析流程

#### 第一步：项目地图（第一方池）
- **模型**：Composer 2.5
- **任务**：目录结构、主入口、数据流、模块关系图、阅读顺序
- **参考**：`03-技术分析/nav_pipline工程代码阅读笔记.md`、`02-架构设计/Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md`

#### 第二步：深挖关键路径（第一方池）
- **模型**：Grok 4.5
- **任务**：沿 nav_pipline 追调用链到底；对照 `02-架构设计/Go2-VLA-SLAM-Token技术方案.md` 核验一致性
- **优势**：长任务不易半途而废

#### 第三步：架构评审（API 池）
- **模型**：Claude Fable 5（关键节点）或 Sonnet 5（日常评审）
- **任务**：架构 trade-off、SLAM Token 风险点、改进建议
- **参考**：`02-架构设计/SLAM-Token弱网中间件-汇报材料.md`、`02-架构设计/Go2-VLA-SLAM-Token技术方案.md`

#### 第四步：中文汇报产出（API 池）
- **模型**：GLM 5.2
- **任务**：将分析结果整理为中文汇报材料、executive summary

#### 系统排障（按需，API 池）
- **模型**：GPT-5.6 Sol
- **适用**：Docker EGL、Habitat-Sim CMake、CUDA 编译链等环境级问题

---

## 6. 实用技巧

### 6.1 先小后大

1. Composer 2.5 产出模块地图
2. Grok 4.5 深挖 1–2 条关键链路
3. Fable 5 / Sonnet 5 做综合判断
4. GLM 5.2 输出中文汇报

### 6.2 用 @ 文件定向喂上下文

```
@03-技术分析/nav_pipline工程代码阅读笔记.md
@02-架构设计/Go2-VLA-SLAM-Token技术方案.md
@某个核心源码目录
```

比让模型全库乱搜更准、更省 token。

### 6.3 长分析尽量续聊

同一会话追问比每次重讲背景便宜很多。Anthropic 模型 cache read 仅为输入价 10%。

### 6.4 Ask 模式 vs Agent 模式

| 模式 | 适合模型 | 适合任务 |
|------|----------|----------|
| **Ask 模式** | Grok 4.5 / Sonnet 5 / Kimi K2.7 | 读论文、解释设计、评审方案 |
| **Agent 模式** | Composer 2.5 / Grok 4.5 / Sol | 自动搜代码、跨文件追踪、环境排障 |

### 6.5 Max 模式使用原则

仅在以下情况开启：需要超大上下文窗口、使用 Sol/Fable 等需 Max Mode 的模型。多数场景用 **定向 @ 文件 + 分阶段分析** 更划算。

### 6.6 BYOK Base URL 开关

使用 DeepSeek/Qwen/**OpenCode Zen** BYOK 时，Override Base URL 会影响 Cursor 内置模型。用 Zen/国内模型时开启，切回 Composer/Grok 时**必须关闭**（见 §3.5.5）。

---

## 7. Prompt 模板

### 7.1 项目地图（Composer 2.5）

```
请分析 @<项目目录> 的整体结构：
1. 列出顶层目录及每个目录的职责
2. 找出主入口、核心数据流
3. 画出模块依赖关系（可用 mermaid）
4. 给出推荐阅读顺序，并说明每条链路的阅读目的
输出保存为 markdown 笔记格式。
```

### 7.2 关键链路深挖（Grok 4.5）

```
基于 @<已有笔记> 和 @<核心源码目录>，深入追踪 <功能名> 的完整调用链：
1. 从入口到出口的每一步调用
2. 关键数据结构及其流转
3. 与 @<技术方案.md> 的设计是否一致，列出不一致处
4. 潜在问题与改进建议
```

### 7.3 架构评审（Fable 5 / Sonnet 5）

```
基于以下材料，做架构评审：
@<阅读笔记.md>
@<技术方案.md>
@<汇报材料.md>

请输出：
1. 当前架构优缺点
2. 关键设计 trade-off 分析
3. 风险点与缓解措施
4. 可落地的改进建议（按优先级排序）
5. 若用于对外汇报，给出 1 页 executive summary
```

### 7.4 英文论文批量速读（Grok 4.5）

```
请阅读以下 VLN 相关论文（@<论文.pdf 或粘贴摘要>），输出结构化文献笔记：

1. 问题定义：这篇论文解决什么 VLN 子问题？
2. 核心方法：模型架构、输入输出、损失函数（如有公式请保留）
3. 实验设置：数据集、baseline、主要指标
4. 关键结果：SOTA 对比、ablation 结论
5. 局限与可改进点
6. 与 @02-架构设计/Go2-VLA-SLAM-Token技术方案.md 的关联：哪些思路可借鉴、哪些不适用

输出格式：markdown 表格 + 每条 3–5 句摘要，便于写入知识体系文档。
```

### 7.5 英文论文精读（Sonnet 5）

```
请精读这篇 VLN 论文：@<论文.pdf>

深度拆解：
1. 方法部分：逐步解释每个模块的设计动机与数学形式
2. 与经典方法（如 R2R、CMA、HAMT）的差异
3. 实验部分：哪些结论有统计支撑，哪些是作者主张
4. 复现难度评估：需要哪些仿真环境、数据、算力
5. 对 @02-架构设计/Go2-VLA-SLAM-Token技术方案.md 的具体启发：可引入的模块、需规避的坑

输出：一份可纳入 `Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md` 的精读笔记。
```

### 7.6 中文汇报（GLM 5.2）

```
基于以下技术分析材料，撰写中文汇报文档：
@<架构评审结果.md>
@<技术方案.md>

请输出：
1. 项目背景与目标（1 段）
2. 核心技术方案概述（含架构图描述）
3. 关键创新点与 trade-off
4. 当前进展与风险
5. 下一步计划（按优先级）
格式：适合向技术负责人汇报的 markdown 文档。
```

### 7.7 系统排障（Sol）

```
我在 Ubuntu 24.04 上遇到以下环境/编译问题：
<粘贴完整报错日志>

环境信息：
- GPU: RTX 5070, Driver 595.84
- OS: Ubuntu 24.04
- 相关组件: <Docker/Habitat-Sim/CUDA 等>

请逐步排查并给出可执行的修复命令。
```

---

## 8. 额度预估与兜底

| 使用强度 | 月总用量参考 | Pro+ 是否够用 |
|----------|-------------|---------------|
| 每天 Tab 补全 | 通常 < $20 | 绰绰有余 |
| 少量 Agent | 通常 < $20 | 够用 |
| 每天 Agent（含项目分析） | $60–$100 | 基本够用，第一方池扛大部分 |
| 重度多 Agent / 自动化 | $200+ | 考虑 Ultra 或开启按需计费 |

**$60 严格预算建议**：

- 关闭按需付费
- 80% 任务走 Composer/Grok（第一方池）
- API 池按 Sonnet 8% + Sol 8% + Kimi 5% + GLM 3% + Fable 2% 分配（英文论文精读走 Sonnet，中文资料走 Kimi）
- DeepSeek BYOK、**OpenCode Zen BYOK** 和本地 Ollama 不计入 Pro+ 额度

超出包含用量后可选：开启按需用量（同 API 费率）或升级 Ultra（$200/月，$400 API 额度）。

---

## 9. 快速查阅卡片

```
┌──────────────────────────────────────────────────────────────┐
│  Pro+ 模型选型速查（$60 预算版）                              │
├──────────────────────────────────────────────────────────────┤
│  日常改代码          →  Composer 2.5          [第一方池]    │
│  长 Agent / 深读工程 →  Grok 4.5              [第一方池]    │
│  中等复杂推理        →  GPT-5.6 Terra         [API 池]     │
│  系统级硬核 Debug    →  GPT-5.6 Sol           [API 池]     │
│  架构与关键决策      →  Claude Fable 5        [API 池, 偶尔]│
│  读英文论文（速读）  →  Grok 4.5              [第一方池]   │
│  读英文论文（精读）  →  Sonnet 5              [API 池]     │
│  读中文论文/文档     →  Kimi K2.7 Code        [API 池]     │
│  写中文汇报          →  GLM 5.2               [API 池]     │
│  便宜试模型 / 不耗 Pro+  →  Zen BYOK（§3.5）   [Zen 账户]   │
│    首选 mimo-v2.5-free / deepseek-v4-flash-free              │
│    进阶 kimi-k2.7-code / glm-5.2                             │
│  VLN 视觉实验        →  Qwen2.5-VL            [本地 Ollama] │
│  离线编码            →  Qwen2.5-Coder         [本地 Ollama] │
│  代码自动补全        →  Cursor Tab            [内置, 无限]  │
│  便宜算法推理        →  DeepSeek R1           [BYOK/本地]  │
│  ⚠️ 用 Zen 时开 Override；切回 Composer 必须关 Override    │
│  避免                →  Opus fast / 滥用 Max / Fable 日常  │
└──────────────────────────────────────────────────────────────┘
```

---

## 10. 相关本地文档

| 文件 | 用途 |
|------|------|
| `03-技术分析/nav_pipline工程代码阅读笔记.md` | nav 工程代码阅读笔记 |
| `02-架构设计/Go2-VLA-SLAM-Token技术方案.md` | VLA-SLAM-Token 技术方案 |
| `02-架构设计/SLAM-Token弱网中间件-汇报材料.md` | 弱网中间件汇报材料 |
| `02-架构设计/Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md` | 流式空间数据管道知识体系 |
| `04-文献阅读/文献阅读prompt.md` | 文献阅读 Prompt 模板 |

---

*文档基于 Cursor 官方定价页与 Pro+ 方案整理，定价可能随官方更新而变化，请以 [cursor.com/cn/docs/models-and-pricing](https://cursor.com/cn/docs/models-and-pricing) 为准。*
