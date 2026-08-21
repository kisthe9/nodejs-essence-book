"""图 16-1 全片回放：一个请求的一生 · 六幕（章节徽章随行）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-16-1.svg")
C = F.C

parts = [F.header(820, "全片回放：一个请求的一生", "ONE REQUEST · FULL REPLAY")]


def seg_text(x, y, segs, fs=11):
    """一行混排文字：('m', '[12]') 章节徽章用橙色，('t', …) 正文用 body 色。"""
    spans = []
    for kind, t in segs:
        if kind == "m":
            spans.append(f'<tspan font-weight="700" fill="{C["accent"]}">{t}</tspan>')
        else:
            spans.append(f'<tspan fill="{C["body"]}">{t}</tspan>')
    return f'<text x="{x}" y="{y}" font-size="{fs}">{"".join(spans)}</text>'


def stage_row(y, tag, segs, h=34):
    out = [F.box(46, y, 64, h, tag, fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True, fs=12.5)]
    out.append(F.box(122, y, 652, h, "", stroke=C["line"]))
    out.append(seg_text(136, y + h / 2 + 4, segs))
    return out


rows = [
    ("启动", [("m", "[12]"), ("t", "装配线 → "), ("m", "[11]"), ("t", "三层容器 → "), ("m", "[3]"),
              ("t", "require+穿门 → "), ("m", "[6]"), ("t", "listen-fd → "), ("m", "[4]"), ("t", "循环入睡")]),
    ("连接", [("t", "内核握手 → "), ("m", "[4/5]"), ("t", "epoll 醒 → accept 得 conn-fd"), ("m", "[6]"),
              ("t", " → "), ("m", "[9]"), ("t", "emit('connection')")]),
    ("请求", [("t", "字节进内核缓冲 → "), ("m", "[5]"), ("t", "循环 read 至 EAGAIN → "), ("m", "[7]"),
              ("t", "零拷贝入 Buffer → "), ("m", "[9]"), ("t", "emit('request')")]),
    ("处理", [("m", "[5]"), ("t", "readFile 走线程池 · 主线程继续接客 → 完工唤醒 → "), ("m", "[3]"),
              ("t", "MakeCallback → 你的 cb")]),
    ("响应", [("t", "res.end → "), ("m", "[8]"), ("t", "背压控流 → "), ("m", "[6]"),
              ("t", "write(conn-fd) 多态分发 → 网卡 → 浏览器")]),
    ("退场", [("t", "SIGTERM → "), ("m", "[12]"), ("t", "server.close 撤句柄 → 循环自然停 → 善终")]),
]

ys = [84, 136, 188, 240, 306, 358]
for (tag, segs), y in zip(rows, ys):
    h = 52 if tag == "处理" else 34
    parts.extend(stage_row(y, tag, segs, h=h))
    if tag == "处理":
        parts.append(seg_text(136, y + 42, [("m", "[15]"),
                                            ("t", "因果链全程随行：跨线程池、跨事件循环，上下文不丢")], fs=10.5))

# 幕间小箭头
for y1, y2 in [(118, 136), (170, 188), (222, 240), (292, 306), (340, 358)]:
    parts.append(F.varrow(78, y1, y2))

# 多核注脚
parts.append(F.box(46, 412, 728, 40, "", stroke=C["line"], fill=C["band"]))
parts.append(seg_text(60, 436, [("m", "[14]"),
                                ("t", "以上全部 × N 份容器 · cluster 分发连接；跨容器靠 "),
                                ("m", "[15]"), ("t", " 的“携带 + 重新 run”接续")], fs=11))

F.build(OUT, 820, 480, *parts)
