import io
import math
from typing import List, Tuple

import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageColor

# -----------------------------
# Helpers
# -----------------------------
MM_PER_INCH = 25.4
DEFAULT_DPI = 300

PAPERS = {
    "A4 (210×297mm)": (210, 297),
    "Letter (8.5×11in)": (8.5 * MM_PER_INCH, 11 * MM_PER_INCH),
    "4×6 Photo (inches)": (4 * MM_PER_INCH, 6 * MM_PER_INCH),
}

SHAPES = ["Rounded Rect", "Circle", "Square"]
DECOR_POS = [
    "None",
    "Left",
    "Right",
    "Top",
    "Bottom",
    "Corners",
    "Random (per sticker)",
]


def mm_to_px(mm: float, dpi: int) -> int:
    return int(round(mm / MM_PER_INCH * dpi))


def safe_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def load_font(uploaded, size: int):
    if uploaded is not None:
        try:
            return ImageFont.truetype(uploaded, size=size)
        except Exception:
            st.warning("업로드한 폰트를 불러오지 못했어요. 기본 폰트를 사용합니다.")
            return safe_font(size)
    return safe_font(size)


def draw_rounded_rectangle(draw: ImageDraw.ImageDraw, xy: Tuple[int, int, int, int], radius: int, fill, outline=None, width: int = 1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def place_decor(base: Image.Image, decor: Image.Image, where: str, margin_px: int, scale: float, rng_seed: int = 0):
    import random
    rnd = random.Random(rng_seed)
    W, H = base.size
    d = decor.convert("RGBA")
    short_side = min(W, H)
    target = int(short_side * scale)
    if target <= 0:
        return base
    w, h = d.size
    ratio = target / max(w, h)
    nw, nh = max(1, int(w * ratio)), max(1, int(h * ratio))
    d = d.resize((nw, nh), Image.LANCZOS)

    positions = []
    if where == "Left":
        positions = [(margin_px, (H - nh) // 2)]
    elif where == "Right":
        positions = [(W - nw - margin_px, (H - nh) // 2)]
    elif where == "Top":
        positions = [((W - nw) // 2, margin_px)]
    elif where == "Bottom":
        positions = [((W - nw) // 2, H - nh - margin_px)]
    elif where == "Corners":
        positions = [
            (margin_px, margin_px),
            (W - nw - margin_px, margin_px),
            (margin_px, H - nh - margin_px),
            (W - nw - margin_px, H - nh - margin_px),
        ]
    elif where == "Random (per sticker)":
        positions = [(rnd.randint(margin_px, max(margin_px, W - nw - margin_px)),
                      rnd.randint(margin_px, max(margin_px, H - nh - margin_px)))]
    else:
        return base

    canvas = base.convert("RGBA")
    for (x, y) in positions:
        canvas.alpha_composite(d, (x, y))
    return canvas.convert("RGB")


def create_single_sticker(
    text: str,
    sticker_w_mm: float,
    sticker_h_mm: float,
    dpi: int,
    bg_color: Tuple[int, int, int],
    text_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int],
    border_px: int,
    radius_px: int,
    shape: str,
    font_file,
    font_scale: float,
    padding_mm: float,
    decor_img: Image.Image | None,
    decor_where: str,
    decor_scale: float,
) -> Image.Image:
    W = mm_to_px(sticker_w_mm, dpi)
    H = mm_to_px(sticker_h_mm, dpi)
    pad = mm_to_px(padding_mm, dpi)

    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    inner = (border_px, border_px, W - border_px - 1, H - border_px - 1)

    if shape == "Circle":
        r = min(W, H) // 2 - border_px
        cx, cy = W // 2, H // 2
        bbox = (cx - r, cy - r, cx + r, cy + r)
        draw.ellipse(bbox, fill=bg_color, outline=border_color, width=border_px)
        text_box = bbox
    elif shape == "Square":
        side = min(W, H) - 2 * border_px
        x0 = (W - side) // 2
        y0 = (H - side) // 2
        bbox = (x0, y0, x0 + side, y0 + side)
        draw.rectangle(bbox, fill=bg_color, outline=border_color, width=border_px)
        text_box = bbox
    else:
        draw_rounded_rectangle(draw, inner, radius_px, fill=bg_color, outline=border_color, width=border_px)
        text_box = inner

    short = min(W, H)
    font_px = max(10, int(short * font_scale))
    font = load_font(font_file, font_px)

    tw, th = draw.textbbox((0, 0), text, font=font)[2:]
    max_w = (text_box[2] - text_box[0]) - 2 * pad
    max_h = (text_box[3] - text_box[1]) - 2 * pad
    while (tw > max_w or th > max_h) and font_px > 8:
        font_px = int(font_px * 0.9)
        font = load_font(font_file, font_px)
        tw, th = draw.textbbox((0, 0), text, font=font)[2:]

    tx = text_box[0] + (max_w - tw) // 2 + pad
    ty = text_box[1] + (max_h - th) // 2 + pad

    draw.text((tx, ty), text, font=font, fill=text_color)

    if decor_img is not None and decor_where != "None":
        img = place_decor(img, decor_img, decor_where, margin_px=pad, scale=decor_scale, rng_seed=hash(text) & 0xFFFF)

    return img


def pack_sheet(sticker: Image.Image, paper_mm: Tuple[float, float], dpi: int, margin_mm: float, gap_mm: float, cols: int | None, rows: int | None) -> Image.Image:
    Wp = mm_to_px(paper_mm[0], dpi)
    Hp = mm_to_px(paper_mm[1], dpi)
    margin = mm_to_px(margin_mm, dpi)
    gap = mm_to_px(gap_mm, dpi)

    sheet = Image.new("RGB", (Wp, Hp), (255, 255, 255))

    sw, sh = sticker.size
    max_cols = max(1, (Wp - 2 * margin + gap) // (sw + gap))
    max_rows = max(1, (Hp - 2 * margin + gap) // (sh + gap))

    if cols is None or cols <= 0 or cols > max_cols:
        cols = max_cols
    if rows is None or rows <= 0 or rows > max_rows:
        rows = max_rows

    used_w = cols * sw + (cols - 1) * gap
    used_h = rows * sh + (rows - 1) * gap
    x0 = (Wp - used_w) // 2
    y0 = (Hp - used_h) // 2

    for i in range(rows):
        for j in range(cols):
            x = x0 + j * (sw + gap)
            y = y0 + i * (sh + gap)
            sheet.paste(sticker, (x, y))
    return sheet

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🎨 네임스티커 사진 생성기")

text = st.text_input("스티커 글자 (1~5자)", "홍길동")
sticker_w = st.number_input("스티커 가로(mm)", 20, 100, 40)
sticker_h = st.number_input("스티커 세로(mm)", 20, 100, 30)

bg_color = st.color_picker("배경 색상", "#FFFFFF")
text_color = st.color_picker("글자 색상", "#000000")
border_color = st.color_picker("테두리 색상", "#000000")
border_px = st.slider("테두리 두께(px)", 0, 10, 2)
radius_px = st.slider("모서리 둥글기(px)", 0, 50, 10)

shape = st.selectbox("스티커 모양", SHAPES)

font_file = st.file_uploader("폰트 업로드 (ttf/otf)")
font_scale = st.slider("폰트 크기 비율", 0.1, 1.0, 0.5)
padding_mm = st.slider("여백 (mm)", 0, 10, 2)

decor_file = st.file_uploader("장식 이미지 업로드 (png)")
decor_where = st.selectbox("장식 위치", DECOR_POS)
decor_scale = st.slider("장식 크기 비율", 0.05, 0.5, 0.2)

paper = st.selectbox("출력 용지", list(PAPERS.keys()))
margin_mm = st.slider("여백 (mm)", 0, 20, 5)
gap_mm = st.slider("스티커 간격 (mm)", 0, 10, 2)

if st.button("스티커 생성"):
    decor_img = None
    if decor_file:
        decor_img = Image.open(decor_file)

    sticker_img = create_single_sticker(
        text, sticker_w, sticker_h, DEFAULT_DPI,
        ImageColor.getrgb(bg_color),
        ImageColor.getrgb(text_color),
        ImageColor.getrgb(border_color),
        border_px, radius_px, shape,
        font_file, font_scale, padding_mm,
        decor_img, decor_where, decor_scale
    )

    st.subheader("개별 스티커 미리보기")
    st.image(sticker_img)

    buf_single = io.BytesIO()
    sticker_img.save(buf_single, format="PNG")
    st.download_button("개별 스티커 다운로드", buf_single.getvalue(), "sticker.png", "image/png")

    sheet_img = pack_sheet(sticker_img, PAPERS[paper], DEFAULT_DPI, margin_mm, gap_mm, None, None)
    st.subheader("전체 시트 미리보기")
    st.image(sheet_img)

    buf_sheet = io.BytesIO()
    sheet_img.save(buf_sheet, format="PNG")
    st.download_button("전체 시트 다운로드", buf_sheet.getvalue(), "sticker_sheet.png", "image/png")

