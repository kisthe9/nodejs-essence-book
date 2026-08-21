"""图 2-2 一段 JS 的一生 · 分层编译管线（纵向 stage + arrow）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-2-2.svg")
C = F.C


def stage_card(y, name, desc, fill=None, stroke=None, nfill=None, dfill=None):
    fill = fill or C["card"]
    stroke = stroke or C["line"]
    nfill = nfill or C["label"]
    dfill = dfill or C["muted"]
    return (
        f'<rect x="190" y="{y}" width="440" height="54" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>\n'
        f'<text x="210" y="{y+23}" font-size="13" font-weight="700" fill="{nfill}">{name}</text>\n'
        f'<text x="210" y="{y+42}" font-size="11.5" fill="{dfill}">{desc}</text>'
    )


def cond(x, y, text, accent=False):
    fill = C["accent_deep"] if accent else C["muted"]
    return f'<text x="{x}" y="{y}" font-size="11.5" fill="{fill}">{text}</text>'


parts = [F.header(820, "一段 JS 的一生 · 分层编译管线", "TIERED COMPILATION")]

# 顶部：源代码 → Parser → AST
parts.append(F.box(150, 96, 120, 38, "源代码", bold=True))
parts.append(F.arrow(270, 115, 316, 115))
parts.append(F.box(320, 96, 120, 38, "Parser", bold=True))
parts.append(F.arrow(440, 115, 486, 115))
parts.append(F.box(490, 96, 200, 38, "抽象语法树（AST）", bold=True))
parts.append(F.path_arrow("M 590 134 V 156 H 410 V 166"))

# 四级编译阶段
parts.append(stage_card(172, "Ignition 解释器", "字节码 · 逐条执行"))
parts.append(F.varrow(410, 230, 258))
parts.append(cond(430, 248, "某函数被反复调用（变“热”）"))

parts.append(stage_card(262, "Sparkplug", "字节码直译机器码 · 快而粗糙"))
parts.append(F.varrow(410, 320, 348))
parts.append(cond(430, 338, "热上加热"))

parts.append(stage_card(352, "Maglev / TurboFan", "逐级加深的优化机器码"))
parts.append(F.varrow(410, 410, 438))
parts.append(cond(430, 428, "假设失败（比如参数类型突然变了）", accent=True))

parts.append(stage_card(442, "去优化（Deopt）", "退回低级层",
                        fill=C["ink"], stroke=C["ink"], nfill="#ffffff", dfill="#c3c9d6"))

F.build(OUT, 820, 530, *parts)
