# cvdevpg206414f9efed-c--g-51cecc-qtw04-revoke9

## 摘要

（存包时没给 `--summary`）

**各步运行**（产物 manifest，最近一轮先后）：

| 步 | 页 | cv | 最后一轮起 → 止（洛杉矶） | 耗时合计 |
|---|---|---|---|---|
| page_survey | 204 | 0.5.31 | 10-28 04:35 → 10-28 04:35 | 0.0 分 |
| invert_detect | 204 | 0.5.31 | 10-28 04:35 → 10-28 04:37 | 1.8 分 |
| border_detect | 204 | 0.5.31 | 10-28 04:37 → 10-28 04:42 | 17.7 分 |
| border_detect_gate | 204 | 0.5.31 | 10-28 04:42 → 10-28 04:46 | 18.5 分 |
| seal_detect | 204 | 0.5.31 | 10-28 04:46 → 10-28 04:48 | 2.0 分 |
| column_warp | 204 | 0.5.31 | 10-28 04:48 → 10-28 04:51 | 12.1 分 |
| column_gate | 204 | dev+g38746280cc06 | 10-30 15:33 → 10-30 15:34 | 1.1 分 |
| row_segment | 204 | dev+g38746280cc06 | 10-30 20:50 → 10-30 21:26 | 142.4 分 |
| row_segment_gate | 204 | dev+g38746280cc06 | 10-30 15:56 → 10-30 21:26 | 0.4 分 |
| cell_shrink | 204 | dev+g38746280cc06 | 10-30 16:51 → 10-30 21:26 | 8.5 分 |
| glyph_match | 204 | dev+g38746280cc06 | 10-30 15:41 → 10-30 21:26 | 7.4 分 |
| rare_candidates | 204 | dev+g38746280cc06 | 10-30 15:50 → 10-30 21:26 | 1.2 分 |
| align_ref | 204 | dev+g38746280cc06 | 10-30 21:26 → 10-30 21:26 | 0.4 分 |
| context_decide | 204 | dev+g38746280cc06 | 10-30 21:26 → 10-30 21:27 | 0.6 分 |
| seed_admit | 204 | dev+g206414f9efed | 10-31 15:10 → 10-31 15:13 | 7.9 分 |

## 基本信息

- 册：04
- 存包：2026-10-31T22:14:05Z；说明：册04 撤回 9 条日巳曰人裁后重落 seed_admit；放行 97.5%；56 格人裁绑丢退回待审
- 基线（存包时该册的 main）：`cv0.5.31-c--g-e3b0c4-qtw-first`
- 包：`products/995ejelvk0/04/cvdevpg206414f9efed-c--g-51cecc-qtw04-revoke9`（3077 个文件，12.7 MB）；取回 `guji products pack fetch 04 --label cvdevpg206414f9efed-c--g-51cecc-qtw04-revoke9 --to <目录>`

## 版本

| cv | cv commit | 语料库 | 底库 | 字形库钉号 | 人裁指纹 | 中心库 rev（seed_admit 跑时） |
|---|---|---|---|---|---|---|
| dev+g206414f9efed | 206414f9efed | — | — | — | h1:727:51ceccf864ba45d7 | 995ejelvk0@main:383597（204 页） |

## 册配置（存包时）

```yaml
# 《欽定全唐文》嘉慶內府本 第 04 册＝清華 CADAL 卷3-4＋卷5-6 两件（去封面封底，共 204 页），一页一半叶。
# 页序＝物理叶序；页表 R2 995ejelvk0/04。
id: "04"
title: 欽定全唐文（卷3–6）
edition: keben
raw_dir: data_full/04
raw_pattern: "{page}.png"
# 每半叶九行、每行 22 字（叶100 右列实数 22），大字正文夹双行小注
expected_cols: 9
chars_per_line: 22
period_prior: 205
frame_bar_strategy: border_line
dev_set: [1, 2, 20, 50, 51, 100, 101, 150, 200, 204]

# 参校语料：Kanripo KR4h0168（NKFB 嘉慶本逐列錄入，一行＝一列，CC BY-SA 4.0）；book-text Work d59f2nqla48x
references:
  - file: qtw_kanripo_grid.txt
    quality: best
    label: Kanripo KR4h0168
    line_is_column: true

# Step7 标准开关（runbook S3）
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

