# 995ejelvk0 《欽定全唐文》清嘉慶二十一年揚州刻本（內府本）

| | |
|---|---|
| book-index 条目 | `Book/…/995ejelvk0-…json`；作品 Work `d59f2nqla48x`，一千卷首四卷 |
| 底本 | 清華大學圖書館藏，CADAL 扫描，Commons `Category:欽定全唐文`（`CADAL01022799`–`CADAL01023293` 的「卷N-N+1」件） |
| 页表 | R2 `995ejelvk0/<册>`；册名 01…，约 184 页/册，分册表见 ai-team／项目文件 A31/全唐文选本/分册表.md |
| 控制台 URL id | `995ejelvk0`（`workspace.yaml`，书 ID） |

2026-10-28 A31 开档。取代九月 `qtw-draft` 的旧登记（旧 06–10 册的页表被新册覆盖）。通用步骤见 ai-team `通用/新开一部书.md`。

## 这套扫描

- 每个 CADAL 件＝原装一册（两卷），首页书名签封面、末页封底；一页一半叶，约 3456×6493 灰度，无水印。
- cv 册＝相邻两个原装册（边界仍在书名签上）。封面、封底不入页表。
- 版式（九行二十二字、粗右下边框、双行小注）要单独量，不照搬殿本。

## 目录

| 路径 | 内容 | git |
|---|---|---|
| `data_full/<册>/` | 原图 `<页>.png`，R2 取 | 不进 |
| `products/`、`output/`、`cache/` | 产物、派生库 | 不进 |
| `code/` | 本书书级代码（Step3 行切分分叉：row_boundaries、jiazhu_split），版本 `k<N>`，见 `code/README.md` | 进 |

## 仓的来历

2026-10-30 起一部书一个仓：本仓根目录即工作区（`GUJI_WORKSPACE` 指向本仓根），原先在
`open-guji/guji-workspace` 的 `995ejelvk0-欽定全唐文清嘉慶二十一年揚州刻本內府本/` 搬来，内容不变。
册配置、字形库、人裁、参校语料在中心库（工作区 id `995ejelvk0`（书 ID；2026-10-30 由短 id `qtw` 改来）），搬仓不动它们：`guji db pull -w <本仓根>`。
字形库借库 `glyph_lib.borrow: [siku-zongmu]` 指的是中心库里的字形库，不是 git 仓；旧仓 `siku-zongmu-workspace` 已归档。
