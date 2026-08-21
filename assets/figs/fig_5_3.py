"""图 5-3 文件路：线程池——阻塞没有消失，只是转移了。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-5-3.svg")
C = F.C

CX = 261  # 主流程中轴


def ctext(x, y, text, size=11.5, fill=None, weight=None):
    fill = fill or C["muted"]
    wt = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="{fill}"{wt}>{text}</text>'


def card2(x, y, w, h, l1, l2, l1fill=None, l2fill=None):
    l1fill = l1fill or C["label"]
    l2fill = l2fill or C["muted"]
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{C["card"]}" stroke="{C["line"]}" stroke-width="1.2"/>\n'
        f'<text x="{x+w/2}" y="{y+h/2-4}" text-anchor="middle" font-size="12" font-weight="700" fill="{l1fill}">{l1}</text>\n'
        f'<text x="{x+w/2}" y="{y+h/2+14}" text-anchor="middle" font-size="11" fill="{l2fill}">{l2}</text>'
    )


parts = [F.header(820, "文件路：雇四个工人替你阻塞", "FILE ROAD · THREAD POOL")]

# 主流程
parts.append(F.box(76, 90, 370, 38, "JS · fs.readFile('big.log', cb)", stroke=C["ink2"], bold=True, fs=12))
parts.append(F.varrow(CX, 128, 150))
parts.append(F.box(76, 154, 370, 38, "把任务 (fd, buffer, offset) 投进任务队列", fs=11.5))
parts.append(F.varrow(CX, 192, 214))

# 线程池 zone
parts.append(F.zone(76, 218, 370, 128, "线程池 · 默认 4 个工人线程"))
parts.append(ctext(CX, 272, "工人取任务 → 调用阻塞的 read()", 12, C["label"], 700))
parts.append(ctext(CX, 296, "实实在在地卡住 —— 卡的不是主线程", 11.5, C["muted"]))

parts.append(F.note(CX + 16, 372, "读完了", size=11))
parts.append(F.varrow(CX, 346, 388))

# 唤醒与回调
parts.append(card2(76, 392, 370, 52, "通过事件循环的唤醒机制通知主线程", "向一个内部管道写一字节 · 让 epoll_wait 醒来"))
parts.append(F.varrow(CX, 444, 466))
parts.append(F.box(76, 470, 370, 40, "主线程在下一圈循环里执行 cb(data)",
                   fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True, fs=12))

# 右侧批注：原图的两处旁注
parts.append(F.note(490, 152, "主线程立刻返回", "继续转事件循环 —— '异步'的来源", accent=True, size=12))
parts.append(F.note(490, 262, "阻塞没有消失", "只是转移了", accent=True, size=12))
parts.append(F.note(490, 410, "文件路的终点，汇回网络路的", "事件机制（epoll 被写醒）", size=11))

F.build(OUT, 820, 540, *parts)
