"""图 7-1 零拷贝解剖：JS、V8、物理内存三方同址。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-7-1.svg")
C = F.C

W, H = 820, 420

parts = [F.header(W, "零拷贝解剖：同一块物理内存", "BUFFER · BACKINGSTORE · SYSCALL")]

# 三列
parts.append(F.box(46, 110, 200, 88, "", stroke=C["ink2"]))
parts.append(f'<text x="62" y="136" font-size="10.5" fill="{C["faint"]}" letter-spacing="2.5">JS 视角</text>')
parts.append(f'<text x="62" y="162" font-size="13" font-weight="700" fill="{C["label"]}">Buffer 实例</text>')
parts.append(f'<text x="62" y="184" font-size="11.5" fill="{C["muted"]}">（Uint8Array 的子类）</text>')

parts.append(F.box(310, 110, 240, 88, "", stroke=C["ink2"]))
parts.append(f'<text x="326" y="136" font-size="10.5" fill="{C["faint"]}" letter-spacing="2.5">V8 内部</text>')
parts.append(f'<text x="326" y="162" font-size="13" font-weight="700" fill="{C["label"]}">ArrayBuffer</text>')
parts.append(f'<text x="326" y="184" font-size="11.5" fill="{C["body"]}">└ BackingStore · 裸内存的托管句柄</text>')

parts.append(F.box(614, 110, 160, 88, "", stroke=C["ink2"]))
parts.append(f'<text x="630" y="136" font-size="10.5" fill="{C["faint"]}" letter-spacing="2.5">物理内存</text>')
parts.append(f'<text x="630" y="162" font-size="13" font-weight="700" fill="{C["label"]}">一段真实的</text>')
parts.append(f'<text x="630" y="184" font-size="13" font-weight="700" fill="{C["label"]}">字节内存</text>')

# 横向箭头
parts.append(F.arrow(248, 154, 308, 154))
parts.append(f'<text x="256" y="144" font-size="11" fill="{C["muted"]}">继承自</text>')
parts.append(F.arrow(552, 154, 612, 154))
parts.append(f'<text x="562" y="144" font-size="11" fill="{C["muted"]}">持有</text>')

# 物理内存 → 系统调用
parts.append(F.varrow(694, 200, 258))

# 底部系统调用
parts.append(F.box(46, 262, 728, 64, "", fill=C["ink"], stroke=C["ink"]))
parts.append(f'<text x="410" y="288" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">C++ 侧拿到 BackingStore 的裸指针 → read(fd, 该指针, len)</text>')
parts.append(f'<text x="410" y="310" text-anchor="middle" font-size="11.5" fill="{C["accent"]}">内核直接把数据写进这块内存 · 两个世界之间零次复制</text>')

parts.append(F.note(46, 356, "buf[0] 读到的字节，就是内核当初写入的那个字节 —— 同一个物理地址", size=12.5))
parts.append(F.note(46, 380, "字符串方案要三级复制：内核缓冲 → C++ 中转 → 编码转换 → V8 堆字符串", size=11.5))

F.build(OUT, W, H, *parts)
