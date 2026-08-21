"""图 6-1 fd 的三层结构：fd 表 → struct file → inode。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-6-1.svg")
C = F.C

W, H = 820, 440


def card_title(x, y, title):
    return f'<text x="{x}" y="{y}" font-size="13.5" font-weight="700" fill="{C["label"]}">{title}</text>'


def card_line(x, y, text, accent=False, muted=False):
    col = C["accent_deep"] if accent else (C["muted"] if muted else C["body"])
    wt = ' font-weight="700"' if accent else ""
    return f'<text x="{x}" y="{y}" font-size="12"{wt} fill="{col}">{text}</text>'


parts = [F.header(W, "fd 背后的三层结构", "FD · STRUCT FILE · INODE")]

# 左区：进程内 fd 表（数组式）
parts.append(F.zone(46, 78, 214, 268, "进程内 · fd 表"))
for i, n in enumerate([0, 1, 2, 3]):
    y = 116 + i * 46
    parts.append(F.box(64, y, 178, 34, "", stroke=C["ink2"]))
    parts.append(F.badge(72, y + 7, n if n < 3 else "…", accent=False))
    parts.append(f'<text x="104" y="{y+22}" font-size="12" fill="{C["label"]}">fd {n if n < 3 else "3 …"}</text>')
parts.append(f'<text x="64" y="324" font-size="11" fill="{C["muted"]}">数组下标 · 进程私有</text>')

# 中区：struct file
parts.append(F.zone(302, 78, 216, 268, "内核态 · 每次 open 新建"))
parts.append(F.box(318, 116, 184, 150, "", stroke=C["ink2"]))
parts.append(card_title(332, 142, "struct file"))
parts.append(card_line(332, 168, "· f_op 操作函数表", accent=True))
parts.append(card_line(332, 192, "· f_pos 读写偏移"))
parts.append(card_line(332, 216, "· f_flags 打开标志"))
parts.append(card_line(332, 248, "一次打开的“会话记录”", muted=True))

# 右区：inode
parts.append(F.zone(560, 78, 214, 268, "资源本体 · 内核全局唯一"))
parts.append(F.box(576, 116, 182, 150, "", stroke=C["ink2"]))
parts.append(card_title(590, 142, "inode"))
parts.append(card_line(590, 168, "· 磁盘文件的 inode"))
parts.append(card_line(590, 192, "· socket 的 inode"))
parts.append(card_line(590, 216, "· pipe 的 inode"))
parts.append(card_line(590, 248, "socket/pipe 是内存中匿名对象", muted=True))

# 箭头：fd 行 → struct file → inode
for i in range(3):
    y = 133 + i * 46
    parts.append(F.arrow(242, y, 316, 176 + i * 14))
parts.append(F.arrow(502, 191, 574, 191))

# 底部注脚
parts.append(F.note(46, 380, "进程私有的“号码牌”", size=12))
parts.append(F.note(318, 380, "打开方式与进度的“会话记录”", size=12))
parts.append(F.note(576, 380, "资源的本体", size=12))
parts.append(F.box(46, 396, 728, 34, "write(fd)：内核顺着三层找到 f_op —— 同一个系统调用，多态分发", fill=C["band"], tfill=C["label"], bold=True, fs=12))

F.build(OUT, W, H, *parts)
