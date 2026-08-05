# exam-analysis｜國中教育會考數學科試題分析

分析台灣國中教育會考數學科 **110～115 年（近 6 年）** 共 12 份試卷、**163 道試題**，統計各單元出題頻率，產出應考策略報告與 16:9 資訊圖表。

## 這個專案做了什麼

1. 讀取 6 個年度的試題本與答案本 PDF（`input/`）
2. 以關鍵字初篩 + 人工校對對照表，將 163 題逐題歸入數學單元
   （PDF 文字抽取常遺失根號、分數線、指數等符號，所以最後一哩一定要人工校對）
3. 統計單元出現次數與占比，排出考點排行榜
4. 依「C 到 B」「B 到 A」兩種晉級目標，分別擬定應考策略
5. 用 Python 同時產出 PNG（簡報用）與 SVG（網頁自適應用）雙軌資訊圖表

## 產出成果

成果全部在 `output/`（**不進版控**，只走雲端硬碟同步）：

| 檔案 | 內容 |
| --- | --- |
| `classification.csv` | 逐題分類明細（年度、題號、單元、初篩是否命中） |
| `unit_frequency.md` | 單元頻率排行榜與各年度分佈表 |
| `analysis_report.md` | 完整文字報告：單元頻率排行榜、考點拆解、應考策略 |
| `1_past_exam_analysis.png` / `.svg` | 歷屆試題單元頻率分析 |
| `2_overall_strategy.png` / `.svg` | 整體應考策略 |
| `3_strategy_c_to_b.png` / `.svg` | C 到 B 晉級策略 |
| `4_strategy_b_to_a.png` / `.svg` | B 到 A 晉級策略 |

圖表規格：橫式 16:9（1920×1080）、淺色高對比配色。SVG 不寫死寬高，改用
`viewBox` + `width="100%"`，用瀏覽器直接開啟就會自適應縮放，不會出現橫向捲軸。

## 技術底座

- **Python 3** + **Pillow** — 繪製 PNG
- 自製 `DualCanvas` 類別 — 一次呼叫同時輸出 Pillow 點陣圖與 SVG 字串，兩軌保證一致
- 依賴以 [PEP 723](https://peps.python.org/pep-0723/) inline metadata 宣告在腳本開頭，可直接用 `uv run` 執行

## 重新產生

逐題分類與頻率統計：

```bash
uv run scripts/classify_and_analyze.py
```

資訊圖表：

```bash
uv run scripts/generate_infographics.py
```

沒有 uv 的話，先 `pip install pypdf pillow` 再用 `python` 執行同樣的路徑。

腳本以自身位置推導專案根目錄，在任何電腦、任何工作目錄下執行都會寫進本專案的
`output/`。中文字型會依序尋找微軟正黑體 → 思源黑體 → PingFang，找不到會出示警告。

## 資料夾結構

| 路徑 | 用途 | 版控 |
| --- | --- | :---: |
| `input/` | 原始試題與答案 PDF | ✗ |
| `output/` | 報告與資訊圖表 | ✗ |
| `scripts/` | 可重現分析與繪圖的腳本 | ✓ |
| `scratch/` | 一次性暫存物，丟掉也無所謂 | ✗ |
| `agents.md` | 跨 Agent 專案藍圖 | ✓ |
| `handoff.md` | 交接檔（含本機路徑，不進 repo） | ✗ |

## 專案規範與安全

本專案為公開 repo，嚴格遵守 [agents.md](agents.md)：

- 嚴禁將學生真實姓名、真實個資、學號寫入任何檔案；測試一律用去識別化虛擬資料
- 嚴禁 commit 任何 API Key、Token、密碼
- 原始試題 PDF 與所有產出不進 repo，避免大型二進位檔膨脹倉庫
