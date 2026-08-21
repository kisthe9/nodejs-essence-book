"""图 3-2 内置模块注册：编译期声明 → 运行期按名取用（双栏对照）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-3-2.svg")
C = F.C


def text(x, y, s, fs=12, fill=None, bold=False, anchor=None):
    fill = fill or C["body"]
    wt = ' font-weight="700"' if bold else ''
    an = f' text-anchor="{anchor}"' if anchor else ''
    return f'<text x="{x}" y="{y}" font-size="{fs}" fill="{fill}"{wt}{an}>{s}</text>'


parts = [F.header(820, "内置模块：编译期注册 · 运行期取用", "BUILTIN REGISTRY")]

# 左栏 · 编译期
parts.append(F.zone(60, 110, 292, 240, "编译期 · COMPILE TIME"))
parts.append(F.box(84, 160, 244, 40, "src/*.cc 里的注册宏声明", bold=True, fs=12.5))
parts.append(text(206, 240, "约 70 个模块", fs=12, fill=C["muted"], anchor="middle"))
parts.append(text(206, 264, "fs / tcp_wrap / buffer / crypto …", fs=11, fill=C["faint"], anchor="middle"))

# 中间 · 构建时展开
parts.append(F.arrow(356, 230, 458, 230))
parts.append(text(407, 216, "构建时", fs=11.5, fill=C["muted"], anchor="middle"))
parts.append(text(407, 256, "统一展开", fs=11.5, fill=C["muted"], anchor="middle"))

# 右栏 · 运行期
parts.append(F.zone(462, 110, 300, 240, "运行期 · RUNTIME"))
parts.append(F.box(486, 160, 252, 40, "internalBinding('fs')", bold=True, fs=12.5))
parts.append(F.arrow(506, 232, 526, 232))
parts.append(text(534, 236, "查内置注册表", fs=12, fill=C["label"]))
parts.append(F.arrow(506, 272, 526, 272))
parts.append(text(534, 276, "初始化并返回导出对象", fs=12, fill=C["label"]))

F.build(OUT, 820, 420, *parts)
