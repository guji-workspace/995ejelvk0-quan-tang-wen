"""全唐文 Step3 行切分的书级钩子（cv `impl/keben/row_hooks`；k8，2026-11-13 切分线）。

k1–k7 整份复制了 cv 的 row_boundaries、jiazhu_split（2026-11-04 分叉），每次公用修复都要人手同步（A22《切分开关收敛》
QTW 第 3 条）。k8 起只留与 cv 不同的几段，挂成钩子；两份 fork 删掉，其余照走 cv 的。四个钩子：

- `grid_adjust`＝`rephase_short_grid`（k4 节末短列重定相位）。
- `jiazhu_heads`＝`single_row_heads`（`jiazhu_single_head`：「字｜闕」＋「一」一行就完的雙行段头；k5 iso 量缝）。
- `half_a_left`＝`_half_a_left`（`jiazhu_half_a`：奇数字段尾的右半格左缘）。
- `jiazhu_pair_ok`＝`has_mid_gap`（k6：两行之间总有白缝，没缝的是左右结构整字，不拆）。

函数体与常量逐字照抄 k7 的 fork（只把 `jiazhu_split.X` 换成本模块的 X）；改动以后照常过期。
"""
from __future__ import annotations

from collections.abc import Sequence

import cv2
import numpy as np

# ── 常量：逐条对应 extractor.py 的 JIAZHU_* / JZ_* ──────────────
# 迁移时值全部照搬。**不要凭感觉调**——每个值后面都跟着一个实测案例。
INK_THRESHOLD = 128        # = extractor.BINARY_THRESHOLD_PATCH

SPAN_T = 0.75              # 两子列合起来占**列距**的比例下限。两册抽样 4023

MASS_W = 0.6               # 单个子列宽度上限（× 墨迹跨度）

CC_MIN = 500               # 段中位「两侧较小 maxCC」低于此 → 噪点段否决

# 段端收编（奇数字末行只剩一个字 / 末行两字量不出缝）
TAIL_MIN_INK = 100         # 收编候选的总墨下限（px）

TAIL_A_FRAC = 0.8          # 单字尾：缝右（a 侧）墨占比下限

HALF_MIN_INK = 30          # 拆出来的半格墨少于此不发格子（段末单半）

def _binary(patch: np.ndarray, ink_threshold: int = INK_THRESHOLD) -> np.ndarray:
    if patch.ndim == 3:
        patch = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
    return (patch < ink_threshold).astype(np.uint8)

# ── 人裁强制：这一格就是雙行小注，从中间拆开（2026-09-30）──────────────────────
# 判据（`gap_center`：缝宽≥3px、缝在墨迹跨度 30~70%、搭档格凑段）对提要末尾 2~3 行的短版本小注会
# 落空：缝只有 2px、缝偏出窗口、或搭档量不出缝凑不成段（vol02 12:7:9 / 97:9:19 / 180:8:8 等）。
# 人看图一眼就知道是小注，所以给一条**不看判据**的通道：人指认的格直接拆。
# 缝不求准——取墨迹跨度中段 35~65% 里**墨量最少的那条谷**（并列取最靠中心的一段的中点），
# 没有空谷就是笔画最少的那一列；两半墨量不够 `HALF_MIN_INK` 的半边由调用方照旧不发格子。
FORCED_BAND = (0.35, 0.65)

#: 强制拆的缝列最多容这么多墨点（扫描噪点）；再多就是笔画连着，不拆（Sheldon 11-13 人审：单字被切成左右小注）
FORCED_GAP_MAX_INK = 1

#: 量缝时扔掉的框线行：横向开运算后这一行的横线墨合计 ≥ 墨跨度的 GAP_LINE_W（上下各带 2 行）。只会让「有缝」更容易成立（照旧拆），不会多合
GAP_LINE_W = 0.5

GAP_LINE_SEG = 0.08    # 横向开运算的核长（占墨跨度）：框线断成几截、斜一两像素也认得出

GAP_LINE_EDGE = 0.2    # 框线只在格的上下各 20% 里找

def has_mid_gap(patch: np.ndarray, ink_threshold: int = INK_THRESHOLD,
                band: tuple[float, float] = (0.30, 0.70)) -> bool:
    """墨的横向跨度中间 `band` 里有没有一列墨不超过 FORCED_GAP_MAX_INK（真夹注两字之间总有缝）。
    墨太少量不出时当有缝（不改原判）。"""
    binary = _binary(patch, ink_threshold).copy()
    if binary.sum() < 80:
        return True
    # 横贯大半格宽的横线（列末下版框线，常断成几截、略斜）不算：它把缝盖住了（列末「四其」「司如」）
    xp0 = binary.sum(axis=0)
    ink0 = np.flatnonzero(xp0 > 0)
    if len(ink0) < 10:
        return True
    w0 = int(ink0[-1]) - int(ink0[0]) + 1
    k = max(9, int(GAP_LINE_SEG * w0))
    horiz = cv2.morphologyEx(binary, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (k, 1)))
    h = binary.shape[0]
    rows = np.flatnonzero(horiz.sum(axis=1) >= GAP_LINE_W * w0)
    rows = rows[(rows < GAP_LINE_EDGE * h) | (rows >= (1 - GAP_LINE_EDGE) * h)]   # 只认格的上下边带，字中间的长横画不动
    for y in rows:
        binary[max(0, y - 2):y + 3] = 0
    xp = binary.sum(axis=0)
    ink = np.flatnonzero(xp > 0)
    if len(ink) < 10:
        return True
    x0, x1 = int(ink[0]), int(ink[-1])
    span = x1 - x0 + 1
    lo = x0 + int(span * band[0])
    hi = x0 + int(np.ceil(span * band[1]))
    return bool(xp[lo:hi + 1].min() <= FORCED_GAP_MAX_INK)

def single_row_heads(entries: list[tuple[int, tuple[float, float] | None]], runs: dict[int, float],
                     patches: dict[int, np.ndarray], eligible: set[int] | None = None,
                     ink_threshold: int = INK_THRESHOLD, ruler: float | None = None) -> dict[int, float]:
    """一行就完的雙行小注段头（`segment_column` 的 `jiazhu_single_head`，2026-11-04 全唐文）：

    「闕一字」这类三字小注排成两行：头一行「字｜闕」两字并排，第二行只有右半一个「一」。`link_runs` 要
    连着两行量得出缝（`MIN_RUN`），只有一行量得出时整段落空：头一行当整宽正文字、两字挤一格，第二行成了
    單行小注。这里补认：量得出缝（strength ≥ `CC_MIN`）、不在段里的一格，下一格墨 ≥`TAIL_A_FRAC` 落在
    这条缝右边（单字尾的口径）→ 这一格记成段（只一行），段尾交给 `adopt_run_tails` 照常收成 `jiazhu_a`。
    返回补进来的 `{格号: 缝中心}`，不改输入。"""
    out: dict[int, float] = {}
    measured = {i: c for i, c in entries if c is not None}
    for i, (cx, strength) in sorted(measured.items()):
        if i in runs or i - 1 in runs or i + 1 in runs or strength < CC_MIN:
            continue
        if eligible is not None and (i not in eligible or i + 1 not in eligible):
            continue
        nxt = patches.get(i + 1)
        if nxt is None or (i + 1) in measured:
            continue
        cxi = int(round(cx))
        if cxi <= 0 or cxi >= nxt.shape[1]:
            continue
        ys, xs = np.nonzero(_binary(nxt, ink_threshold))
        if xs.size < TAIL_MIN_INK or float((xs >= cxi).mean()) < TAIL_A_FRAC:
            continue
        out[i] = cx
    # 孤立一行的夹注（2026-11-13）：碑誌正文页列首、列尾、列中只一行的「闕｜一」「其｜三」，前后没有能连段的行。
    # 量得出缝（strength ≥`CC_MIN`）且缝够宽（`_iso_wide_gap`），或宽缝并排两字（`_pair_wide_gap`，左半只一两横、
    # 墨量比过不了 `gap_center` 的也算；量出缝而 strength 不够的是噪点，不收）→ 记成段（只一行）。两条都卡「一侧只是一根竖笔」（`_thin_stroke_side`）：
    # 「川」三竖分开、缝也宽（039:65:8:1）。
    for i in sorted(patches):
        if i in runs or i in out or (eligible is not None and i not in eligible):
            continue
        m = measured.get(i)
        if m is not None and m[1] >= CC_MIN and _iso_wide_gap(patches[i], m[0], ink_threshold) \
                and not _thin_stroke_side(patches[i], m[0], ink_threshold):
            out[i] = m[0]
        elif (m is None or m[1] >= CC_MIN) and (cxp := _pair_wide_gap(patches[i], ruler, ink_threshold)) is not None:
            out[i] = cxp
    return out

def _pair_wide_gap(patch: np.ndarray, ruler: float | None,
                   ink_threshold: int = INK_THRESHOLD) -> float | None:
    """宽中缝并排两字（不看两侧墨量比）：跨度 ≥`SPAN_T`×尺、缝落在跨度 30–70%、缝宽 ≥`ISO_GAP_FRAC`×格框宽、
    两侧各 ≥`ISO_SIDE_MIN_INK` 墨、各自宽 ≤`MASS_W`×跨度 → 缝中心；否则 None。"""
    binary = _strip_rule_rows(_binary(patch, ink_threshold))
    xp = binary.sum(axis=0)
    w = xp.shape[0]
    ink = np.flatnonzero(xp > 0)
    if ink.size < 10:
        return None
    x0, x1 = int(ink[0]), int(ink[-1])
    span = x1 - x0 + 1
    if span / float(ruler or w) < SPAN_T:
        return None
    best = None
    a = None
    for x in range(x0, x1 + 2):
        z = x <= x1 and xp[x] == 0
        if z and a is None:
            a = x
        elif not z and a is not None:
            if a - x0 > 0.30 * span and x - x0 < 0.70 * span and (best is None or x - a > best[1] - best[0]):
                best = (a, x)
            a = None
    if best is None or best[1] - best[0] < ISO_GAP_FRAC * w:
        return None
    left, right = binary[:, x0:best[0]], binary[:, best[1]:x1 + 1]
    if min(int(left.sum()), int(right.sum())) < ISO_SIDE_MIN_INK:
        return None
    if max(left.shape[1], right.shape[1]) > MASS_W * span:
        return None
    cx = float(best[0] + best[1]) / 2
    if _thin_stroke_side(patch, cx, ink_threshold):
        return None
    return cx

def _thin_stroke_side(patch: np.ndarray, cx: float, ink_threshold: int = INK_THRESHOLD) -> bool:
    """缝 `cx` 某一侧的墨只是一根竖笔：墨框宽 < `THIN_SIDE_W`×格框宽、高 > `THIN_SIDE_H`×格高（「川」的「丿」）。
    并排小注每侧是一整个小字，「一」「二」又扁又宽，都不会这样。"""
    binary = _strip_rule_rows(_binary(patch, ink_threshold))
    h, w = binary.shape
    c = int(round(cx))
    for side in (binary[:, :c], binary[:, c:]):
        if side.size == 0 or not side.any():
            continue
        n, _lab, stats, _cen = cv2.connectedComponentsWithStats(np.ascontiguousarray(side), 8)
        keep = [k for k in range(1, n) if stats[k, 4] >= THIN_SIDE_SPECK * side.sum()]   # 去散点、纸渣
        if not keep:
            continue
        x0 = min(stats[k, 0] for k in keep)
        x1 = max(stats[k, 0] + stats[k, 2] for k in keep)
        y0 = min(stats[k, 1] for k in keep)
        y1 = max(stats[k, 1] + stats[k, 3] for k in keep)
        if (x1 - x0) < THIN_SIDE_W * w and (y1 - y0) > THIN_SIDE_H * h:
            return True
    return False

#: 孤立一行的雙行小注（2026-11-13 全唐文 g5 层 1，切分线）：碑誌正文页（reference_profile text）列首、列尾、列中
#: 只有一行的「闕｜一」「其｜三」两字并排，`link_runs` 要连两行、`single_row_heads` 原判据要下一格是右半单字尾，
#: 都落空，两字挤成一个整宽格（g5 正文页宽格 341 个，列尾 96、列首／列中孤立 201）。单格 `gap_center` 会被左右
#: 结构正文字骗（039 抽 12 页：量得出缝的正文字 27 个，隱刑邪知比謝張後州如…），但它们的中缝窄：缝宽／格框宽
#: 正文字最大 0.033，小注对 0.049 起（中位约 0.09）。缝宽 ≥ `ISO_GAP_FRAC` 才认这一行是段（只一行）。
ISO_GAP_FRAC = 0.042

THIN_SIDE_W = 0.15          # 一侧墨框宽 < 此 × 格框宽、

THIN_SIDE_H = 0.6           # 高 > 此 × 格高 → 只是一根竖笔

THIN_SIDE_SPECK = 0.05      # 量墨框时不算面积 < 此 × 该侧墨的连通体（散点）

RULE_ROW_FRAC = 0.5         # 一行墨 ≥ 此 × 格框宽算框线行

RULE_EDGE = 0.2             # 只在格上下各这么高的带里找框线行

RULE_ROW_PAD = 6           # 框线行上下连带抹掉的行数（px）

ISO_SIDE_MIN_INK = 40     # 宽缝并排两字每侧墨下限（px），「一」一横约 150–300

def _strip_rule_rows(binary: np.ndarray) -> np.ndarray:
    """抹掉横贯格框的行（列尾下版框线、列首上框条：一行墨 ≥`RULE_ROW_FRAC`×格框宽），不让它把中缝填死
    （039:82:6:22「二｜闕」）。框线是断的、略斜，不要求连成一段；只看格的上下 `RULE_EDGE` 带，
    格中间并排两字各一横加起来过半宽的行不抹，免得抹出假缝。"""
    h = binary.shape[0]
    edge = RULE_EDGE * h
    rows = [r for r in np.flatnonzero(binary.sum(axis=1) >= RULE_ROW_FRAC * binary.shape[1])
            if r < edge or r >= h - edge]
    if not rows:
        return binary
    out = binary.copy()
    for r in rows:   # 框线常是斜的、粗细不匀：连上下各 RULE_ROW_PAD 行一起抹
        out[max(0, r - RULE_ROW_PAD):r + RULE_ROW_PAD + 1] = 0
    return out

def _iso_wide_gap(patch: np.ndarray | None, cx: float, ink_threshold: int = INK_THRESHOLD) -> bool:
    """`cx` 那条缝（列投影全零的一段）够宽：≥ `ISO_GAP_FRAC` × 格框宽。"""
    if patch is None:
        return False
    xp = _strip_rule_rows(_binary(patch, ink_threshold)).sum(axis=0)
    w = xp.shape[0]
    c = int(round(cx))
    if c <= 0 or c >= w - 1 or xp[c] != 0:
        return False
    a = z = c
    while a > 0 and xp[a - 1] == 0:
        a -= 1
    while z < w - 1 and xp[z + 1] == 0:
        z += 1
    return (z - a + 1) >= ISO_GAP_FRAC * w


#: 短列重定相位（`rephase_short_grid`）：列里只有一段字、不超过这么多格高时才管
SHORT_BLOCK_MAX = 5.5

#: 字段之间空过这么多格高就算段断开（下面再有墨就不是「只有一段」）
SHORT_BLOCK_GAP = 1.5

#: 一行墨超过内容宽的这个比例才算有墨（滤掉纸面噪点）
SHORT_INK_FRAC = 0.04

#: 相位最多挪这么多格高
SHORT_SHIFT_MAX = 0.75

#: 字段里的格线合计压墨不到内容宽的这么多倍，算没切进字（格线擦着笔尖不算）
SHORT_CUT_INK = 0.3

def rephase_short_grid(row_proj: np.ndarray, bounds: Sequence[float], period: float, dst_w: int) -> list[float]:
    """节末短列（只剩一到五个字、下面整列空）的等距格网重定相位，全唐文书级（切分线 2026-11-11 f3）。

    等距格网的相位逐列按全列墨投影的傅里叶分量定（`impl/keben/row_grid`）。整列只有一两个字时分量很弱，
    相位被纸面噪点带偏，格网整体压低半格到一格，首字被拦腰切（020:28:1「烈」、030:120:1「奏」、
    020:140:4「子宜體予意」等 9 列，f3 待审第一层）。这里只看这一段字：在 ±0.75 格内找一个整体平移，
    让落在字段里的格线压的墨最少、首字不落到首条格线之上；原格网已经不压墨就原样返回（长列、正常列逐字节不变）。"""
    b = [float(y) for y in bounds]
    h = len(row_proj)
    if h == 0 or period <= 0 or len(b) < 2:
        return b
    sm = np.convolve(row_proj, np.ones(5) / 5.0, mode="same")
    ink = sm > max(2.0, SHORT_INK_FRAC * dst_w)
    ys = np.flatnonzero(ink[12:]) + 12          # 顶上十来行常是版框线
    ys = ys[ys < h - 0.3 * period]               # 列底常带一截下版框线
    if len(ys) == 0:
        return b
    top = int(ys[0])
    bot = top
    for y in ys:
        if y - bot > SHORT_BLOCK_GAP * period:
            return b                                # 下面还有墨：不是只有一段字的短列
        bot = int(y)
    if bot - top > SHORT_BLOCK_MAX * period:
        return b
    lo, hi = top - 0.3 * period, bot + 0.3 * period

    def cost(d: float) -> float:
        c = 0.0
        for y in b:
            yy = y + d
            if lo <= yy <= hi:
                c += float(sm[int(min(max(round(yy), 0), h - 1))])
        return c

    base = cost(0.0)
    if b[0] <= top and base <= SHORT_CUT_INK * dst_w:
        return b                                    # 原格网没切进字里：不动
    best_d, best_c = 0.0, base if b[0] <= top else float("inf")
    r = int(SHORT_SHIFT_MAX * period)
    for d in sorted(range(-r, r + 1), key=abs):
        if b[0] + d > top or b[0] + d < -0.5 * period:
            continue
        c = cost(float(d))
        if c < best_c:
            best_d, best_c = float(d), c
    if best_d == 0.0 or (b[0] <= top and best_c > 0.5 * base):
        return b
    return [y + best_d for y in b]

def _half_a_left(patch: np.ndarray, cxi: int, ink_threshold: int) -> int | None:
    """`jiazhu_half_a`：只有右半有字的夹注格，右半格的左缘（格内 x）。压着右半（x ≥ 缝）的连通块
    （面积 ≥ `HALF_A_MIN_AREA`，滤掉噪点）里最靠左的一个像素，不超过缝；右半连同这些块墨不到
    `HALF_MIN_INK` 时返回 None（字整个偏在左半，交回按墨多的一半发）。"""
    import cv2
    ink = (patch < ink_threshold).astype(np.uint8)
    if ink.size == 0 or cxi >= ink.shape[1]:
        return None
    n, lab, stats, _ = cv2.connectedComponentsWithStats(ink, connectivity=8)
    x0 = cxi
    for i in set(np.unique(lab[:, max(cxi, 0):])) - {0}:
        if stats[i, cv2.CC_STAT_AREA] >= HALF_A_MIN_AREA:
            x0 = min(x0, int(stats[i, cv2.CC_STAT_LEFT]))
    if int(ink[:, x0:].sum()) < HALF_MIN_INK:
        return None
    return x0

HALF_A_MIN_AREA = 20


# ---- 钩子（cv row_hooks 的同名入口） ----

grid_adjust = rephase_short_grid
half_a_left = _half_a_left


def jiazhu_heads(entries, runs, patches, eligible=None, ink_threshold: int = INK_THRESHOLD, ruler=None):
    return single_row_heads(entries, runs, patches, eligible=eligible, ink_threshold=ink_threshold, ruler=ruler)


#: k6 段内摘格量缝的带（与 fork 里 `has_mid_gap` 的缺省带一致）
PAIR_BAND = (0.30, 0.70)


def jiazhu_pair_ok(patch: np.ndarray, ink_threshold: int, forced: bool) -> bool:
    return has_mid_gap(patch, ink_threshold, FORCED_BAND if forced else PAIR_BAND)




# ── 空列首格只有上框粗条＋细线（k9，2026-11-14，台账 R018）──────────────────────────────
# 全唐文上版框是一道粗条（≈45–70px）下面隔 25–40px 一道细线。none 页（卷末、目录）的空列里，列窗被认成抬头往上伸进
# 粗条、或上版框探得偏高，首格就是「粗条＋细线」，切成「一／幸／士」。cv 的缺省判据（seg/profile.frame_only_edge_cells）
# 要求墨贴着 border_top 0.2 格高以内，粗条离 border_top 远、或这列没有 border_top，就漏了。
# 这里只看首格本身：有一道粗条（行墨 ≥ EFO_BAR_W 列宽、厚 ≥ EFO_BAR_H 格高），粗条以下 EFO_ZONE 格高以外没有墨，
# 粗条以外的墨段都薄（≤ EFO_THIN 格高：细线、框边残墨）。真字的横笔（一、二、三、土…）厚不到 0.15 格高，
# 粗条下面有字的列，字落在 EFO_ZONE 以外。054（1611 列）、060（1745 列）全册首格过一遍，只认出空列首格与列首单独的粗条格。
EFO_SPECK = 0.08      # 一行墨 ≥ 此 × 列宽才算有墨（同 seg/profile.FRAME_EDGE_SPECK）
EFO_BAR_W = 0.8       # 粗条：墨段里最宽一行 ≥ 此 × 列宽
EFO_BAR_H = 0.15      # 粗条：厚 ≥ 此 × 格高（period 205 时 31px）
EFO_ZONE = 0.25       # 最下一道粗条以下这么多格高以内可以有细线
EFO_THIN = 0.1        # 粗条以外的墨段厚 ≤ 此 × 格高


def _ink_runs(row: np.ndarray, t: float) -> list[tuple[int, int, float]]:
    out, st = [], None
    for i, x in enumerate(list(row) + [0.0]):
        if x >= t and st is None:
            st = i
        elif x < t and st is not None:
            out.append((st, i - 1, float(max(row[st:i]))))
            st = None
    return out


def edge_frame_only(gray: np.ndarray, spans, content_x, border_top, border_bottom, period: float,
                    ink_threshold: int = INK_THRESHOLD) -> list[int]:
    """首格（`spans[0]`）里只有上框粗条（＋细线）→ [0]，否则 []。cv `row_hooks.edge_frame_only`，与缺省判据取并集。"""
    if not spans or not period:
        return []
    h, w = gray.shape[:2]
    x0, x1 = (int(content_x[0]), int(content_x[1])) if content_x else (0, w)
    x0, x1 = max(0, x0), min(w, max(x1, x0 + 1))
    a, b = max(0, int(spans[0][0])), min(h, int(spans[0][1]))
    if b <= a:
        return []
    row = (gray[a:b, x0:x1] < ink_threshold).sum(axis=1) / float(x1 - x0)
    runs = _ink_runs(row, EFO_SPECK)
    bars = [r for r in runs if r[2] >= EFO_BAR_W and r[1] - r[0] + 1 >= EFO_BAR_H * period]
    if not bars:
        return []
    be = max(r[1] for r in bars)
    if any(r[0] > be + EFO_ZONE * period for r in runs):
        return []
    if any(r[1] - r[0] + 1 > EFO_THIN * period for r in runs if r not in bars):
        return []
    return [0]
