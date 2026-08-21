"""图 7-2 两档分配：8KB slab 切分 vs ≥4KB 独立分配。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-7-2.svg")
C = F.C

W, H = 820, 600

parts = [F.header(W, "两档分配：小额找零与大额转账", "POOL SLICE VS STANDALONE")]

# 顶部请求
parts.append(F.pill(410, 84, 320, "分配请求 · Buffer.allocUnsafe(size)"))

# 分支
parts.append(F.line(410, 116, 410, 136))
parts.append(F.line(230, 136, 590, 136))
parts.append(F.varrow(230, 136, 158))
parts.append(F.varrow(590, 136, 158))

# 判定
parts.append(F.box(90, 162, 280, 44, "size &lt; 4KB（池的一半）", bold=True, fs=13, stroke=C["ink2"]))
parts.append(F.box(450, 162, 280, 44, "size ≥ 4KB（达到半池）", bold=True, fs=13, stroke=C["ink2"]))
parts.append(F.varrow(230, 206, 228))
parts.append(F.varrow(590, 206, 228))

# 动作
parts.append(F.box(90, 232, 280, 60, "", stroke=C["line"]))
parts.append(f'<text x="230" y="257" text-anchor="middle" font-size="12.5" font-weight="700" fill="{C["label"]}">从预分配的 8KB “找零池”里切一片</text>')
parts.append(f'<text x="230" y="277" text-anchor="middle" font-size="11" fill="{C["muted"]}">复用共享池 · 快</text>')
parts.append(F.box(450, 232, 280, 60, "", stroke=C["line"]))
parts.append(f'<text x="590" y="257" text-anchor="middle" font-size="12.5" font-weight="700" fill="{C["label"]}">独立分配一块大小恰好的专属内存</text>')
parts.append(f'<text x="590" y="277" text-anchor="middle" font-size="11" fill="{C["muted"]}">避免霸占找零池</text>')

# 左：slab 切分
parts.append(F.zone(46, 320, 470, 200, "途径一 · 8KB slab 共享切分"))
parts.append(F.box(66, 372, 430, 48, "", fill=C["band"], stroke=C["ink2"]))
parts.append(F.box(66, 372, 86, 48, "", fill=C["card"], stroke=C["ink2"]))
parts.append(f'<text x="109" y="400" text-anchor="middle" font-size="10.5" fill="{C["label"]}">切片 a · 3B</text>')
parts.append(F.box(152, 372, 120, 48, "", fill=C["card"], stroke=C["ink2"]))
parts.append(f'<text x="212" y="400" text-anchor="middle" font-size="10.5" fill="{C["label"]}">切片 b · 10B</text>')
parts.append(f'<rect x="272" y="372" width="224" height="48" rx="4" fill="none" stroke="{C["line"]}" stroke-width="1.2" stroke-dasharray="4 4"/>')
parts.append(f'<text x="384" y="400" text-anchor="middle" font-size="10.5" fill="{C["muted"]}">剩余 · 装不下就换新池</text>')
# offset 刻度
for x, t in [(66, "offset 0"), (152, "offset 8 · 8 字节对齐"), (272, "offset 24")]:
    parts.append(F.line(x, 420, x, 428, col=C["muted"], w=1))
    parts.append(f'<text x="{x}" y="444" font-size="10.5" fill="{C["muted"]}">{t}</text>')
parts.append(f'<text x="66" y="482" font-size="11" fill="{C["body"]}">多个小 Buffer 共享同一个 ArrayBuffer · 各自持有偏移量</text>')

# 右：独立分配
parts.append(F.zone(536, 320, 238, 200, "途径二 · 独立分配"))
parts.append(F.box(556, 372, 198, 48, "专属 ArrayBuffer", bold=True, fs=12, stroke=C["ink2"]))
parts.append(f'<text x="655" y="444" text-anchor="middle" font-size="10.5" fill="{C["muted"]}">大小 = 请求大小</text>')
parts.append(f'<text x="556" y="482" font-size="11" fill="{C["body"]}">达到半池不再进池</text>')

# 底部
parts.append(F.note(46, 552, "半池分界是“严格小于”：alloc(4095) 还在池里 · alloc(4096) 独立分配", size=12.5, accent=True))
parts.append(F.note(46, 576, "长度为 0 的分配直接返回现成的空 Buffer，不占任何内存", size=11.5))

F.build(OUT, W, H, *parts)
