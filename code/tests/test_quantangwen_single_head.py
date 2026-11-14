"""jiazhu_split.single_row_heads：一行就完的雙行小注段头（全唐文「字｜闕」＋「一」，2026-11-04）。"""
import numpy as np

from guji_book.quantangwen import row_hooks as J


def _patch(right: bool, left: bool, w: int = 40, h: int = 40) -> np.ndarray:
    p = np.full((h, w), 255, np.uint8)
    if right:
        p[5:35, 24:36] = 0
    if left:
        p[5:35, 4:16] = 0
    return p


def test_head_row_followed_by_right_half_tail_is_adopted():
    entries = [(1, (20.0, 900.0)), (2, None), (3, None)]
    big = np.full((40, 40), 255, np.uint8)
    big[5:35, 6:34] = 0                       # 列尾整宽正文字（没有中缝）
    patches = {1: _patch(True, True), 2: _patch(True, False), 3: big}
    assert J.single_row_heads(entries, {}, patches, eligible={1, 2, 3}) == {1: 20.0}


def test_next_row_full_width_is_not_adopted():
    entries = [(1, (20.0, 900.0)), (2, None)]
    big = np.full((40, 40), 255, np.uint8)
    big[5:35, 6:34] = 0                       # 下一格是整宽正文字
    lr = np.full((40, 40), 255, np.uint8)
    lr[5:35, 4:19] = 0
    lr[5:35, 20:36] = 0                       # 左右结构正文字，缝只 1px（宽缝的并排两字见 iso_row 测试）
    patches = {1: lr, 2: big}
    assert J.single_row_heads(entries, {}, patches, eligible={1, 2}) == {}


def test_weak_gap_skipped_wide_gap_next_to_run_adopted():
    patches = {1: _patch(True, True), 2: _patch(True, False)}
    assert J.single_row_heads([(1, (20.0, J.CC_MIN - 1)), (2, None)], {}, patches) == {}
    # 紧挨着已认的段、缝又宽（2026-11-13）：当段头收进来
    assert J.single_row_heads([(1, (20.0, 900.0)), (2, None)], {2: 20.0}, patches) == {1: 20.0}
