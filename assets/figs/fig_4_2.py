"""图 4-2 插队者：微任务优先级（高→低，阶段间隙排空）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-4-2.svg")
C = F.C


def dash_hline(x1, x2, y):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{C["line"]}" stroke-width="1" stroke-dasharray="4 4"/>'


def ctext(x, y, text, size=11.5, fill=None, weight=None):
    fill = fill or C["muted"]
    wt = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="{fill}"{wt}>{text}</text>'


parts = [F.header(820, "插队者：微任务的优先级", "MICROTASK PRIORITY")]

# 左列：优先级三级卡片
parts.append(F.stage(46, 96, 450, 52, 1, "process.nextTick 队列", "Node 自己维护 · 最高优先级"))
parts.append(F.stage(46, 164, 450, 52, 2, "Promise 微任务队列", "V8 维护"))

# 两条虚线之间：排空说明（对应原图括号注）
parts.append(dash_hline(46, 496, 234))
parts.append(ctext(271, 257, "以上两个队列在事件循环每个阶段切换的间隙被排空", 11.5, C["body"]))
parts.append(ctext(271, 275, "且 nextTick 队列先于 Promise 队列", 11.5, C["muted"]))
parts.append(dash_hline(46, 496, 290))

parts.append(F.stage(46, 306, 450, 52, 3, "七阶段里的宏任务回调", "timers / poll / check …"))

# 中缝：优先级方向标尺
parts.append(F.path_arrow("M 521 106 V 348"))
parts.append(ctext(521, 96, "高", 11, C["muted"]))
parts.append(ctext(521, 368, "低", 11, C["muted"]))

# 右栏：排空规则
parts.append(F.vrule(546, 90, 392))
parts.append(F.ksection(570, 112, "DRAIN · 排空", "排空，不是排队", [
    ("阶段间隙全量清空", "body"),
    ("nextTick 先 · Promise 后", "body"),
    ("宏任务按阶段依次放行", "body"),
    ("递归微任务会饿死循环", "muted"),
]))

F.build(OUT, 820, 420, *parts)
