---
name: antigravity-exam-analysis
description: 國中會考與考試試題統計分析、滿版響應式資訊圖表繪製及 Git 檔案忽略指南。說「分析會考試題」「生圖表」「產出應考策略」時載入。
---

# 試題分析與響應式資訊圖表生成指南

本指南適用於：下載考試試題、統計單元頻率、擬定晉級應考策略，並程式化生成適用於螢幕呈現、滿版且具備瀏覽器響應式縮放功能的雙軌（PNG & SVG）資訊圖表。

## 1. 試題下載與文本分類 (Exam Analysis)
- **試題下載**：將下載的歷屆 PDF/HTML 檔案存放於本地 `input/` 目錄。
- **文本提取與分類**：
  - 設定數學核心主題的關鍵字/Regex 進行初篩。
  - **解決符號丟失 (Symbol Loss)**：因 PDF 提取時常遺失根號、分數線、指數等數學符號，必須建立「人工校對對照表」（Override Dictionary）手動修正每題分類，確保達到 100% 分類精準度。
- **策略撰寫**：根據單元出題頻率 Top 排行，針對不同目標級分撰寫突破指引（如 C 到 B 固守基本題，B 到 A 攻克進階幾何與非選）。

## 2. 雙引擎資訊圖表設計 (PIL + SVG Canvas)
- **規格佈局**：全面使用**橫式 16:9 (1920x1080)** 規格，利於簡報及網頁呈現。
- **美學風格與主題切換**：
  - **暗黑美學 (Dark Mode)**：使用深沉有層次的背景（如 slate-900 `#0f172a`、teal-950 `#042f2e`）搭配明亮鮮明的標題與文字（slate-50 `#f8fafc`、amber-400 `#fbbf24`）。
  - **淺色美學 (Light Mode - 推薦高對比度)**：使用柔和舒服的淺色背景（如 slate-50 `#f8fafc`、teal-50 `#f0fdfa`、orange-50 `#fff7ed`、purple-50 `#faf5ff`），純白卡片本體（`#ffffff`），搭配高對比度的深色文字（slate-800/900、teal-800、orange-900、purple-900 文字），以提高屏幕閱讀與列印時的清晰度。
- **大字型與版面填充 (重要)**：
  - 避免格子空曠。文字大小應設計為：主標題 `38px`、次標題 `24~26px`、正文與說明 `18~22px`、行高 `1.35`。
  - 卡片尺寸與文字行數應相互契合，讓文字排版顯得飽滿且易讀。
- **雙軌生成實作**：使用 Python 類別（例如 `DualCanvas`）封裝 Pillow (`PIL.ImageDraw`) 與 SVG 字串拼接，同時產出高畫質 PNG 與向量 SVG。

## 3. 瀏覽器自適應響應式設定 (Responsive SVG)
- **移除硬編碼寬高**：SVG 根節點**不可**直接寫死 `width="1920" height="1080"`，否則在瀏覽器中直接開啟會因過寬而產生橫向滾動條。
- **改用 viewBox 自適應**：
  - 設定 `viewBox="0 0 {width} {height}"` 定義內部座標系。
  - 設定 `width="100%" height="100%"` 使其填滿容器（如瀏覽器視窗）。
  - 設定 `preserveAspectRatio="xMidYMid meet"` 確保縮放時保持 16:9 比例且完美置中。
  - **SVG 根節點範例**：
    ```xml
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
    ```

## 4. Git 儲存庫管理與隱私防護 (Git Best Practices)
- **數據與產出忽略**：
  - 將原始試題資料夾 `input/` 與生成圖表/報告的 `output/` 資料夾加入 `.gitignore` 排除追蹤，避免大型檔案與大量二進位圖檔膨脹 GitHub 倉庫。
  - 若已有檔案不小心被追蹤，在修改 `.gitignore` 後執行以下命令移除 Git 快取追蹤（此指令**不會**刪除本地實體檔案）：
    ```bash
    git rm -r --cached input/ output/
    git add .gitignore
    git commit -m "chore: ignore input/ and output/ directories"
    ```
- **個資去識別化**：上傳前務必確認原始 PDF、統計結果及報告中絕不包含學生的真實姓名、真實個資或敏感學號，只使用完全去識別化的數據。
