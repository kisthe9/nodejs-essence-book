"""图 3-7 穿门之旅：require('http') 全链路（纵向树 + 右侧批注）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-3-7.svg")
C = F.C


def anno(y, s, fill=None, bold=False):
    fill = fill or C["muted"]
    wt = ' font-weight="700"' if bold else ''
    return f'<text x="774" y="{y}" text-anchor="end" font-size="11" fill="{fill}"{wt}>← {s}</text>'


def elbow(x1, y1, x2, y2):
    mid = (y1 + y2) / 2
    return f'<path d="M {x1} {y1} V {mid} H {x2} V {y2}" fill="none" stroke="{C["ink2"]}" stroke-width="1.2"/>'


parts = [F.header(820, "穿门之旅 · require('http')", "CROSSING THE DOOR")]

# 逐级下钻的调用链
parts.append(F.box(70, 100, 280, 40, "require('http')", stroke=C["ink2"], bold=True, fs=12.5))
parts.append(elbow(86, 140, 126, 164))
parts.append(F.box(110, 164, 280, 40, "http.js ──require──▶ net.js", fs=12))
parts.append(elbow(126, 204, 166, 228))
parts.append(F.box(150, 228, 280, 40, "internalBinding('tcp_wrap')",
                   fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True, fs=12.5))
parts.append(elbow(166, 268, 206, 292))
parts.append(F.box(190, 292, 280, 40, "new TCP()", stroke=C["ink2"], bold=True, fs=12.5))

# new TCP() 的两个动作
parts.append(f'<path d="M 206 332 V 424 M 206 376 H 226 M 206 424 H 226" fill="none" stroke="{C["ink2"]}" stroke-width="1.2"/>')
parts.append(F.box(230, 356, 300, 40, "初始化 libuv 的 TCP 句柄（uv_tcp_init）", fs=11))
parts.append(F.box(230, 404, 300, 40, "通过内部字段与 JS 对象互相绑定", fs=11.5))

# 后续调用沿绑定直达
parts.append(F.box(70, 476, 200, 40, "server.listen(8080)", stroke=C["ink2"], bold=True, fs=12))
parts.append(F.path_arrow("M 170 476 V 462 H 380 V 450"))

# 右侧批注
parts.append(anno(124, "门内：CJS 五步加载"))
parts.append(anno(188, "内置模块相互依赖，纯 JS"))
parts.append(anno(252, "穿门：拿到 C++ 导出", fill=C["accent_deep"], bold=True))
parts.append(anno(316, "C++ 侧创建 TCPWrap 实例"))
parts.append(anno(500, "后续调用沿着绑定直达 C++"))

F.build(OUT, 820, 540, *parts)
