# hanzi-glyphs · 汉字字形 SVG 资产库

13 种书体、**183,717 件**单字轮廓 SVG，覆盖 **33,704 个**现代汉字。每件字形都带出处与许可，
可直接用于古文字研究、字形展示、教学与字体设计参考。

**在线浏览**：<https://zhouyongh.github.io/hanzi-glyphs/viewer/index.html>
不用下载，打开就能先看看各书体的字形长什么样。

**版本 1.0.0** · 自包含：克隆即用，不依赖任何外部仓库或网络服务。

## 书体层

| 层键 | 书体 | 件数 |
|---|---|---:|
| `oracle-bone` | 甲骨文 | 14,448 |
| `seal` | 篆书 | 10,610 |
| `bronze` | 金文 | 11,689 |
| `clerical` | 隶书 | 12,584 |
| `chu` | 楚文字 | 12,894 |
| `guwen` | 傳抄古文字 | 20,435 |
| `qin` | 秦系简牘 | 3,708 |
| `regular` | 楷书 | 6,763 |
| `running` | 行书 | 6,763 |
| `cursive` | 草书 | 6,763 |
| `song-hans` | 宋体（简） | 27,797 |
| `song-hant` | 宋体（繁） | 17,665 |
| `hei-hant-hk` | 黑体（港） | 31,598 |

## 快速上手

**1. 取得本库**

克隆仓库（检出后约 0.9 GB，含全部 SVG），或在仓库页面选 **Code → Download ZIP**：

```bash
git clone https://github.com/zhouyongh/hanzi-glyphs.git
cd hanzi-glyphs
```

**2. 浏览字形**

在线浏览（与包内 `viewer/` 相同）：<https://zhouyongh.github.io/hanzi-glyphs/viewer/index.html>

本地浏览需经 HTTP 打开（`file://` 下浏览器会拦截请求），在仓库目录内启动：

```bash
python -m http.server 8000
# 打开 http://127.0.0.1:8000/viewer/index.html
```

浏览器支持按现代字、码位或路径搜索，按书体层与质量筛选，中英文切换；点开任一字形可看出处与许可。

**3. 按字取 SVG**

在 `glyphs.csv` 中按 `modern_char` 或 `unicode` 查到该件的 `layer` 与 `path`，
文件即位于 `glyphs/<layer>/<path>`。

```python
import csv
from pathlib import Path

root = Path(".")
with (root / "glyphs.csv").open(encoding="utf-8-sig", newline="") as fh:
    rows = list(csv.DictReader(fh))

hit = next(r for r in rows if r["modern_char"] == "永" and r["layer"] == "regular")
svg = (root / "glyphs" / hit["layer"] / hit["path"]).read_text(encoding="utf-8")
print(hit["path"], hit["license"])      # 006C38.svg OFL-1.1
```

网页端可直接用浏览器的精简索引（行格式 `[path, 现代字, 码位, quality, license]`）：

```js
// 在模块或 async 函数中运行；页面需经 HTTP 打开（file:// 下 fetch 被浏览器拦截）
const { rows } = await fetch("viewer/data/layer-regular.json").then(r => r.json());
const hit = rows.find(r => r[1] === "永");
const svg = await fetch(`glyphs/regular/${hit[0]}`).then(r => r.text());
```

## 里面有什么

```
glyphs.csv        核心资产表：一行一件字形（layer, path, 现代字, 码位, 出处, 许可）
quality.csv       质量伴随表：逐件证据强度
glyphs/           13 个书体层的 SVG 文件
viewer/           字形浏览器（单文件网页 + 索引）
LICENSES.md       许可范围、逐来源署名、三部许可全文
manifest.json     版本、件数与完整性哈希
scripts/          自包含验收与发布打包
SPEC.md           技术规格：字段定义、质量分级、验收与发布
```

## 字形文件

- 每件是**一个字的轮廓 SVG**，自带 `viewBox`（尺寸随来源不同），按 `viewBox` 渲染即可；
  轮廓为单色，可按需改色。
- 同一字形形式可能登记在多个现代字（异体字）下，因此文件数多于唯一字形图数，这是有意保留的覆盖。
- 6,280 件古文字没有可靠的现代字对应（`modern_char` 与 `unicode` 为空），只能按路径取用。

## 许可与引用

逐件许可以 `glyphs.csv` 的 `license` 列为准，不可按层推断：

| 许可 | 件数 | 义务 |
|---|---:|---|
| CC0-1.0 | 85,167 | 无署名义务 |
| CC-BY-4.0 | 1,201 | 引用须附署名（见 `LICENSES.md` §2） |
| OFL-1.1 | 97,349 | 分发须随附 `LICENSES.md`；不得改标许可，不得单独出售字体本身 |

引用一件字形时，建议给出：`layer` + `path`、`source` + `source_ref` + `source_url`、`license`。
许可全文、逐来源署名与版权行见 **[LICENSES.md](LICENSES.md)**。

## 使用前请知悉

- 本库是**研究型字形数据集，不是可安装或用于排版的字体**。
- 全库未经全面人工或古文字学审定；逐件 `quality` 字段标注证据强度，其中 140,050 件（76.23%）
  尚无合格证据。学术引用前请按 `quality`、`source`、`source_url` 复核。
- 字段定义、质量分级与验收细节见 **[SPEC.md](SPEC.md)**。

## 校验

```bash
python scripts/validate_core.py    # 自包含验收：表、资产、哈希与清单
```

`manifest.json` 记录版本、逐层件数、质量分布，以及两张表与全部资产的哈希，可据此确认内容未被改动。

## 致谢

这些字形不是我们画的，是很多人一笔一笔留下来的：

- **汉典（zdic.net）**：把甲骨、金文、篆书、隶书、楚文字、傳抄古文字、秦系简牘逐字整理成矢量字形，
  并以 CC0 释出。本库的古文字形大多来自这里。
- **中央研究院「小學堂」汉字字形资料库**：公开各分辨率「字形圖片」与字形屬性資訊，并以 CC0 1.0 释出。
  本库古文字七层都收了它的字形；上游原件是位图，本库的 SVG 是自动描摹的派生件。
- **Li Qing-sheng、Bian Yu-lin**（浙江传媒学院）：甲骨文字形的参数化矢量数据集
  *Oracle Bone Glyphs: Parametric Vector Dataset*（v0.3，1,203 件），以 CC BY 4.0 公开；
  本库甲骨文层收录其中 1,201 件。
- **Ma Shan Zheng、Zhi Mang Xing、Liu Jian Mao Cao** 三个书法字体项目（各依其书法家的手迹），
  **Google Fonts / Adobe**（Noto Serif SC、TC），**Chiron Fonts**（Chiron Hei HK）：
  楷、行、草、宋、黑六层的轮廓来源。
- **郭沫若**主编、**胡厚宣**总编辑的《甲骨文合集》，**中国社会科学院考古研究所**编的《殷周金文集成》，
  **容庚**编著（张振林、马国权摹补）的《金文编》，**许慎**的《说文解字》，
  **汉语大字典字形组**编的《秦汉魏晋篆隶字形表》，**罗福颐**编的《汉印文字征》，
  **滕壬生**的《楚系简帛文字编》，**汤馀惠**主编的《战国文字编》，**方勇**的《秦简牍文字编》，
  **徐在国**编的《传抄古文字编》，**何琳仪**的《战国古文字典》，**张守中**的《睡虎地秦简文字编》：
  古文字各层的字形，摹本多出自这些书。
- 历代**拓本与摹本**的制作者，《说文解字》两千年来传抄、刊刻的人——他们大多没有留下名字。
- **Unicode Consortium**（篆书区块与 `SealSources.txt`）、**OpenCC**（篆书反查表，
  用于核对篆书码位的取舍）、**fontTools**（六个字体层的轮廓提取）：码位与工具。

这些出处我们无法一一联系。如有字形违反相关规定，或存在其他不妥之处，请联系我们，我们会将其删除，并对此致歉。

我们能做的，是把每一个字形的来路记清楚。
