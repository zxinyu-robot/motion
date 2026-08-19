# -*- coding: utf-8 -*-
"""专利04（语义优先与自组网自适应的空间数据语义化上传融合）全部附图（图1-图8）。"""
import os
from _patent_draw import new_canvas, box, arrow, caption, label, frame, vflow, save

OUT = os.path.dirname(os.path.abspath(__file__))
def P(name): return os.path.join(OUT, name)


def fig1():
    XM, YM = 100.0, 144.0
    fig, ax = new_canvas(XM, YM, figw=8.4)
    items = [
        ("机器人端传感器采集与本地 SLAM", "101"),
        ("计算任务语义价值 V_sem  →  分级 P0 / P1 / P2 / P3", "102"),
        ("基于共享语义字典进行语义提取与语义编码（联合信源信道编码）", "103"),
        ("感知自组网链路状态：跳数 / 带宽 / 丢包 / 拥塞 / 拓扑", "104"),
        ("自适应选择：编码强度 / 上传等级 / 路由路径", "105"),
        ("经移动自组网多跳转发（含中继与机会式转发）  →  边缘节点", "106"),
        ("边缘端语义解码与语义恢复", "107"),
        ("多机一致性 + 几何 / 协方差 可信校验（抑制幻觉）", "108"),
        ("跨机器人匹配  →  约束生成  →  世界模型增量更新", "109"),
    ]
    vflow(ax, items, cx=44, w=74, top=YM - 8, bot=12, fontsize=10.5)
    caption(ax, "图1  方法总体流程图", XM)
    save(fig, P("04-图1-方法总体流程图.png"))


def fig2():
    XM, YM = 108.0, 90.0
    fig, ax = new_canvas(XM, YM, figw=9.8)
    rs = [("机器人R1（数据源）", 68), ("机器人R2（数据源）", 56), ("机器人R3（数据源）", 44)]
    for name, y in rs:
        box(ax, 18, y, 24, 9, name, fontsize=9, ref_side="left")
    box(ax, 48, 62, 22, 10, "无人机（中继）", fontsize=9.5, ref="201")
    box(ax, 48, 44, 22, 9, "机器人R4（中继）", fontsize=9, ref="202")
    box(ax, 74, 56, 14, 10, "R5（网关）", fontsize=9.5, ref="203")
    box(ax, 94, 56, 14, 10, "边缘节点", fontsize=9.5, ref="204")
    for name, y in rs:
        arrow(ax, 18 + 12, y, 48 - 11, 58 if y > 52 else 46)
    arrow(ax, 48 + 11, 62, 74 - 7, 57)
    arrow(ax, 48 + 11, 44, 74 - 7, 55)
    arrow(ax, 74 + 7, 56, 94 - 7, 56)
    label(ax, 33, 71, "Mesh 多跳", fontsize=9)
    label(ax, 54, 30, "角色可动态切换：数据源、中继、网关、边缘 之间相互转换", fontsize=9.5)
    label(ax, 54, 22, "链路中断时：邻居发现  →  重路由 / 机会式转发（DTN）", fontsize=9.5)
    caption(ax, "图2  移动自组网拓扑与节点角色切换示意图", XM)
    save(fig, P("04-图2-移动自组网拓扑与节点角色切换示意图.png"))


def fig3():
    XM, YM = 110.0, 100.0
    fig, ax = new_canvas(XM, YM, figw=10.0)
    box(ax, 55, YM - 12, 96, 9,
        "V_sem = u1·V_task + u2·V_anomaly + u3·V_constraint + u4·V_novelty + u5·V_quality - u6·V_redundancy",
        fontsize=9.2, ref="301")
    prio = [
        ("P0（最高）：任务关键语义观测", "302"),
        ("P1：位姿约束 / 回环 / 协方差", "303"),
        ("P2：几何摘要（降采样 / 占据栅格）", "304"),
        ("P3（最低）：稠密原始几何（链路充裕补传）", "305"),
    ]
    top, bot = YM - 26, 18
    ys = [top - (top - bot) * (i + 0.5) / 4 for i in range(4)]
    for (txt, ref), y in zip(prio, ys):
        box(ax, 30, y, 44, 11, txt, fontsize=9, ref=ref, ref_side="left")
    arrow(ax, 55, YM - 12 - 4.5, 30, ys[0] + 5.5)
    label(ax, 36, YM - 20, "分级", fontsize=9)
    box(ax, 85, (top + bot) / 2, 38, 56,
        "语义数据包字段：\npacket_id / source_agent_id\npriority（P0-P3）\nsemantic_dict_version\ncodec_version / payload_type\npayload / map_quality_score\npose_covariance / validity\nrouting_hint（max_hops / deadline）",
        fontsize=8.6, ref="306")
    caption(ax, "图3  任务语义价值分级与多级语义包结构图", XM)
    save(fig, P("04-图3-语义价值分级与多级语义包结构图.png"))


def fig4():
    XM, YM = 108.0, 92.0
    fig, ax = new_canvas(XM, YM, figw=9.8)
    inputs = [
        ("V_sem（语义价值）", "401"),
        ("Q_link（链路质量）", "402"),
        ("Q_path（路径质量）", "403"),
        ("Q_edge（边缘负载）", "404"),
        ("C_data（数据成本）", "405"),
    ]
    top, bot = YM - 14, 30
    ys = [top - (top - bot) * (i + 0.5) / 5 for i in range(5)]
    for (txt, ref), y in zip(inputs, ys):
        box(ax, 20, y, 28, 9, txt, fontsize=9, ref=ref, ref_side="left")
    cx, cy = 58, (top + bot) / 2
    box(ax, cx, cy, 30, 16,
        "D_upload =\na·V_sem + b·Q_link\n+ c·Q_path + d·Q_edge\n- e·C_data", fontsize=8.8)
    label(ax, cx, cy + 8 + 2.5, "406", fontsize=11)
    for y in ys:
        arrow(ax, 20 + 14, y, cx - 15, cy + (y - cy) * 0.1)
    box(ax, 92, cy, 26, 34,
        "编码强度自适应\n冗余（前向纠错 / 多路径）自适应\n路由自适应（max_hops / deadline）\n机会缓存补传",
        fontsize=8.4, ref="407")
    arrow(ax, cx + 15, cy, 92 - 13, cy)
    caption(ax, "图4  自组网链路自适应上传决策模块图", XM)
    save(fig, P("04-图4-自组网链路自适应上传决策模块图.png"))


def fig5():
    XM, YM = 108.0, 116.0
    fig, ax = new_canvas(XM, YM, figw=9.0)
    items = [
        ("接收语义数据包", "501"),
        ("语义解码与恢复（依共享字典 + 协商版本）", "502"),
        ("来源与版本校验：packet_id / agent_id / 字典版本 / 时间戳 / 坐标系", "503"),
        ("可信校验（抑制幻觉）", "504"),
        ("跨机器人匹配  →  约束生成（按置信度入全局位姿图）", "505"),
        ("写入世界模型  →  发布更新事件", "506"),
    ]
    ys, h = vflow(ax, items, cx=42, w=60, top=YM - 8, bot=12, fontsize=9.2, ref_side="left")
    box(ax, 88, ys[3], 32, h * 2.4,
        "多机一致性校验\n几何 / 协方差校验\n时间新鲜度 / 有效期校验\n仅生成式重建且无原始观测支撑\n→ 标记“低可信 / 待确认”",
        fontsize=8.2, ref="504a")
    arrow(ax, 42 + 30, ys[3], 88 - 16, ys[3])
    caption(ax, "图5  边缘端语义解码与可信融合流程图", XM)
    save(fig, P("04-图5-边缘端语义解码与可信融合流程图.png"))


def fig6():
    XM, YM = 108.0, 110.0
    fig, ax = new_canvas(XM, YM, figw=9.4)
    box(ax, 42, YM - 14, 44, 10, "生成语义包并按优先级排队", fontsize=10, ref="601", ref_side="left")
    box(ax, 42, YM - 34, 26, 10, "链路可达？", fontsize=10, ref="602", ref_side="left")
    arrow(ax, 42, YM - 14 - 5, 42, YM - 34 + 5)
    # 否：右侧缓存→机会式转发
    box(ax, 84, YM - 34, 38, 11, "本地缓存（P0 优先保留）\n周期性邻居发现", fontsize=9, ref="603")
    box(ax, 84, YM - 58, 30, 10, "机会式转发（DTN）", fontsize=9.5, ref="604")
    arrow(ax, 42 + 13, YM - 34, 84 - 19, YM - 34)
    label(ax, 64, YM - 31, "否", fontsize=9)
    arrow(ax, 84, YM - 34 - 5.5, 84, YM - 58 + 5)
    label(ax, 92, YM - 46, "遇可达邻居 / 移动网关", fontsize=8.2, rotation=90)
    # 是：多跳转发
    box(ax, 30, YM - 58, 28, 10, "多跳转发至边缘", fontsize=9.5, ref="605")
    arrow(ax, 42 - 8, YM - 34 - 5, 30, YM - 58 + 5)
    label(ax, 28, YM - 45, "是", fontsize=9)
    box(ax, 50, YM - 78, 26, 10, "边缘确认", fontsize=10, ref="606")
    arrow(ax, 30, YM - 58 - 5, 50 - 8, YM - 78 + 5)
    arrow(ax, 84, YM - 58 - 5, 50 + 10, YM - 78 + 4)
    box(ax, 50, YM - 96, 50, 10, "依缺失列表补传（P0 / P1 优先，后补 P2 / P3）", fontsize=9.2, ref="607")
    arrow(ax, 50, YM - 78 - 5, 50, YM - 96 + 5)
    caption(ax, "图6  拒止 / 间歇通信环境下机会式缓存与补传流程图", XM)
    save(fig, P("04-图6-机会式缓存与补传流程图.png"))


def fig7():
    XM, YM = 112.0, 104.0
    fig, ax = new_canvas(XM, YM, figw=10.2)
    left = ["应用：全量数据", "TCP：有序可靠重传", "IP", "MAC / PHY"]
    right = ["应用 / 中间件：语义分级 P0-P3", "（绕过 TCP）数据报 / L2 帧：差异化可靠",
             "MAC / PHY：信道状态反馈", "跨层（信道驱动语义编码）"]
    top = YM - 18
    lys = [top - 16 * i for i in range(4)]
    for i, (lt, y) in enumerate(zip(left, lys)):
        box(ax, 28, y, 40, 11, lt, fontsize=9.2,
            ref=("701" if i == 0 else "702" if i == 1 else None), ref_side="left")
    for i, (rt, y) in enumerate(zip(right, lys)):
        box(ax, 82, y, 50, 11, rt, fontsize=8.8,
            ref=("703" if i == 0 else "704" if i == 1 else None))
    arrow(ax, 28 + 20, (lys[1] + lys[2]) / 2, 82 - 25, (lys[1] + lys[2]) / 2)
    label(ax, 55, (lys[1] + lys[2]) / 2 + 3, "对比", fontsize=10)
    label(ax, 28, 18, "传统方案（TCP）", fontsize=10)
    label(ax, 82, 18, "本发明（数据链路层语义传输）", fontsize=10)
    label(ax, 28, 11, "问题：队头阻塞 / 误判拥塞降速 / 重传开销", fontsize=8.6)
    label(ax, 82, 11, "优势：消除队头阻塞 / 按语义配可靠性", fontsize=8.6)
    caption(ax, "图7  TCP 传输与数据链路层语义传输协议栈对比图", XM)
    save(fig, P("04-图7-TCP与数据链路层语义传输协议栈对比图.png"))


def fig8():
    XM, YM = 114.0, 92.0
    fig, ax = new_canvas(XM, YM, figw=10.4)
    box(ax, 18, YM - 18, 18, 11, "P0 / P1", fontsize=10, ref="801", ref_side="left")
    box(ax, 72, YM - 18, 62, 13,
        "DDS QoS：RELIABLE / TRANSPORT_PRIORITY\n确定性：5G-TSN（URLLC）/ 有线 TSN",
        fontsize=8.6, ref="802")
    arrow(ax, 18 + 9, YM - 18, 72 - 31, YM - 18)
    label(ax, 33, YM - 14, "映射", fontsize=9)
    box(ax, 18, YM - 38, 18, 11, "P2 / P3", fontsize=10, ref="803", ref_side="left")
    box(ax, 72, YM - 38, 62, 11, "DDS QoS：BEST_EFFORT；5G-TSN（eMBB）",
        fontsize=8.8, ref="804")
    arrow(ax, 18 + 9, YM - 38, 72 - 31, YM - 38)
    label(ax, 33, YM - 34, "映射", fontsize=9)
    frame(ax, 8, 12, XM - 16, 30)
    label(ax, XM / 2, 38, "链路状态驱动切换（切换对上层 World Model 透明）", fontsize=10)
    rows = [
        "有基础设施  →  5G-TSN / TSN（确定性承载）",
        "无基础设施  →  IEEE 802.11s（Mesh 自组网）",
        "极弱带宽    →  IEEE 802.15.4（心跳 / P0 兜底）",
    ]
    for i, r in enumerate(rows):
        label(ax, XM / 2, 31 - i * 6.5, r, fontsize=9.2)
    caption(ax, "图8  多模异构链路自适应承载与协议映射示意图", XM)
    save(fig, P("04-图8-多模异构链路自适应承载与协议映射图.png"))


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6(); fig7(); fig8()
    print("ALL P04 DONE")
