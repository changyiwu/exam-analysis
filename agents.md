# exam-analysis（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

## 專案簡介
分析 110~115 年（近 6 年）台灣國中教育會考數學科試題，統計單元頻率並產出應考策略報告與視覺化資訊圖表。

## 關鍵時程
- 試題分析與資訊圖表產出：2026-06-24（已完成）

## 目標與路線圖
- [x] 110~115 年會考數學試題 162 題分類與統計分析
- [x] 繪製淺色美學 16:9 資訊圖表 (1.試題分析, 2.整體策略, 3.C到B策略, 4.B到A策略)
- [x] 產出完整文字報告 analysis_report.md
- [ ] 依據新需求進行下一階段分析擴充

## 資料夾結構
- `.agents/`：Agent 相關配置
- `input/`：輸入原始數據與試題資料
- `output/`：分析成果與視覺化圖表產出（含 analysis_report.md、PNG / SVG 圖表）
- `scratch/`：分析與繪圖腳本（classify_and_analyze.py, generate_infographics.py）
- `ANTIGRAVITY.md`：專案規範說明
- `README.md`：專案說明文件

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `agents.md`＋`handoff.md` | 每個 session |
| L2 | GitHub | [changyiwu/exam-analysis](https://github.com/changyiwu/exam-analysis) | 指定時 |
| L3 | Obsidian | `exam-analysis/專案工作流程.md` | 有需要時 |

## 工作約定
- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- 嚴禁寫入學生的真實姓名、真實個資或學號
- 嚴禁將 API Key 或敏感憑證 commit 至 GitHub
- 所有回應與文件使用繁體中文
