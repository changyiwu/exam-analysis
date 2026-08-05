# /// script
# dependencies = [
#   "pillow",
# ]
# ///
import os
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 一律以「腳本自身位置」推導專案根目錄，不寫死任何使用者路徑
PROJECT_ROOT = Path(__file__).resolve().parent.parent
output_dir = PROJECT_ROOT / "output"
os.makedirs(output_dir, exist_ok=True)


def _pick_font(candidates):
    """回傳第一個實際存在的字型檔；都找不到就回 None（改用 PIL 預設字型）。"""
    for path in candidates:
        if Path(path).exists():
            return str(path)
    return None


# 中文字型：Windows 微軟正黑體優先，其次思源黑體 / macOS 黑體
FONT_BOLD_PATH = _pick_font([
    r"C:\Windows\Fonts\msjhbd.ttc",
    r"C:\Windows\Fonts\NotoSansTC-Bold.otf",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
])
FONT_REG_PATH = _pick_font([
    r"C:\Windows\Fonts\msjh.ttc",
    r"C:\Windows\Fonts\NotoSansTC-Regular.otf",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
])
if FONT_REG_PATH is None:
    print("⚠️ 找不到任何中文字型，PNG 中文會變成方框；請安裝微軟正黑體或思源黑體。")

# 彩色 emoji 字型（COLR/CBDT）。中文字型不含 emoji 字符，缺這個 PNG 的 emoji 會變空心方框。
FONT_EMOJI_PATH = _pick_font([
    r"C:\Windows\Fonts\seguiemj.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
])
if FONT_EMOJI_PATH is None:
    print("⚠️ 找不到彩色 emoji 字型，PNG 內的 emoji 會變成方框（SVG 版不受影響）。")

# 涵蓋本專案用到的符號：⏳ ⚠ ★ 等雜項符號，以及 U+1F300 以上的表情符號區段。
# 後面的 \uFE0F（VS16）與 \u200D（ZWJ）用來把變體選擇符與組合序列一起吃進同一段。
# \u5916\u5C64\u5FC5\u9808\u662F\u300C\u6355\u7372\u300D\u7FA4\u7D44\uFF0Cre.split \u624D\u6703\u628A emoji \u7247\u6BB5\u7559\u5728\u7D50\u679C\u88E1\u800C\u4E0D\u662F\u4E1F\u6389\u3002
EMOJI_PATTERN = re.compile(
    r"((?:[\u231A-\u23FF\u2600-\u27BF\u2B00-\u2BFF"
    r"\U0001F000-\U0001FAFF][\uFE0E\uFE0F\u200D]*)+)"
)

class DualCanvas:
    def __init__(self, width, height, bg_color):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        
        # Pillow initialization
        # 用 RGBA 才能讓 embedded_color 正確合成彩色 emoji，存檔時再轉回 RGB
        self.img = Image.new("RGBA", (width, height), color=self.hex_to_rgb(bg_color))
        self.draw = ImageDraw.Draw(self.img)
        self._emoji_fonts = {}
        
        # SVG initialization
        self.svg_elements = []
        self.svg_elements.append(f'<rect width="{width}" height="{height}" fill="{bg_color}" />')

    def hex_to_rgb(self, hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    def draw_rect(self, x, y, w, h, fill_color, rx=0, border_color=None, border_width=0):
        fill_rgb = self.hex_to_rgb(fill_color) if fill_color else None
        outline_rgb = self.hex_to_rgb(border_color) if border_color else None
        
        if rx > 0:
            self.draw.rounded_rectangle(
                [x, y, x + w, y + h],
                radius=rx,
                fill=fill_rgb,
                outline=outline_rgb,
                width=border_width
            )
        else:
            self.draw.rectangle(
                [x, y, x + w, y + h],
                fill=fill_rgb,
                outline=outline_rgb,
                width=border_width
            )
            
        # SVG compile
        fill_val = fill_color if fill_color else "none"
        stroke_attrs = ""
        if border_color and border_width > 0:
            stroke_attrs = f' stroke="{border_color}" stroke-width="{border_width}"'
        rx_attr = f' rx="{rx}"' if rx > 0 else ""
        self.svg_elements.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}"{rx_attr} fill="{fill_val}"{stroke_attrs} />'
        )

    def draw_line(self, x1, y1, x2, y2, color, width=1):
        color_rgb = self.hex_to_rgb(color)
        self.draw.line([x1, y1, x2, y2], fill=color_rgb, width=width)
        
        self.svg_elements.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" />'
        )

    def draw_circle(self, cx, cy, r, fill_color, border_color=None, border_width=0):
        fill_rgb = self.hex_to_rgb(fill_color) if fill_color else None
        outline_rgb = self.hex_to_rgb(border_color) if border_color else None
        
        self.draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=fill_rgb,
            outline=outline_rgb,
            width=border_width
        )
        
        fill_val = fill_color if fill_color else "none"
        stroke_attrs = ""
        if border_color and border_width > 0:
            stroke_attrs = f' stroke="{border_color}" stroke-width="{border_width}"'
        self.svg_elements.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill_val}"{stroke_attrs} />'
        )

    def emoji_font(self, font_size):
        """取得 emoji 字型；沒有 Segoe UI Emoji 時回傳 None。"""
        if not FONT_EMOJI_PATH:
            return None
        if font_size not in self._emoji_fonts:
            self._emoji_fonts[font_size] = ImageFont.truetype(FONT_EMOJI_PATH, font_size)
        return self._emoji_fonts[font_size]

    def split_emoji_runs(self, text, font, font_size):
        """把一行字切成 (片段, 字型) 序列，emoji 片段配 emoji 字型。

        中文字型沒有 emoji 字符，整行用同一個字型畫會變成空心方框，
        所以畫 PNG 前先分段；SVG 那邊交給瀏覽器自己 fallback，不需分段。
        """
        emoji_font = self.emoji_font(font_size)
        if emoji_font is None:
            return [(text, font)]
        runs = []
        for part in EMOJI_PATTERN.split(text):
            if not part:
                continue
            runs.append((part, emoji_font if EMOJI_PATTERN.fullmatch(part) else font))
        return runs or [(text, font)]

    def measure_text(self, text, font, font_size):
        """量一行字的寬度，emoji 片段用 emoji 字型量。"""
        total = 0
        for part, part_font in self.split_emoji_runs(text, font, font_size):
            total += self.draw.textlength(part, font=part_font)
        return total

    def wrap_chinese_text(self, text, font, max_width, font_size):
        lines = []
        current_line = ""
        for char in text:
            test_line = current_line + char
            if self.measure_text(test_line, font, font_size) > max_width:
                lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        return lines

    def draw_text(self, x, y, text, font_size, color, font_type='regular', anchor='start', max_width=None, line_spacing=1.35):
        font_path = FONT_BOLD_PATH if font_type == 'bold' else FONT_REG_PATH
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
        color_rgb = self.hex_to_rgb(color)
        
        svg_anchor = "start"
        if anchor == 'middle':
            svg_anchor = "middle"
        elif anchor == 'end':
            svg_anchor = "end"
            
        if max_width:
            lines = self.wrap_chinese_text(text, font, max_width, font_size)
        else:
            lines = [text]

        current_y = y
        font_weight = "bold" if font_type == 'bold' else "normal"

        for line in lines:
            align_offset = 0
            if anchor in ('middle', 'end'):
                w = self.measure_text(line, font, font_size)
                align_offset = -w / 2 if anchor == 'middle' else -w

            # 逐段畫：emoji 片段用 Segoe UI Emoji 並開啟 embedded_color 以保留彩色。
            # 兩種字型的 ascent 不同，若沿用預設的「上緣對齊」，emoji 會浮得比中文高；
            # 改成統一以中文字型的基線為準（anchor="ls"），兩者才會坐在同一條線上。
            baseline = current_y + font.getmetrics()[0]
            cursor = x + align_offset
            for part, part_font in self.split_emoji_runs(line, font, font_size):
                is_emoji = part_font is not font
                self.draw.text(
                    (cursor, baseline), part,
                    fill=color_rgb, font=part_font, anchor="ls", embedded_color=is_emoji,
                )
                cursor += self.draw.textlength(part, font=part_font)

            escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            self.svg_elements.append(
                f'<text x="{x}" y="{current_y + font_size}" fill="{color}" '
                f'font-family="Microsoft JhengHei, Segoe UI Emoji, Apple Color Emoji, sans-serif" font-size="{font_size}" '
                f'font-weight="{font_weight}" text-anchor="{svg_anchor}">{escaped_line}</text>'
            )
            current_y += font_size * line_spacing
            
        return current_y - y

    def save_files(self, filename_base):
        # Save PNG
        png_path = os.path.join(output_dir, f"{filename_base}.png")
        self.img.convert("RGB").save(png_path, "PNG")
        print(f"Saved PNG: {png_path}")
        
        # Save SVG
        svg_path = os.path.join(output_dir, f"{filename_base}.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" '
                f'width="100%" height="100%" preserveAspectRatio="xMidYMid meet">\n'
            )
            for el in self.svg_elements:
                f.write(f"  {el}\n")
            f.write("</svg>\n")
        print(f"Saved SVG: {svg_path}")

# ==================== INFOGRAPHIC 1: 歷屆試題分析 (Landscape) ====================
def build_info_1():
    # Style: Light Slate Theme 16:9
    c = DualCanvas(1920, 1080, "#f8fafc")
    
    # Grid background decoration
    for x in range(100, 1920, 200):
        c.draw_line(x, 0, x, 1080, "#e2e8f0", 1)
    for y in range(100, 1080, 200):
        c.draw_line(0, y, 1920, y, "#e2e8f0", 1)
        
    # Header card
    c.draw_rect(50, 40, 1820, 110, "#ffffff", rx=12, border_color="#cbd5e1", border_width=2)
    c.draw_rect(50, 40, 15, 110, "#0284c7", rx=0)
    c.draw_text(90, 52, "國中教育會考數學科", 22, "#475569", "bold")
    c.draw_text(90, 82, "6 年歷屆試題單元分析 (110~115 年)", 38, "#0f172a", "bold")
    
    # Top Metrics Row
    metric_w = 580
    metric_h = 100
    c.draw_rect(50, 170, metric_w, metric_h, "#ffffff", rx=10, border_color="#cbd5e1", border_width=1)
    c.draw_text(70, 182, "總分析題數", 20, "#475569")
    c.draw_text(70, 210, "163 題", 36, "#0284c7", "bold")

    c.draw_rect(670, 170, metric_w, metric_h, "#ffffff", rx=10, border_color="#cbd5e1", border_width=1)
    c.draw_text(690, 182, "代數領域佔比 (Top 1)", 20, "#475569")
    c.draw_text(690, 210, "35.6% (58題)", 36, "#4f46e5", "bold")

    c.draw_rect(1290, 170, metric_w, metric_h, "#ffffff", rx=10, border_color="#cbd5e1", border_width=1)
    c.draw_text(1310, 182, "幾何領域佔比 (決勝點)", 20, "#475569")
    c.draw_text(1310, 210, "32.5% (53題)", 36, "#e11d48", "bold")

    # Main Section: Left Column (Topic Rankings)
    c.draw_rect(50, 290, 930, 740, "#ffffff", rx=12, border_color="#cbd5e1", border_width=1)
    c.draw_text(80, 310, "🏆 歷屆會考主題單元出現頻率 Top 10（同次數並列同名次）", 24, "#0f172a", "bold")

    # (名次, 單元, 題數, 佔比, 色票)；數據來源：scripts/classify_and_analyze.py
    top_topics = [
        (1, "幾何: 三角形與多邊形性質", 18, "11.04%", "#0284c7"),
        (2, "代數: 二元一次聯立方程式", 12, "7.36%", "#0284c7"),
        (2, "代數: 比例式與正反比", 12, "7.36%", "#0369a1"),
        (4, "幾何: 三角形全等與相似", 11, "6.75%", "#4f46e5"),
        (5, "幾何: 圓的性質", 10, "6.13%", "#4f46e5"),
        (6, "代數: 直角坐標與二元一次圖形", 9, "5.52%", "#6366f1"),
        (7, "數與式: 數線與數的運算", 8, "4.91%", "#7c3aed"),
        (7, "數與式: 因數與倍數", 8, "4.91%", "#7c3aed"),
        (7, "代數: 乘法公式與多項式", 8, "4.91%", "#7c3aed"),
        (10, "並列：等差等比／不等式／統計圖表／機率", 7, "各 4.29%", "#475569")
    ]

    chart_y = 360
    for rank, topic, count, pct, color in top_topics:
        c.draw_circle(90, chart_y + 20, 16, color)
        c.draw_text(90, chart_y + 8, str(rank), 16, "#ffffff", "bold", anchor="middle")
        c.draw_text(125, chart_y + 6, topic, 22, "#1e293b", "bold")
        c.draw_text(850, chart_y + 6, f"{count}題 ({pct})", 22, "#475569", anchor="end")

        # Horizontal Bar Chart
        bar_w = 360
        c.draw_rect(125, chart_y + 34, bar_w, 10, "#e2e8f0", rx=5)
        fill_w = int(bar_w * (count / 18))
        c.draw_rect(125, chart_y + 34, fill_w, 10, color, rx=5)

        chart_y += 63

    # Main Section: Right Column (Domain & Insights)
    c.draw_rect(1010, 290, 860, 740, "#ffffff", rx=12, border_color="#cbd5e1", border_width=1)
    c.draw_text(1040, 310, "📊 會考命題趨勢與領域分佈", 26, "#0f172a", "bold")
    
    # 3 Domain Columns
    domains = [
        ("代數與函數", "35.6%", "聯立方程式、比例式、二次函數。58 題居各領域之冠，著重公式運算與數學建模應用。", "#4f46e5"),
        ("幾何與圖形", "32.5%", "多邊形、圓、相似形、三心。53 題緊追在後，決勝A等級的關鍵，著重推理證明與輔助線。", "#e11d48"),
        ("數與式/統計機率", "31.9%", "因倍數、根式、統計圖表與機率，共 52 題。基本分基本盤，難度中易，應全拿分。", "#0d9488")
    ]
    
    dom_x = 1040
    for dom_title, dom_pct, dom_desc, dom_color in domains:
        c.draw_rect(dom_x, 360, 240, 240, "#f8fafc", rx=10, border_color="#cbd5e1", border_width=1)
        c.draw_text(dom_x + 120, 375, dom_title, 22, dom_color, "bold", anchor="middle")
        c.draw_text(dom_x + 120, 410, dom_pct, 44, dom_color, "bold", anchor="middle")
        c.draw_text(dom_x + 15, 470, dom_desc, 18, "#334155", max_width=210, line_spacing=1.35)
        dom_x += 280

    # 3 Insights Rows
    insights = [
        ("趨勢一 | 多邊形性質獨強，占 11.0%", "三角形與多邊形性質 18 題居冠，每年穩定出 2~4 題；聯立方程式與比例式各 12 題並列第 2，三者是必守基本盤。", "#0284c7"),
        ("趨勢二 | 幾何為奪 A 關鍵", "相似形 11 題、圓性質 10 題，加上三心與立體共 53 題。多落在第 16 題後及非選，鑑別度高，需熟練輔助線構思。", "#e11d48"),
        ("趨勢三 | 生活素養與建模", "長題敘述多，融入文旦分類、疫苗實驗、齒輪比。考生須養成「閱讀理解、假設變數、列出算式」的建模習慣。", "#d97706")
    ]
    
    ins_y = 640
    for ins_title, ins_desc, ins_color in insights:
        c.draw_rect(1040, ins_y, 800, 110, "#f8fafc", rx=8, border_color="#cbd5e1", border_width=1)
        c.draw_rect(1040, ins_y, 8, 110, ins_color, rx=0)
        c.draw_text(1065, ins_y + 12, ins_title, 24, ins_color, "bold")
        c.draw_text(1065, ins_y + 45, ins_desc, 18, "#334155", max_width=750, line_spacing=1.35)
        ins_y += 130

    c.save_files("1_past_exam_analysis")

# ==================== INFOGRAPHIC 2: 準備會考應考策略 (Landscape, Large/Filled Text) ====================
def build_info_2():
    c = DualCanvas(1920, 1080, "#f0fdfa")
    
    # Grid lines
    for x in range(100, 1920, 200):
        c.draw_line(x, 0, x, 1080, "#ccfbf1", 1)
    for y in range(100, 1080, 200):
        c.draw_line(0, y, 1920, y, "#ccfbf1", 1)
        
    # Header card
    c.draw_rect(50, 40, 1820, 110, "#ffffff", rx=12, border_color="#99f6e4", border_width=2)
    c.draw_rect(50, 40, 15, 110, "#d97706", rx=0)
    c.draw_text(90, 52, "國中教育會考數學科", 22, "#0d9488", "bold")
    c.draw_text(90, 82, "會考應考策略與準備方針", 38, "#115e59", "bold")
    
    # Left Column: Time Allocation (Enlarged Text: Title 24, Time 20, Description 20)
    c.draw_rect(50, 170, 930, 860, "#ffffff", rx=12, border_color="#99f6e4", border_width=1)
    c.draw_text(80, 195, "⏳ 考場 80 分鐘答題時間黃金分配", 26, "#0f766e", "bold")
    
    steps = [
        ("第一階段：基礎搶分 (Q1~15)", "用時：約 25 分鐘 (每題 1.5 分)", "快速穩健寫完前段基礎題。考點單一，務必仔細讀題計算，完成後順手代值驗算，固守基本分入袋。", "#0d9488"),
        ("第二階段：非選攻防 (非選 2 題)", "用時：約 20 分鐘 (每題 10 分)", "搶攻步驟得分！會考非選採步驟計分，只要寫出未知數假設與合理列式就能拿1~2分，絕不可留白！", "#0d9488"),
        ("第三階段：進階鑑別 (Q16~25)", "用時：約 25 分鐘 (每題 2.5 分)", "挑戰後半段幾何、二次函數等高鑑別題。若卡關超過3分鐘解不出，立刻圈起跳過，切忌在一題死磕。", "#0d9488"),
        ("第四階段：檢查除錯 (最後檢查)", "用時：約 10 分鐘 (全力除錯)", "優先驗算前 15 題！並確認答案卡無劃記偏移、非選列式無漏寫單位。此階段往往能挽回3-5分粗心失分。", "#d97706")
    ]
    
    grid_coords = [
        (80, 250),
        (530, 250),
        (80, 620),
        (530, 620)
    ]
    
    for idx, (title, time_info, desc, col) in enumerate(steps):
        gx, gy = grid_coords[idx]
        c.draw_rect(gx, gy, 420, 330, "#f0fdfa", rx=8, border_color="#99f6e4", border_width=1)
        
        # Step Circle
        c.draw_circle(gx + 40, gy + 45, 22, col)
        c.draw_text(gx + 40, gy + 34, str(idx+1), 18, "#ffffff", "bold", anchor="middle")
        
        c.draw_text(gx + 75, gy + 32, title, 24, "#115e59", "bold")
        c.draw_text(gx + 40, gy + 85, time_info, 20, col, "bold")
        c.draw_text(gx + 40, gy + 125, desc, 20, "#334155", max_width=340, line_spacing=1.35)

    # Right Column: Mindsets (Enlarged Text: Title 24, Body 22 for visual fullness)
    c.draw_rect(1010, 170, 860, 860, "#ffffff", rx=12, border_color="#99f6e4", border_width=1)
    c.draw_text(1040, 195, "💡 衝刺期準備三大心法", 26, "#0f766e", "bold")
    
    mindsets = [
        ("心法一", "素養長題「先看問題，再圈條件」", "會考長題敘述繁瑣。養成「先讀題目最後一句求什麼」的習慣，帶著目標再回頭圈選關鍵數據與變數關係，能大幅節省時間，免受背景雜訊干擾思路。", "#ea580c"),
        ("心法二", "「列式即給分」！非選擇題千萬別交白卷", "會考非選題評分重視解題邏輯而非僅看答案。作答時清楚寫下「設未知數為...」與根據中文列出的方程。即便最後計算出錯，也能拿到1~2級分！", "#ea580c"),
        ("心法三", "計時 80 分鐘模擬，進行「限速訓練」", "許多考生在考場寫不完，是因為缺乏時間意識。在考前衝刺期演練歷屆或模考時，強迫自己計時80分鐘，比照真實會考答題順序，建立答題節奏與抗壓力。", "#0d9488")
    ]
    
    mind_y = 250
    for label, title, body, col_val in mindsets:
        c.draw_rect(1040, mind_y, 790, 230, "#f0fdfa", rx=8, border_color="#99f6e4", border_width=1)
        c.draw_rect(1040, mind_y, 8, 230, col_val, rx=0)
        
        c.draw_rect(1065, mind_y + 18, 90, 32, col_val, rx=4)
        c.draw_text(1110, mind_y + 24, label, 16, "#ffffff", "bold", anchor="middle")
        
        c.draw_text(1170, mind_y + 20, title, 24, col_val, "bold")
        c.draw_text(1065, mind_y + 70, body, 22, "#334155", max_width=740, line_spacing=1.35)
        
        mind_y += 260

    c.save_files("2_overall_strategy")

# ==================== INFOGRAPHIC 3: 從 C 到 B 突破策略 (Landscape, Large/Filled Text) ====================
def build_info_3():
    c = DualCanvas(1920, 1080, "#fff7ed")
    
    # Grid lines
    for x in range(100, 1920, 200):
        c.draw_line(x, 0, x, 1080, "#ffedd5", 1)
    for y in range(100, 1080, 200):
        c.draw_line(0, y, 1920, y, "#ffedd5", 1)
        
    # Header card
    c.draw_rect(50, 40, 1820, 110, "#ffffff", rx=12, border_color="#fed7aa", border_width=2)
    c.draw_rect(50, 40, 15, 110, "#ea580c", rx=0)
    c.draw_text(90, 52, "會考數學科等級晉升", 22, "#c2410c", "bold")
    c.draw_text(90, 82, "從 C 到 B 突破策略：固守基本分", 38, "#7c2d12", "bold")
    
    # Target Box
    c.draw_rect(50, 170, 1820, 60, "#dc2626", rx=8)
    c.draw_text(960, 186, "🎯 精準目標：選擇題答對 10 ~ 13 題，即可成功脫 C 達 B！", 24, "#ffffff", "bold", anchor="middle")
    
    # Left Column: The 6 Core Basic Units (Grid 2x3, Title 24, Desc 20 for visual fullness)
    c.draw_rect(50, 250, 930, 780, "#ffffff", rx=12, border_color="#fed7aa", border_width=1)
    c.draw_text(80, 275, "🎯 衝刺複習：主攻這 6 個「高頻且好拿分」基礎單元", 26, "#7c2d12", "bold")
    
    basic_units = [
        ("1. 二元一次聯立方程 (12題)", "七下單元。6 年考 12 題，並列第 2 高頻。考解聯立方程式或生活代數列式，熟記消去法即可穩拿分。", "#e11d48"),
        ("2. 比例式與正反比 (12題)", "七下單元。6 年考 12 題，並列第 2 高頻。考齒輪比、速率、單位換算，多為單一步驟的比例運算。", "#e11d48"),
        ("3. 直角坐標與圖形 (9題)", "七下單元。考象限判斷、讀取坐標點。通常配合坐標點移動，是看圖說故事送分題。", "#e11d48"),
        ("4. 數線與數的運算 (8題)", "七上單元。考正負數運算、絕對值大小、分配律簡化計算。是全卷最容易的第一題出處。", "#ea580c"),
        ("5. 因數與倍數 (8題)", "七上單元。考質數判斷、公因數公倍數。多結合生活情境（如拼貼紙片不裁切）。", "#ea580c"),
        ("6. 統計圖表與數據 (7題)", "九下單元。考直方圖、折線圖判讀，或是中位數與眾數。純閱讀圖表即可得分。", "#ea580c")
    ]
    
    grid_coords = [
        (80, 330), (530, 330),
        (80, 560), (530, 560),
        (80, 790), (530, 790)
    ]
    
    for idx, (title, desc, col) in enumerate(basic_units):
        gx, gy = grid_coords[idx]
        c.draw_rect(gx, gy, 420, 210, "#fff7ed", rx=8, border_color="#fed7aa", border_width=1)
        c.draw_rect(gx, gy, 8, 210, col, rx=0)
        c.draw_text(gx + 25, gy + 15, title, 24, col, "bold")
        c.draw_text(gx + 25, gy + 50, desc, 20, "#334155", max_width=370, line_spacing=1.35)

    # Right Column: Action Plan (Title 26, Body 22 for visual fullness)
    c.draw_rect(1010, 250, 860, 780, "#ffffff", rx=12, border_color="#fed7aa", border_width=1)
    c.draw_text(1040, 275, "📋 C 到 B 衝刺實戰拿分指南", 26, "#7c2d12", "bold")
    
    actions = [
        ("指南一", "果斷放棄難題！時間留給前 15 題", "會考後半段（16-25題）多是複雜的幾何相似、證明或圓形題目，對C級同學太耗時。請在考場上果斷跳過，將省下的時間全部用來反覆檢查前 15 題，確保寫過的題目絕對能拿分。", "#ea580c"),
        ("指南二", "杜絕粗心錯誤！寫完立刻用「簡單代值」驗算", "待加強的同學往往不是不會，而是死在計算錯誤（如負負得正、分配律漏乘）。寫完一題方程式或算式題，立刻將答案代回原式子中，確認左右兩邊相等，確防粗心。", "#ea580c"),
        ("指南三", "非選題大膽作答！哪怕只寫出『假設未知數』", "非選第一題多是代數應用題。即使不會解題，也必須用中文寫下：『設未知數 x 為...，設 y 為...』並試著照題目寫出式子。會考非選只要有合理的假設與列式就能拿1分，這往往是脫C關鍵！", "#dc2626")
    ]
    
    act_y = 330
    for label, title, body, col_val in actions:
        c.draw_rect(1040, act_y, 790, 200, "#fff7ed", rx=8, border_color="#fed7aa", border_width=1)
        c.draw_rect(1040, act_y, 8, 200, col_val, rx=0)
        
        c.draw_rect(1065, act_y + 18, 90, 32, col_val, rx=4)
        c.draw_text(1110, act_y + 24, label, 16, "#ffffff", "bold", anchor="middle")
        
        c.draw_text(1170, act_y + 20, title, 24, col_val, "bold")
        c.draw_text(1065, act_y + 65, body, 22, "#334155", max_width=740, line_spacing=1.35)
        act_y += 230

    c.save_files("3_strategy_c_to_b")

# ==================== INFOGRAPHIC 4: 從 B 到 A 精熟策略 (Landscape, Large/Filled Text) ====================
def build_info_4():
    c = DualCanvas(1920, 1080, "#faf5ff")
    
    # Grid lines
    for x in range(100, 1920, 200):
        c.draw_line(x, 0, x, 1080, "#f3e8ff", 1)
    for y in range(100, 1080, 200):
        c.draw_line(0, y, 1920, y, "#f3e8ff", 1)
        
    # Header card
    c.draw_rect(50, 40, 1820, 110, "#ffffff", rx=12, border_color="#e9d5ff", border_width=2)
    c.draw_rect(50, 40, 15, 110, "#7c3aed", rx=0)
    c.draw_text(90, 52, "會考數學科等級晉升", 22, "#6d28d9", "bold")
    c.draw_text(90, 82, "從 B 到 A 精熟策略：攻克進階與非選", 38, "#4c1d95", "bold")
    
    # Target Box
    c.draw_rect(50, 170, 1820, 60, "#7e22ce", rx=8)
    c.draw_text(960, 188, "🎯 精準目標：選擇題錯 2 ~ 4 題內，非選拿 4 ~ 6 分，勇奪 A 等級！", 24, "#ffffff", "bold", anchor="middle")
    
    # Left Column: The 5 Core Advanced Units (Card height = 125, Desc = 22 for visual fullness)
    c.draw_rect(50, 250, 930, 780, "#ffffff", rx=12, border_color="#e9d5ff", border_width=1)
    c.draw_text(80, 275, "🎯 核心突破：攻克這 5 大「決勝鑑別度」高難度單元", 26, "#4c1d95", "bold")
    
    adv_units = [
        ("1. 三角形與多邊形性質 (18題，全卷第 1)", "平行線與截角定理、特殊四邊形長度/角度。常與摺疊對稱結合考角度變化。", "#7c3aed"),
        ("2. 三角形全等與相似 (11題，第 4)", "九上核心。相似判定性質與比例線段結合。此為非選幾何證明的核心考點。", "#7c3aed"),
        ("3. 圓的性質 (10題，第 5)", "九上核心。圓周角與切線推導、弦心距與弧長。是高鑑別度題目的常客。", "#7c3aed"),
        ("4. 三角形三心 (6題，每年必考 1 題)", "九上核心。掌握三心定義與性質（如重心2:1、內心到三邊等距、外心外接圓）。", "#4f46e5"),
        ("5. 二次函數 (6題，每年必考 1 題)", "九下單元。配方法求頂點、對稱性、平移與交點。常結合生活軌跡考極值。", "#4f46e5")
    ]
    
    adv_y = 330
    for idx, (title, desc, col) in enumerate(adv_units):
        c.draw_rect(80, adv_y, 870, 125, "#faf5ff", rx=8, border_color="#e9d5ff", border_width=1)
        c.draw_rect(80, adv_y, 8, 125, col, rx=0)
        c.draw_text(105, adv_y + 15, title, 24, col, "bold")
        c.draw_text(105, adv_y + 48, desc, 22, "#334155", max_width=760, line_spacing=1.35)
        adv_y += 140
 
    # Right Column: Action Plan (Card height = 150, Body = 20 for visual fullness)
    c.draw_rect(1010, 250, 860, 780, "#ffffff", rx=12, border_color="#e9d5ff", border_width=1)
    c.draw_text(1040, 275, "📋 B 到 A 實戰高分拿分指南", 26, "#4c1d95", "bold")
    
    actions_a = [
        ("指南一", "非選題作答步驟化，力求緊扣「定理與邏輯」", "幾何題作答不可僅列算式，必須寫出『因為...，所以...』並註明使用的幾何定理。代數應用題也需寫下變數假設與最終合理性檢驗，以防遭酌扣1分。", "#7c3aed"),
        ("指南二", "建立「幾何輔助線」反射，破解幾何題卡關", "後半段幾何多需輔助線。平時練習應建立反射動作：看到切線連接圓心與切點（垂直）；看到中點構造中線或平行線。多尋找相似形或直角三角形。", "#7c3aed"),
        ("指南三", "建立錯題本，深度挖掘「錯題的考點本質」", "從 B 到 A 的關鍵在於不犯相同錯誤。將寫錯的題目整理至錯題本中，用紅筆標記出『這題考了什麼隱藏觀念』、『當初我的盲點在哪』。考前反覆溫習。", "#4f46e5"),
        ("指南四", "一題多解與限速訓練，提升考場解題應變力", "平時練習對同一個幾何題想出兩種不同解法（如坐標化 vs 相似比），建立多元思路。並在模考時強迫自己縮短前15題時間，保留精力給難題。", "#4f46e5")
    ]
    
    act_y_a = 330
    for label, title, body, col_val in actions_a:
        c.draw_rect(1040, act_y_a, 790, 150, "#faf5ff", rx=8, border_color="#e9d5ff", border_width=1)
        c.draw_rect(1040, act_y_a, 8, 150, col_val, rx=0)
        
        c.draw_rect(1065, act_y_a + 12, 90, 32, col_val, rx=4)
        c.draw_text(1110, act_y_a + 18, label, 16, "#ffffff", "bold", anchor="middle")
        
        c.draw_text(1170, act_y_a + 14, title, 24, col_val, "bold")
        c.draw_text(1065, act_y_a + 55, body, 20, "#334155", max_width=750, line_spacing=1.35)
        act_y_a += 170

    c.save_files("4_strategy_b_to_a")

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    print("Generating Infographics in Landscape 16:9 with Enlarged/Filled Text...")
    build_info_1()
    build_info_2()
    build_info_3()
    build_info_4()
    print("All Large-Text Infographics generated successfully.")
