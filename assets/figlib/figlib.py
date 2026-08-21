"""全书插图渲染库 · 风格已锁定：B2 深蓝编辑部风。

tokens 与组件几何为全书统一规范，勿随意改动；新组件按需追加，
追加后全书图可一键重生成（各图 spec 位于 assets/figs/fig_*.py）。
"""

SANS = "'Source Han Sans SC','Noto Sans CJK SC',sans-serif"

C = dict(
    ink="#16213e",        # 主色·深navy：标题/强调填充/退出节点
    ink2="#2a3550",       # 结构线/序号块/箭头
    label="#1d2740",      # 卡片内主文字
    body="#3d4763",       # 栏内正文
    muted="#7a8296",      # 次级说明
    faint="#8b93a7",      # kicker/眉标
    line="#c9cfdd",       # 卡片描边/分隔细线
    band="#f4f6fa",       # 区域色带
    card="#ffffff",       # 卡片底/页面底
    accent="#e8862e",     # 唯一高亮色·橙
    accent_deep="#c56a15",
)


def svg_open(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{SANS}">\n<defs>\n'
        f'<marker id="ar" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto">'
        f'<path d="M1,1 L8,4 L1,7" fill="none" stroke="{C["ink2"]}" stroke-width="1.5"/></marker>\n'
        f'<marker id="ara" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto">'
        f'<path d="M1,1 L8,4 L1,7" fill="none" stroke="{C["accent"]}" stroke-width="1.5"/></marker>\n'
        f'</defs>\n<rect x="0" y="0" width="{w}" height="{h}" fill="{C["card"]}"/>\n'
    )


def svg_close():
    return '</svg>\n'


def header(w, title, kicker):
    x2 = w - 46
    return (
        f'<text x="46" y="40" font-size="18" fill="{C["ink"]}" font-weight="800" letter-spacing="1">{title}</text>\n'
        f'<text x="{x2}" y="40" text-anchor="end" font-size="10.5" fill="{C["faint"]}" letter-spacing="3">{kicker}</text>\n'
        f'<line x1="46" y1="54" x2="{x2}" y2="54" stroke="{C["ink"]}" stroke-width="2"/>\n'
        f'<line x1="46" y1="58.5" x2="{x2}" y2="58.5" stroke="{C["line"]}" stroke-width="0.8"/>\n'
    )


def zone(x, y, w, h, label):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{C["band"]}" stroke="{C["ink2"]}" stroke-width="1.4"/>\n'
        f'<text x="{x+16}" y="{y+24}" font-size="10.5" fill="{C["muted"]}" letter-spacing="2.5">{label}</text>\n'
    )


def stage(x, y, w, h, num, label, desc, active=False, sub=None):
    fill = C["ink"] if active else C["card"]
    stroke = C["ink"] if active else C["line"]
    sw = 1.4 if active else 1.2
    lab = "#ffffff" if active else C["label"]
    desc_fill = "#c3c9d6" if active else C["muted"]
    by = y + (h - 20) / 2
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>',
        f'<rect x="{x+12}" y="{by}" width="20" height="20" rx="3" fill="{C["accent"] if active else C["ink2"]}"/>',
        f'<text x="{x+22}" y="{by+14.5}" font-size="12" font-weight="700" fill="#ffffff" text-anchor="middle">{num}</text>',
    ]
    if sub:
        out.append(
            f'<text x="{x+44}" y="{y+h/2-2}" font-size="13.5" font-weight="700" fill="{lab}">{label}'
            f'<tspan font-weight="400" fill="{desc_fill}" font-size="12">　{desc}</tspan></text>'
        )
        out.append(f'<text x="{x+44}" y="{y+h/2+15}" font-size="11" fill="{C["accent"] if active else C["muted"]}">{sub}</text>')
    else:
        out.append(
            f'<text x="{x+44}" y="{y+h/2+5}" font-size="13.5" fill="{lab}">{label}'
            f'<tspan fill="{desc_fill}" font-size="12">　{desc}</tspan></text>'
        )
    return '\n'.join(out)


def varrow(x, y1, y2):
    return f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{C["ink2"]}" stroke-width="1.4" fill="none" marker-end="url(#ar)"/>'


def path_arrow(d, accent=False):
    col = C["accent"] if accent else C["ink2"]
    mk = "ara" if accent else "ar"
    sw = 2 if accent else 1.4
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" marker-end="url(#{mk})"/>'


def note(x, y, *lines, accent=False, size=12):
    col = C["accent_deep"] if accent else C["muted"]
    wt = ' font-weight="700"' if accent else ''
    return '\n'.join(
        f'<text x="{x}" y="{y+i*17}" font-size="{size}" fill="{col}"{wt}>{t}</text>'
        for i, t in enumerate(lines)
    )


def pill(cx, y, w, text, h=32):
    return (
        f'<rect x="{cx-w/2}" y="{y}" width="{w}" height="{h}" rx="3" fill="{C["ink"]}"/>\n'
        f'<text x="{cx}" y="{y+h/2+4.5}" text-anchor="middle" font-size="12.5" fill="#ffffff">{text}</text>'
    )


def vrule(x, y1, y2):
    return f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{C["line"]}" stroke-width="1"/>'


def box(x, y, w, h, text, fill=None, stroke=None, tfill=None, fs=12, r=4, bold=False):
    fill = fill or C["card"]
    stroke = stroke or C["line"]
    tfill = tfill or C["label"]
    wt = ' font-weight="700"' if bold else ''
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>\n'
        f'<text x="{x+w/2}" y="{y+h/2+4.5}" text-anchor="middle" font-size="{fs}" fill="{tfill}"{wt}>{text}</text>'
    )


def arrow(x1, y1, x2, y2, accent=False):
    col = C["accent"] if accent else C["ink2"]
    mk = "ara" if accent else "ar"
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1.4" fill="none" marker-end="url(#{mk})"/>'


def line(x1, y1, x2, y2, col=None, w=1.2):
    col = col or C["ink2"]
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}"/>'


def badge(x, y, n, accent=True):
    fill = C["accent"] if accent else C["ink2"]
    return (
        f'<rect x="{x}" y="{y}" width="20" height="20" rx="3" fill="{fill}"/>\n'
        f'<text x="{x+10}" y="{y+14.5}" font-size="12" font-weight="700" fill="#ffffff" text-anchor="middle">{n}</text>'
    )


def lane_divider(x, y1, y2):
    return f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{C["line"]}" stroke-width="1" stroke-dasharray="4 4"/>'


def ksection(x, y, kicker, title, lines):
    """右栏知识条目：kicker + 粗题 + 橙色短下划线 + 行列表 [(text, 'body'|'muted')]"""
    out = [
        f'<text x="{x}" y="{y}" font-size="10.5" fill="{C["faint"]}" letter-spacing="2.5">{kicker}</text>',
        f'<text x="{x}" y="{y+24}" font-size="14" fill="{C["ink"]}" font-weight="800">{title}</text>',
        f'<line x1="{x}" y1="{y+36}" x2="{x+44}" y2="{y+36}" stroke="{C["accent"]}" stroke-width="3"/>',
    ]
    ly = y + 64
    for text, kind in lines:
        if kind == "muted":
            out.append(f'<text x="{x}" y="{ly}" font-size="11.5" fill="{C["faint"]}">{text}</text>')
        else:
            out.append(f'<text x="{x}" y="{ly}" font-size="12.5" fill="{C["body"]}">{text}</text>')
        ly += 24
    return '\n'.join(out)


def build(path, w, h, *parts):
    with open(path, "w") as f:
        f.write(svg_open(w, h))
        f.write('\n'.join(parts))
        f.write('\n' + svg_close())
    print("wrote", path)
