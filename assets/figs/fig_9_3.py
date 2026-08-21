"""图 9-3 谁在继承 EventEmitter。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-9-3.svg")
C = F.C

W, H = 820, 560

rows = [
    ("Stream 家族", "Readable · Writable · Duplex · Transform", "'data' 'end' 'drain' 'error'"),
    ("net.Server / net.Socket", "服务器与连接对象", "'connection' 'data' 'close'"),
    ("http.Server", "继承 net.Server", "'request' 'upgrade'"),
    ("ChildProcess", "child_process 的产物", "'exit' 'message'"),
    ("Worker", "worker_threads", "'message' 'exit'"),
    ("process 对象本身", "全局唯一", "'beforeExit' 'SIGINT' 'uncaughtException'"),
]

parts = [F.header(W, "谁在继承 EventEmitter", "EVERY I/O OBJECT EMITS")]

parts.append(F.box(46, 92, 200, 44, "EventEmitter", fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True, fs=13))
parts.append(F.line(146, 136, 146, 504))

for i, (title, sub, events) in enumerate(rows):
    y = 170 + i * 62
    cy = y + 24
    parts.append(F.line(146, cy, 190, cy))
    parts.append(F.box(190, y, 300, 48, "", stroke=C["ink2"]))
    parts.append(f'<text x="206" y="{y+21}" font-size="12.5" font-weight="700" fill="{C["label"]}">{title}</text>')
    parts.append(f'<text x="206" y="{y+38}" font-size="10.5" fill="{C["muted"]}">{sub}</text>')
    parts.append(f'<text x="510" y="{cy+4}" font-size="11.5" fill="{C["body"]}">{events}</text>')

parts.append(F.note(46, 550, "I/O 对象的一生 = 多种、多次、不定时的事情 —— EventEmitter 是最小完备接口", size=12))

F.build(OUT, W, 576, *parts)
