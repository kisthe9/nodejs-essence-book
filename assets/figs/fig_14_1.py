"""图 14-1 两种复制规格：Worker Threads（线程级）与 Cluster（进程级）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-14-1.svg")
C = F.C

parts = [F.header(820, "两种复制规格：不共享，只传消息", "WORKER THREADS VS CLUSTER")]


def container_col(x, tag):
    """一侧容器的三件套：Isolate / Environment / 事件循环。"""
    out = [F.note(x, 130, tag, size=12)]
    out.append(F.box(x, 142, 190, 36, f"Isolate {tag[-1]}", stroke=C["ink2"], fs=11.5))
    out.append(F.box(x, 186, 190, 36, f"Environment {tag[-1]}", stroke=C["ink2"], fs=11.5))
    out.append(F.box(x, 230, 190, 36, f"事件循环 {tag[-1]}", stroke=C["ink2"], fs=11.5))
    return '\n'.join(out)


# 规格一：Worker Threads（同一进程内两个线程）
parts.append(F.zone(46, 76, 728, 230, "规格一 · Worker Threads · 线程级复制"))
parts.append(container_col(120, "主线程 A"))
parts.append(container_col(510, "Worker 线程 B"))
# 消息通道（accent 双向）
parts.append(F.arrow(312, 196, 506, 196, accent=True))
parts.append(F.arrow(506, 212, 312, 212, accent=True))
parts.append(F.note(366, 184, "postMessage", accent=True, size=11))
parts.append(F.note(120, 292, "同一进程内：SharedArrayBuffer 是唯一真正共享的内存（需 Atomics）", size=11))

# 规格二：Cluster / child_process
parts.append(F.zone(46, 326, 728, 190, "规格二 · Cluster / child_process · 进程级复制"))
parts.append(F.box(120, 380, 240, 56, "进程 1 · 完整 Node 实例", stroke=C["ink2"], fs=12, bold=True))
parts.append(F.box(460, 380, 240, 56, "进程 2 · 完整 Node 实例", stroke=C["ink2"], fs=12, bold=True))
parts.append(F.arrow(362, 400, 456, 400, accent=True))
parts.append(F.arrow(456, 416, 362, 416, accent=True))
parts.append(F.note(396, 390, "IPC", accent=True, size=11))
parts.append(F.note(120, 468, "彻底隔离：一个崩了另一个毫发无损", size=11))
parts.append(F.note(460, 468, "cluster 另借 fd 传递共享同一端口（第 6 章）", size=11))

F.build(OUT, 820, 540, *parts)
