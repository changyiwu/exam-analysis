# exam-analysis 專案駕駛艙 (Project Cockpit)

本專案旨在分析 110~115 年（近 6 年）台灣國中教育會考數學科試題，統計單元頻率並產出應考策略與資訊圖表。

---

## 📊 專案關鍵數據與狀態

*   **專案狀態**：🟢 試題分析與資訊圖表已成功產出 (橫式 16:9)
*   **最新更新時間**：2026-06-09
*   **總分析試題數**：162 題 (110~115 年，每年 27 題)
*   **數學主題單元數**：21 個分類
*   **產出成果**：9 個檔案，存放於 [output/](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/output/)
*   **公開 GitHub 倉庫**：[changyiwu/exam-analysis](https://github.com/changyiwu/exam-analysis)

---

## 📈 歷屆會考單元出題頻率 Top 5

1.  **代數: 二元一次聯立方程式**：21 題 (12.96%)
2.  **幾何: 三角形與多邊形性質**：21 題 (12.96%)
3.  **幾何: 圓的性質**：11 題 (6.79%)
4.  **代數: 比例式與正反比**：9 題 (5.56%)
5.  **代數: 直角坐標與二元一次圖形**：9 題 (5.56%)
    *   *同並列第 5 名*：**統計與機率: 統計圖表與數據**：9 題 (5.56%)

> [!NOTE]
> 代數與幾何為會考數學兩大台柱，合占 **71%** 的出題分佈。其中，幾何單元（圓、相似形、三心）是決勝 A 等級的關鍵。

---

## 📂 產出成果檔案索引

*   📄 **分析與策略報告**：[analysis_report.md](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/output/analysis_report.md)
*   🎨 **資訊圖表 1 (試題分析)**：[PNG 圖片](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/output/1_past_exam_analysis.png) | [SVG 向量圖](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/output/1_past_exam_analysis.svg)
*   🎨 **資訊圖表 2 (應考策略)**：[PNG 圖片](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/output/2_overall_strategy.png) | [SVG 向量圖](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/output/2_overall_strategy.svg)
*   🎨 **資訊圖表 3 (C到B策略)**：[PNG 圖片](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/output/3_strategy_c_to_b.png) | [SVG 向量圖](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/output/3_strategy_c_to_b.svg)
*   🎨 **資訊圖表 4 (B到A策略)**：[PNG 圖片](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/output/4_strategy_b_to_a.png) | [SVG 向量圖](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/output/4_strategy_b_to_a.svg)

---

## 🛠️ 開發資源與腳本

*   🐍 **試題分析腳本**：[classify_and_analyze.py](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/scratch/classify_and_analyze.py) (含 162 題精確分類手動校正對照表)
*   🐍 **圖表繪製腳本**：[generate_infographics.py](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/scratch/generate_infographics.py) (Pillow + SVG 渲染引擎)
*   📓 **專案開發筆記**：[PROJECT_NOTES.md](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/PROJECT_NOTES.md)
*   📜 **專案 AI 代理規範**：[ANTIGRAVITY.md](file:///c:/Users/chang/我的雲端硬碟/agents/antigravity/exam-analysis/ANTIGRAVITY.md)
