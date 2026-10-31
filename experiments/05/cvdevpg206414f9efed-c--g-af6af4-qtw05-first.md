# cvdevpg206414f9efed-c--g-af6af4-qtw05-first

## 摘要

（存包时没给 `--summary`）

**各步运行**（产物 manifest，最近一轮先后）：

| 步 | 页 | cv | 最后一轮起 → 止（洛杉矶） | 耗时合计 |
|---|---|---|---|---|
| page_survey | 222 | dev+g206414f9efed | 10-31 11:35 → 10-31 11:35 | 0.0 分 |
| invert_detect | 222 | dev+g206414f9efed | 10-31 11:35 → 10-31 11:37 | 1.9 分 |
| border_detect | 222 | dev+g206414f9efed | 10-31 11:37 → 10-31 11:45 | 32.7 分 |
| border_detect_gate | 222 | dev+g206414f9efed | 10-31 11:45 → 10-31 11:56 | 43.6 分 |
| seal_detect | 222 | dev+g206414f9efed | 10-31 11:56 → 10-31 11:58 | 1.9 分 |
| column_warp | 222 | dev+g206414f9efed | 10-31 11:58 → 10-31 12:02 | 14.9 分 |
| column_gate | 222 | dev+g206414f9efed | 10-31 12:02 → 10-31 12:02 | 0.7 分 |
| row_segment | 222 | dev+g206414f9efed | 10-31 12:13 → 10-31 13:00 | 184.9 分 |
| row_segment_gate | 222 | dev+g206414f9efed | 10-31 12:07 → 10-31 13:00 | 0.3 分 |
| cell_shrink | 222 | dev+g206414f9efed | 10-31 12:07 → 10-31 13:02 | 8.7 分 |
| glyph_match | 222 | dev+g206414f9efed | 10-31 12:11 → 10-31 13:11 | 32.4 分 |
| rare_candidates | 222 | dev+g206414f9efed | 10-31 13:11 → 10-31 13:13 | 6.9 分 |
| align_ref | 222 | dev+g206414f9efed | 10-31 13:13 → 10-31 13:13 | 0.4 分 |
| context_decide | 222 | dev+g206414f9efed | 10-31 13:13 → 10-31 13:14 | 0.8 分 |
| seed_admit | 222 | dev+g206414f9efed | 10-31 13:14 → 10-31 13:16 | 5.7 分 |

## 基本信息

- 册：05
- 存包：2026-10-31T20:51:46Z；说明：全唐文册05首跑（卷7-10，222页）：格距205、Kanripo钉位194页、目录页参照21页、格位表；放行96.0%
- 基线（存包时该册的 main）：`cv0.5.31-c--g-e3b0c4-qtw-first`
- 包：`products/995ejelvk0/05/cvdevpg206414f9efed-c--g-af6af4-qtw05-first`（3347 个文件，11.4 MB）；取回 `guji products pack fetch 05 --label cvdevpg206414f9efed-c--g-af6af4-qtw05-first --to <目录>`

## 版本

| cv | cv commit | 语料库 | 底库 | 字形库钉号 | 人裁指纹 | 中心库 rev（seed_admit 跑时） |
|---|---|---|---|---|---|---|
| dev+g206414f9efed | 206414f9efed | — | — | — | h1:343:af6af42db0384b79 | 995ejelvk0@main:376972（222 页） |

## 册配置（存包时）

```yaml
# 《欽定全唐文》嘉慶內府本 第 05 册＝清華 CADAL 卷7-8＋卷9-10（2 件，去封面封底，共 222 页），一页一半叶。
# 页序＝物理叶序；页表 R2 995ejelvk0/05。第二先行册（用户 2026-10-31 定），配置照册 04 实测。
id: "05"
title: 欽定全唐文（卷7–10）
edition: keben
raw_dir: data_full/05
raw_pattern: "{page}.png"
# 每半叶九行、每行 22 字，大字正文夹双行小注（册 04 实测）
expected_cols: 9
chars_per_line: 22
period_prior: 205        # 册 04 实测真格距（自相关会估成 159）
frame_bar_strategy: border_line
dev_set: [1, 2, 20, 50, 51, 100, 101, 150, 200, 222]

references:
  - file: qtw_kanripo_grid.txt
    quality: best
    label: Kanripo KR4h0168
    line_is_column: true

iron_gate: true
params:
  row_segment:
    layout_prior: corpus/qtw_layout.jsonl
  align_ref:
    page_pins: page_pins.jsonl
  seed_admit:
    ji_yi_si_review: true
    ji_yi_si_ctx_rule: true
    rare_ref: true
    context_guard_diff: true
    context_guard_ref_blank: true
    context_guard_ref_prefer: true
    shadow_veto: true
    shadow_conf: 0.8
    lane_witness3: true
    lane_coord: true
    lane_seal: true
```

## 前后对比

（存包时没给 `--report <diff 目录>`）

## 记事

