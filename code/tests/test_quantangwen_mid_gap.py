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
