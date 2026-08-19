# SLAM-Token 主专利（交底书骨架 / 调度入口）

> **整链叙事**：`叙事/C族技术交底故事.md`  
> **核心 + 卫星（2026-08-03）**：  
> - **C-b** `交底书/Cb_发明专利_内容寻址LayerDelta封装与版本组合_技术交底书.md`  
> - **C-c** `交底书/Cc_发明专利_AccessTicket消费契约分发_技术交底书.md`  
> - **C-h** `交底书/Ch_发明专利_多机器人地图版本并发管理_技术交底书.md`  
> - **C-a** `交底书/Ca_…端侧增量分层空间地图库_技术交底书.md`（薄）  
> **后续素材**：`历史素材/C2_…初稿.md` → C-d/e；`历史素材/C0_…初稿.md` → 已映射 C-b  
> **附图**：整链 `附图/C-图1`～`图8`；分案 `Cb/Cc/Ch/Ca-图*`  
> **打包清单**：`交代理人打包清单.md`  
> **保密**：`patent-sensitive`

---

## 目的

端侧分层库（C-a）把局部世界打成 **LayerDelta**（C-b）经版本 DAG + compose 组织；边侧按 **AccessTicket**（C-c）按需物化视图；多机写冲突由 **C-h** 仲裁；拼接与动作闭环见 C-d/e（素材 C2）。

## 技术问题

1. 全量点云/视频上云不可持续；增量对象与版本组合语义不清。  
2. 单一低维地图出口难支撑多维消费者；缺消费契约而非购图鉴权。  
3. 多机并发写缺 base_version 条件控制；动作链路与版本闭环另案 C-d/e。

## 核心方案（上位 · 已拆案）

| 编号 | 内容 |
|------|------|
| **C-b** | LayerDelta 信封 + 内容寻址 DAG + compose 纯函数 |
| **C-c** | AccessTicket：layer/region/version_cap/qos + lazy materialization |
| **C-h** | base_version_hash 乐观并发 + 冲突仲裁 |
| **C-a** | 端侧增量分层库（薄；划界南湖） |
| **C-d/e** | 按需拼接、ActionGroup、校验降级（C2 素材） |

弱网细调度 → 从属 + A4/论文；**勿把 content-hash 单独当 C-b 唯一区别特征**。

## 分案状态


| 编号 | 角色 | 状态 |
|------|------|------|
| **C-b** | 核心 A+B | 交底 md+png ✅ |
| **C-c** | 卫星 C | 交底 md+png ✅ |
| **C-h** | 卫星 D | 交底 md+png ✅ |
| **C-a** | 上游薄 | 交底 md+png ✅ |
| **C-d/e** | 拼接/动作 | C2 初稿素材 |
| ~~C0~~ | 历史 | → C-b |
| ~~C2~~ | 历史 | → C-d/e |

## 交所最小包

见 `交代理人打包清单.md`：C-b +（可选 C-c/C-h/C-a）+ 分案附图 + 可选 `叙事/C族技术交底故事.md` + 申请人信息；输出在 `正式包/`。

## 【需代理人确认】

C-b/C-c/C-h 交费顺序；C-b 对表 NNG + hash 近邻；C-c 对表高德购图令牌；C-h 与 A3 划界；EVICT≠障碍消失进 C-b 从属。

---

## 文档元数据


| 字段 | 值 |
|------|-----|
| id | PAT-SLAM-TOKEN-MAIN |
| type | patent |
| title | C 族 SLAM-Token 调度骨架 |
| stage | disclosure |
| status | in-progress |
| priority | P0 |
| confidentiality | patent-sensitive |
| inventors | 曾欣宇 |
| sources | C族技术交底故事；Cb/Cc/Ch/Ca 交底；专利族谱 |
| updated | 2026-08-03 |
| next | docx/png ✅；代理人特征表 |
