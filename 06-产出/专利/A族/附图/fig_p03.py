# -*- coding: utf-8 -*-
"""专利03（World Model 增量更新与查询方法）全部附图（图1-图5）。"""
import os
from _patent_draw import new_canvas, box, arrow, caption, label, frame, vflow, save

OUT = os.path.dirname(os.path.abspath(__file__))
def P(name): return os.path.join(OUT, name)


def fig1():
    XM, YM = 100.0, 128.0
    fig, ax = new_canvas(XM, YM, figw=8.6)
    layers = [
        ("地图层：全局地图 / 已知区域 / 不确定区 / 质量栅格", "101"),
        ("拓扑层：节点 / 边 / 区域关系（房间 / 走廊 / 楼梯 / 门）", "102"),
        ("语义层：对象 / 区域 / 异常", "103"),
        ("机器人层：机器人状态 / 能力 / 健康", "104"),
        ("任务层：任务目标 / 进度 / 失败 / 待执行", "105"),
        ("通信层：网络状态 / 连接 / 延迟", "106"),
        ("历史层：观测 / 事件（回放 / 审计 / 训练）", "107"),
    ]
    top, bot = YM - 22, 16
    n = len(layers)
    slot = (top - bot) / n
    h = slot * 0.72
    ys = [top - slot * (i + 0.5) for i in range(n)]
    for (txt, ref), y in zip(layers, ys):
        box(ax, 46, y, 72, h, txt, ref=ref, fontsize=10.5)
    y_hi, y_lo = ys[0] + h / 2, ys[-1] - h / 2
    frame(ax, 8, y_lo - 4, 80, (y_hi - y_lo) + 8)
    label(ax, 46, y_hi + 7, "世界状态（World State）", fontsize=13)
    caption(ax, "图1  空间世界模型总体层级结构图", XM)
    save(fig, P("03-图1-世界模型总体层级结构图.png"))


def fig2():
    XM, YM = 100.0, 132.0
    fig, ax = new_canvas(XM, YM, figw=8.6)
    items = [
        ("接收世界模型增量", "201"),
        ("格式校验  →  时间校验（过期 / 乱序 / 版本）", "202"),
        ("坐标转换（依地图契约转全局坐标系）", "203"),
        ("对象关联（空间距离 / 类别 / 时间 / 外观）", "204"),
        ("冲突处理（多机不同观测）", "205"),
        ("状态更新：新增 / 更新 / 删除 / 过期 / 确认  作用于目标层", "206"),
        ("历史记录（来源写入历史索引）", "207"),
        ("通知订阅者（调度 / 导航 / 数据闭环 / 告警）", "208"),
    ]
    vflow(ax, items, cx=44, w=70, top=YM - 8, bot=12, fontsize=10.8)
    caption(ax, "图2  世界模型增量更新流程图", XM)
    save(fig, P("03-图2-世界模型增量更新流程图.png"))


def fig3():
    XM, YM = 104.0, 100.0
    fig, ax = new_canvas(XM, YM, figw=9.6)
    inputs = [
        ("传感器置信 C_sensor", "301"),
        ("定位 C_localization", "302"),
        ("时间新鲜度 C_time", "303"),
        ("地图质量 C_map_quality", "304"),
        ("健康 C_agent_health", "305"),
    ]
    top, bot = YM - 14, 40
    ys = [top - (top - bot) * (i + 0.5) / len(inputs) for i in range(len(inputs))]
    for (txt, ref), y in zip(inputs, ys):
        box(ax, 20, y, 30, 9, txt, fontsize=9.2, ref=ref, ref_side="left")
    cx, cy = 56, (top + bot) / 2
    box(ax, cx, cy, 20, 12, "C_obs =\nΣ pi·Ci", fontsize=11)
    label(ax, cx, cy + 6 + 2.5, "306", fontsize=11)
    for y in ys:
        arrow(ax, 20 + 15, y, cx - 10, cy + (y - cy) * 0.1)
    box(ax, 82, cy, 38, 40,
        "新观测明显优于旧  →  更新对象状态\n新≈旧  →  合并 / 提升置信度\n矛盾且均高  →  标记冲突 / 请求补充\n超有效期  →  过期 / 移入历史层\n多次异常  →  提升区域风险等级",
        fontsize=9, ref="307")
    arrow(ax, cx + 10, cy, 82 - 19, cy)
    caption(ax, "图3  多源观测冲突处理流程图", XM)
    save(fig, P("03-图3-多源观测冲突处理流程图.png"))


def fig4():
    XM, YM = 104.0, 92.0
    fig, ax = new_canvas(XM, YM, figw=9.6)
    apps = [
        ("导航规划", "401"),
        ("多机调度", "402"),
        ("巡检业务", "403"),
        ("数据闭环", "404"),
        ("模型训练", "405"),
    ]
    top, bot = YM - 16, 16
    ys = [top - (top - bot) * (i + 0.5) / len(apps) for i in range(len(apps))]
    for (txt, ref), y in zip(apps, ys):
        box(ax, 18, y, 22, 9, txt, fontsize=10, ref=ref, ref_side="left")
    cy = (top + bot) / 2
    box(ax, 70, cy, 50, 46,
        "World Model 查询接口\n对象查询 / 区域查询 / 机器人查询\n任务查询 / 历史查询 / 训练数据查询\n──────────────\n输入：类别 / 区域 / 置信度 / 时间窗口阈值\n返回：位姿 / 置信度 / 最后观测 / 来源机器人",
        fontsize=9.2, ref="406")
    for y in ys:
        arrow(ax, 18 + 11, y, 70 - 25, cy + (y - cy) * 0.5)
    caption(ax, "图4  查询接口与上层应用关系图", XM)
    save(fig, P("03-图4-查询接口与上层应用关系图.png"))


def fig5():
    XM, YM = 110.0, 92.0
    fig, ax = new_canvas(XM, YM, figw=10.0)
    box(ax, 24, YM - 16, 28, 11, "SLAM 运行时", fontsize=11, ref="501", ref_side="left")
    box(ax, 70, YM - 16, 30, 11, "世界模型", fontsize=11, ref="502")
    arrow(ax, 24 + 14, YM - 16, 70 - 15, YM - 16)
    label(ax, 47, YM - 11, "子图 / 位姿 / 语义增量", fontsize=8.8)
    subs = [
        ("任务调度系统", "503"),
        ("导航规划", "504"),
        ("巡检业务", "505"),
        ("数据闭环系统", "506"),
        ("模型训练系统", "507"),
    ]
    n = len(subs)
    xs = [12 + (XM - 24) * (i + 0.5) / n for i in range(n)]
    sy = 30
    for (txt, ref), x in zip(subs, xs):
        box(ax, x, sy, 18, 11, txt, fontsize=9.2)
        label(ax, x, sy - 5.5 - 3, ref, fontsize=10)
        arrow(ax, 70, YM - 16 - 5.5, x, sy + 5.5)
    label(ax, 70, (YM - 16 + sy) / 2 + 8, "发布更新事件（订阅 / 发布）", fontsize=9)
    # 反向请求
    arrow(ax, xs[0], sy + 5.5, 60, YM - 16 - 5.5)
    label(ax, 33, sy + 16, "补采 / 复检请求（反向下发）", fontsize=8.8)
    caption(ax, "图5  世界模型与各系统交互图", XM)
    save(fig, P("03-图5-世界模型与各系统交互图.png"))


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
    print("ALL P03 DONE")
