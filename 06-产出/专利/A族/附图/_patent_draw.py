# -*- coding: utf-8 -*-
"""专利附图绘制公共模块：黑白线条、方框、带引线的附图标记、底部图号。

符合专利说明书附图规范：
- 纯黑白线条图，白底，无灰度填充、无彩色；
- 每个部件/步骤用阿拉伯数字附图标记（如 101、102）标注，并以引线+引出点指向部件；
- 中文使用宋体（Songti）；
- 图号（如"图1"）置于附图下方居中；
- 整张图带外边框；输出 300dpi PNG。
"""
import os
os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mplcache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

SONGTI_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
]


def _songti_path() -> str | None:
    for path in SONGTI_CANDIDATES:
        if os.path.isfile(path):
            return path
    return None


def font(size=13):
    from matplotlib.font_manager import FontProperties

    path = _songti_path()
    if path:
        return FontProperties(fname=path, size=size)
    return FontProperties(family="sans-serif", size=size)


def new_canvas(xmax=100.0, ymax=140.0, figw=8.5):
    figh = figw * ymax / xmax
    fig, ax = plt.subplots(figsize=(figw, figh))
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.axis("off")
    # 外边框
    ax.add_patch(Rectangle((1.2, 1.2), xmax - 2.4, ymax - 2.4, fill=False,
                           edgecolor="black", linewidth=1.5))
    return fig, ax


def box(ax, cx, cy, w, h, text, ref=None, fontsize=13, lw=1.4, ref_side="right"):
    """以 (cx, cy) 为中心画黑框白底文字框；ref 以引线+引出点标注附图标记。"""
    x0, y0 = cx - w / 2, cy - h / 2
    ax.add_patch(Rectangle((x0, y0), w, h, fill=True, facecolor="white",
                           edgecolor="black", linewidth=lw))
    ax.text(cx, cy, text, ha="center", va="center",
            fontproperties=font(fontsize), color="black", linespacing=1.6)
    if ref is not None:
        if ref_side == "right":
            xe = cx + w / 2
            xn = xe + 5.0
            ax.plot([xe, xn - 1.4], [cy, cy], color="black", lw=0.8)
            ax.plot([xe], [cy], marker="o", ms=2.4, color="black")
            ax.text(xn, cy, str(ref), ha="left", va="center", fontproperties=font(fontsize))
        else:
            xe = cx - w / 2
            xn = xe - 5.0
            ax.plot([xn + 1.4, xe], [cy, cy], color="black", lw=0.8)
            ax.plot([xe], [cy], marker="o", ms=2.4, color="black")
            ax.text(xn, cy, str(ref), ha="right", va="center", fontproperties=font(fontsize))


def arrow(ax, x1, y1, x2, y2, lw=1.4, two_way=False):
    style = "<|-|>" if two_way else "-|>"
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, lw=lw, color="black",
                                 shrinkA=0, shrinkB=0))


def frame(ax, x0, y0, w, h, lw=1.4, dashed=False):
    """画一个无填充的外框（用于容器/分组）。"""
    ls = (0, (5, 4)) if dashed else "solid"
    ax.add_patch(Rectangle((x0, y0), w, h, fill=False, edgecolor="black",
                           linewidth=lw, linestyle=ls))


def label(ax, x, y, s, fontsize=11, ha="center", va="center", rotation=0):
    ax.text(x, y, s, ha=ha, va=va, fontproperties=font(fontsize),
            color="black", rotation=rotation, linespacing=1.5)


def caption(ax, s, xmax=100.0):
    ax.text(xmax / 2, 4.5, s, ha="center", va="center",
            fontproperties=font(15), color="black")


def vflow(ax, items, cx=44, w=64, top=128, bot=12, fontsize=11.5,
          hfrac=0.62, ref_side="right"):
    """竖直流程：items=[(text, ref), ...]，自上而下排布并连下行箭头。返回 (ys, h)。"""
    n = len(items)
    slot = (top - bot) / n
    h = slot * hfrac
    ys = [top - slot * (i + 0.5) for i in range(n)]
    for (txt, ref), y in zip(items, ys):
        box(ax, cx, y, w, h, txt, ref=ref, fontsize=fontsize, ref_side=ref_side)
    for i in range(n - 1):
        arrow(ax, cx, ys[i] - h / 2, cx, ys[i + 1] + h / 2)
    return ys, h


def save(fig, path):
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved:", path)
