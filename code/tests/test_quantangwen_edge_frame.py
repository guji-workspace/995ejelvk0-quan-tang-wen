"""row_hooks.edge_frame_only：空列首格只有上框粗条（＋细线）记空（k9，台账 R018）。"""
import numpy as np

from guji_book.quantangwen import row_hooks as J

P, W = 205.0, 350


def _cell(*bands, h=220):
    """bands：(y0, y1, x0, x1) 涂黑。"""
    g = np.full((h, W), 255, np.uint8)
    for y0, y1, x0, x1 in bands:
        g[y0:y1, x0:x1] = 0
    return g


def _hit(g):
    return J.edge_frame_only(g, [(0, g.shape[0]), (g.shape[0], g.shape[0] + 200)], (0, W), None, None, P, 128)


def test_bar_and_thin_line_is_frame():
    assert _hit(_cell((20, 70, 0, W), (100, 110, 0, W))) == [0]


def test_bar_only_is_frame():
    assert _hit(_cell((150, 195, 5, W - 5))) == [0]


def test_char_under_bar_is_not_frame():
    g = _cell((20, 70, 0, W), (100, 110, 0, W), (140, 200, 120, 200))     # 粗条下方 70px 有字
    assert _hit(g) == []


def test_yi_stroke_is_not_frame():
    assert _hit(_cell((100, 120, 40, 310))) == []                         # 「一」横笔：薄、不满宽


def test_thick_stroke_below_bar_is_not_frame():
    assert _hit(_cell((20, 70, 0, W), (90, 120, 60, 290))) == []          # 紧贴粗条下的厚笔画（不是细线）
