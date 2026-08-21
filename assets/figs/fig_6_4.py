"""图 6-4 IPC 的全部秘密：两个 fd 指向同一个 inode。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-6-4.svg")
C = F.C

W, H = 820, 430

parts = [F.header(W, "IPC：两个进程的 fd 指向同一个 inode", "PIPE · SHARED INODE")]

# 左右 fd 表
parts.append(F.zone(46, 90, 210, 126, "进程 A · fd 表"))
parts.append(F.box(64, 132, 174, 40, "", stroke=C["ink2"]))
parts.append(F.badge(72, 142, 4))
parts.append(f'<text x="102" y="157" font-size="12.5" fill="{C["label"]}">fd 4 · 写端</text>')

parts.append(F.zone(564, 90, 210, 126, "进程 B · fd 表"))
parts.append(F.box(582, 132, 174, 40, "", stroke=C["ink2"]))
parts.append(F.badge(590, 142, 7))
parts.append(f'<text x="620" y="157" font-size="12.5" fill="{C["label"]}">fd 7 · 读端</text>')

# 中间 pipe inode
parts.append(F.box(316, 118, 188, 70, "", stroke=C["accent"], fill=C["card"]))
parts.append(f'<text x="410" y="146" text-anchor="middle" font-size="13.5" font-weight="700" fill="{C["label"]}">pipe 的 inode</text>')
parts.append(f'<text x="410" y="170" text-anchor="middle" font-size="11.5" fill="{C["muted"]}">64KB 内核环形缓冲</text>')

parts.append(F.arrow(256, 152, 314, 152))
parts.append(F.arrow(562, 152, 506, 152))

# 数据流
parts.append(F.box(46, 280, 190, 44, "A 写入字节", fs=12.5, bold=True, stroke=C["ink2"]))
parts.append(F.arrow(240, 302, 304, 302))
parts.append(F.box(310, 280, 200, 44, "内核缓冲区", fs=12.5, fill=C["band"]))
parts.append(F.arrow(514, 302, 578, 302))
parts.append(F.box(584, 280, 190, 44, "B 读出字节", fs=12.5, bold=True, stroke=C["ink2"]))

parts.append(F.note(46, 368, "内核里没有“发消息”这回事 —— 只有共享的缓冲区", size=12.5, accent=True))
parts.append(F.note(46, 392, "达成“共享同一个 inode”只有两条途径：fork 继承 与 SCM_RIGHTS 传递", size=11.5))

F.build(OUT, W, H, *parts)
