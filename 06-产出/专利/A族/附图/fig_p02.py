# -*- coding: utf-8 -*-
"""专利02（基于地图质量的子图自适应上传融合）全部附图（图1-图5）。"""
import os
from _patent_draw import new_canvas, box, arrow, caption, label, vflow, save

OUT = os.path.dirname(os.path.abspath(__file__))
def P(name): return os.path.join(OUT, name)


def fig1():
    XM, YM = 100.0, 132.0
    fig, ax = new_canvas(XM, YM, figw=8.6)
    items = [
        ("机器人端传感器采集", "101"),
        ("本地里程计与局部建图  →  候选局部子图生成（事件驱动）", "102"),
        ("计算地图质量评分 Q_map", "103"),
        ("获取系统状态：网络 Q_net / 边缘负载 Q_edge / 任务优先级 Q_task", "104"),
        ("综合评分 S_upload  →  上传策略选择", "105"),
        ("完整 / 轻量 / 摘要 / 延迟 / 请求边缘确认", "106"),
        ("边缘端完整性校验与质量复评", "107"),
        ("跨机器人匹配  →  约束生成  →  位姿图优化  →  全局地图更新", "108"),
    ]
    vflow(ax, items, cx=44, w=72, top=YM - 8, bot=12, fontsize=11)
    caption(ax, "图1  子图自适应上传方法总体流程图", XM)
    save(fig, P("02-图1-子图自适应上传方法总体流程图.png"))


def fig2():
    XM, YM = 100.0, 96.0
    fig, ax = new_canvas(XM, YM, figw=9.2)
    inputs = [
        ("重叠度 Q_overlap", "201"),
        ("几何 Q_geometry", "202"),
        ("协方差 Q_uncertainty", "203"),
        ("特征 Q_feature", "204"),
        ("语义 Q_semantic", "205"),
        ("运动稳定 Q_motion", "206"),
    ]
    top, bot = YM - 12, 16
    ys = [top - (top - bot) * (i + 0.5) / len(inputs) for i in range(len(inputs))]
    for (txt, ref), y in zip(inputs, ys):
        box(ax, 18, y, 26, 9, txt, fontsize=9.5, ref=ref, ref_side="left")
    cx, cy = 54, (top + bot) / 2
    box(ax, cx, cy, 26, 16, "地图质量评分\nQ_map = Σ wi·Qi", fontsize=11)
    label(ax, cx, cy + 8 + 2.5, "207", fontsize=11)
    for y in ys:
        arrow(ax, 18 + 13, y, cx - 13, cy + (y - cy) * 0.12)
    box(ax, 86, cy, 22, 30,
        "平台相关指标（可选）\n四足：足端接触/地形粗糙度\n无人机：姿态稳定/视觉模糊\n自动导引车：轮速一致/载荷",
        fontsize=8.8, ref="208")
    arrow(ax, 86 - 11, cy, cx + 13, cy)
    caption(ax, "图2  地图质量评分计算模块图", XM)
    save(fig, P("02-图2-地图质量评分计算模块图.png"))


def fig3():
    XM, YM = 106.0, 92.0
    fig, ax = new_canvas(XM, YM, figw=9.8)
    box(ax, 53, YM - 14, 22, 10, "评估", fontsize=11, ref="302")
    strat = [
        (18, "完整上传", "301", "S_upload高且网络好"),
        (42, "轻量上传", "303", "网络一般"),
        (66, "摘要上传", "304", "网络较差"),
        (90, "请求边缘确认", "305", "质量高但网络差"),
    ]
    sy = 54
    for x, txt, ref, cond in strat:
        box(ax, x, sy, 20, 10, txt, fontsize=10)
        arrow(ax, 53, YM - 14 - 5, x, sy + 5)
        label(ax, x, sy + 8.5, cond, fontsize=8.2)
        label(ax, x, sy - 5 - 3, ref, fontsize=11)
    box(ax, 40, 24, 28, 10, "延迟上传（本地缓存）", fontsize=10)
    label(ax, 40, 24 - 5 - 3, "306", fontsize=11)
    box(ax, 86, 24, 18, 10, "补传", fontsize=10, ref="307")
    for x, txt, ref, cond in strat[:3]:
        arrow(ax, x, sy - 5, 40 + (x - 40) * 0.2, 24 + 5)
    label(ax, 26, 39, "网络极差", fontsize=8.5)
    arrow(ax, 40 + 14, 24, 86 - 9, 24)
    label(ax, 65, 27, "网络恢复", fontsize=8.5)
    caption(ax, "图3  多级上传策略状态转换图", XM)
    save(fig, P("02-图3-多级上传策略状态转换图.png"))


def fig4():
    XM, YM = 100.0, 122.0
    fig, ax = new_canvas(XM, YM, figw=8.4)
    items = [
        ("接收子图", "401"),
        ("校验：子图ID / 机器人ID / 时间戳 / 坐标系 / 版本 / 完整性", "402"),
        ("机器人端质量评分复评", "403"),
        ("按全局地图需求 + 区域覆盖 + 任务优先级 排序融合队列", "404"),
        ("跨机器人重叠检索  →  约束生成：迭代最近点 / 正态分布变换 / 扫描上下文 / 语义匹配", "405"),
        ("按约束置信度 + 子图质量 判定是否入全局位姿图（低置信→鲁棒核/延迟验证）", "406"),
        ("更新全局地图 / 地图质量图层 / 子图索引", "407"),
    ]
    vflow(ax, items, cx=44, w=74, top=YM - 8, bot=12, fontsize=10.5)
    caption(ax, "图4  边缘端融合队列处理流程图", XM)
    save(fig, P("02-图4-边缘端融合队列处理流程图.png"))


def fig5():
    XM, YM = 108.0, 106.0
    fig, ax = new_canvas(XM, YM, figw=9.4)
    box(ax, 32, YM - 18, 40, 11, "监测网络状态\n带宽 / 往返时延 / 抖动 / 丢包 / 队列", fontsize=10, ref="501", ref_side="left")
    box(ax, 32, YM - 40, 24, 9, "网络分级判定", fontsize=10, ref="502", ref_side="left")
    arrow(ax, 32, YM - 18 - 5.5, 32, YM - 40 + 4.5)
    branches = [
        ("良好", "完整子图上传", "503"),
        ("一般", "降采样点云 + 关键帧", "504"),
        ("较差", "描述子 + 位姿 + 质量评分（摘要）", "505"),
        ("极差", "本地缓存 + 周期性心跳", "506"),
    ]
    by = [YM - 30, YM - 46, YM - 62, YM - 78]
    for (lv, txt, ref), y in zip(branches, by):
        box(ax, 80, y, 42, 9, txt, fontsize=9.2, ref=ref)
        arrow(ax, 32 + 12, YM - 40, 80 - 21, y)
        label(ax, 54, (YM - 40 + y) / 2 + 1.5, lv, fontsize=9)
    box(ax, 80, 13, 42, 9, "按边缘端缺失子图列表补传", fontsize=9.5, ref="507")
    arrow(ax, 80, by[3] - 4.5, 80, 13 + 4.5)
    label(ax, 86, (by[3] + 13) / 2, "网络恢复", fontsize=8.5, rotation=90)
    caption(ax, "图5  弱网环境下摘要上传与补传流程图", XM)
    save(fig, P("02-图5-弱网环境摘要上传与补传流程图.png"))


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
    print("ALL P02 DONE")
