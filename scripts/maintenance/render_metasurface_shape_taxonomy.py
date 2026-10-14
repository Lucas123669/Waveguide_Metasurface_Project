"""Draw original, qualitative shape-taxonomy figures; never generate fab layouts."""

from __future__ import annotations

import argparse
from io import StringIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle, Wedge
import numpy as np


BLUE = "#1763a6"
DARK = "#16436a"
MUTED = "#536b80"
PALE = "#f1f6fc"
TEAL = "#168985"


def font_setup(font_path: str | None) -> None:
    candidates = [Path(font_path)] if font_path else [Path("C:/Windows/Fonts/msyh.ttc")]
    for candidate in candidates:
        if candidate.is_file():
            font_manager.fontManager.addfont(str(candidate))
            plt.rcParams["font.family"] = font_manager.FontProperties(fname=candidate).get_name()
            break
    else:
        plt.rcParams["font.family"] = ["Noto Sans CJK SC", "SimHei", "sans-serif"]
    plt.rcParams.update({"axes.unicode_minus": False, "svg.fonttype": "path", "svg.hashsalt": "metasurface-shape-taxonomy-v1"})


def panel(ax, title: str, detail: str, source: str) -> None:
    ax.set(xlim=(0, 10), ylim=(0, 8), aspect="equal")
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.12, 0.1), 9.76, 7.7,
                              boxstyle="round,pad=0.02,rounding_size=0.25",
                              facecolor=PALE, edgecolor="#ceddec", linewidth=1))
    ax.text(0.6, 7.05, title, fontsize=16, weight="bold", color=DARK)
    ax.text(0.6, 2.0, detail, fontsize=11, color=DARK, linespacing=1.45, va="top")
    ax.text(0.6, 0.43, source, fontsize=10, color=MUTED)


def poly(ax, points, color=BLUE):
    ax.add_patch(Polygon(points, closed=True, facecolor=color, edgecolor=DARK, linewidth=1.2))


def six_triangles(ax, center, radius, side):
    for k in range(6):
        theta = k * np.pi / 3
        c = np.array(center) + radius * np.array([np.cos(theta), np.sin(theta)])
        angles = theta + np.pi + np.arange(3) * 2 * np.pi / 3
        vertices = c + side / np.sqrt(3) * np.column_stack([np.cos(angles), np.sin(angles)])
        poly(ax, vertices, TEAL)


def overview(out: Path) -> None:
    fig, axes = plt.subplots(2, 4, figsize=(16, 9.4))
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.075, top=0.86, wspace=0.04, hspace=0.08)
    fig.text(0.04, 0.94, "超表面版图：七类平面轮廓", fontsize=25, weight="bold", color=DARK)
    fig.text(0.04, 0.898, "按俯视轮廓分类；柱 / 孔、组合数量、材料层和刻蚀深度另行记录", fontsize=14, color=MUTED)
    specs = [
        ("01  圆形", "参数：直径\n圆柱 / 圆盘 / 圆孔", "库内例子：Si-1550:C2，Q1-03"),
        ("02  矩形", "参数：长、宽、旋转角\n包含方形、纳米棒、纳米鳍", "库内例子：L02，F-11 / F-21"),
        ("03  椭圆形", "参数：长轴、短轴、旋转角\n椭圆柱 / 椭圆孔", "库内例子：L01，Q1-11"),
        ("04  三角形", "参数：边长或顶点、旋转角\n等边 / 等腰 / 一般三角形", "库内例子：blueprints 六三角孔"),
        ("05  梯形", "参数：上下底、平面高度、偏移\n梯形柱 / 梯形孔", "库内例子：F-03，F-25"),
        ("06  环形", "参数：内外轮廓、环宽、开口\n闭环 / 同心环 / 开口环", "库内例子：Q1-11，F-14 / F-26"),
        ("07  特殊结构", "参数：子类型 + 多边形 / 高度图\nH、V、十字、自由曲线等", "库内例子：F-14，F-13"),
        ("组合方式：独立字段", "同一轮廓可构成多结构元胞\n数量、位置、取向分别配置", "示例：四椭圆孔 / 六三角孔"),
    ]
    for ax, spec in zip(axes.flat, specs):
        panel(ax, *spec)
    ax = axes.flat[0]
    ax.add_patch(Circle((5, 4.4), 1.5, facecolor=BLUE, edgecolor=DARK))
    ax = axes.flat[1]
    ax.add_patch(Rectangle((1.9, 3.45), 2.0, 2.0, facecolor=BLUE, edgecolor=DARK))
    ax.add_patch(Rectangle((5.2, 3.8), 3.0, 1.25, facecolor=BLUE, edgecolor=DARK))
    ax = axes.flat[2]
    ax.add_patch(Ellipse((5, 4.4), 4.5, 2.3, angle=28, facecolor=BLUE, edgecolor=DARK))
    poly(axes.flat[3], [(3, 3.1), (7, 3.1), (5, 6.3)])
    poly(axes.flat[4], [(2.5, 3.1), (7.5, 3.1), (6.4, 5.7), (3.6, 5.7)])
    ax = axes.flat[5]
    ax.add_patch(Wedge((2.9, 4.4), 1.4, 0, 360, width=0.5, facecolor=BLUE, edgecolor=DARK))
    ax.add_patch(Wedge((7.0, 4.4), 1.4, 35, 325, width=0.5, facecolor=BLUE, edgecolor=DARK))
    ax = axes.flat[6]
    poly(ax, [(1, 3.15), (1.5, 3.15), (1.5, 4.2), (2.45, 4.2), (2.45, 3.15),
              (2.95, 3.15), (2.95, 5.85), (2.45, 5.85), (2.45, 4.7), (1.5, 4.7),
              (1.5, 5.85), (1, 5.85)])
    poly(ax, [(3.8, 5.75), (4.25, 5.9), (5.0, 3.95), (5.75, 5.9), (6.2, 5.75),
              (5.15, 3.15), (4.85, 3.15)])
    poly(ax, [(7.4, 3.1), (7.95, 3.1), (7.95, 4.2), (9, 4.2), (9, 4.75),
              (7.95, 4.75), (7.95, 5.85), (7.4, 5.85), (7.4, 4.75),
              (6.5, 4.75), (6.5, 4.2), (7.4, 4.2)])
    ax = axes.flat[7]
    for x, y, angle in [(2.3, 3.9, 25), (3.6, 3.9, -25), (2.3, 5.0, -25), (3.6, 5.0, 25)]:
        ax.add_patch(Ellipse((x, y), 1.0, 0.5, angle=angle, facecolor=TEAL, edgecolor=DARK))
    six_triangles(ax, (7.1, 4.45), 1.05, 0.85)
    fig.text(0.04, 0.029, "原创定性示意 · 非论文原图 · 不按比例 · 蓝色表示被分类的轮廓，不指定曝光极性", fontsize=11, color=MUTED)
    save(fig, out, "metasurface_shape_taxonomy")


def compositions(out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 6.0))
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.12, top=0.79, wspace=0.04)
    fig.text(0.04, 0.93, "基本轮廓与超胞组合：分别记录", fontsize=25, weight="bold", color=DARK)
    fig.text(0.04, 0.855, "一个设计单元可包含多个轮廓；胞边界与各结构的位置关系也属于设计参数", fontsize=14, color=MUTED)
    specs = [
        ("L01：四椭圆孔", "形状：ellipse    类型：hole\n组合：两对椭圆孔，共四个", "依据：L01 项目笔记；位置仅示意"),
        ("L02 偏转：三纳米棒", "形状：rectangle    类型：pillar\n组合：三个不同响应的元原子", "依据：L02 项目笔记；尺寸仅示意"),
        ("blueprints：六三角孔", "形状：triangle    类型：hole\n组合：六个三角孔形成一个元胞", "依据：现有生成器；几何仅示意"),
    ]
    for ax, spec in zip(axes, specs):
        panel(ax, *spec)
    ax = axes[0]
    ax.add_patch(Rectangle((2.35, 2.55), 5.3, 3.55, facecolor="#d6e6f3", edgecolor=BLUE, linestyle="--"))
    for x, y, angle in [(3.6, 3.6, 22), (5.45, 3.6, -22), (4.15, 5.1, -22), (6, 5.1, 22)]:
        ax.add_patch(Ellipse((x, y), 1.35, 0.68, angle=angle, facecolor="white", edgecolor=BLUE, linewidth=1.6))
    ax = axes[1]
    ax.add_patch(Rectangle((1.5, 2.65), 7, 3.2, facecolor="none", edgecolor=BLUE, linestyle="--"))
    for x, height, label in [(3, 1.5, "−2π/3"), (5, 2.2, "0"), (7, 1.9, "+2π/3")]:
        ax.add_patch(Rectangle((x - .45, 4.35 - height / 2), .9, height, facecolor=BLUE, edgecolor=DARK))
        ax.text(x, 6.0, label, fontsize=13, ha="center", color=DARK)
    ax = axes[2]
    angles = np.pi / 6 + np.arange(6) * np.pi / 3
    outline = np.array([5, 4.4]) + 2.0 * np.column_stack([np.cos(angles), np.sin(angles)])
    ax.add_patch(Polygon(outline, closed=True, facecolor="none", edgecolor=BLUE, linestyle="--"))
    six_triangles(ax, (5, 4.4), 1.1, .95)
    fig.text(0.04, 0.047, "原创定性示意 · 不按比例 · 虚线为示意胞边界；不得从图中提取论文尺寸、精确位置或加工参数", fontsize=11, color=MUTED)
    save(fig, out, "metasurface_supercell_composition")


def save(fig, output: Path, name: str) -> None:
    fig.savefig(output / f"{name}.png", dpi=220, facecolor="white")
    buffer = StringIO()
    fig.savefig(buffer, format="svg", facecolor="white", metadata={"Date": None})
    svg = "\n".join(line.rstrip() for line in buffer.getvalue().splitlines()) + "\n"
    (output / f"{name}.svg").write_text(svg, encoding="utf-8")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "docs/reports/design/figures")
    parser.add_argument("--font", help="Optional path to a Chinese font")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    font_setup(args.font)
    overview(args.output_dir)
    compositions(args.output_dir)
    print(f"Wrote two PNG figures and their SVG versions to {args.output_dir}")


if __name__ == "__main__":
    main()
