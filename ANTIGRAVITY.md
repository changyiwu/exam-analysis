# AntiGravity 專案規範 - exam-analysis (試題分析)

此檔案為 `exam-analysis` 專案專屬之 AI 代理人開發規範，後續開發時請務必遵循。

## 專案概述
- **專案名稱**：exam-analysis (試題分析)
- **專案用途**：用於分析試題與考試成績，提供直觀且美觀的分析介面。
- **部署狀態**：目前無部署需求。
- **儲存庫屬性**：公開 (Public) GitHub Repository。

---

## 核心開發原則

### 1. 視覺與設計美學 (Aesthetics)
- **拒絕陽春**：網頁介面必須具備現代設計感 (視覺美學至上)。
- **色彩系統**：使用和諧且具層次感的色彩調配 (如 HSL)，避免使用純紅、純綠、純藍等預設顏色。預設支持暗色模式與玻璃擬態 (Glassmorphism)。
- **字型與排版**：引進現代字型 (如 Inter、Outfit 等 Google Fonts)，拒絕瀏覽器預設字型。
- **動態效果**：加入平滑的 Hover 效果與微動畫 (Micro-animations) 以增強使用者互動感。
- **無佔位符**：不使用 placeholder 圖片或虛假字樣。若有需要，應使用圖片生成工具生成對應素材。

### 2. 安全規範 (Security)
- **隱私至上**：此專案涉及試題與成績，**嚴禁將學生的真實姓名、真實個資、學號**或任何敏感個資寫入程式碼或 Markdown 檔案。若需要測試資料，一律使用去識別化的虛擬資料。
- **金鑰防護**：嚴禁將任何 API Key、Token、密碼等敏感憑證 commit 至 GitHub。

---

## 每日工作流程

### 開工步驟 (說「開工」時執行)
1. 讀取 `agents.md`（專案藍圖）與 `handoff.md`（交接檔）盤點上次進度與本次待辦。
2. 檢查 `git status` 與 commit 歷史。
3. 向使用者回報當前狀態與建議下一步。

### 收工步驟 (說「收工」時執行)
1. **隱私與敏感資訊檢查**：確認無 API Key、Token 與學生真實個資。
2. **更新 L1/L3 筆記**：更新 `agents.md` 藍圖進度、改寫 `handoff.md` 交接檔，並將詳細紀錄寫入 Obsidian (`exam-analysis/專案工作流程.md`)。
3. **Git 同步**：提交 commit 並 push 至遠端 Repository changyiwu/exam-analysis。
