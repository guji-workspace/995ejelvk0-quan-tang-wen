"""k10 只占右半的孤立小字（全唐文「闕」「并序」「疑」小写数字，2026-11-16 Sheldon，台账 R029）。"""
import numpy as np

from guji_book.quantangwen import row_hooks as J

W, H = 100, 100


def _cell(x0: int, x1: int, y0: int = 25, y1: int = 75) -> np.ndarray:
    p = np.full((H, W), 255, np.uint8)
    p[y0:y1, x0:x1] = 0
    return p


def _big() -> np.ndarray:
    return _cell(10, 90, 8, 92)


def test_right_small_alone_becomes_run():
    """「疑」：左缘 0.42、右缘 0.92，前后都是正文大字 → 记成段，缝取小字左缘。"""
    patches = {1: _big(), 2: _cell(42, 92), 3: _big()}
    got = J.single_row_heads([(1, None), (2, None), (3, None)], {}, patches, eligible={1, 2, 3}, ruler=W)
    assert got == {2: 41.0}


def test_narrow_body_char_bu_is_not_small():
    """正文窄字「卜」：偏右，但右缘只到 0.72。"""
    patches = {1: _big(), 2: _cell(44, 72, 8, 92), 3: _big()}
    assert J.single_row_heads([(1, None), (2, None), (3, None)], {}, patches, eligible={1, 2, 3}, ruler=W) == {}


def test_shifted_column_body_char_is_not_small():
    """偏列：整列字都往右挪，单看墨框像右半小字，但不比本列中位偏右。"""
    patches = {k: _cell(30, 96, 8, 92) for k in range(1, 6)}
    patches[3] = _cell(46, 94, 10, 90)
    got = J.single_row_heads([(k, None) for k in range(1, 6)], {}, patches, eligible=set(range(1, 6)), ruler=W)
    assert got == {}


def test_pair_ok_keeps_lone_right_small():
    assert J.jiazhu_pair_ok(_cell(42, 92), 128, forced=False)
    assert not J.jiazhu_pair_ok(_big(), 128, forced=False)
