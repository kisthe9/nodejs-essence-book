"""图 9-1 异步因果链：何时触发是异步，如何分发是同步。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-9-1.svg")
C = F.C

W, H = 820, 440

parts = [F.header(W, "异步性来自何时，同步性留在如何", "WHEN ASYNC · HOW SYNC")]

# 第一排
parts.append(F.box(46, 110, 222, 52, "内核 · fd 就绪", bold=True, fs=12.5, stroke=C["ink2"]))
parts.append(F.arrow(268, 136, 298, 136))
parts.append(F.box(300, 110, 222, 52, "epoll_wait 返回", fs=12.5, stroke=C["ink2"]))
parts.append(F.arrow(522, 136, 552, 136))
parts.append(F.box(554, 110, 220, 52, "libuv 调 C++ 回调", fs=12.5, stroke=C["ink2"]))

# 折行
parts.append(F.varrow(664, 162, 198))

# 第二排
parts.append(F.box(554, 202, 220, 52, "MakeCallback 进入 JS", fs=12.5, stroke=C["ink2"]))
parts.append(F.arrow(554, 228, 524, 228))
parts.append(F.box(250, 202, 272, 52, "socket.emit('data', buf)", fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True, fs=12.5))

# 异步性标注
parts.append(f'<path d="M 386 268 L 394 282 L 378 282 Z" fill="{C["accent"]}"/>')
parts.append(F.note(250, 306, "异步性来自这里 —— 事件循环决定何时触发", accent=True, size=12.5))
parts.append(F.note(250, 330, "emit 本身只是同步分发：for 循环调用监听器", size=12))

# 底部结论
parts.append(F.box(46, 362, 728, 44, "何时触发 = 异步（事件循环掌管） · 如何分发 = 同步（for 循环）", fill=C["band"], tfill=C["label"], bold=True, fs=12.5))

F.build(OUT, W, H, *parts)
