"""图 3-1 require 的五步旅程（纵向流程 + 缓存命中分支）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-3-1.svg")
C = F.C


def box2(x, y, w, h, l1, l2, fill=None, stroke=None, t1=None, t2=None):
    fill = fill or C["card"]
    stroke = stroke or C["line"]
    t1 = t1 or C["label"]
    t2 = t2 or C["muted"]
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>\n'
        f'<text x="{x+w/2}" y="{y+h/2-3}" text-anchor="middle" font-size="12" font-weight="700" fill="{t1}">{l1}</text>\n'
        f'<text x="{x+w/2}" y="{y+h/2+14}" text-anchor="middle" font-size="10.5" fill="{t2}">{l2}</text>'
    )


parts = [F.header(820, "require 的五步旅程", "REQUIRE PIPELINE")]

# 入口
parts.append(F.pill(310, 76, 190, "require('foo')"))
parts.append(F.varrow(310, 112, 130))

# 五步
X, W, H, GAP = 70, 480, 52, 18
ys = [132, 202, 272, 342, 412]
parts.append(F.stage(X, ys[0], W, H, 1, "解析", "把 'foo' 变成绝对路径",
                     sub="核心模块？相对路径？node_modules 逐级向上找？"))
parts.append(F.stage(X, ys[1], W, H, 2, "查缓存", "Module._cache 里有？"))
parts.append(F.stage(X, ys[2], W, H, 3, "建模块对象", "new Module(filename)，塞入缓存",
                     sub="注意：先入缓存，再执行"))
parts.append(F.stage(X, ys[3], W, H, 4, "编译执行", "把文件内容包进一层函数再执行",
                     sub="(function(exports, require, module, __filename, __dirname) { …你的代码… })"))
parts.append(F.stage(X, ys[4], W, H, 5, "返回", "module.exports"))

for i in range(4):
    parts.append(F.varrow(X + W / 2, ys[i] + H + 2, ys[i + 1] - 2))

# 第 2 步的缓存命中分支
y2 = ys[1] + H / 2
parts.append(F.arrow(X + W + 4, y2, X + W + 46, y2))
parts.append(box2(X + W + 50, ys[1] + 2, 172, 48, "有：直接返回缓存的 exports", "（到此结束）"))
parts.append(F.note(X + W + 12, y2 - 8, "有", size=10.5))

F.build(OUT, 820, 500, *parts)
