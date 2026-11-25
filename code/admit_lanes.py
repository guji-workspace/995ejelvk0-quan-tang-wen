"""全唐文书级放行通道（cv 钩子 `impl/keben/admit_lanes.noref_lanes`，cv 模块头有签名与 `facts` 说明）。

2026-11-24 CV4（Sheldon 定「搬进全唐文书仓」，QTW 同意）：只有全唐文 001–003（总目、姓氏韻編）用的四条无参照补放通道
solo_adapt／num_run／solo_cal／lead_5b 从 open-guji-cv `steps/seed_admit.py` 原样搬来，判据一行没改；cv 里对应的 28 个
参数删掉（写了非缺省值报错）。取值改写在册配置 `params.seed_admit.book_lanes`，键名与原 cv 参数同名，例：

    book_lanes:
      data: [config/groups/char_cov_profile.json]   # solo_adapt 字表，内容哈希进参数指纹
      solo_adapt_pct: p10
      num_run_cov: 0.995
      solo_cal: true
      lead_5b: true

各键含义、缺省与依据见下面 `LaneParams` 的说明（抄自原 cv 参数文档）。四条通道的次序同原来：solo_adapt → num_run →
solo_cal → lead_5b，都在 cv 的 solo_5b 之后、ref_lib_5b_veto 之前。只许 import open_guji_cv.seg／book_api 与本目录模块。
"""
from __future__ import annotations

from dataclasses import dataclass, fields

#: 己已巳（cv `utils.ji_yi_si.FAMILY`）
_JYS = frozenset("己已巳")
#: solo_adapt 字表缺省位置（相对数据目录；原 cv `solo_adapt_profile` 空时找这里）
DEFAULT_PROFILE = "config/groups/char_cov_profile.json"


class _Facts:
    """纯函数里用的 is_gap／is_hanzi：`noref_lanes` 进来时换成 cv 给的 facts。"""
    is_gap = staticmethod(lambda ch: False)
    is_hanzi = staticmethod(lambda ch: False)


_F = _Facts()


@dataclass(frozen=True)
class LaneParams:
    """四条通道的取值（`book_lanes` 里的键；缺省值同原 cv 参数，缺省＝关）。

    - `solo_adapt_pct`（"p10"／"p25"，None 关）：无参照格按字自适应门槛放行（2026-11-08，Sheldon 定方向）。本格库首位 c 的
      cov ≥ max(`solo_adapt_floor`, c 自比的该百分位)；c 自比样本 ≥ `solo_adapt_min_n`、留一法掉出比例 ≤ 0.2；5-b 首位就是 c；
      领先每个语义不同的候选 ≥ `solo_adapt_gap`；`solo_adapt_window` 内的高危字对／形近表对手、互比超限都不放。通道
      `match_solo_adapt`。字表 `solo_adapt_profile`（相对数据目录，须同时写进 `data`）。依据：front4 001、front5 002／003
      p10 档离线放 2,236 格未见确定错放。`solo_adapt_risk_gap`：高危对手落后够多不拦（front7 168 格未见错）；
      `solo_adapt_abstain_ok`／`solo_adapt_abstain_skip`：首位不在字组、只因 group_flow_abstain 被挡照判（真 除外）；
      `solo_adapt_near_slack`／`solo_adapt_near_gap`：差自比分位一点的格要领先更多（front8 862 格未见错）；
      `solo_adapt_nf_ok`：只因 near_form 疑问被挡照判（front8 105 格）。
    - `num_run_cov`（None 关）：无参照格「数字串里的数字」放过 never_match 护栏（2026-11-08，总目／韻編卷数小注）。库首位是
      数字、cov ≥ 这个值、领先 ≥ `num_run_gap`、同列紧挨着的前后格至少一个也是数字 → 放，通道 `match_num_run`。
      `num_run_juan_cov`：数字串前的「卷」（后一格是数字）也放；`num_run_cov_5b`／`num_run_gap_5b`：5-b 首位就是库首位的
      数字格 cov 降档、领先升档。依据：front3 逐格看图，never_match 待审数字 1,094 格、near_form／字组挡的 1,368 格全对。
    - `solo_cal`：无参照格 5a 校准直放（2026-11-08 Sheldon 定「直接放」，按 004 校准）。库首位 cov 与领先第一个异字的差落在
      `solo_cal_tiers` 任一档 → 放，通道 `match_solo_cal`；首位或第一个异字在 `solo_cal_skip`、首位在字组或形近表不放。
      `solo_cal_5b_cov`：库首位＝5-b 首位、cov ≥ 这个值就放；`solo_cal_allow`：白名单字只走 5-b 档、多认 near_form（front9
      整组 0 错的字）；`solo_cal_5b_canon`：比 5-b 首位前先按本书码位表归一（愼 5、吕 2）。
    - `lead_5b`：无参照格库与 5-b 不一致时听 5-b（2026-11-09）。5-b 首位领先其余候选 ≥ `lead_5b_gap_out`（不在库候选里）或
      ≥ `lead_5b_gap_in` 且库分 ≥ `lead_5b_lib_min`（＝库第二名）→ 放 5-b 首位，通道 `match_lead_5b`；`solo_cal_skip` 里的字不放。
    """
    solo_adapt_pct: str | None = None
    solo_adapt_floor: float = 0.94
    solo_adapt_gap: float = 0.01
    solo_adapt_min_n: int = 5
    solo_adapt_window: float = 0.05
    solo_adapt_profile: str = DEFAULT_PROFILE
    solo_adapt_risk_gap: float | None = None
    solo_adapt_abstain_ok: bool = False
    solo_adapt_abstain_skip: str = ""
    solo_adapt_near_slack: float | None = None
    solo_adapt_near_gap: float = 0.03
    solo_adapt_nf_ok: bool = False
    num_run_cov: float | None = None
    num_run_gap: float = 0.01
    num_run_juan_cov: float | None = None
    num_run_cov_5b: float | None = None
    num_run_gap_5b: float = 0.02
    solo_cal: bool = False
    solo_cal_tiers: str = "0.98:0.03,0.95:0.05"
    solo_cal_skip: str = "己已巳于干曰日代伐遣遺真"
    solo_cal_5b_cov: float | None = None
    solo_cal_allow: str = ""
    solo_cal_5b_canon: bool = False
    lead_5b: bool = False
    lead_5b_gap_out: float = 0.023
    lead_5b_gap_in: float = 0.015
    lead_5b_lib_min: float = 0.935

    @classmethod
    def parse(cls, raw: dict) -> "LaneParams":
        names = {f.name for f in fields(cls)}
        bad = sorted(k for k in raw if k not in names and k != "data")
        if bad:
            raise ValueError(f"book_lanes 有不认识的键 {bad}（全唐文书仓 code/admit_lanes.py）")
        p = cls(**{k: v for k, v in raw.items() if k != "data"})
        if p.solo_adapt_pct is not None:
            if p.solo_adapt_pct not in ("p10", "p25"):
                raise ValueError(f"solo_adapt_pct 只认 p10／p25，收到 {p.solo_adapt_pct!r}")
            if p.solo_adapt_profile not in (raw.get("data") or []):
                raise ValueError(f"book_lanes.solo_adapt_profile={p.solo_adapt_profile!r} 要同时写进 book_lanes.data（字表进指纹）")
        return p


def noref_lanes(*, out, mmap, amap, rare, coord, params, facts) -> int:
    """四条无参照补放通道，次序与原 cv 相同。→ 升级格数。"""
    p = LaneParams.parse(params)
    _F.is_gap, _F.is_hanzi = facts.is_gap, facts.is_hanzi
    n = 0
    if p.solo_adapt_pct is not None:
        n += _solo_adapt_pass(p, out, mmap, amap, rare, coord, facts)
    if p.num_run_cov is not None:
        n += _num_run_pass(p, out, mmap, amap, coord, rare if p.num_run_cov_5b is not None else None, facts)
    if p.solo_cal:
        n += _solo_cal_pass(p, out, mmap, amap, rare if p.solo_cal_5b_cov is not None else None, coord, facts,
                            canon=(facts.canonical_char if p.solo_cal_5b_canon else None))
    if p.lead_5b:
        n += _lead_5b_pass(p, out, mmap, amap, rare, coord, facts)
    return n


_ADAPT_CACHE: dict = {}


def load_adapt_profile(path: str) -> dict | None:
    """读字表（schema `char_cov_profile/1`）→ {"prof": {字: {n, miss, p10, p25, med}}, "cross": {"a|b": 上限}, "risk": {(a, b)}}。"""
    if not path:
        return None
    if path in _ADAPT_CACHE:
        return _ADAPT_CACHE[path]
    import json as _json
    with open(path, encoding="utf-8") as f:
        raw = _json.load(f)
    if raw.get("schema") != "char_cov_profile/1":
        raise ValueError(f"{path}: 不是 char_cov_profile/1 字表")
    risk = set()
    for a, b in raw.get("risk", []):
        risk.add((a, b))
        risk.add((b, a))
    out = {"prof": raw["prof"], "cross": raw.get("cross", {}), "risk": risk}
    _ADAPT_CACHE[path] = out
    return out


#: 字表 `cross` 只记互比 ≥ 这个值的字对（`scripts/char_cov_profile.py` 的 min_cross）
_ADAPT_CROSS_MIN = 0.90
_ADAPT_OK_DOUBTS = ("上下文 margin 不足", "库 unsure", "库 same 但准入被拦", "group_flow_ref_missing")


def solo_adapt_decide(*, cands: list, rare_top: str | None, guard, doubts, prof: dict, cross: dict, risk: set,
                      pct: str, floor: float, gap_min: float, min_n: int, window: float, are_variants,
                      group_chars, near_form_chars, risk_gap: float | None = None, abstain_ok: bool = False,
                      abstain_skip: str = "", near_slack: float | None = None, near_gap: float = 0.03,
                      nf_ok: bool = False) -> tuple[str, float, float] | None:
    """`LaneParams.solo_adapt_pct` 的判据，纯函数（离线评测与线上共用）。→ (放行字, cov, gap) 或 None。"""
    if guard is not None or not cands:
        return None
    ranked = sorted(cands, key=lambda t: -t[1])
    c, v = ranked[0]
    v = float(v)
    ok = _ADAPT_OK_DOUBTS
    if abstain_ok and c not in group_chars and c not in abstain_skip:
        ok = ok + ("group_flow_abstain",)     # solo_adapt_abstain_ok：首位不在字组，字组流程弃权不算数
    if nf_ok and c not in group_chars and c not in near_form_chars:
        ok = ok + ("near_form",)              # solo_adapt_nf_ok：形近家族字只是候选；窗口内的形近表对手下面照拦
    if any(not (isinstance(d, str) and d.startswith(ok)) for d in (doubts or [])):
        return None
    if (not c or _F.is_gap(c) or c in _JYS or not _F.is_hanzi(c) or c in group_chars or c in near_form_chars):
        return None
    pc = prof.get(c)
    thr = max(floor, pc[pct]) if pc else 1.0
    if not pc or pc["n"] < min_n or pc["miss"] > 0.2 or v < thr - (near_slack or 0.0):
        return None
    below = v < thr                       # solo_adapt_near_slack：差分位一点的格，领先要更大
    if rare_top != c:                     # 5-b 首位必须就是库首位（不认异体）
        return None
    rivals = [(d, float(w)) for d, w in ranked[1:] if d and d != c and not are_variants(d, c)]
    gap = v - max((w for _, w in rivals), default=0.0)
    if gap < gap_min or (below and gap < near_gap):
        return None
    for d, w in rivals:
        if w < v - window:
            continue
        if (c, d) in risk and risk_gap is not None and v - w >= risk_gap:
            continue                      # solo_adapt_risk_gap：高危对手落后够多，不拦
        if (c, d) in risk or d in near_form_chars:
            return None                   # 高危字对／形近表
        xm = cross.get(f"{c}|{d}", _ADAPT_CROSS_MIN)   # 字表只记 ≥ 0.90 的互比；没记＝c 的刻例像 d 不到 0.90
        if w > xm + 0.005:
            return None                   # 本格像 d 的程度超过 c 的刻例像 d 的上限
        xr = cross.get(f"{d}|{c}")
        if xr is not None and v <= xr:
            return None                   # d 的刻例也能这么像 c
    return c, v, round(gap, 4)


def _solo_adapt_pass(p: "LaneParams", out: list, mmap: dict, amap: dict, rare, coord: dict[str, str], facts) -> int:
    """无参照格按字自适应门槛放行。→ 升级格数。见 `LaneParams.solo_adapt_pct`。"""
    prof = load_adapt_profile(facts.data_path(p.solo_adapt_profile))
    if prof is None or rare is None:
        return 0
    are_variants, group_chars, NEAR_FORM_CHARS = facts.are_variants, facts.group_chars, facts.near_form_chars
    rmap = {r.id: r.candidates[0].char for cc in rare.columns for r in cc.chars if r.candidates and r.candidates[0].char}
    n = 0
    for col in out:
        for rec in col.chars or []:
            if rec.admit or rec.provenance == "human" or rec.channel == "human":
                continue
            if rec.id in amap or (coord.get(rec.id) or "") not in ("", *facts.gap_chars):
                continue                  # 有整理本对位的格归别的通道
            m = mmap.get(rec.id)
            if m is None or not m.candidates:
                continue
            got = solo_adapt_decide(cands=list(m.candidates), rare_top=rmap.get(rec.id), guard=m.guard, doubts=rec.doubts,
                                    prof=prof["prof"], cross=prof["cross"], risk=prof["risk"], pct=p.solo_adapt_pct,
                                    floor=p.solo_adapt_floor, gap_min=p.solo_adapt_gap, min_n=p.solo_adapt_min_n,
                                    window=p.solo_adapt_window, are_variants=are_variants, group_chars=group_chars,
                                    near_form_chars=NEAR_FORM_CHARS, risk_gap=p.solo_adapt_risk_gap,
                                    abstain_ok=p.solo_adapt_abstain_ok, abstain_skip=p.solo_adapt_abstain_skip,
                                    near_slack=p.solo_adapt_near_slack, near_gap=p.solo_adapt_near_gap,
                                    nf_ok=p.solo_adapt_nf_ok)
            if got is None:
                continue
            ch, cov1, gap = got
            rec.admit, rec.channel, rec.provenance, rec.char = True, "match_solo_adapt", "match_solo_adapt", ch
            rec.doubts = []
            rec.evidence = {**rec.evidence, "no_glyph_lib": True, "solo_adapt": {
                "lib": ch, "cov": round(cov1, 4), "gap": gap, "self": round(float(prof["prof"][ch][p.solo_adapt_pct]), 4)}}
            n += 1
    return n


#: `num_run_cov` 认的数字（卷数小注只用到这些）
NUM_RUN_DIGITS = frozenset("一二三四五六七八九十百千")
#: `num_run_cov` 允许的疑问（前缀）；别的疑问一律不碰
_NUM_RUN_OK_DOUBTS = ("护栏:never_match", "库 unsure", "库 same 但准入被拦", "上下文 margin 不足", "near_form",
                      "group_flow_ref_missing", "group_flow_abstain")
#: 邻格「是数字」时库首位的最低 cov（邻格未放行时）
_NUM_RUN_NEIGHBOR_COV = 0.98


def num_run_decide(*, cands: list, guard, doubts, prev: str | None, nxt: str | None, cov_min: float,
                   gap_min: float, are_variants, juan_cov: float | None = None, rare_top: str | None = None,
                   cov_5b: float | None = None, gap_5b: float | None = None) -> tuple[str, float, float] | None:
    """`LaneParams.num_run_cov` 的判据，纯函数（离线评测与线上共用）。`cands`：库候选 [(字, cov)]；
    `prev`／`nxt`：同列同半格前后格的字（已判成数字才算，调用方给 None 表示不是／没有）。→ (放行字, cov, gap) 或 None。"""
    if guard not in (None, "never_match") or not cands:
        return None
    if any(not (isinstance(d, str) and d.startswith(_NUM_RUN_OK_DOUBTS)) for d in (doubts or [])):
        return None
    ranked = sorted(cands, key=lambda t: -t[1])
    top, cov1 = ranked[0]
    if (cov_5b is not None and rare_top is not None and rare_top == top and top in NUM_RUN_DIGITS
            and cov_5b <= float(cov1) < cov_min):
        # 原门槛差一点、5-b 首位作证的数字：cov 降档、领先升档（num_run_cov_5b）；够原门槛的照原规则
        cov_min, gap_min = cov_5b, max(gap_min, gap_5b if gap_5b is not None else gap_min)
    if top == "卷" and juan_cov is not None:
        # 卷数前的「卷」：只认后一格是数字
        if float(cov1) < juan_cov or nxt not in NUM_RUN_DIGITS:
            return None
    elif top not in NUM_RUN_DIGITS or float(cov1) < cov_min:
        return None
    elif prev not in NUM_RUN_DIGITS and nxt not in NUM_RUN_DIGITS:
        return None
    rivals = [float(v) for c, v in ranked[1:] if c and c != top and not are_variants(c, top)]
    gap = float(cov1) - (max(rivals) if rivals else 0.0)
    if gap < gap_min:
        return None
    return top, float(cov1), round(gap, 4)


def _num_run_pass(p: "LaneParams", out: list, mmap: dict, amap: dict, coord: dict[str, str], rare, facts) -> int:
    """无参照格「数字串里的数字」放过 never_match 护栏。→ 升级格数。见 `LaneParams.num_run_cov`。"""
    are_variants = facts.are_variants
    rmap = ({r.id: r.candidates[0].char for cc in rare.columns for r in cc.chars if r.candidates and r.candidates[0].char}
            if rare is not None and p.num_run_cov_5b is not None else {})

    def digit_of(rec) -> str | None:
        if rec.admit:
            return rec.char if rec.char in NUM_RUN_DIGITS else None
        m = mmap.get(rec.id)
        if m is None or not m.candidates:
            return None
        c, v = max(m.candidates, key=lambda t: t[1])
        return c if c in NUM_RUN_DIGITS and float(v) >= _NUM_RUN_NEIGHBOR_COV else None

    n = 0
    for col in out:
        recs = list(col.chars or [])
        # 先按放行前的状态定邻格（本支放的格不互相作证，结果与格的先后无关）
        digit = {r.id: digit_of(r) for r in recs}
        by_sub: dict = {}
        for r in recs:
            by_sub.setdefault(r.sub, []).append(r)
        for seq in by_sub.values():
            for i, rec in enumerate(seq):
                if rec.admit or rec.provenance == "human" or rec.channel == "human":
                    continue
                if rec.id in amap or (coord.get(rec.id) or "") not in ("", *facts.gap_chars):
                    continue              # 有整理本对位的格归别的通道
                m = mmap.get(rec.id)
                if m is None or not m.candidates:
                    continue
                prev = digit[seq[i - 1].id] if i > 0 else None
                nxt = digit[seq[i + 1].id] if i + 1 < len(seq) else None
                got = num_run_decide(cands=list(m.candidates), guard=m.guard, doubts=rec.doubts, prev=prev, nxt=nxt,
                                     cov_min=p.num_run_cov, gap_min=p.num_run_gap, are_variants=are_variants,
                                     juan_cov=p.num_run_juan_cov, rare_top=rmap.get(rec.id),
                                     cov_5b=p.num_run_cov_5b, gap_5b=p.num_run_gap_5b)
                if got is None:
                    continue
                ch, cov1, gap = got
                rec.admit, rec.channel, rec.provenance, rec.char = True, "match_num_run", "match_num_run", ch
                rec.doubts = []
                rec.evidence = {**rec.evidence, "no_glyph_lib": True, "num_run": {
                    "lib": ch, "cov": round(cov1, 4), "gap": gap, "prev": prev, "next": nxt}}
                n += 1
    return n


#: `solo_cal` 允许的疑问（前缀）；group_flow_abstain 只在首位不在字组时认（字组首位本来就不放）；near_form 照拦
_SOLO_CAL_OK_DOUBTS = ("上下文 margin 不足", "护栏:never_match", "库 unsure", "库 same 但准入被拦",
                       "group_flow_ref_missing", "group_flow_abstain")


def _parse_cal_tiers(spec: str) -> list[tuple[float, float]]:
    out = []
    for part in (spec or "").split(","):
        if part.strip():
            c, g = part.split(":")
            out.append((float(c), float(g)))
    return out


def solo_cal_decide(*, cands: list, guard, doubts, tiers: list, skip: str, group_chars, near_form_chars,
                    rare_top: str | None = None, cov_5b: float | None = None,
                    ok_doubts: tuple = _SOLO_CAL_OK_DOUBTS, allow: str = "") -> tuple[str, float, float, str] | None:
    """`LaneParams.solo_cal` 的判据，纯函数。`cands`：库候选 [(字, cov)]。→ (放行字, cov, gap, 档) 或 None；
    档＝"tier"（cov／gap 档）或 "5b"（库首位＝5-b 首位且 cov ≥ cov_5b）。"""
    if guard not in (None, "never_match") or not cands:
        return None
    ranked = sorted(cands, key=lambda t: -t[1])
    c, v = ranked[0]
    v = float(v)
    if not c or _F.is_gap(c) or not _F.is_hanzi(c):
        return None
    got = _solo_cal_plain(c, v, ranked, doubts=doubts, tiers=tiers, skip=skip, group_chars=group_chars,
                          near_form_chars=near_form_chars, rare_top=rare_top, cov_5b=cov_5b, ok_doubts=ok_doubts)
    if got is None and c in allow and cov_5b is not None and rare_top == c and v >= cov_5b:
        # 白名单字（`solo_cal_allow`）：照常的档没放时，5-b 档不看 skip／字组／形近表，多认 near_form
        okd = ok_doubts + ("near_form",)
        if all(isinstance(d, str) and d.startswith(okd) for d in (doubts or [])):
            rival = next((float(w) for d, w in ranked[1:] if d and d != c), None)
            got = c, v, round(v - rival if rival is not None else v, 4), "allow"
    return got


def _solo_cal_plain(c, v, ranked, *, doubts, tiers, skip, group_chars, near_form_chars, rare_top, cov_5b, ok_doubts):
    if c in skip or c in group_chars or c in near_form_chars:
        return None
    if any(not (isinstance(d, str) and d.startswith(ok_doubts)) for d in (doubts or [])):
        return None
    rival = next(((d, float(w)) for d, w in ranked[1:] if d and d != c), None)
    if rival is not None and rival[0] in skip:
        return None
    gap = v - rival[1] if rival is not None else v
    if any(v >= tc and gap >= tg for tc, tg in tiers):
        return c, v, round(gap, 4), "tier"
    if cov_5b is not None and rare_top == c and v >= cov_5b:
        return c, v, round(gap, 4), "5b"
    return None


def _solo_cal_pass(p: "LaneParams", out: list, mmap: dict, amap: dict, rare, coord: dict[str, str], facts,
                   canon=None) -> int:
    """无参照格 5a 校准直放。→ 升级格数。见 `LaneParams.solo_cal`。
    `canon`：本书码位归一（`solo_cal_5b_canon` 开时给）；5-b 首位与库首位归一后同字，就把 5-b 首位当库首位比。"""
    group_chars, NEAR_FORM_CHARS = facts.group_chars, facts.near_form_chars
    tiers = _parse_cal_tiers(p.solo_cal_tiers)
    rmap = ({r.id: r.candidates[0].char for cc in rare.columns for r in cc.chars if r.candidates and r.candidates[0].char}
            if rare is not None and p.solo_cal_5b_cov is not None else {})
    n = 0
    for col in out:
        for rec in col.chars or []:
            if rec.admit or rec.provenance == "human" or rec.channel == "human":
                continue
            if rec.id in amap or (coord.get(rec.id) or "") not in ("", *facts.gap_chars):
                continue                  # 有整理本对位的格归别的通道
            m = mmap.get(rec.id)
            if m is None or not m.candidates:
                continue
            rt = rmap.get(rec.id)
            if canon is not None and rt:
                lt = max(m.candidates, key=lambda t: t[1])[0]
                if lt and rt != lt and canon(rt) == canon(lt):
                    rt = lt
            got = solo_cal_decide(cands=list(m.candidates), guard=m.guard, doubts=rec.doubts, tiers=tiers,
                                  skip=p.solo_cal_skip, group_chars=group_chars, near_form_chars=NEAR_FORM_CHARS,
                                  rare_top=rt, cov_5b=p.solo_cal_5b_cov, allow=p.solo_cal_allow)
            if got is None:
                continue
            ch, cov1, gap, how = got
            rec.admit, rec.channel, rec.provenance, rec.char = True, "match_solo_cal", "match_solo_cal", ch
            rec.doubts = []
            rec.evidence = {**rec.evidence, "no_glyph_lib": True,
                            "solo_cal": {"lib": ch, "cov": round(cov1, 4), "gap": gap, "by": how, "rare": rmap.get(rec.id)}}
            n += 1
    return n


#: `lead_5b` 允许的疑问（前缀）
_LEAD_5B_OK_DOUBTS = ("库 unsure", "上下文 margin 不足")


def lead_5b_decide(*, cands: list, rare: list, guard, doubts, cell_id: str, skip: str, are_variants,
                   gap_out: float, gap_in: float, lib_min: float,
                   ok_doubts: tuple = _LEAD_5B_OK_DOUBTS) -> tuple[str, float, str] | None:
    """`LaneParams.lead_5b` 的判据，纯函数。`cands`：库候选 [(字, cov)]；`rare`：5-b 候选 [(字, 分)]（按 5-b 原序，
    首位＝5-b 首选）。→ (放行字, 5-b 领先量, 档 "out"／"in") 或 None。"""
    if guard is not None or not cands or not rare:
        return None
    if cell_id and cell_id[-1].isalpha():
        return None                       # 拆分子格（001:162:2:17b）多是半字碎块
    if any(not (isinstance(d, str) and d.startswith(ok_doubts)) for d in (doubts or [])):
        return None
    ranked = sorted(cands, key=lambda t: -t[1])
    c = ranked[0][0]
    r0, s0 = rare[0][0], float(rare[0][1])
    if (not r0 or _F.is_gap(r0) or not _F.is_hanzi(r0) or not c or r0 == c
            or r0 in skip or c in skip or are_variants(r0, c)):
        return None
    lead = s0 - max((float(s) for d, s in rare[1:] if d != r0), default=0.0)
    lib = [d for d, _ in ranked]
    if r0 not in lib:
        return (r0, round(lead, 4), "out") if lead >= gap_out else None
    second = next((d for d in lib[1:] if d and d != c), None)
    if r0 == second and lead >= gap_in and float(dict(ranked)[r0]) >= lib_min:
        return r0, round(lead, 4), "in"
    return None


def _lead_5b_pass(p: "LaneParams", out: list, mmap: dict, amap: dict, rare, coord: dict[str, str], facts) -> int:
    """无参照格库与 5-b 不一致时听 5-b。→ 升级格数。见 `LaneParams.lead_5b`。"""
    if rare is None:
        return 0
    are_variants = facts.look_alike   # C 对也跳过（同规则 A）
    rlist = {r.id: [(x.char, x.score) for x in r.candidates] for cc in rare.columns for r in cc.chars if r.candidates}
    n = 0
    for col in out:
        for rec in col.chars or []:
            if rec.admit or rec.provenance == "human" or rec.channel == "human":
                continue
            if rec.id in amap or (coord.get(rec.id) or "") not in ("", *facts.gap_chars):
                continue
            m = mmap.get(rec.id)
            if m is None or not m.candidates or rec.id not in rlist:
                continue
            got = lead_5b_decide(cands=list(m.candidates), rare=rlist[rec.id], guard=m.guard, doubts=rec.doubts,
                                 cell_id=rec.id, skip=p.solo_cal_skip, are_variants=are_variants,
                                 gap_out=p.lead_5b_gap_out, gap_in=p.lead_5b_gap_in, lib_min=p.lead_5b_lib_min)
            if got is None:
                continue
            ch, lead, how = got
            lib_top = sorted(m.candidates, key=lambda t: -t[1])[0]
            rec.admit, rec.channel, rec.provenance, rec.char = True, "match_lead_5b", "match_lead_5b", ch
            rec.doubts = []
            rec.evidence = {**rec.evidence, "no_glyph_lib": True,
                            "lead_5b": {"rare": ch, "lead": lead, "by": how, "lib": lib_top[0],
                                        "lib_cov": round(float(lib_top[1]), 4)}}
            n += 1
    return n


