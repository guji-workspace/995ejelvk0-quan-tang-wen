"""jiazhu_split.has_mid_gap：中间没有空白列的格不拆成左右小注（k6，Sheldon 11-13 人审「单字被切成左右小注」）。"""
import numpy as np

from guji_book.quantangwen import row_hooks as J

W = 100


def _pair(gap: int) -> np.ndarray:
    """左右两个部件（各两根竖笔），中缝 gap 像素。"""
    p = np.full((60, W), 255, np.uint8)
    c = W // 2
    for x in (c + gap // 2, c + gap // 2 + 30, c - gap // 2 - 4, c - gap // 2 - 34):
        p[5:50, x:x + 4] = 0
    return p


def test_true_pair_has_gap():
    assert J.has_mid_gap(_pair(6))


def test_left_right_char_has_no_gap():
    """左右结构整字：两部件之间有一横连着（勞、勝的笔画），中段没有一列空白。"""
    p = _pair(6)
    p[25:28, 14:86] = 0                                          # 横笔贯穿两部件
    assert not J.has_mid_gap(p)
    assert not J.jiazhu_pair_ok(p, J.INK_THRESHOLD, forced=True)


def test_frame_line_does_not_hide_gap():
    """列末格被下版框线横穿（「四其」「司如」）：去掉横线后仍量得出缝。"""
    p = _pair(6)
    p[55:58, 2:98] = 0
    assert J.has_mid_gap(p)
    assert J.jiazhu_pair_ok(p, J.INK_THRESHOLD, forced=True)


def _touching_pair() -> np.ndarray:
    """并排两字挨着：左字一横伸到右字，中缝被连上（001 韻編页「十八」「九百」）。墨框扁。"""
    p = np.full((60, 160), 255, np.uint8)
    p[10:50, 30:34] = 0           # 左字竖
    p[29:31, 8:84] = 0            # 左字横（细），伸到右字
    p[10:50, 84:88] = 0           # 右字两竖
    p[10:50, 130:134] = 0
    p[10:13, 84:134] = 0
    return p


def test_wide_touching_pair():
    p = _touching_pair()
    assert not J.has_mid_gap(p, J.INK_THRESHOLD, J.FORCED_BAND)
    assert J.wide_touching_pair(p)
    assert J.jiazhu_pair_ok(p, J.INK_THRESHOLD, forced=True)
    assert J.jiazhu_pair_ok(p, J.INK_THRESHOLD, forced=False)


def test_square_left_right_char_still_merged():
    """左右结构整字（勝）：中缝被一道粗横连着，人指认也不拆。"""
    p = _pair(6)
    p[25:28, 14:86] = 0
    assert not J.wide_touching_pair(p)
    assert not J.jiazhu_pair_ok(p, J.INK_THRESHOLD, forced=True)
