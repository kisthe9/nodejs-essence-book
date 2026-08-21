"""图 8-2 背压：write 返回 false 与 drain 的自动刹车闭环。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-8-2.svg")
C = F.C

W, H = 820, 460

parts = [F.header(W, "背压：pipe 的自动刹车闭环", "BACKPRESSURE · WRITE / DRAIN")]

# 生产者
parts.append(F.box(46, 150, 180, 70, "", stroke=C["ink2"]))
parts.append(f'<text x="136" y="180" text-anchor="middle" font-size="13" font-weight="700" fill="{C["label"]}">readable · 生产者</text>')
parts.append(f'<text x="136" y="202" text-anchor="middle" font-size="11" fill="{C["muted"]}">快（磁盘读）</text>')

# 水箱：writable 内部缓冲
parts.append(F.box(330, 110, 180, 170, "", stroke=C["ink2"]))
parts.append(f'<rect x="331.5" y="170" width="177" height="108.5" fill="{C["band"]}"/>')
parts.append(f'<line x1="330" y1="170" x2="510" y2="170" stroke="{C["accent"]}" stroke-width="1.4" stroke-dasharray="5 4"/>')
parts.append(f'<text x="336" y="162" font-size="10.5" fill="{C["accent_deep"]}" font-weight="700">highWaterMark · 水位线</text>')
for x in (346, 392, 438):
    parts.append(f'<rect x="{x}" y="246" width="40" height="18" rx="3" fill="{C["card"]}" stroke="{C["ink2"]}" stroke-width="1"/>')
parts.append(f'<text x="420" y="300" text-anchor="middle" font-size="11" fill="{C["muted"]}">writable 内部缓冲</text>')

# 消费者
parts.append(F.box(610, 150, 164, 70, "", stroke=C["ink2"]))
parts.append(f'<text x="692" y="180" text-anchor="middle" font-size="13" font-weight="700" fill="{C["label"]}">writable · 消费者</text>')
parts.append(f'<text x="692" y="202" text-anchor="middle" font-size="11" fill="{C["muted"]}">慢（网络发）</text>')

# 正向数据流
parts.append(F.arrow(226, 185, 328, 185))
parts.append(f'<text x="252" y="176" font-size="11" fill="{C["body"]}">data</text>')
parts.append(f'<text x="232" y="206" font-size="11" fill="{C["body"]}">write(chunk)</text>')
parts.append(F.arrow(510, 240, 608, 240))
parts.append(f'<text x="520" y="232" font-size="11" fill="{C["body"]}">消费 · 慢</text>')

# 反向刹车（accent）
parts.append(F.path_arrow("M 420 110 V 88 H 136 V 146", accent=True))
parts.append(F.note(150, 80, "write(chunk) 返回 false → readable.pause() · 上游停读", accent=True, size=11.5))
parts.append(F.path_arrow("M 480 280 V 332 H 136 V 224", accent=True))
parts.append(F.note(150, 352, "缓冲排空后发 'drain' → readable.resume() · 恢复", accent=True, size=11.5))

parts.append(F.note(46, 398, "false 不是拒收：数据照单全收，缓冲可以涨过水位线（没有硬上限）", size=12))
parts.append(F.note(46, 422, "无视 false 是 Stream OOM 的头号原因；pipe / pipeline 替你接好这个闭环", size=12))

F.build(OUT, W, H, *parts)
