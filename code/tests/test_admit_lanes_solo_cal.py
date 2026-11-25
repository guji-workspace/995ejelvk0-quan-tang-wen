"""seed_admit 无参照格 5a 校准直放（全唐文书级通道 `book_lanes.solo_cal`，原 cv seed_admit，2026-11-24 搬来）。"""
from __future__ import annotations

import pytest

import open_guji_cv.steps  # noqa: F401
from guji_book.quantangwen.admit_lanes import _parse_cal_tiers, solo_cal_decide
from guji_book.quantangwen import admit_lanes as AL
from open_guji_cv.steps import seed_admit as _sa

AL._F.is_gap, AL._F.is_hanzi = _sa.is_gap, _sa._is_hanzi   # 纯函数用的 facts（noref_lanes 进来时由 cv 给）

TIERS = _parse_cal_tiers("0.98:0.03,0.95:0.05")
SKIP = "己已巳于干曰日代伐遣遺"
KW = dict(guard=None, doubts=["库 unsure(cov=0.97)", "上下文 margin 不足(0.02)"], tiers=TIERS, skip=SKIP,
          group_chars=frozenset("王玉"), near_form_chars=frozenset("七匕士土"))


def test_tiers():
    assert TIERS == [(0.98, 0.03), (0.95, 0.05)]
    assert solo_cal_decide(cands=[("張", 0.985), ("振", 0.95)], **KW) == ("張", 0.985, 0.035, "tier")
    assert solo_cal_decide(cands=[("張", 0.96), ("振", 0.905)], **KW) == ("張", 0.96, 0.055, "tier")
    assert solo_cal_decide(cands=[("張", 0.96)], **KW) == ("張", 0.96, 0.96, "tier")       # 没有异字：gap＝cov
    assert solo_cal_decide(cands=[("張", 0.985), ("張", 0.97), ("振", 0.95)], **KW) == ("張", 0.985, 0.035, "tier")


def test_5b_tier():
    cands = [("張", 0.955), ("振", 0.95)]
    assert solo_cal_decide(cands=cands, **KW) is None
    assert solo_cal_decide(cands=cands, rare_top="張", cov_5b=0.95, **KW) == ("張", 0.955, 0.005, "5b")
    assert solo_cal_decide(cands=cands, rare_top="振", cov_5b=0.95, **KW) is None      # 5-b 不同意（汪→注 这类）
    assert solo_cal_decide(cands=[("張", 0.945), ("振", 0.90)], rare_top="張", cov_5b=0.95, **KW) is None


@pytest.mark.parametrize("cands,over", [
    ([("張", 0.985), ("振", 0.96)], {}),                           # 0.98 档 gap 不够
    ([("張", 0.97), ("振", 0.93)], {}),                            # 0.95 档 gap 不够
    ([("張", 0.94), ("振", 0.80)], {}),                            # cov 太低
    ([("代", 0.99), ("張", 0.90)], {}),                            # 首位在排除对
    ([("張", 0.99), ("遣", 0.90)], {}),                            # 第一个异字在排除对
    ([("王", 0.99), ("張", 0.90)], {}),                            # 首位在字组
    ([("張", 0.99), ("振", 0.90)], {"guard": "conflict"}),
    ([("張", 0.99), ("振", 0.90)], {"doubts": ["occluded"]}),
    ([("張", 0.99), ("振", 0.90)], {"doubts": ["库里没有这个字"]}),
    ([("張", 0.99), ("振", 0.90)], {"doubts": ["near_form"]}),     # 形近疑问照拦
    ([("士", 0.99), ("張", 0.90)], {}),                            # 首位在形近表
])
def test_blocks(cands, over):
    assert solo_cal_decide(cands=cands, **{**KW, **over}) is None


def test_ok_doubts():
    for d in ("护栏:never_match", "group_flow_abstain", "上下文 margin 不足(0.0)"):
        assert solo_cal_decide(cands=[("張", 0.99), ("振", 0.90)], **{**KW, "doubts": [d]}) is not None
    assert solo_cal_decide(cands=[("張", 0.99), ("振", 0.90)], **{**KW, "guard": "never_match"}) is not None



def test_solo_cal_canon():
    """solo_cal_5b_canon：5-b 首位按本书码位归一后与库首位同字算一致（原 cv test_seed_admit_c38_nm5b）。"""
    from types import SimpleNamespace as NS

    def run(canon):
        p = AL.LaneParams(solo_cal=True, solo_cal_5b_cov=0.95, solo_cal_allow="愼")
        rec = NS(id="001:1:1:1", char="愼", admit=False, channel=None, provenance="", doubts=["库 unsure(cov=0.96)"],
                 evidence={})
        rare = NS(columns=[NS(chars=[NS(id="001:1:1:1", candidates=[NS(char="慎")])])])
        mmap = {"001:1:1:1": NS(candidates=[("愼", 0.96), ("真", 0.90)], guard=None)}
        facts = _sa._AdmitFacts(None)
        return AL._solo_cal_pass(p, [NS(chars=[rec])], mmap, {}, rare, {}, facts, canon=canon), rec

    assert run(None)[0] == 0
    n, rec = run(lambda c: {"慎": "愼"}.get(c, c))
    assert n == 1 and rec.char == "愼" and rec.channel == "match_solo_cal"
