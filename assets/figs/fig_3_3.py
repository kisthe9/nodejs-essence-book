"""图 3-3 BaseObject 双向绑定：JS 对象 ↔ C++ 对象（双栏泳道）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-3-3.svg")
C = F.C


def text(x, y, s, fs=12, fill=None, bold=False, anchor=None):
    fill = fill or C["body"]
    wt = ' font-weight="700"' if bold else ''
    an = f' text-anchor="{anchor}"' if anchor else ''
    return f'<text x="{x}" y="{y}" font-size="{fs}" fill="{fill}"{wt}{an}>{s}</text>'


parts = [F.header(820, "BaseObject · JS 与 C++ 对象的双向绑定", "BASEOBJECT BINDING")]

# 泳道：JS 世界 / C++ 世界
parts.append(F.zone(60, 96, 300, 250, "JS 世界"))
parts.append(F.zone(470, 96, 290, 250, "C++ 世界"))
parts.append(F.lane_divider(410, 96, 346))

# 左：Socket 对象（两个内部字段）
parts.append(F.box(84, 140, 252, 38, "Socket 对象", bold=True, fs=13, stroke=C["ink2"]))
parts.append(F.box(84, 196, 252, 34, "内部字段[0] · 类型标记", fs=11.5))
parts.append(F.box(84, 244, 252, 34, "内部字段[1] · C++ 指针", fs=11.5))

# 右：TCPWrap 实例（一张大卡）
parts.append(f'<rect x="494" y="140" width="242" height="150" rx="4" fill="{C["card"]}" stroke="{C["ink2"]}" stroke-width="1.2"/>')
parts.append(text(615, 172, "TCPWrap 实例", fs=13, fill=C["label"], bold=True, anchor="middle"))
parts.append(text(615, 204, "（持有真实的", fs=11.5, fill=C["muted"], anchor="middle"))
parts.append(text(615, 226, "libuv TCP 句柄）", fs=11.5, fill=C["muted"], anchor="middle"))

# 下行：内部字段 → C++ 对象
parts.append(F.arrow(340, 213, 488, 213))
parts.append(F.arrow(340, 261, 488, 261, accent=True))

# 上行：persistent 句柄（反向引用）
parts.append(F.path_arrow("M 615 294 V 386 H 210 V 352"))
parts.append(text(414, 378, "persistent 句柄（反向引用）", fs=11.5, fill=C["muted"], anchor="middle"))

F.build(OUT, 820, 440, *parts)
