# -*- coding: utf-8 -*-
"""专利01（多机异构空间数据运行时架构）全部附图（图1-图7）。"""
import os
from _patent_draw import new_canvas, box, arrow, caption, label, vflow, save

OUT = os.path.dirname(os.path.abspath(__file__))
def P(name): return os.path.join(OUT, name)


def fig1():
    XM, YM = 100.0, 140.0
    fig, ax = new_canvas(XM, YM, figw=8.6)
    items = [
        ("多形态机器人节点\n（四足机器人 / 无人机 / 自动导引车 / 自主移动机器人 / 固定传感器）", "101"),
        ("机器人端空间数据采集层\n传感器采集 / 建图前端 / 局部子图 / 语义观测 / 状态监控", "102"),
        ("统一协议层\n机器人契约 / 局部子图 / 语义观测 / 任务事件 / 语义数据包", "103"),
        ("自组网传输层\n组网 / 动态路由 / 角色切换 / 机会式转发 / 语义优先分级回传", "104"),
        ("边缘端空间数据运行时\n时间同步 / 坐标统一 / 质量评估 / 语义解码 / 可信校验 / 子图融合 / 地图更新", "105"),
        ("空间世界模型层\n几何地图 / 语义地图 / 动态对象 / 任务状态 / 机器人状态 / 不确定性", "106"),
        ("上层应用\n多机调度 / 巡检 / 物流 / 回放评估 / 数据集构建 / 模型训练", "107"),
    ]
    ys, h = vflow(ax, items, cx=44, w=64, top=YM - 8, bot=14, fontsize=11.5)
    xr = 90
    arrow(ax, xr, ys[6] + h / 2, xr, ys[0] - h / 2)
    label(ax, xr + 3, (ys[0] + ys[6]) / 2, "反向下发数据补充请求", fontsize=11, rotation=90)
    caption(ax, "图1  系统总体架构图", XM)
    save(fig, P("01-图1-系统总体架构图.png"))


def fig2():
    XM, YM = 100.0, 118.0
    fig, ax = new_canvas(XM, YM, figw=8.6)
    items = [
        ("传感器采集\n激光雷达 / 相机 / 惯性测量单元 / 卫星定位 / 关节状态 / 轮速 / 电量 / 资源", "201"),
        ("建图前端与状态估计", "202"),
        ("平台相关状态生成\n四足地形状态 / 无人机飞行约束 / 自动导引车载荷状态", "203"),
        ("语义处理\n目标 / 异常区域 / 障碍物 / 可通行区域  →  语义观测", "204"),
        ("消息封装\n机器人状态 / 局部子图 / 语义观测 / 任务事件", "205"),
        ("经通信接口（数据分发服务 / 消息队列 / 远程调用 等）发送至边缘端", "206"),
    ]
    ys, h = vflow(ax, items, cx=38, w=52, top=YM - 8, bot=12, fontsize=11, ref_side="left")
    # 202 侧分支
    bx, bw = 82, 30
    box(ax, bx, ys[1], bw, h, "局部位姿 / 关键帧\n局部地图点 / 局部子图", fontsize=10.5, ref="202a")
    arrow(ax, 38 + 52 / 2, ys[1], bx - bw / 2, ys[1])
    caption(ax, "图2  机器人端数据采集流程图", XM)
    save(fig, P("01-图2-机器人端数据采集流程图.png"))


def fig3():
    XM, YM = 100.0, 122.0
    fig, ax = new_canvas(XM, YM, figw=8.4)
    items = [
        ("接收多机上传数据", "301"),
        ("时间同步检查  →  坐标统一（依机器人契约 / 地图契约）", "302"),
        ("完整性校验  →  质量评估 / 是否参与当前融合窗口判定", "303"),
        ("子图间约束计算：迭代最近点 / 正态分布变换 / 扫描上下文 / 语义匹配", "304"),
        ("加入全局位姿图 / 因子图  →  局部 / 全局优化", "305"),
        ("更新全局地图 / 语义地图 / 拓扑图 / 不确定区域", "306"),
        ("写入空间世界模型", "307"),
    ]
    vflow(ax, items, cx=44, w=72, top=YM - 8, bot=12, fontsize=11)
    caption(ax, "图3  边缘端子图融合流程图", XM)
    save(fig, P("01-图3-边缘端子图融合流程图.png"))


def fig4():
    XM, YM = 100.0, 92.0
    fig, ax = new_canvas(XM, YM, figw=9.0)
    # 根节点
    box(ax, 50, YM - 14, 56, 11,
        "机器人契约\n（机器人ID / 机器人类型 / 传感器配置 / 约束）", ref="401", fontsize=11)
    children = [
        (16, "机器人状态\n位姿 / 健康", "402"),
        (38, "局部子图\n关键帧 / 协方差", "403"),
        (62, "语义观测\n对象 / 位姿 / 置信度", "404"),
        (86, "任务事件\n任务状态", "405"),
    ]
    cy = 30
    for cx, txt, ref in children:
        box(ax, cx, cy, 20, 13, txt, fontsize=10)
        arrow(ax, 50, YM - 14 - 11 / 2, cx, cy + 13 / 2)
        label(ax, cx, cy - 13 / 2 - 3, ref, fontsize=11)
    label(ax, 50, YM - 24, "机器人ID 贯穿各对象引用", fontsize=10)
    # 子图ID 被语义观测来源引用
    arrow(ax, 38 + 10, cy, 62 - 10, cy)
    label(ax, 50, cy - 9, "来源引用\n（子图ID / 传感器ID）", fontsize=9.5)
    caption(ax, "图4  统一数据对象关系图", XM)
    save(fig, P("01-图4-统一数据对象关系图.png"))


def fig5():
    XM, YM = 100.0, 108.0
    fig, ax = new_canvas(XM, YM, figw=8.6)
    items = [
        ("机器人端 / 边缘端增量  →  世界模型增量", "501"),
        ("校验  →  对象关联  →  冲突处理", "502"),
        ("更新结构化世界状态", "503"),
        ("查询接口", "504"),
        ("返回世界状态", "505"),
    ]
    ys, h = vflow(ax, items, cx=40, w=56, top=YM - 8, bot=14, fontsize=11, ref_side="left")
    # 503 侧：历史索引/置信度维护
    box(ax, 84, ys[2], 26, h, "历史索引 /\n置信度维护", fontsize=10, ref="503a")
    arrow(ax, 40 + 56 / 2, ys[2], 84 - 26 / 2, ys[2])
    # 504 与 上层应用 双向
    box(ax, 84, ys[3], 26, h, "上层应用\n调度/导航/巡检/\n数据闭环/训练", fontsize=9.5, ref="506")
    arrow(ax, 40 + 56 / 2, ys[3], 84 - 26 / 2, ys[3], two_way=True)
    label(ax, 62, ys[3] + 5.5, "查询 / 返回", fontsize=9)
    caption(ax, "图5  空间世界模型更新与查询流程图", XM)
    save(fig, P("01-图5-世界模型更新与查询流程图.png"))


def fig6():
    XM, YM = 100.0, 86.0
    fig, ax = new_canvas(XM, YM, figw=9.2)
    rows = [
        (YM - 14, "场景一  园区巡检", "无人机（外立面/屋顶）\n四足（楼梯/地下室）\n自动导引车（道路运输）", "园区全局世界模型", "601"),
        (YM - 38, "场景二  工业厂区", "四足（热成像/声音/点云）\n无人机（高处管线）\n自动导引车（固定路线）", "设备异常+位置+时间\n世界模型", "602"),
        (YM - 62, "场景三  应急救援", "无人机（粗略地图）\n四足（室内补充点云/语义）", "未探索/危险/可通行区\n世界模型", "603"),
    ]
    for y, title, src, wm, ref in rows:
        box(ax, 22, y, 32, 16, src, fontsize=9.5, ref=ref, ref_side="left")
        box(ax, 54, y, 16, 11, "边缘融合", fontsize=10)
        box(ax, 82, y, 28, 13, wm, fontsize=9.5)
        arrow(ax, 22 + 16, y, 54 - 8, y)
        arrow(ax, 54 + 8, y, 82 - 14, y)
        label(ax, 22, y + 10, title, fontsize=10)
    caption(ax, "图6  多场景实施例示意图", XM)
    save(fig, P("01-图6-多场景实施例示意图.png"))


def fig7():
    XM, YM = 106.0, 90.0
    fig, ax = new_canvas(XM, YM, figw=9.8)
    # 左侧三机器人
    rs = [("机器人R1", 70), ("机器人R2", 58), ("机器人R3", 46)]
    for name, y in rs:
        box(ax, 16, y, 20, 9, name, fontsize=10)
    # Mesh 多跳 中继
    box(ax, 46, 64, 22, 11, "移动中继\n（无人机）", fontsize=10, ref="701")
    box(ax, 46, 46, 22, 9, "机器人R4\n（远端多跳）", fontsize=9.5)
    box(ax, 72, 58, 14, 10, "网关节点", fontsize=10)
    label(ax, 72, 58 - 5 - 3, "702", fontsize=11)
    box(ax, 92, 58, 14, 10, "边缘节点", fontsize=9.5, ref="703")
    for name, y in rs:
        arrow(ax, 16 + 10, y, 46 - 11, 60 if y > 55 else 48)
    arrow(ax, 46 + 11, 64, 72 - 7, 59)
    arrow(ax, 46 + 11, 46, 72 - 7, 57)
    arrow(ax, 72 + 7, 58, 92 - 7, 58)
    label(ax, 31, 73, "Mesh 多跳", fontsize=9.5)
    # 图例
    label(ax, 50, 30, "每条链路标注：跳数 / 带宽 / 丢包率 / 时延", fontsize=10)
    label(ax, 50, 23, "回传分级：P0 任务关键语义 > P1 位姿约束/回环 > P2 几何摘要 > P3 稠密几何", fontsize=10)
    label(ax, 50, 16, "弱网策略：仅传 P0/P1，链路恢复后按缺失列表补传 P2/P3", fontsize=10)
    caption(ax, "图7  自组网传输层拓扑与语义优先分级回传流程图", XM)
    save(fig, P("01-图7-自组网拓扑与语义优先分级回传图.png"))


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6(); fig7()
    print("ALL P01 DONE")
