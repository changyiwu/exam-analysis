# exam-analysis（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

## 專案簡介
分析 110~115 年（近 6 年）台灣國中教育會考數學科試題，統計單元頻率並產出應考策略報告與視覺化資訊圖表。

## 關鍵時程
- 試題分析與資訊圖表產出：2026-06-24（已完成）

## 目標與路線圖
- [x] 110~115 年會考數學試題逐題分類與統計分析（163 題）
- [x] 繪製淺色美學 16:9 資訊圖表 (1.試題分析, 2.整體策略, 3.C到B策略, 4.B到A策略)
- [x] 產出完整文字報告 analysis_report.md
- [x] 補回試題分類腳本 `scripts/classify_and_analyze.py`（重新逐題校對 163 題，可完整重跑）
- [x] 依重新校對的 163 題統計改寫 `analysis_report.md` 並重繪四張資訊圖表
- [ ] 擴充至 116 年試題
- [ ] 加入難度指數（P）與鑑別度指數（D）分析

## 資料夾結構

| 路徑 | 用途 | 進 repo |
| --- | --- | :---: |
| `.agents/` | Agent 相關配置（含專案技能 `skills/exam-analysis.md`） | ✓ |
| `input/` | 原始試題與答案 PDF | ✗ |
| `output/` | 分析成果：analysis_report.md、PNG / SVG 圖表 | ✗ |
| `scripts/` | **可重現**的分析與繪圖腳本（`classify_and_analyze.py`、`generate_infographics.py`） | ✓ |
| `scratch/` | 一次性暫存物，丟掉也無所謂 | ✗ |
| `README.md` | 專案說明文件 | ✓ |
| `AGENTS.md` | 專案藍圖（本檔） | ✓ |
| `handoff.md` | 交接檔（每次收工必更新；含本機路徑不進 repo） | ✗ |

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `AGENTS.md`＋`handoff.md` | 每個 session |
| L2 | GitHub | [changyiwu/exam-analysis](https://github.com/changyiwu/exam-analysis) | 指定時 |
| L3 | Obsidian | `exam-analysis/專案工作流程.md` | 有需要時 |

## 三個檔案的職責（依「時效性」分家，不是依「詳細程度」）

| 檔案 | 時效 | 寫入方式 | 放什麼 |
|------|------|---------|--------|
| `handoff.md` | **只對下一個 session 有效**，過期即丟 | 每次收工整份重寫 | 做到哪、下一步、**這次**的暫時 workaround |
| `AGENTS.md`（本檔） | **長期有效**，每個 session 都適用 | 只有規則本身變了才改 | 目標、路線圖、常設規則、結構 |
| Obsidian／`git log` | **歷史**：發生過什麼、為什麼 | 只增不刪 | 決策紀錄、踩坑完整版、逐次進度 |

驗收標準：**`handoff.md` 整份刪掉，不應損失任何長期資訊**——會的話代表該升級進本檔卻沒升級。

**本檔不要出現的東西**：❌ `## 最近進度`／逐次工作紀錄、❌ 決策理由與踩坑完整版。歷史寫 L3 筆記的〈🗓️ 最近更動紀錄〉〈🧠 決策紀錄〉〈🕳️ 踩坑筆記〉；踩過的坑只把**結論**收斂成一條祈使句寫進〈工作約定〉，原因留 L3。

## 工作約定
- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 能重現成果的腳本一律放 `scripts/` 並進版控；`scratch/` 已 gitignore，只放丟掉也無所謂的暫存物
- 腳本內禁止寫死使用者家目錄或 Agent 暫存路徑，一律用 `Path(__file__)` 推導專案根目錄
- 圖表與報告的數字一律以 `scripts/classify_and_analyze.py` 的輸出為準；要改分類就改 `OVERRIDES` 後重跑兩支腳本，不要手動改報告或圖表裡的數字
- 所有回應與文件使用繁體中文

## 安全規範

- **隱私至上**：本專案涉及試題與成績，**嚴禁將學生的真實姓名、真實個資、學號**或任何敏感個資寫入程式碼或 Markdown 檔案。需要測試資料時一律使用去識別化的虛擬資料
- **金鑰防護**：嚴禁將任何 API Key、Token、密碼等敏感憑證 commit 至 GitHub
- 本專案為公開 repo `changyiwu/exam-analysis`，上述規範沒有例外

## 視覺與設計美學

- **拒絕陽春**：網頁介面必須具備現代設計感，視覺美學至上
- **色彩系統**：使用和諧且具層次感的色彩調配（如 HSL），避免純紅、純綠、純藍等預設顏色；預設支援暗色模式與玻璃擬態（Glassmorphism）
- **字型與排版**：引進現代字型（如 Inter、Outfit 等 Google Fonts），拒絕瀏覽器預設字型
- **動態效果**：加入平滑的 Hover 效果與微動畫（Micro-animations）增強互動感
- **無佔位符**：不使用 placeholder 圖片或虛假字樣；有需要時應以圖片生成工具產生對應素材
- **PNG 的 emoji**：只用在 24px 以上的面板標題，20px 左右的小標籤不放 emoji（會糊成一團）；文字繪製統一以中文字型基線對齊，避免 emoji 浮高
