"""图 5-2 网络路全景：等待被集中批发给内核。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-5-2.svg")
C = F.C


def ctext(x, y, text, size=11.5, fill=None, weight=None):
    fill = fill or C["muted"]
    wt = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="{fill}"{wt}>{text}</text>'


def card2(x, y, w, h, l1, l2, l1fill=None, l2fill=None):
    l1fill = l1fill or C["label"]
    l2fill = l2fill or C["muted"]
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{C["card"]}" stroke="{C["line"]}" stroke-width="1.2"/>\n'
        f'<text x="{x+w/2}" y="{y+h/2-4}" text-anchor="middle" font-size="12.5" font-weight="700" fill="{l1fill}">{l1}</text>\n'
        f'<text x="{x+w/2}" y="{y+h/2+14}" text-anchor="middle" font-size="11" fill="{l2fill}">{l2}</text>'
    )


parts = [F.header(820, "网络路全景", "NETWORK ROAD · EPOLL")]

# 第一行：万级连接 → 非阻塞 → 登记进 epoll
parts.append(F.box(46, 96, 190, 40, "1 万个 socket", stroke=C["ink2"], bold=True))
parts.append(ctext(347, 108, "全部设为非阻塞", 11.5, C["muted"]))
parts.append(F.arrow(236, 116, 456, 116))
parts.append(F.box(460, 96, 314, 40, "全部登记进 epoll", stroke=C["ink2"], bold=True))

# 第二行：poll 阶段 epoll_wait
parts.append(F.path_arrow("M 617 136 V 154 H 410 V 172"))
parts.append(F.box(250, 176, 320, 40, "主线程在 poll 阶段调用 epoll_wait", bold=True, fs=12))

# 两个分支
parts.append(F.path_arrow("M 340 216 V 232 H 216 V 248"))
parts.append(F.path_arrow("M 480 216 V 232 H 595 V 248"))
parts.append(card2(66, 252, 300, 62, "无事发生：阻塞", "线程休眠 · CPU 让给别人"))
parts.append(card2(430, 252, 330, 62, "N 个 fd 就绪：醒来", "逐个 read/write · 都不会卡，因为已就绪"))

# 就绪分支汇向 MakeCallback
parts.append(F.varrow(595, 314, 340))
parts.append(F.box(430, 344, 330, 44, "MakeCallback 派发回 JS（第 4 章）",
                   fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True, fs=12.5))

# 收束一句
parts.append(ctext(410, 424, "主线程没有为任何一个连接单独等待过 —— 等待被集中批发给了内核",
                   12.5, C["accent_deep"], 700))

F.build(OUT, 820, 450, *parts)
