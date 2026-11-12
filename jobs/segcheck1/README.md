# segcheck1：全唐文 016–075 整书切分体检（11-12 PST）

Sheldon 11-12：「整体看看切分 尤其用新的切分错误检测办法」「不要后台跑 提交任务单」。

- 60 单，kind=command，只读、不出包（output.pack=false）：取各册最新包（`products pack fetch --label`）→ `cache warm` → `guji seg check <册> --job`。
- cv 钉 dev ec3e7e1（含 #1447 seg_screen 判据）。
- **前提**：执行机跟 guji-manager main。`seg check`（#527/#529）与任务单收 `seg`、`--job` 输出（#535）都要先发到 main，否则 spec 校验会拒（run 不收 seg）。
- 结果在每单「run3」输出尾巴：要看的列清单在前、处置计数与结论压尾。
- 各册包名取自 11-12 `guji products pack list` 最新一个；031–075 下一轮重跑后若要复查，按新包重出单。
