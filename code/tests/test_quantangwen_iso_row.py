"""jiazhu_split.single_row_heads：孤立一行的雙行小注（全唐文正文页「闕｜一」，2026-11-13 g5 层 1）。"""
import numpy as np

from guji_book.quantangwen import jiazhu_split as J

W = 100


def _pair(gap: int, left_rows=(5, 35), left_ink=True) -> np.ndarray:
    """右半一块字、左半一块字（或一横），中缝 gap 像素。"""
    p = np.full((40, W), 255, np.uint8)
    c = W // 2
    p[5:35, c + gap // 2: c + gap // 2 + 40] = 0                  # 右半「闕」
    if left_ink:
        p[left_rows[0]:left_rows[1], c - gap // 2 - 40: c - gap // 2] = 0
    return p


def _thin_one() -> np.ndarray:
    return _pair(10, left_rows=(19, 21))                          # 左半只一横「一」


def test_iso_row_alone_is_adopted():
    patches = {1: _pair(10)}
    assert J.single_row_heads([(1, (50.0, 900.0))], {}, patches, eligible={1}, ruler=W) == {1: 50.0}


def test_chuan_three_strokes_is_not_split():
    """「川」：三竖分开、缝宽，但左侧只是一根竖笔。"""
    p = np.full((40, W), 255, np.uint8)
    p[3:37, 12:17] = 0          # 丿
    p[8:34, 50:55] = 0
    p[3:38, 84:90] = 0
    assert J._pair_wide_gap(p, W * 0.9) is None
    assert J.single_row_heads([(1, (35.0, 900.0))], {}, {1: p}, eligible={1}, ruler=W * 0.9) == {}


def test_narrow_gap_left_right_char_is_not_split():
    patches = {1: _pair(2), 3: _pair(10), 4: _pair(10)}
    got = J.single_row_heads([(1, (50.0, 900.0)), (3, None), (4, None)], {3: 50.0, 4: 50.0}, patches,
                             eligible={1, 3, 4}, ruler=W)
    assert got == {}


def test_thin_left_numeral_pair_is_adopted_even_under_rule_line():
    p = _thin_one()
    p[37, :] = 0                                                  # 下版框线，断成两截、略斜
    p[36, 60:] = 0
    p[38, :30] = 0
    p[37, 45] = 255
    patches = {1: p, 3: _pair(10), 4: _pair(10)}
    got = J.single_row_heads([(1, None), (3, None), (4, None)], {3: 50.0, 4: 50.0}, patches,
                             eligible={1, 3, 4}, ruler=W)
    assert set(got) == {1} and abs(got[1] - 50.0) <= 2


def test_pair_wide_gap_rejects_one_sided_cell():
    assert J._pair_wide_gap(_pair(10, left_ink=False), W) is None
