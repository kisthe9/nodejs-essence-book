"""图 6-5 cluster 共享端口：把 listen-fd 寄给每个 worker。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-6-5.svg")
C = F.C

W, H = 820, 470

parts = [F.header(W, "cluster 共享端口：把 listen-fd 寄给每个 worker", "SCM_RIGHTS · SHARED LISTEN FD")]

# 主进程
parts.append(F.box(240, 92, 340, 48, "", fill=C["ink"], stroke=C["ink"]))
parts.append(f'<text x="410" y="112" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">主进程：创建监听 socket</text>')
parts.append(f'<text x="410" y="130" text-anchor="middle" font-size="11" fill="#c3c9d6">得到 listen-fd</text>')

# 寄出箭头
parts.append(F.path_arrow("M 330 140 V 174 H 200 V 196"))
parts.append(F.path_arrow("M 490 140 V 174 H 620 V 196"))
parts.append(F.note(96, 152, "IPC 通道 · SCM_RIGHTS", size=11))
parts.append(F.note(96, 168, "把 listen-fd 寄给 worker 1", size=11))
parts.append(F.note(548, 168, "同样寄给 worker 2 …", size=11))

# workers
parts.append(F.box(90, 200, 220, 44, "worker 1 · fd 表得一个 fd", fs=12, bold=True, stroke=C["ink2"]))
parts.append(F.box(510, 200, 220, 44, "worker 2 · fd 表得一个 fd", fs=12, bold=True, stroke=C["ink2"]))

# 汇聚到同一 inode
parts.append(F.path_arrow("M 200 244 V 272 H 360 V 296"))
parts.append(F.path_arrow("M 620 244 V 272 H 460 V 296"))

parts.append(F.box(290, 300, 240, 52, "", stroke=C["accent"]))
parts.append(f'<text x="410" y="322" text-anchor="middle" font-size="13" font-weight="700" fill="{C["label"]}">同一个监听 socket 的 inode</text>')
parts.append(f'<text x="410" y="342" text-anchor="middle" font-size="11" fill="{C["muted"]}">号码各异 · 背后是同一份资源</text>')

parts.append(F.note(46, 396, "每个 worker 都在自己的 epoll 里监听它", size=12.5))
parts.append(F.note(46, 418, "内核把新连接分给其中一个 —— 没有端口复用魔法，没有转发代理", size=12.5))
parts.append(F.note(46, 444, "child.send(msg, socket) 的第二个参数，走的就是这条途径", size=11.5, accent=True))

F.build(OUT, W, H, *parts)
