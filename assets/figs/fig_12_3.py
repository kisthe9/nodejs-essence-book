"""图 12-3 火把交接：内置加载器 → CJS 加载器 → 私有 require。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-12-3.svg")
C = F.C

parts = [F.header(820, "模块加载：火把交接的位置", "LOADER HANDOFF · STEP ④")]

# 引导期
parts.append(F.box(70, 84, 440, 76, "", stroke=C["ink2"]))
parts.append(F.note(86, 108, "引导期 · 内置加载器", size=12.5))
parts.append(F.note(86, 126, "lib/internal/bootstrap/loaders.js", size=10.5))
parts.append(F.note(86, 146, "加载引导脚本与 lib/ 全家桶", size=11))

# 交接箭头
parts.append(F.path_arrow("M 290 162 V 196", accent=True))
parts.append(F.note(306, 184, "④ 火把交接", accent=True, size=12))

# 主模块
parts.append(F.box(70, 200, 440, 76, "", stroke=C["ink2"]))
parts.append(F.note(86, 224, "主模块 · CJS 加载器", size=12.5))
parts.append(F.note(86, 242, "lib/internal/modules/cjs/loader.js", size=10.5))
parts.append(F.note(86, 262, "第一次为你的代码服务", size=11))

parts.append(F.varrow(290, 278, 312))

# 每次 require
parts.append(F.box(70, 316, 440, 62, "", stroke=C["line"], fill=C["band"]))
parts.append(F.note(86, 340, "你的每次 require：同一台 CJS 加载器", size=12))
parts.append(F.note(86, 360, "require 是按本模块位置现场制作的私有副本", size=11))

# 右栏：两本通行证
parts.append(F.vrule(540, 84, 420))
parts.append(F.ksection(564, 96, "ONE SHELL · TWO PASSES", "同一壳 · 两本通行证", [
    ("内置壳多出两参数：", "body"),
    ("internalBinding → 穿门直达 C++", "body"),
    ("primordials → 原始副本", "body"),
    ("用户壳：__filename / __dirname", "body"),
    ("摸不到门内参数", "muted"),
    ("出生证上就没发", "muted"),
]))
parts.append(F.note(564, 340, "权限的差异就是函数签名的差异", accent=True, size=12))

parts.append(F.note(70, 412, "此前加载器只服务门内自己人；主模块是第一个“用户待遇”的模块", size=11.5))

F.build(OUT, 820, 450, *parts)
