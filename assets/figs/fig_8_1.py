"""图 8-1 四种流，一个家族：继承树。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-8-1.svg")
C = F.C

W, H = 820, 520

parts = [F.header(W, "四种流，一个家族", "STREAM FAMILY TREE")]

# 根
parts.append(F.box(60, 88, 200, 40, "EventEmitter", fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True, fs=13))
parts.append(f'<text x="276" y="113" font-size="11.5" fill="{C["muted"]}">← 所有流都是事件发射器（第 9 章）</text>')
parts.append(F.line(160, 128, 160, 150))

# Stream
parts.append(F.box(100, 150, 160, 36, "Stream", bold=True, fs=13, stroke=C["ink2"]))
parts.append(F.line(180, 186, 180, 442))

rows = [
    (210, "Readable", "数据的源头 · fs.createReadStream, http 请求体", 220),
    (262, "Writable", "数据的去处 · fs.createWriteStream, http 响应", 220),
    (314, "Duplex", "既是源又是去处 · net.Socket（双向、两套独立缓冲）", 220),
    (424, "(PassThrough)", "什么都不做的 Transform · 常用于观测/计数", 220),
]
for y, name, desc, x in rows:
    cy = y + 18
    parts.append(F.line(180, cy, x, cy))
    parts.append(F.box(x, y, 170, 36, name, bold=True, fs=12.5, stroke=C["ink2"]))
    parts.append(f'<text x="402" y="{cy+4}" font-size="11.5" fill="{C["body"]}">{desc}</text>')

# Transform：Duplex 的子类
parts.append(F.line(305, 350, 305, 370))
parts.append(F.box(280, 370, 170, 36, "Transform", bold=True, fs=12.5, stroke=C["ink2"]))
parts.append(f'<text x="462" y="392" font-size="11.5" fill="{C["body"]}">中途加工站 · zlib.createGzip, crypto 流</text>')

parts.append(F.note(60, 492, "Duplex 内部是两套互不相干的缓冲区；Transform 用加工函数把两套缓冲打通", size=12))

F.build(OUT, W, H, *parts)
