"""图 4-3 完整的一次心跳：从数据到达到回调执行（三泳道时序）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-4-3.svg")
C = F.C

KX, LX, JX = 160, 410, 660  # 三条生命线：内核 / libuv / JS


def ctext(x, y, text, size=11.5, fill=None, weight=None):
    fill = fill or C["muted"]
    wt = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="{fill}"{wt}>{text}</text>'


def float_card(cx, y, w, text, h=28, size=11, fill=None, stroke=None, tfill=None, bold=False):
    fill = fill or C["band"]
    stroke = stroke or C["line"]
    tfill = tfill or C["body"]
    wt = ' font-weight="700"' if bold else ""
    return (
        f'<rect x="{cx-w/2}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>\n'
        f'<text x="{cx}" y="{y+h/2+4}" text-anchor="middle" font-size="{size}" fill="{tfill}"{wt}>{text}</text>'
    )


parts = [F.header(820, "完整的一次心跳：从数据到达到回调执行", "ONE HEARTBEAT · SEQUENCE")]

# 泳道头 + 生命线
parts.append(F.box(KX - 80, 84, 160, 32, "内核", stroke=C["ink2"], bold=True, fs=12.5))
parts.append(F.box(LX - 80, 84, 160, 32, "libuv", stroke=C["ink2"], bold=True, fs=12.5))
parts.append(F.box(JX - 80, 84, 160, 32, "JS 运行时", stroke=C["ink2"], bold=True, fs=12.5))
for x in (KX, LX, JX):
    parts.append(F.lane_divider(x, 122, 508))

# 内核侧：数据到达
parts.append(float_card(KX, 134, 176, "socket 收到数据 · fd 变为可读"))

# epoll_wait（poll 阶段，阻塞中）
parts.append(ctext((KX + LX) / 2, 188, "epoll_wait · poll 阶段，阻塞中", 11.5, C["body"]))
parts.append(F.arrow(LX - 2, 196, KX + 4, 196))

# 返回就绪 fd 列表
parts.append(ctext((KX + LX) / 2, 230, "返回就绪 fd 列表", 11.5, C["body"]))
parts.append(F.arrow(KX + 4, 238, LX - 2, 238))

# libuv 自查：找句柄、读数据
parts.append(float_card(LX, 262, 280, "按 fd 找到对应的 TCPWrap · 调用 C++ 读回调", h=32))
parts.append(ctext((KX + LX) / 2, 322, "read() · 把数据读进缓冲区", 11.5, C["body"]))
parts.append(F.arrow(LX - 2, 330, KX + 4, 330))

# MakeCallback 放行到 JS（唯一高亮）
parts.append(ctext((LX + JX) / 2, 366, "MakeCallback · socket 的 JS 回调执行", 11.5, C["body"], 700))
parts.append(F.arrow(LX + 4, 374, JX - 4, 374, accent=True))
parts.append(ctext((LX + JX) / 2, 392, "('data' 事件 · 第 9 章)", 10.5, C["faint"]))

# 回调返回
parts.append(ctext((LX + JX) / 2, 414, "回调返回", 11.5, C["body"]))
parts.append(F.arrow(JX - 4, 422, LX + 4, 422))

# 排空微任务：心跳的缝隙
parts.append(float_card(LX, 446, 280, "排空 nextTick / 微任务队列", h=34, fill=C["card"],
                        stroke=C["accent"], tfill=C["accent_deep"], bold=True))
parts.append(F.note(568, 466, "await 在这个缝隙里恢复", accent=True, size=11))

parts.append(ctext(LX, 502, "然后继续下一阶段", 11.5, C["muted"]))

F.build(OUT, 820, 540, *parts)
