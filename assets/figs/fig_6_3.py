"""图 6-3 fd 1 背后是什么：取决于进程怎么被启动。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-6-3.svg")
C = F.C

W, H = 820, 420

rows = [
    ("node app.js", "TTY（终端设备）"),
    ("node app.js &gt; out.log", "磁盘文件的 inode"),
    ("node app.js | grep err", "一个 pipe 的 inode"),
    ("由子进程方式被 spawn", "父进程创建的 pipe"),
]

parts = [F.header(W, "fd 1 背后是什么？取决于进程怎么被启动", "FD 1 · FOUR DESTINATIONS")]
parts.append(f'<text x="46" y="92" font-size="11" fill="{C["faint"]}" letter-spacing="2.5">启动方式</text>')
parts.append(f'<text x="470" y="92" font-size="11" fill="{C["faint"]}" letter-spacing="2.5">fd 1 指向的 inode</text>')

for i, (left, right) in enumerate(rows):
    y = 106 + i * 62
    parts.append(F.box(46, y, 330, 44, left, fs=12.5, bold=True, stroke=C["ink2"]))
    parts.append(F.arrow(380, y + 22, 464, y + 22))
    parts.append(F.box(470, y, 304, 44, right, fs=12.5, fill=C["band"]))

parts.append(F.note(46, 378, "同一行 console.log，写终端、写文件、写管道 —— 代码零改动", size=12.5))
parts.append(F.note(46, 400, "这就是 6.1 多态分发的日常应用", size=11.5))

F.build(OUT, W, H, *parts)
