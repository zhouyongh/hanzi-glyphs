# 技术规格 · hanzi-glyphs core

**版本 1.0.0**。本文件是字段定义、质量分级与验收发布的技术规格；面向使用者的说明见
[README.md](README.md)。本包为自包含的汉字字形资产库：13 个标准书体层、183,717 件主字形 SVG，
以自然键 `(layer, path)` 标识，克隆或解压后即可独立使用与验收，不依赖任何外部仓库。

**产品边界**：本库是研究型汉字字形 SVG 数据集，不是可直接安装或用于排版的字体。183,717 件中
140,050 件（76.23%）尚无合格质量证据，且全库未经全面人工或古文字学审定；学术引用前请按逐件
`quality`、`source`、`source_url` 与 `license` 字段复核。

```
hanzi-glyphs-core-1.0.0/
  glyphs.csv          # 核心资产表（8 列，183,717 行）
  quality.csv         # 质量伴随表（4 列，183,717 行）
  glyphs/             # 13 层主字形 SVG（183,717 件，仅各层直接子文件）
    oracle-bone/ … hei-hant-hk/
  LICENSES.md         # 许可范围、逐来源署名、CC0/CC-BY/OFL 全文
  manifest.json       # 版本、件数、质量分布、两表与资产哈希（完整性清单）
  README.md           # 使用说明（发布首页）
  SPEC.md             # 本文件（技术规格）
  scripts/
    validate_core.py  # 自包含验收（只用本文件夹的表与资产）
    make_release.py   # 打发布归档（zip + sha256）
    build_viewer.py   # 由两表生成浏览器索引
  viewer/
    index.html        # 自包含字形浏览器（单文件应用）
    data/             # 逐层搜索索引 + 出处详情 + meta（由 build_viewer.py 生成）
```

## 1. 核心资产表 `glyphs.csv`

一行一件 SVG 字形资产。UTF-8，首行表头，空值用空字段（不写 `null`/`None`/`N/A`）。

| 列 | 说明 |
|---|---|
| `layer` | 13 个标准书体层之一（见下表） |
| `path` | 层内相对路径，与 `layer` 构成自然键；完整位置 = `glyphs/<layer>/<path>` |
| `modern_char` | 对应现代汉字；无可靠对应为空 |
| `unicode` | `modern_char` 的 6 位大写十六进制码位；按字符串处理；与 `modern_char` 同有或同空 |
| `source` | 稳定来源代码（见 §4），非显示名 |
| `source_ref` | 来源内部条目标识，不透明字符串 |
| `source_url` | 来源定位 URL |
| `license` | 该件许可：`CC0-1.0` / `CC-BY-4.0` / `OFL-1.1`（逐件取值，不可按层推断） |

**13 个标准层键**（中文仅作显示别名，不另建机器键）：

| 键 | 书体 | 键 | 书体 |
|---|---|---|---|
| `oracle-bone` | 甲骨文 | `regular` | 楷书 |
| `seal` | 篆书 | `running` | 行书 |
| `bronze` | 金文 | `cursive` | 草书 |
| `clerical` | 隶书 | `song-hans` | 宋体（简） |
| `chu` | 楚文字 | `song-hant` | 宋体（繁） |
| `guwen` | 傳抄古文字 | `hei-hant-hk` | 黑体（港） |
| `qin` | 秦系简牘 | | |

约束（`scripts/validate_core.py` 自包含校验）：

- `(layer, path)` 唯一；每行 `path` 在 `glyphs/` 存在；无未登记 SVG、无多余、无子目录。
- `layer` 只出现上述 13 键。
- `unicode` 非空时匹配 `^[0-9A-F]{6}$`；`modern_char` 非空时恰好一个字符且码位一致。
- `source` 属受控代码集、`license` 属三值集；`source_ref`、`source_url`、`license` 全部非空。
- `path` 以 `/` 分隔、不以 `/` 开头、禁止绝对路径与 `.`/`..` 段、大小写敏感、存原始相对路径
  不存 URL 编码；为层直接子文件。完整位置由 `glyphs/<layer>/<path>` 计算。

**关于同字节重复（有意保留，不去重）**：包内约 11%（20,339 份额外副本）的 SVG 字节完全相同
但路径不同。这是**有意登记**而非采集冗余：同一个字形形式（同一 `source_ref` / `source_url`）
登记到多个现代字/异体字下，例如甲骨 `41_EBC2.svg` 同见于 `0001.svg=㐁` 与 `10040.svg=𠀬`；
字体层也有同形多 Unicode 的合理情况。核心表的行单位是「(现代字, 字形形式) 登记」，不是
「唯一字形图」，故不按字节去重——去重会抹掉异体字覆盖。字际共享关系属身份/演进层，不在本表表达。

## 2. 质量伴随表 `quality.csv`

`layer,path,quality,note`。`(layer, path)` 与核心表一一对应、完整覆盖；缺行属交付错误
（不等于 `unverified`）。质量表可独立更新，不改写核心表。

`quality` 只记**证据强度**，不按来源类别或层名批量推定：

| 值 | 含义 | 件数 |
|---|---|---:|
| `byte-verified` | 当前 SVG 的 `sha256` 与上游 `source_sha256` 相等（逐字节对回上游 SVG） | 13,006 |
| `metric-passed` | 描摹件 `trace_iou ≥ 0.97`（弱指标达标，**非人工核验**） | 18,387 |
| `watermark-stripped` | 上游件含近白色角标标记（汉典「ZDIC.NET」「漢典」），本包仅删除该标记元素，其余字节与上游一致 | 12,274 |
| `unverified` | 无上述三类合格证据（字体提取件、拓片反转、哈希不等的受控修改件等） | 140,050 |
| `failed` | 抽检明确判失败（本包已移除，不留失败件） | 0 |
| **合计** | | **183,717** |

诚实标注：`unverified` 占多数（76.23%），表示「尚无合格证据」，不代表字形有误；`metric-passed`
是机器指标达标，不等于人工复核。消费者应据此自行判断引用风险。

**角标剔除（`watermark-stripped` 的来由）**：汉典「傳抄」来源的上游 SVG 在画面四角带有
近白色角标（拉丁字样 `ZDIC.NET` 或竖排「漢典」），白底上几乎不可见，暗底或反相印刷则显现。
本包对这类 12,274 件删除全部近白填充元素（逐字节切除，其余内容不变），并按「对上游件施加
同一删除规则后 `sha256` 相等」判定为 `watermark-stripped`。`scripts/validate_core.py`
另设守卫：任一资产若仍含近白填充即判失败。

## 3. 失败件处置

本包**不含失败件**。抽检判失败的 32 件转换件（拓片位图自动转换/描摹失真的矢量 SVG）
已从核心表与资产中移除：失真件不作为可引用字形交付。其拓片原件作为证据留在仓库侧，
不在本包；如需引用这些字的原始拓片，另行取得证据。

`quality.csv` 保留 `note` 列以稳定表结构，当前全部为空。`failed` 仍为受控质量值之一，
但本包计数为 0；验收脚本保留失败件 note 语法守卫（期望拆分 0/0/0）。

## 4. 来源代码 `source`

稳定、受控，不随显示名漂移。当前 21 个：

| 代码 | 上游数据集 |
|---|---|
| `zdic-jiaguwen` / `zdic-jinwen` / `zdic-zhuanshu` / `zdic-lishu` / `zdic-qinwenzi` / `zdic-chuwenzi` / `zdic-chuanchao` | 汉典 zdic.net 各字形栏 |
| `xxt-jiaguwen` / `xxt-jinwen` / `xxt-xiaozhuan` / `xxt-lishu` / `xxt-chuwenzi` / `xxt-chuanchao` / `xxt-qinwenzi` | 小学堂（中研院）各字形资料库 |
| `jgw-parametric-0.3` | Oracle Bone Glyphs: Parametric Vector Dataset (v0.3) |
| `font-noto-serif-sc` / `font-noto-serif-tc` / `font-chiron-hei-hk` / `font-liujianmaocao` / `font-mashanzheng` / `font-zhimangxing` | OFL 字体轮廓提取件；`source_url` 指向固定提交下的上游字体文件（见 LICENSES.md §4） |

## 5. 许可与引用

逐件许可见 `glyphs.csv` 的 `license` 列；范围、署名与三部许可全文见 **`LICENSES.md`**。

- **CC0-1.0**（汉典/小学堂，85,167 件）：无署名义务。
- **CC-BY-4.0**（JGW，1,201 件）：引用须附 `LICENSES.md` §2 的署名文字。
- **OFL-1.1**（六个字体层，97,349 件）：分发须随附 `LICENSES.md`（含版权行与许可全文），
  不得改标为 CC0/CC-BY，不得单独出售字体本身。

引用一件字形时，建议给出：`layer` + `path`（自然键）、`source` + `source_ref` + `source_url`
（出处）、`license`（许可），CC-BY 件另附署名。

## 6. 版本与完整性

`manifest.json` 记录版本、总行数、逐层件数、质量分布，以及完整性哈希：

- `sha256.glyphs.csv` / `sha256.quality.csv`：两张表的字节哈希。
- `assets_sha256`：全部 183,717 件 SVG 的聚合哈希；`assets_count` 为资产件数。
  复算方法：对每件取文件 `sha256`，按 `<layer>/<path>` 排序，拼成 UTF-8 行
  `<layer>/<path>\t<file_sha256>`、以 `\n` 连接（末尾无换行），再取 `sha256`。

消费者据此 pin 住版本并校验两表与资产字节未被改动；资产结构（路径解析、逐层件数、
无多余无子目录）由 `scripts/validate_core.py` 校验。

## 7. 验收与发布

```bash
python scripts/validate_core.py   # 自包含验收
python scripts/make_release.py    # 打发布归档
```

`make_release.py` 在**上级目录**生成 `hanzi-glyphs-core-<版本>.zip` 与同名 `.sha256`
校验和；归档含本包全部文件，固定时间戳、排序条目，相同输入复算逐字节一致。
校验下载件：`sha256sum -c hanzi-glyphs-core-<版本>.zip.sha256`。

验收校验内容：两表表头与行数、键唯一、13 层键、资产逐行解析与逐层件数、unicode/字符一致、
来源/许可受控与非空、路径语法、质量键一一对应与计数、失败件 note 语法与拆分。
证据级复核（哈希相等、`trace_iou`、JGW 回填）与拓片目标存在性不在本文件夹范围内。

## 8. 字形浏览器

`viewer/index.html` 是一个自包含的单文件浏览器，只读本包的索引与 `glyphs/` 资产，
不依赖任何外部仓库或 CDN。因浏览器安全策略限制 `file://` 下的本地请求，需经本地 HTTP 打开。
服务必须在**包根目录**（同时包含 `glyphs/` 与 `viewer/` 的那一层）启动，而非 `viewer/` 目录：

```bash
python -m http.server 8000     # 于包根目录执行
# 浏览器访问 http://127.0.0.1:8000/viewer/index.html
```

功能与实现要点：

- 搜索现代字 / 码位 / 路径，可按书体层与质量（`byte-verified`/`metric-passed`/`unverified`）过滤。
- 中英文切换：中文态书体层显示甲骨文、金文等中文别名；英文态全页英文，书体层显示
  `oracle-bone`、`seal` 等机器键。选择记忆于本地。
- 逐层懒加载搜索索引；出处详情（`source`/`source_ref`/`source_url`）点开某件时才按层加载。
- 虚拟滚动网格：即使整层数万件，DOM 中只保留可视窗口的单元；SVG 按需读取、缓存并复用节点。
- 点开一件显示自然键 `(layer, path)`（可复制）、unicode、quality、license、文件链接与完整出处。
- 启动自检：若字形基址不可达（服务根目录错误）或处于 `file://`，页首常驻提示说明原因与正确启动方式。
- 缺字显示「未能读取」表示本地文件读取失败，不表示该字形是空的。

索引数据由两表派生，改动 `glyphs.csv`/`quality.csv` 后重新生成：

```bash
python scripts/build_viewer.py
```