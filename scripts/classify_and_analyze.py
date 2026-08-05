# /// script
# dependencies = [
#   "pypdf",
# ]
# ///
"""會考數學試題單元分類與頻率統計。

流程：
  1. 用 pypdf 抽出 input/{年度}_math.pdf 的文字
  2. 依題號切成一題一筆（第一部分選擇題 + 第二部分非選擇題）
  3. 關鍵字規則初篩單元
  4. 用人工校對對照表 OVERRIDES 覆寫最終分類

為什麼一定要有第 4 步：PDF 抽文字時根號、分數線、指數、聯立方程式的大括號
常常整組掉出原位（例如 110 年第 3 題的方程式會被丟到段落最後），只靠關鍵字
無法達到可信的精準度。OVERRIDES 是逐題讀過原卷後的人工判定，為最終依據；
關鍵字規則保留下來只做交叉驗證，執行時會印出兩者的一致率。

用法：
    uv run scripts/classify_and_analyze.py

產出（皆在 output/，未進版控）：
    classification.csv   逐題分類明細
    unit_frequency.md    單元頻率排行榜（Markdown 表格）
"""

import csv
import re
import sys
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"

YEARS = [110, 111, 112, 113, 114, 115]

# 各年度選擇題題數。110 年為 26 題，111 年起改為 25 題；非選擇題固定 2 題。
CHOICE_COUNT = {110: 26, 111: 25, 112: 25, 113: 25, 114: 25, 115: 25}
ESSAY_COUNT = 2

# ---------------------------------------------------------------- 單元定義

NUM_LINE = "數與式: 數線與數的運算"
FACTOR = "數與式: 因數與倍數"
FRAC_EXP = "數與式: 分數與指數律"
RADICAL = "數與式: 根式的運算"
SEQUENCE = "數與式: 等差與等比"
SCI_NOTE = "數與式: 科學記號"
SIMUL_EQ = "代數: 二元一次聯立方程式"
INEQUALITY = "代數: 一元一次不等式"
RATIO = "代數: 比例式與正反比"
POLYNOMIAL = "代數: 乘法公式與多項式"
QUAD_EQ = "代數: 一元二次方程式"
COORDINATE = "代數: 直角坐標與二元一次圖形"
QUAD_FUNC = "代數: 二次函數"
POLYGON = "幾何: 三角形與多邊形性質"
CONGRUENT = "幾何: 三角形全等與相似"
TRI_CENTER = "幾何: 三角形三心"
CIRCLE = "幾何: 圓的性質"
SOLID = "幾何: 立體圖形"
PYTHAGORAS = "幾何: 畢氏定理"
STATISTICS = "統計與機率: 統計圖表與數據"
PROBABILITY = "統計與機率: 機率"

# 排序用：同次數時依領域順序呈現
UNIT_ORDER = [
    NUM_LINE, FACTOR, FRAC_EXP, RADICAL, SEQUENCE, SCI_NOTE,
    SIMUL_EQ, INEQUALITY, RATIO, POLYNOMIAL, QUAD_EQ, COORDINATE, QUAD_FUNC,
    POLYGON, CONGRUENT, TRI_CENTER, CIRCLE, SOLID, PYTHAGORAS,
    STATISTICS, PROBABILITY,
]

# ------------------------------------------------- 關鍵字初篩規則（依序比對）

KEYWORD_RULES = [
    (r"科學記號|×\s*10\s*[-−]|10\s*[-−]\s*\d", SCI_NOTE),
    (r"機率|機會相等", PROBABILITY),
    (r"直方圖|折線圖|長條圖|盒鬚|中位數|平均數|眾數|四分位|百分率|調查", STATISTICS),
    (r"角柱|角錐|圓柱|圓錐|展開圖|前視圖|上視圖|俯視圖|表面積|體積|正方體", SOLID),
    (r"重心|外心|內心|外接圓|內切圓", TRI_CENTER),
    (r"畢氏|斜邊", PYTHAGORAS),
    (r"圓心角|圓周角|弦心距|切線|弧|半圓|直徑|圓\s*[OＯ]|一圓", CIRCLE),
    (r"相似|全等|對應點|對應頂點|面積比|中點連線", CONGRUENT),
    (r"二次函數|拋物線|頂點", QUAD_FUNC),
    (r"一元二次方程", QUAD_EQ),
    (r"聯立方程", SIMUL_EQ),
    (r"等差|等比|數列", SEQUENCE),
    (r"三角形|四邊形|平行四邊形|菱形|梯形|矩形|正方形|內角|外角|多邊形|線對稱|摺線", POLYGON),
    (r"坐標平面|象限|一次函數|直線\s*[LＬ]|方程式為\s*[xy]", COORDINATE),
    (r"最簡根式|根號|化簡\s*\d+\s*的", RADICAL),
    (r"因式分解|多項式|乘法公式", POLYNOMIAL),
    (r"質因數|最大公因數|最小公倍數|因數|倍數", FACTOR),
    (r"不等式|至少要|最多可|範圍為", INEQUALITY),
    (r"比例|正比|反比|齒輪|比值|速率", RATIO),
    (r"指數|次方|最簡分數|通分", FRAC_EXP),
    (r"數線|絕對值", NUM_LINE),
]

# ------------------------------------------- 人工校對對照表（逐題讀原卷判定）

OVERRIDES = {
    # ---- 110 年（選擇 26 題 + 非選 2 題）
    "110-選1": COORDINATE, "110-選2": NUM_LINE, "110-選3": SIMUL_EQ,
    "110-選4": POLYGON, "110-選5": FRAC_EXP, "110-選6": RADICAL,
    "110-選7": COORDINATE, "110-選8": POLYNOMIAL, "110-選9": STATISTICS,
    "110-選10": CIRCLE, "110-選11": PROBABILITY, "110-選12": INEQUALITY,
    "110-選13": SEQUENCE, "110-選14": FRAC_EXP, "110-選15": CONGRUENT,
    "110-選16": SIMUL_EQ, "110-選17": CIRCLE, "110-選18": QUAD_FUNC,
    "110-選19": POLYGON, "110-選20": SIMUL_EQ, "110-選21": POLYGON,
    "110-選22": FACTOR, "110-選23": CONGRUENT, "110-選24": RATIO,
    "110-選25": CONGRUENT, "110-選26": TRI_CENTER,
    "110-非1": NUM_LINE, "110-非2": FACTOR,

    # ---- 111 年
    "111-選1": NUM_LINE, "111-選2": POLYNOMIAL, "111-選3": FACTOR,
    "111-選4": SOLID, "111-選5": FRAC_EXP, "111-選6": RADICAL,
    "111-選7": COORDINATE, "111-選8": POLYNOMIAL, "111-選9": PROBABILITY,
    "111-選10": QUAD_EQ, "111-選11": SIMUL_EQ, "111-選12": SCI_NOTE,
    "111-選13": CIRCLE, "111-選14": STATISTICS, "111-選15": POLYGON,
    "111-選16": PYTHAGORAS, "111-選17": POLYGON, "111-選18": SIMUL_EQ,
    "111-選19": TRI_CENTER, "111-選20": CONGRUENT, "111-選21": CIRCLE,
    "111-選22": QUAD_FUNC, "111-選23": CONGRUENT, "111-選24": RATIO,
    "111-選25": INEQUALITY,
    "111-非1": SEQUENCE, "111-非2": PROBABILITY,

    # ---- 112 年
    "112-選1": NUM_LINE, "112-選2": POLYNOMIAL, "112-選3": SOLID,
    "112-選4": RADICAL, "112-選5": COORDINATE, "112-選6": FRAC_EXP,
    "112-選7": COORDINATE, "112-選8": POLYGON, "112-選9": FACTOR,
    "112-選10": QUAD_EQ, "112-選11": RATIO, "112-選12": PROBABILITY,
    "112-選13": SOLID, "112-選14": QUAD_FUNC, "112-選15": SEQUENCE,
    "112-選16": SIMUL_EQ, "112-選17": TRI_CENTER, "112-選18": INEQUALITY,
    "112-選19": CIRCLE, "112-選20": POLYGON, "112-選21": RATIO,
    "112-選22": CONGRUENT, "112-選23": CONGRUENT, "112-選24": STATISTICS,
    "112-選25": RATIO,
    "112-非1": RATIO, "112-非2": POLYGON,

    # ---- 113 年
    "113-選1": FRAC_EXP, "113-選2": SOLID, "113-選3": SIMUL_EQ,
    "113-選4": COORDINATE, "113-選5": SEQUENCE, "113-選6": PROBABILITY,
    "113-選7": POLYGON, "113-選8": SCI_NOTE, "113-選9": STATISTICS,
    "113-選10": POLYNOMIAL, "113-選11": RADICAL, "113-選12": QUAD_FUNC,
    "113-選13": RATIO, "113-選14": INEQUALITY, "113-選15": FACTOR,
    "113-選16": COORDINATE, "113-選17": POLYGON, "113-選18": CONGRUENT,
    "113-選19": NUM_LINE, "113-選20": POLYGON, "113-選21": CIRCLE,
    "113-選22": TRI_CENTER, "113-選23": POLYGON, "113-選24": SIMUL_EQ,
    "113-選25": INEQUALITY,
    "113-非1": RATIO, "113-非2": CIRCLE,

    # ---- 114 年
    "114-選1": FRAC_EXP, "114-選2": POLYNOMIAL, "114-選3": POLYGON,
    "114-選4": SIMUL_EQ, "114-選5": POLYGON, "114-選6": COORDINATE,
    "114-選7": STATISTICS, "114-選8": RADICAL, "114-選9": SEQUENCE,
    "114-選10": POLYNOMIAL, "114-選11": PROBABILITY, "114-選12": SOLID,
    "114-選13": QUAD_EQ, "114-選14": SIMUL_EQ, "114-選15": NUM_LINE,
    "114-選16": CONGRUENT, "114-選17": PYTHAGORAS, "114-選18": FACTOR,
    "114-選19": INEQUALITY, "114-選20": POLYGON, "114-選21": QUAD_FUNC,
    "114-選22": TRI_CENTER, "114-選23": CIRCLE, "114-選24": RATIO,
    "114-選25": RATIO,
    "114-非1": STATISTICS, "114-非2": FACTOR,

    # ---- 115 年
    "115-選1": SIMUL_EQ, "115-選2": SOLID, "115-選3": RADICAL,
    "115-選4": PROBABILITY, "115-選5": NUM_LINE, "115-選6": STATISTICS,
    "115-選7": POLYNOMIAL, "115-選8": SCI_NOTE, "115-選9": QUAD_EQ,
    "115-選10": SIMUL_EQ, "115-選11": NUM_LINE, "115-選12": CONGRUENT,
    "115-選13": COORDINATE, "115-選14": QUAD_FUNC, "115-選15": POLYGON,
    "115-選16": TRI_CENTER, "115-選17": SEQUENCE, "115-選18": CIRCLE,
    "115-選19": CIRCLE, "115-選20": FACTOR, "115-選21": CONGRUENT,
    "115-選22": POLYGON, "115-選23": INEQUALITY, "115-選24": RATIO,
    "115-選25": RATIO,
    "115-非1": SEQUENCE, "115-非2": POLYGON,
}

# ------------------------------------------------------------------ 抽文字


def extract_text(year):
    pdf = INPUT_DIR / f"{year}_math.pdf"
    if not pdf.exists():
        raise FileNotFoundError(f"找不到試題檔：{pdf}")
    reader = PdfReader(pdf)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def split_questions(year, text):
    """切出該年度所有題目。回傳 [(題號, 題幹文字), ...]。"""
    # 砍掉封面作答說明，從「第一部分：選擇題」的標題列開始
    head = re.search(r"第一部分[：:]\s*選擇題", text)
    body = text[head.start():] if head else text
    tail = re.search(r"第二部分[：:]\s*非選擇題", body)
    part1, part2 = (body[:tail.start()], body[tail.start():]) if tail else (body, "")

    def cut(section, prefix, expected):
        # 只認「編號連續遞增」的行首題號，避免選項與圖說中的數字被誤判
        marks, want = [], 1
        for m in re.finditer(r"(?m)^\s*(\d{1,2})\.\s", section):
            if int(m.group(1)) == want:
                marks.append(m.start())
                want += 1
        out = []
        for i, start in enumerate(marks):
            end = marks[i + 1] if i + 1 < len(marks) else len(section)
            stem = re.sub(r"\s+", " ", section[start:end]).strip()
            out.append((f"{prefix}{i + 1}", stem))
        if len(out) != expected:
            print(f"⚠️ {year} 年{prefix}題切出 {len(out)} 題，預期 {expected} 題", file=sys.stderr)
        return out

    return cut(part1, "選", CHOICE_COUNT[year]) + cut(part2, "非", ESSAY_COUNT)


def classify_by_keyword(stem):
    """關鍵字初篩；比對不到回傳 None。"""
    for pattern, unit in KEYWORD_RULES:
        if re.search(pattern, stem):
            return unit
    return None


# -------------------------------------------------------------------- 產出


def write_csv(rows, path):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["年度", "題號", "最終分類", "關鍵字初篩結果", "初篩是否命中", "題幹摘要"])
        for r in rows:
            w.writerow([
                r["year"], r["qid"], r["unit"], r["guess"] or "（無）",
                "是" if r["guess"] == r["unit"] else "否",
                r["stem"][:80],
            ])


def write_frequency_md(rows, path):
    total = len(rows)
    counts = Counter(r["unit"] for r in rows)
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], UNIT_ORDER.index(kv[0])))

    lines = [
        "# 會考數學單元頻率統計（110～115 年）",
        "",
        f"共 {len(YEARS)} 個年度、{total} 題"
        f"（110 年 26 選 + 2 非選，111～115 年各 25 選 + 2 非選）。",
        "",
        "| 排名 | 主題單元分類 | 出現次數 | 所占比例 |",
        "| :---: | :--- | :---: | :---: |",
    ]
    rank, prev_count = 0, None
    for i, (unit, count) in enumerate(ranked, start=1):
        if count != prev_count:
            rank, prev_count = i, count
        lines.append(f"| {rank} | {unit} | {count} | {count / total * 100:.2f}% |")
    lines += [f"| - | **總計** | **{total}** | **100%** |", "", "## 各年度分佈", ""]

    header = "| 主題單元分類 | " + " | ".join(f"{y} 年" for y in YEARS) + " | 合計 |"
    lines += [header, "| :--- |" + " :---: |" * (len(YEARS) + 1)]
    per_year = {y: Counter(r["unit"] for r in rows if r["year"] == y) for y in YEARS}
    for unit, count in ranked:
        cells = " | ".join(str(per_year[y].get(unit, 0)) for y in YEARS)
        lines.append(f"| {unit} | {cells} | {count} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    rows = []
    for year in YEARS:
        for qid, stem in split_questions(year, extract_text(year)):
            key = f"{year}-{qid}"
            guess = classify_by_keyword(stem)
            unit = OVERRIDES.get(key)
            if unit is None:
                print(f"⚠️ {key} 不在人工校對表中，暫用初篩結果：{guess}", file=sys.stderr)
                unit = guess or "未分類"
            rows.append({"year": year, "qid": qid, "unit": unit, "guess": guess, "stem": stem})

    write_csv(rows, OUTPUT_DIR / "classification.csv")
    write_frequency_md(rows, OUTPUT_DIR / "unit_frequency.md")

    hit = sum(1 for r in rows if r["guess"] == r["unit"])
    print(f"共分類 {len(rows)} 題")
    print(f"關鍵字初篩與人工校對一致：{hit}/{len(rows)}（{hit / len(rows) * 100:.1f}%）")
    print(f"已寫入 {OUTPUT_DIR / 'classification.csv'}")
    print(f"已寫入 {OUTPUT_DIR / 'unit_frequency.md'}")


if __name__ == "__main__":
    main()
