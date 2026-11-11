"""row_boundaries.rephase_short_grid：节末短列的等距格网按字段重定相位（全唐文 f3，切分线 2026-11-11）。"""
import numpy as np

from guji_book.quantangwen import row_boundaries as RB

P = 200.0


def _proj(blocks, h=4500, bottom_bar=True):
    rp = np.zeros(h)
    for a, b in blocks:
        rp[a:b] = 120.0
    if bottom_bar:
        rp[h - 20:h - 8] = 300.0           # 下版框线
    return rp


def _grid(start, n=22):
    return [start + i * P for i in range(n + 1)]


def test_one_char_column_grid_pulled_up():
    rp = _proj([(35, 225)])                 # 一个字，顶在列首
    out = RB.rephase_short_grid(rp, _grid(160.0), P, 340)
    assert out[0] <= 35 and out[1] >= 225   # 字整个落在第 1 格
    assert out[0] > 160 - 0.75 * P - 1


def test_long_column_untouched():
    rp = _proj([(20 + i * 200, 190 + i * 200) for i in range(20)])
    g = _grid(165.0)
    assert RB.rephase_short_grid(rp, g, P, 340) == g


def test_short_column_already_fine_untouched():
    rp = _proj([(30, 200), (230, 400)])
    g = _grid(20.0)
    assert RB.rephase_short_grid(rp, g, P, 340) == g


def test_ink_far_below_means_not_short():
    rp = _proj([(35, 225), (2000, 2150)])
    g = _grid(160.0)
    assert RB.rephase_short_grid(rp, g, P, 340) == g
