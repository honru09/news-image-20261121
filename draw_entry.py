#!/usr/bin/env python3
"""
Draws the 1024x1024 newspaper front-page infographic entry.png
for Saturday, 21 November 2026 using only Pillow and Python stdlib.
"""

import hashlib
import math
import os
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1024
HEIGHT = 1024

# Color palette: clean off-white newsprint, dark ink, one red accent, plus scene colors
PAPER_BG = (246, 242, 233)       # Off-white newspaper stock
CARD_TINT = (238, 233, 221)      # Subtle warm tint for icon boxes
INK_DARK = (20, 20, 22)          # Primary dark ink
INK_BODY = (34, 34, 38)          # High-contrast body copy ink
RULE_DARK = (55, 53, 48)         # Structural divider line
RULE_LIGHT = (182, 176, 164)     # Grid divider rule
RED_ACCENT = (194, 28, 28)       # Classic newspaper red accent

# Lead scene palette (dark sky band, drone silhouettes, orange bursts)
SKY_TOP = (15, 20, 30)
SKY_MID = (24, 31, 46)
SKY_HORIZON = (36, 42, 58)
CITY_SILHOUETTE = (10, 13, 20)
DRONE_FILL = (226, 231, 240)
DRONE_TRAIL = (124, 136, 156)
BURST_OUTER = (228, 92, 22)
BURST_MID = (246, 146, 34)
BURST_CORE = (255, 214, 92)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_SANS_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required font not found: {path}")
    return ImageFont.truetype(path, size)


def measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont):
    bbox = font.getbbox(text)
    width = draw.textlength(text, font=font)
    height = bbox[3] - bbox[1]
    return width, height, bbox


def wrap_text_to_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def fit_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: str,
    start_size: int,
    min_size: int,
    max_width: int,
    max_height: int,
    max_lines: int,
    line_spacing_ratio: float = 1.22,
):
    """
    Finds the largest font size <= start_size such that wrapped text fits
    within max_width, max_height, and max_lines without clipping.
    """
    for size in range(start_size, min_size - 1, -1):
        font = load_font(font_path, size)
        lines = wrap_text_to_width(draw, text, font, max_width)
        if len(lines) > max_lines:
            continue
        if any(draw.textlength(line, font=font) > max_width for line in lines):
            continue
        line_step = int(round(size * line_spacing_ratio))
        last_bbox = font.getbbox(lines[-1])
        first_bbox = font.getbbox(lines[0])
        total_h = (len(lines) - 1) * line_step + (last_bbox[3] - first_bbox[1])
        if total_h <= max_height:
            return font, lines, line_step, total_h
    raise ValueError(f"Could not fit text '{text}' in {max_width}x{max_height}")


def draw_fitted_lines(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    line_step: int,
    fill: tuple[int, int, int],
) -> int:
    """Draws wrapped lines starting with visual top at y, returns bottom y."""
    if not lines:
        return y
    first_top = font.getbbox(lines[0])[1]
    cur_y = y - first_top
    bottom_y = y
    for i, line in enumerate(lines):
        ly = cur_y + i * line_step
        draw.text((x, ly), line, font=font, fill=fill)
        bbox = font.getbbox(line)
        bottom_y = max(bottom_y, ly + bbox[3])
    return bottom_y


def draw_starburst(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    outer_r: float,
    inner_r: float,
    points: int,
    fill: tuple[int, int, int],
    rotation_deg: float = 0.0,
):
    pts = []
    for i in range(points * 2):
        angle = math.radians(rotation_deg + i * (180.0 / points))
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, fill=fill)


def draw_drone_silhouette(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    scale: float = 1.0,
    angle_deg: float = 14.0,
):
    """
    Draws a crisp delta-wing attack drone silhouette oriented along angle_deg.
    """
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    def tf(px: float, py: float):
        rx = (px * cos_a - py * sin_a) * scale + cx
        ry = (px * sin_a + py * cos_a) * scale + cy
        return (rx, ry)

    # Dashed motion trail behind drone
    for seg in range(1, 4):
        x0 = -18 - seg * 12
        x1 = x0 + 6
        draw.line([tf(x0, 0), tf(x1, 0)], fill=DRONE_TRAIL, width=2)

    # Delta wing + nose fuselage polygon
    body = [
        tf(18, 0),    # Nose tip
        tf(5, -4),    # Forward fuselage top
        tf(-11, -15), # Upper wingtip leading edge
        tf(-15, -15), # Upper wingtip fin
        tf(-12, -3),  # Inner wing root
        tf(-16, 0),   # Pusher tail center
        tf(-12, 3),   # Inner wing root bottom
        tf(-15, 15),  # Lower wingtip fin
        tf(-11, 15),  # Lower wingtip leading edge
        tf(5, 4),     # Forward fuselage bottom
    ]
    draw.polygon(body, fill=DRONE_FILL)


def draw_lead_scene(base_img: Image.Image, x0: int, y0: int, w: int, h: int):
    """
    Draws the lead story illustration on a dedicated clipped sub-canvas
    using only PIL geometric shapes: dark night sky band, horizon skyline
    silhouette, drone silhouettes, and orange explosion bursts.
    """
    scene = Image.new("RGB", (w, h), SKY_TOP)
    sdraw = ImageDraw.Draw(scene)

    # 3-band dark night sky
    band1_h = int(h * 0.42)
    band2_h = int(h * 0.78)
    sdraw.rectangle([0, 0, w, band1_h], fill=SKY_TOP)
    sdraw.rectangle([0, band1_h, w, band2_h], fill=SKY_MID)
    sdraw.rectangle([0, band2_h, w, h], fill=SKY_HORIZON)

    # Subtle radar grid lines in dark sky
    for gx in range(90, w, 110):
        sdraw.line([(gx, 6), (gx, h - 18)], fill=(34, 43, 62), width=1)

    # Orange bursts kept well inside the sky band above the skyline
    bursts = [
        (248, 52, 24, 10, 10, 15.0),
        (468, 60, 29, 12, 12, 8.0),
        (692, 46, 22, 10, 10, 22.0),
        (826, 60, 27, 11, 12, 35.0),
    ]
    for bx, by, orad, irad, pts, rot in bursts:
        sdraw.ellipse(
            [bx - orad - 5, by - orad - 5, bx + orad + 5, by + orad + 5],
            outline=RED_ACCENT,
            width=2,
        )
        draw_starburst(sdraw, bx, by, orad, irad, pts, BURST_OUTER, rot)
        draw_starburst(sdraw, bx, by, orad * 0.72, irad * 0.72, pts, BURST_MID, rot + 15)
        draw_starburst(sdraw, bx, by, orad * 0.40, irad * 0.40, 8, BURST_CORE, rot)

    # Incoming missile/interceptor trajectories
    sdraw.line([(382, 14), (460, 54)], fill=BURST_MID, width=2)
    sdraw.line([(764, 14), (820, 54)], fill=BURST_MID, width=2)

    # Drone silhouettes flying across the dark sky band
    drones = [
        (142, 34, 1.05, 16.0),
        (336, 28, 0.95, 14.0),
        (566, 34, 1.08, 18.0),
        (624, 68, 0.85, 12.0),
        (886, 32, 0.95, 15.0),
    ]
    for dx, dy, sc, ang in drones:
        draw_drone_silhouette(sdraw, dx, dy, scale=sc, angle_deg=ang)

    # Bottom skyline silhouette band
    skyline_blocks = [
        (0, 13, 48), (48, 20, 36), (84, 16, 52), (136, 23, 40),
        (176, 12, 64), (240, 18, 44), (284, 14, 58), (342, 22, 38),
        (380, 13, 62), (442, 24, 42), (484, 16, 56), (540, 12, 66),
        (606, 21, 46), (652, 15, 54), (706, 23, 42), (748, 13, 60),
        (808, 19, 48), (856, 15, 44), (900, 12, 40),
    ]
    for sx, sh, sw in skyline_blocks:
        bx0 = sx
        bx1 = min(w, bx0 + sw)
        sdraw.rectangle([bx0, h - sh, bx1, h], fill=CITY_SILHOUETTE)

    # Crisp frame around scene
    sdraw.rectangle([0, 0, w - 1, h - 1], outline=INK_DARK, width=2)
    base_img.paste(scene, (x0, y0))


def draw_story_icon(draw: ImageDraw.ImageDraw, kind: str, x0: int, y0: int, size: int):
    """
    Draws a tiny simple geometric icon inside a size x size box at (x0, y0).
    """
    x1 = x0 + size
    y1 = y0 + size
    cx = x0 + size / 2.0
    cy = y0 + size / 2.0

    # Icon frame
    draw.rectangle([x0, y0, x1, y1], fill=CARD_TINT, outline=INK_DARK, width=2)

    if kind == "markets_down":
        draw.line([(x0 + 8, y1 - 10), (x1 - 8, y1 - 10)], fill=INK_DARK, width=2)
        draw.line([(x0 + 8, y0 + 10), (x0 + 8, y1 - 10)], fill=INK_DARK, width=2)
        pts = [(x0 + 11, y0 + 14), (x0 + 22, y0 + 23), (x0 + 29, y0 + 19), (x1 - 11, y1 - 15)]
        draw.line(pts, fill=RED_ACCENT, width=3)
        draw.polygon(
            [(x1 - 9, y1 - 13), (x1 - 19, y1 - 14), (x1 - 11, y1 - 23)],
            fill=RED_ACCENT,
        )

    elif kind == "world_court":
        draw.line([(cx, y0 + 9), (cx, y1 - 10)], fill=INK_DARK, width=3)
        draw.rectangle([cx - 12, y1 - 11, cx + 12, y1 - 8], fill=INK_DARK)
        draw.line([(x0 + 10, y0 + 16), (x1 - 10, y0 + 16)], fill=INK_DARK, width=3)
        for px in (x0 + 13, x1 - 13):
            draw.line([(px, y0 + 16), (px - 5, y0 + 29)], fill=INK_DARK, width=2)
            draw.line([(px, y0 + 16), (px + 5, y0 + 29)], fill=INK_DARK, width=2)
            draw.polygon([(px - 7, y0 + 29), (px + 7, y0 + 29), (px, y0 + 34)], fill=RED_ACCENT)

    elif kind == "peace_statement":
        r = 9
        centers = [(cx, y0 + 17), (cx - 8, y0 + 29), (cx + 8, y0 + 29)]
        for i, (rcx, rcy) in enumerate(centers):
            col = RED_ACCENT if i == 0 else INK_DARK
            draw.ellipse([rcx - r, rcy - r, rcx + r, rcy + r], outline=col, width=3)

    elif kind == "listing_drop":
        bars = [
            (x0 + 10, y0 + 13, y0 + 26, INK_DARK),
            (x0 + 21, y0 + 19, y0 + 33, INK_DARK),
            (x0 + 32, y0 + 25, y1 - 9, RED_ACCENT),
        ]
        for bx, top, bot, col in bars:
            draw.line([(bx + 3, top - 4), (bx + 3, bot + 3)], fill=col, width=2)
            draw.rectangle([bx, top, bx + 6, bot], fill=col)

    elif kind == "hackers_breach":
        draw.arc([cx - 8, y0 + 8, cx + 8, y0 + 24], start=180, end=0, fill=INK_DARK, width=3)
        draw.rectangle([x0 + 12, y0 + 20, x1 - 12, y1 - 9], outline=INK_DARK, width=2)
        bolt = [
            (cx + 2, y0 + 15),
            (cx - 5, y0 + 26),
            (cx + 1, y0 + 26),
            (cx - 3, y1 - 11),
        ]
        draw.line(bolt, fill=RED_ACCENT, width=3)

    elif kind == "strikes_target":
        draw.ellipse([x0 + 10, y0 + 10, x1 - 10, y1 - 10], outline=INK_DARK, width=2)
        draw.ellipse([x0 + 17, y0 + 17, x1 - 17, y1 - 17], outline=RED_ACCENT, width=2)
        draw.line([(cx, y0 + 6), (cx, y1 - 6)], fill=INK_DARK, width=2)
        draw.line([(x0 + 6, cy), (x1 - 6, cy)], fill=INK_DARK, width=2)
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED_ACCENT)

    elif kind == "climate_deadline":
        draw.ellipse([x0 + 9, y0 + 9, x1 - 9, y1 - 9], outline=INK_DARK, width=2)
        draw.arc([x0 + 9, y0 + 15, x1 - 9, y1 - 15], start=0, end=180, fill=RULE_LIGHT, width=1)
        draw.line([(cx, cy), (cx, y0 + 13)], fill=INK_DARK, width=3)
        draw.line([(cx, cy), (x1 - 13, y0 + 16)], fill=RED_ACCENT, width=3)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=INK_DARK)

    elif kind == "eu_marches":
        cone = [(x0 + 11, cy + 2), (x1 - 13, y0 + 12), (x1 - 13, y1 - 14)]
        draw.polygon(cone, fill=INK_DARK)
        draw.line([(x0 + 15, cy + 3), (x0 + 18, y1 - 9)], fill=INK_DARK, width=3)
        draw.line([(x1 - 9, cy - 6), (x1 - 5, cy - 10)], fill=RED_ACCENT, width=3)
        draw.line([(x1 - 9, cy), (x1 - 4, cy)], fill=RED_ACCENT, width=3)
        draw.line([(x1 - 9, cy + 6), (x1 - 5, cy + 10)], fill=RED_ACCENT, width=3)


def build_entry():
    img = Image.new("RGB", (WIDTH, HEIGHT), PAPER_BG)
    draw = ImageDraw.Draw(img)

    margin_x = 42
    content_w = WIDTH - 2 * margin_x
    right_x = WIDTH - margin_x

    # Outer newspaper frame
    draw.rectangle([18, 18, WIDTH - 18, HEIGHT - 18], outline=RULE_DARK, width=2)

    # =========================================================================
    # 1. MASTHEAD ("WORLD NEWS" + "SATURDAY, 21 NOVEMBER 2026")
    # =========================================================================
    draw.rectangle([margin_x, 30, right_x, 35], fill=RED_ACCENT)
    draw.line([(margin_x, 39), (right_x, 39)], fill=INK_DARK, width=2)

    masthead_title = "WORLD NEWS"
    font_masthead = load_font(FONT_SERIF_BOLD, 54)
    mw, mh, mbbox = measure_text(draw, masthead_title, font_masthead)
    mx = (WIDTH - mw) / 2.0
    my = 44 - mbbox[1]
    draw.text((mx, my), masthead_title, font=font_masthead, fill=INK_DARK)

    # Geometric globe emblems flanking the masthead
    for ex in (margin_x + 36, right_x - 36):
        ey = 72
        draw.ellipse([ex - 16, ey - 16, ex + 16, ey + 16], outline=INK_DARK, width=2)
        draw.ellipse([ex - 8, ey - 16, ex + 8, ey + 16], outline=INK_DARK, width=1)
        draw.line([(ex - 16, ey), (ex + 16, ey)], fill=RED_ACCENT, width=2)

    draw.line([(margin_x, 105), (right_x, 105)], fill=INK_DARK, width=1)

    masthead_date = "SATURDAY, 21 NOVEMBER 2026"
    font_date = load_font(FONT_SANS_BOLD, 18)
    dw, dh, dbbox = measure_text(draw, masthead_date, font_date)
    dx = (WIDTH - dw) / 2.0
    dy = 112 - dbbox[1]
    draw.text((dx, dy), masthead_date, font=font_date, fill=INK_DARK)

    # Red square accents flanking the date
    draw.rectangle([dx - 22, 117, dx - 14, 125], fill=RED_ACCENT)
    draw.rectangle([dx + dw + 14, 117, dx + dw + 22, 125], fill=RED_ACCENT)

    draw.line([(margin_x, 137), (right_x, 137)], fill=INK_DARK, width=3)
    draw.line([(margin_x, 142), (right_x, 142)], fill=INK_DARK, width=1)

    # =========================================================================
    # 2. LEAD STORY BLOCK
    # =========================================================================
    scene_y0 = 152
    scene_h = 104
    draw_lead_scene(img, margin_x, scene_y0, content_w, scene_h)

    lead_headline = "Russia's largest overnight air assault on Ukraine"
    lead_line = (
        "Over 400 drones and 110 missiles; some fell in Poland; "
        "Poland's PM calls it a deliberate provocation."
    )

    lead_text_y0 = scene_y0 + scene_h + 14
    lead_bar_x0 = margin_x
    lead_bar_x1 = margin_x + 8
    lead_tx = margin_x + 20
    lead_tw = content_w - 20

    font_lead_h, lead_h_lines, lead_h_step, _ = fit_wrapped_text(
        draw,
        lead_headline,
        FONT_SANS_BOLD,
        start_size=34,
        min_size=24,
        max_width=lead_tw,
        max_height=52,
        max_lines=1,
    )
    h_bottom = draw_fitted_lines(
        draw, lead_tx, lead_text_y0, lead_h_lines, font_lead_h, lead_h_step, INK_DARK
    )

    lead_sub_y0 = h_bottom + 9
    font_lead_b, lead_b_lines, lead_b_step, _ = fit_wrapped_text(
        draw,
        lead_line,
        FONT_SANS_REG,
        start_size=21,
        min_size=15,
        max_width=lead_tw,
        max_height=58,
        max_lines=2,
        line_spacing_ratio=1.24,
    )
    b_bottom = draw_fitted_lines(
        draw, lead_tx, lead_sub_y0, lead_b_lines, font_lead_b, lead_b_step, INK_BODY
    )

    draw.rectangle([lead_bar_x0, lead_text_y0, lead_bar_x1, b_bottom], fill=RED_ACCENT)

    grid_top_rule_y = b_bottom + 14
    draw.line([(margin_x, grid_top_rule_y), (right_x, grid_top_rule_y)], fill=INK_DARK, width=2)

    # =========================================================================
    # 3. 8 MORE STORIES IN A TIDY 2-COLUMN GRID (2 cols x 4 rows)
    # =========================================================================
    stories = [
        (
            "AI shares slide, US markets enter correction",
            "The S&P 500 and Dow drop 3.7% as AI stocks fall.",
            "markets_down",
        ),
        (
            "World court: Myanmar guilty over Rohingya",
            "The ICJ finds Myanmar responsible for genocide against the Rohingya.",
            "world_court",
        ),
        (
            "Trump, Xi, Putin sign joint peace statement",
            "The three leaders issue a peace declaration after meeting in Shenzhen.",
            "peace_statement",
        ),
        (
            "Anthropic shares fall sharply after listing",
            "A weak start after its debut rattles AI stocks.",
            "listing_drop",
        ),
        (
            "Hackers break into US farm department and FBI",
            "Reports say intruders breached two US agencies.",
            "hackers_breach",
        ),
        (
            "Trump considers fresh strikes on Iran",
            "Israel urges action while Iran's foreign minister seeks talks.",
            "strikes_target",
        ),
        (
            "COP31 climate talks pass their deadline",
            "Negotiators remain split over fossil fuels.",
            "climate_deadline",
        ),
        (
            "Gen Z marches spread across 25 European states",
            "Youth-led protests reach 25 countries in Europe.",
            "eu_marches",
        ),
    ]

    footer_rule_y = 956
    grid_y0 = grid_top_rule_y + 4
    grid_y1 = footer_rule_y - 4
    grid_h = grid_y1 - grid_y0
    num_rows = 4
    row_h = grid_h // num_rows

    col_gap = 32
    col_w = (content_w - col_gap) // 2
    col_x = [margin_x, margin_x + col_w + col_gap]
    mid_x = margin_x + col_w + col_gap // 2

    # Central vertical divider rule
    draw.line([(mid_x, grid_y0 + 6), (mid_x, grid_y1 - 6)], fill=RULE_LIGHT, width=2)

    icon_size = 50
    icon_gap = 14

    for idx, (headline, line, icon_kind) in enumerate(stories):
        row = idx // 2
        col = idx % 2

        cell_x = col_x[col]
        cell_y = grid_y0 + row * row_h
        cell_bottom = cell_y + row_h

        if col == 0 and row > 0:
            draw.line(
                [(margin_x, cell_y), (right_x, cell_y)],
                fill=RULE_LIGHT,
                width=1,
            )

        tx = cell_x + icon_size + icon_gap
        tw = col_w - icon_size - icon_gap

        # Pre-fit headline and body line to compute vertical centering in cell
        font_sh, sh_lines, sh_step, sh_h = fit_wrapped_text(
            draw,
            headline,
            FONT_SANS_BOLD,
            start_size=22,
            min_size=16,
            max_width=tw,
            max_height=58,
            max_lines=2,
            line_spacing_ratio=1.20,
        )
        font_sb, sb_lines, sb_step, sb_h = fit_wrapped_text(
            draw,
            line,
            FONT_SANS_REG,
            start_size=18,
            min_size=13,
            max_width=tw,
            max_height=52,
            max_lines=2,
            line_spacing_ratio=1.22,
        )

        gap_hb = 8
        block_h = max(icon_size, sh_h + gap_hb + sb_h)
        pad_top = max(12, (row_h - block_h) // 2)

        ix = cell_x
        iy = cell_y + pad_top
        draw_story_icon(draw, icon_kind, ix, iy, icon_size)

        sh_bottom = draw_fitted_lines(
            draw, tx, cell_y + pad_top, sh_lines, font_sh, sh_step, INK_DARK
        )
        sb_bottom = draw_fitted_lines(
            draw, tx, sh_bottom + gap_hb, sb_lines, font_sb, sb_step, INK_BODY
        )

        if sb_bottom > cell_bottom - 4:
            raise AssertionError(
                f"Story {idx + 2} overflowed cell bottom ({sb_bottom} > {cell_bottom - 4})"
            )

    # =========================================================================
    # 4. FOOTER
    # =========================================================================
    draw.line([(margin_x, footer_rule_y), (right_x, footer_rule_y)], fill=INK_DARK, width=2)
    draw.rectangle([margin_x, footer_rule_y + 4, right_x, footer_rule_y + 7], fill=RED_ACCENT)

    footer_text = "21 November 2026 — the day in world news"
    font_footer = load_font(FONT_SANS_BOLD, 17)
    fw, fh, fbbox = measure_text(draw, footer_text, font_footer)
    fx = (WIDTH - fw) / 2.0
    fy = footer_rule_y + 15 - fbbox[1]
    draw.text((fx, fy), footer_text, font=font_footer, fill=INK_DARK)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out_path, format="PNG", optimize=True)

    size_bytes = os.path.getsize(out_path)
    with open(out_path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()

    with Image.open(out_path) as check_img:
        assert check_img.size == (1024, 1024), f"Unexpected size: {check_img.size}"
    assert size_bytes < 1024 * 1024, f"File too large: {size_bytes} bytes"

    print(f"Saved: {out_path}")
    print(f"Dimensions: 1024x1024")
    print(f"Bytes: {size_bytes}")
    print(f"SHA256: {digest}")


if __name__ == "__main__":
    build_entry()
