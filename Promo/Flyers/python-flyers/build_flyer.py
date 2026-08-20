#!/usr/bin/env python3
# Build a print-ready A5 flyer for DoES Liverpool from real photos of the space.
# A5 portrait @ 300 dpi, 3 mm bleed. Canvas 1818 x 2550; page area 1748 x 2480.
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "site"))

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
FONTS = os.path.join(HERE, "fonts")

# ---------- layout constants ----------
BLEED = 35          # 3 mm at 300 dpi
PAGE_W, PAGE_H = 1748, 2480
W, H = PAGE_W + 2 * BLEED, PAGE_H + 2 * BLEED
M = 80              # page margin

# variant: --nologo drops the sub-headline sentence in the hero, the white
# logo in the black strip, and shifts everything up by the sentence height.
NOLOGO = "--nologo" in sys.argv

# ---------- palette ----------
BLACK = (17, 17, 17)
YELLOW = (255, 209, 0)
PAPER = (250, 248, 243)
STRIP = (237, 234, 226)
GRAY = (90, 90, 90)
WHITE = (255, 255, 255)

# ---------- fonts ----------
_font_cache = {}

def font(kind, size, weight=None):
    key = (kind, size, weight)
    if key in _font_cache:
        return _font_cache[key]
    if kind == "anton":
        f = ImageFont.truetype(os.path.join(FONTS, "Anton-Regular.ttf"), size)
    elif kind == "raoul":
        f = ImageFont.truetype(os.path.join(FONTS, "RaoulTRANSPORTBritannique.ttf"), size)
    elif kind == "bebas":
        f = ImageFont.truetype(os.path.join(FONTS, "BebasNeue-Regular.ttf"), size)
    elif kind == "archivo":
        f = ImageFont.truetype(os.path.join(FONTS, "Archivo"), size)
        try:
            f.set_variation_by_axes([weight if weight else 400, 100])
        except Exception:
            pass
    elif kind == "mono":
        f = ImageFont.truetype(os.path.join(FONTS, "JetBrainsMono.ttf"), size)
        try:
            f.set_variation_by_axes([weight if weight else 400])
        except Exception:
            pass
    else:
        raise ValueError(kind)
    _font_cache[key] = f
    return f

def arch(size, weight=400):
    return font("archivo", size, weight)

def mono(size, weight=400):
    return font("mono", size, weight)

# ---------- helpers ----------
def wrap(draw, text, f, max_w):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def spaced_w(draw, text, f, tracking=3):
    return sum(draw.textlength(c, font=f) for c in text) + (len(text) - 1) * tracking

def draw_spaced(d, xy, text, f, tracking=3, fill=BLACK):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tracking

def cover(src, w, h, centering=(0.5, 0.5)):
    im = Image.open(src)
    if im.mode != "RGB":
        im = im.convert("RGB")
    return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=centering)

def paste(img, piece, x, y):
    img.paste(piece, (x, y), piece if piece.mode == "RGBA" else None)

# ---------- logo variants ----------
def make_logo_variants():
    im = Image.open(os.path.join(ASSETS, "DoESLiverpool.png")).convert("L")
    px = im.load()
    black = Image.new("RGBA", im.size)
    white = Image.new("RGBA", im.size)
    bp, wp = black.load(), white.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            if px[x, y] < 128:
                bp[x, y] = (0, 0, 0, 255)
                wp[x, y] = (255, 255, 255, 255)
    black.save(os.path.join(ASSETS, "logo_black.png"))
    white.save(os.path.join(ASSETS, "logo_white.png"))
    return black, white

# ---------- vertical layout (canvas coords) ----------
# Hero sub-headline sentence (removed in the --nologo variant). Its height is
# the amount everything below the headline moves up by.
SUB_TEXT = "A proper workshop, desks to rent, and a community of makers, hackers & creatives in the heart of Liverpool."
SUB_F = font("archivo", 33, 500)
SUB_LINES = wrap(ImageDraw.Draw(Image.new("RGB", (10, 10))), SUB_TEXT, SUB_F, 1200)
SUB_H = (len(SUB_LINES) * 44) if NOLOGO else 0

HERO_H = 1080 - SUB_H
WY = BLEED + HERO_H                       # white section top
TILE_Y = WY + 300
TILE_H = 292
TILE_GAP = 18
STRIP_Y = TILE_Y + TILE_H + 14
STRIP_H = 68
BY = STRIP_Y + STRIP_H                    # black strip top
BLACK_H = 276
BAND_Y = BY + BLACK_H                     # yellow price band
BAND_H = 96
FY = BAND_Y + BAND_H                      # footer top
FOOTER_H = PAGE_H + BLEED - FY

def assert_fits(label, y_end, limit):
    assert y_end <= limit + 1, f"{label}: {y_end} > {limit}"

# ---------- original variant (frozen) ----------
def build_original():
    make_logo_variants()
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ================= HERO =================
    # Always fit the full 1080 px window so the retained region is
    # pixel-identical between variants; the --nologo variant then crops the
    # bottom SUB_H px (the space the removed sentence occupied).
    HERO_FULL = 1080
    hero = cover(os.path.join(ASSETS, "MainRoomWideShot.jpg"), W, HERO_FULL)

    # top gradient (wordmark legibility), bottom gradient (headline)
    def v_gradient(target, y0, y1, a0, a1):
        g = Image.new("L", (1, y1 - y0))
        for i in range(y1 - y0):
            g.putpixel((0, i), int(a0 + (a1 - a0) * i / (y1 - y0)))
        g = g.resize((W, y1 - y0))
        ov = Image.new("RGB", (W, y1 - y0), BLACK)
        ov.putalpha(g)
        target.paste(ov, (0, y0), ov)

    v_gradient(hero, 0, 300, 150, 0)
    v_gradient(hero, int(HERO_FULL * 0.30), HERO_FULL, 0, 240)
    if NOLOGO:
        hero = hero.crop((0, 0, W, HERO_H))
    img.paste(hero, (0, 0))
    d = ImageDraw.Draw(img)

    px = lambda v: v + BLEED

    # top-left brand chip + wordmark
    chip_s = 104
    chip = Image.new("RGBA", (chip_s, chip_s), YELLOW)
    bird = Image.open(os.path.join(ASSETS, "doesloverpoollogo.png")).convert("RGBA")
    bs = int(chip_s * 0.86)
    bird = bird.resize((bs, bs), Image.LANCZOS)
    chip.paste(bird, ((chip_s - bs) // 2, (chip_s - bs) // 2), bird)
    paste(img, chip, px(M), px(58))
    d.text((px(M) + chip_s + 28, px(64)), "DOES LIVERPOOL", font=font("anton", 56), fill=WHITE)
    d.text((px(M) + chip_s + 30, px(64) + 66), "COMMUNITY MAKER SPACE & CO-WORKING", font=mono(22, 500), fill=YELLOW)

    # headline: COME AND DO / EPIC STUFF.
    hl = font("anton", 150)
    y1 = 585                      # line 1 (canvas)
    y2 = y1 + 166                 # line 2
    d.text((px(M), y1), "COME AND DO", font=hl, fill=WHITE)
    d.text((px(M), y2), "EPIC ", font=hl, fill=YELLOW)
    ew = d.textlength("EPIC ", font=hl)
    d.text((px(M) + ew, y2), "STUFF.", font=hl, fill=WHITE)

    if not NOLOGO:
        sub = SUB_TEXT
        sub_f = SUB_F
        sub_lines = SUB_LINES
        sy = y2 + 168
        for ln in sub_lines:
            d.text((px(M), sy), ln, font=sub_f, fill=WHITE)
            sy += 44
        assert_fits("hero text", sy - 1, HERO_H)
    else:
        assert_fits("hero headline", y2 + 166, HERO_H)

    # ================= WORKSHOP SECTION =================
    d.text((px(M), WY + 52), "THE WORKSHOP", font=font("bebas", 78), fill=BLACK)
    d.rectangle([px(M), WY + 128, px(M) + 210, WY + 140], fill=YELLOW)

    para = ("A proper workshop in the middle of town \u2014 laser cutters, 3D printers, a CNC mill and router, "
            "a stocked electronics bench, embroidery & sewing machines, vinyl cutting and more. "
            "No membership needed to use it.")
    p_f = arch(31, 400)
    p_lines = wrap(d, para, p_f, PAGE_W - 2 * M)
    py = WY + 166
    for ln in p_lines:
        d.text((px(M), py), ln, font=p_f, fill=(40, 40, 40))
        py += 43
    assert_fits("workshop para", py - 1, TILE_Y - 6)

    # equipment tiles
    tiles = [
        ("LaserCutterWorkshop.jpg",   "01 \u00b7 LASER CUTTERS"),
        ("3DPrinters.jpg",            "02 \u00b7 3D PRINTERS"),
        ("ElectronicsWorkbench.jpg",  "03 \u00b7 ELECTRONICS BENCH"),
        ("CNCRouter.jpg",             "04 \u00b7 CNC MILL & ROUTER"),
    ]
    tw = (PAGE_W - 2 * M - 3 * TILE_GAP) // 4
    lf = mono(21, 700)
    for i, (src, label) in enumerate(tiles):
        tx = px(M) + i * (tw + TILE_GAP)
        img.paste(cover(os.path.join(ASSETS, src), tw, TILE_H), (tx, TILE_Y))
        d.rectangle([tx, TILE_Y + TILE_H - 46, tx + tw, TILE_Y + TILE_H], fill=BLACK)
        draw_spaced(d, (tx + 12, TILE_Y + TILE_H - 46 + 13), label, lf, tracking=2, fill=WHITE)

    # plus-strip (full bleed)
    d.rectangle([0, STRIP_Y, W, STRIP_Y + STRIP_H], fill=STRIP)
    plus = ("PLUS: VINYL CUTTING \u00b7 SUBLIMATION & HEAT PRESS \u00b7 EMBROIDERY & SEWING \u00b7 "
            "VACUUM FORMER \u00b7 PEN PLOTTER \u00b7 REFLOW OVEN")
    pf = mono(20, 500)
    pw = spaced_w(d, plus, pf, 1)
    assert pw <= PAGE_W - 2 * M, f"strip text too wide: {pw}"
    draw_spaced(d, (px(M) + (PAGE_W - 2 * M - pw) // 2, STRIP_Y + 24), plus, pf, tracking=1, fill=BLACK)

    # ================= BLACK STRIP =================
    d.rectangle([0, BY, W, BY + BLACK_H], fill=BLACK)
    d.text((px(M), BY + 42), "MAKE \u00b7 WORK \u00b7 MEET", font=font("bebas", 62), fill=YELLOW)

    if not NOLOGO:
        logo_w = Image.open(os.path.join(ASSETS, "logo_white.png"))
        lw_px = 180
        lh_px = int(180 * logo_w.size[1] / logo_w.size[0])
        logo_w = logo_w.resize((lw_px, lh_px), Image.LANCZOS)
        paste(img, logo_w, px(PAGE_W - M - lw_px), BY + 26)

    cols = [
        ("MAKE", "Workshop kit for everyone \u2014 no membership needed to start making."),
        ("WORK", "Desks by the day, week or month \u2014 hotdesk, flexi or permanent."),
        ("MEET", "Free Maker Night \u2014 Thursdays 7\u20139:30pm, 2nd Saturday of each month."),
    ]
    col_gap = 40
    col_w = (PAGE_W - 2 * M - 2 * col_gap) // 3
    cy = BY + 126
    for i, (head, body) in enumerate(cols):
        cx = px(M) + i * (col_w + col_gap)
        d.rectangle([cx, cy, cx + 34, cy + 8], fill=YELLOW)
        d.text((cx, cy + 20), head, font=font("bebas", 52), fill=WHITE)
        bf = arch(24, 400)
        blines = wrap(d, body, bf, col_w - 20)
        byy = cy + 80
        for ln in blines:
            d.text((cx, byy), ln, font=bf, fill=(228, 228, 228))
            byy += 32
        assert_fits(f"black col {head}", byy - 1, BY + BLACK_H - 4)

    # ================= PRICE BAND =================
    d.rectangle([0, BAND_Y, W, BAND_Y + BAND_H], fill=YELLOW)
    price = ("MEMBERSHIP \u00a310/MONTH   \u00b7   DESK \u00a3210/MONTH   \u00b7   WORKSHOP \u00a372/MONTH   "
             "\u00b7   DAY PASS \u00a315 \u00b7 HALF \u00a37.50")
    prf = mono(24, 700)
    prw = spaced_w(d, price, prf, 1)
    assert prw <= PAGE_W - 2 * M, f"price text too wide: {prw}"
    draw_spaced(d, (px(M) + (PAGE_W - 2 * M - prw) // 2, BAND_Y + 35), price, prf, tracking=1, fill=BLACK)

    # ================= FOOTER =================
    qr = Image.open(os.path.join(ASSETS, "qr.png")).convert("RGBA")
    qsize = qr.size[0]
    paste(img, qr, px(M), FY + 20)

    d.text((px(M) + qsize + 44, FY + 40), "SCAN FOR PRICES,", font=mono(22, 500), fill=GRAY)
    d.text((px(M) + qsize + 44, FY + 74), "EVENTS & MORE", font=mono(22, 500), fill=GRAY)
    d.text((px(M) + qsize + 44, FY + 122), "doesliverpool.com", font=font("anton", 58), fill=BLACK)

    cx0 = px(M) + qsize + 44 + 470
    d.rectangle([cx0, FY + 40, cx0 + 34, FY + 48], fill=YELLOW)
    d.text((cx0, FY + 62), "FIND US", font=font("bebas", 46), fill=BLACK)
    cf = arch(27, 400)
    c_lines = [
        "1st Floor, The Tapestry,",
        "68\u201376 Kempston Street,",
        "Liverpool L3 8HL",
        "0151 703 0081 \u00b7 hello@doesliverpool.com",
    ]
    ccy = FY + 118
    for ln in c_lines:
        d.text((cx0, ccy), ln, font=cf, fill=(40, 40, 40))
        ccy += 34
    assert_fits("contact col", ccy - 1, FY + FOOTER_H - 70)

    rule_y = FY + FOOTER_H - 66
    d.rectangle([px(M), rule_y, px(PAGE_W - M), rule_y + 3], fill=BLACK)
    fine = ("DOES LIVERPOOL CIC \u2014 ALL PROFITS GO BACK INTO THE SPACE   \u00b7   10 MIN WALK FROM LIME STREET STATION")
    ff = mono(20, 400)
    fw = spaced_w(d, fine, ff, 2)
    draw_spaced(d, (px(M) + (PAGE_W - 2 * M - fw) // 2, rule_y + 14), fine, ff, tracking=2, fill=GRAY)

    # ---------- save ----------
    suffix = "-v2" if NOLOGO else ""
    out_png = os.path.join(HERE, f"does-liverpool-flyer{suffix}.png")
    out_pdf = os.path.join(HERE, f"does-liverpool-flyer{suffix}.pdf")
    img.save(out_png)
    img.save(out_pdf, resolution=300.0)
    print("saved:", out_png, img.size)
    print("saved:", out_pdf)
    print("layout: hero", HERO_H, "| white", WY, "-", BY, "| black", BY, "-", BAND_Y, "| band", BAND_Y, "-", FY, "| footer", FY, "-", FY + FOOTER_H)

# ---------- nologo variant: full-width, vertically centred ----------
def build_nologo():
    """--nologo variant. Content spans the left/right borders, every section's
    content is vertically centred within its band, and the yellow accents span
    the full width of their titles ('THE WORKSHOP' and the words MAKE/WORK/MEET)."""
    make_logo_variants()
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    px = lambda v: v + BLEED
    PAD = 56

    def text_h(txt, f):
        bb = d.textbbox((0, 0), txt, font=f)
        return bb[3] - bb[1]

    def ink(txt, f):
        """(offset, height) of the glyph ink box relative to the 'la' anchor:
        ink spans y+offset .. y+offset+height."""
        bb = d.textbbox((0, 0), txt, font=f)
        return bb[1], bb[3] - bb[1]

    # ================= HERO =================
    HERO_FULL = 1080
    HERO_H = HERO_FULL - SUB_H
    hero = cover(os.path.join(ASSETS, "MainRoomWideShot.jpg"), W, HERO_FULL)

    def v_gradient(target, y0, y1, a0, a1):
        g = Image.new("L", (1, y1 - y0))
        for i in range(y1 - y0):
            g.putpixel((0, i), int(a0 + (a1 - a0) * i / (y1 - y0)))
        g = g.resize((W, y1 - y0))
        ov = Image.new("RGB", (W, y1 - y0), BLACK)
        ov.putalpha(g)
        target.paste(ov, (0, y0), ov)

    v_gradient(hero, 0, 300, 150, 0)
    v_gradient(hero, int(HERO_FULL * 0.15), HERO_FULL, 0, 245)
    hero = hero.crop((0, 0, W, HERO_H))
    img.paste(hero, (0, 0))
    d = ImageDraw.Draw(img)

    # brand chip + wordmark (top-left)
    chip_s = 104
    chip = Image.new("RGBA", (chip_s, chip_s), YELLOW)
    bird = Image.open(os.path.join(ASSETS, "doesloverpoollogo.png")).convert("RGBA")
    bs = int(chip_s * 0.86)
    bird = bird.resize((bs, bs), Image.LANCZOS)
    chip.paste(bird, ((chip_s - bs) // 2, (chip_s - bs) // 2), bird)
    paste(img, chip, px(PAD), px(58))
    d.text((px(PAD) + chip_s + 28, px(64)), "DoES LIVERPOOL", font=font("raoul", 46), fill=WHITE)
    d.text((px(PAD) + chip_s + 30, px(64) + 66), "COMMUNITY MAKER SPACE & CO-WORKING", font=mono(22, 500), fill=YELLOW)

    # headline, vertically centred in the hero (Raoul title font, sized to
    # match the previous Anton headline height)
    hl = font("raoul", 123)
    off_l, l2_h = ink("STUFF.", hl)
    pitch = 138
    y1 = (HERO_H - (pitch + l2_h)) // 2 - off_l
    y2 = y1 + pitch
    assert y1 > px(58) + chip_s, "headline overlaps brand chip"
    assert_fits("hero headline", y2 + off_l + l2_h, HERO_H)
    d.text((px(PAD), y1), "COME AND DO", font=hl, fill=WHITE)
    d.text((px(PAD), y2), "EPIC ", font=hl, fill=YELLOW)
    ew = d.textlength("EPIC ", font=hl)
    d.text((px(PAD) + ew, y2), "STUFF.", font=hl, fill=WHITE)

    # ================= WORKSHOP SECTION =================
    WY = BLEED + HERO_H
    heading_f = font("raoul", 54)
    off_h, heading_h = ink("THE WORKSHOP", heading_f)
    rule_h = 12
    para = ("A proper workshop in the middle of town \u2014 laser cutters, 3D printers, a CNC mill and router, "
            "a stocked electronics bench, embroidery & sewing machines, vinyl cutting and more. "
            "No membership needed to use it.")
    p_f = arch(31, 400)
    p_lines = wrap(d, para, p_f, PAGE_W - 2 * PAD)
    g1, g2, g3 = 22, 24, 30
    white_m = 40
    STRIP_H = 58
    TILE_GAP = 16

    tile_h = 256
    while True:  # fit the footer: shrink tiles if the page overflows
        group_h = heading_h + g1 + rule_h + g2 + len(p_lines) * 43 + g3 + tile_h
        STRIP_Y = WY + white_m + group_h + white_m
        BY = STRIP_Y + STRIP_H
        # black section height (columns only — the MAKE · WORK · MEET title
        # repeats the column words, so it is omitted)
        word_f = font("raoul", 36)
        off_w, word_h = ink("MAKE", word_f)
        body_f = arch(24, 400)
        col_gap = 40
        col_w = (PAGE_W - 2 * PAD - 2 * col_gap) // 3
        bodies = [
            "Workshop kit for everyone \u2014 no membership needed to start making.",
            "Desks by the day, week or month \u2014 hotdesk, flexi or permanent.",
            "Free Maker Night \u2014 Thursdays 7\u20139:30pm, 2nd Saturday of each month.",
        ]
        body_lines = [wrap(d, b, body_f, col_w - 20) for b in bodies]
        body_h = max(len(x) for x in body_lines) * 32
        col_block = word_h + 10 + rule_h + 14 + body_h
        black_group = col_block
        BLACK_H = black_group + 2 * 26
        BAND_Y = BY + BLACK_H
        BAND_H = 90
        FY = BAND_Y + BAND_H
        FOOTER_H = PAGE_H + BLEED - FY
        if FOOTER_H >= 387 or tile_h <= 170:
            break
        tile_h -= 6
    assert FOOTER_H >= 387, f"footer too small: {FOOTER_H}"

    # heading + title-spanning yellow rule
    gy = WY + white_m - off_h
    d.text((px(PAD), gy), "THE WORKSHOP", font=heading_f, fill=BLACK)
    title_w = d.textlength("THE WORKSHOP", font=heading_f)
    rule_y0 = gy + off_h + heading_h + g1
    d.rectangle([px(PAD), rule_y0, px(PAD) + title_w, rule_y0 + rule_h], fill=YELLOW)

    # paragraph
    py = rule_y0 + rule_h + g2
    for ln in p_lines:
        d.text((px(PAD), py), ln, font=p_f, fill=(40, 40, 40))
        py += 43

    # equipment tiles, spanning the left/right borders
    tiles = [
        ("LaserCutterWorkshop.jpg",   "LASER CUTTERS"),
        ("3DPrinters.jpg",            "3D PRINTERS"),
        ("ElectronicsWorkbench.jpg",  "ELECTRONICS BENCH"),
        ("CNCRouter.jpg",             "CNC MILL & ROUTER"),
    ]
    tile_y = py + g3
    tw = (PAGE_W - 2 * PAD - 3 * TILE_GAP) // 4
    lf = mono(21, 700)
    for i, (src, label) in enumerate(tiles):
        tx = px(PAD) + i * (tw + TILE_GAP)
        img.paste(cover(os.path.join(ASSETS, src), tw, tile_h), (tx, tile_y))
        d.rectangle([tx, tile_y + tile_h - 46, tx + tw, tile_y + tile_h], fill=BLACK)
        lw = spaced_w(d, label, lf, 2)
        draw_spaced(d, (tx + (tw - lw) // 2, tile_y + tile_h - 46 + 13), label, lf, tracking=2, fill=WHITE)

    # plus-strip (full bleed), text vertically centred
    d.rectangle([0, STRIP_Y, W, STRIP_Y + STRIP_H], fill=STRIP)
    plus = ("PLUS: VINYL CUTTING \u00b7 SUBLIMATION & HEAT PRESS \u00b7 EMBROIDERY & SEWING \u00b7 "
            "VACUUM FORMER \u00b7 PEN PLOTTER \u00b7 REFLOW OVEN")
    pf = mono(20, 500)
    pw = spaced_w(d, plus, pf, 1)
    assert pw <= PAGE_W - 2 * PAD, f"strip text too wide: {pw}"
    off_s, ink_s = ink(plus, pf)
    draw_spaced(d, (px(PAD) + (PAGE_W - 2 * PAD - pw) // 2,
                    STRIP_Y + (STRIP_H - ink_s) // 2 - off_s),
                plus, pf, tracking=1, fill=BLACK)

    # ================= BLACK STRIP (columns, vertically centred) =================
    d.rectangle([0, BY, W, BAND_Y], fill=BLACK)
    cy = BY + (BLACK_H - col_block) // 2 - off_w
    for i, ((head, body), lines) in enumerate(zip(
            [("MAKE", bodies[0]), ("WORK", bodies[1]), ("MEET", bodies[2])], body_lines)):
        cx = px(PAD) + i * (col_w + col_gap)
        d.text((cx, cy), head, font=word_f, fill=WHITE)
        ww = d.textlength(head, font=word_f)
        rule_w_y = cy + off_w + word_h + 10
        d.rectangle([cx, rule_w_y, cx + ww, rule_w_y + rule_h], fill=YELLOW)
        byy = rule_w_y + rule_h + 14
        for ln in lines:
            d.text((cx, byy), ln, font=body_f, fill=(228, 228, 228))
            byy += 32
        assert_fits(f"black col {head}", byy - 1, BAND_Y - 6)

    # ================= PRICE BAND =================
    d.rectangle([0, BAND_Y, W, BAND_Y + BAND_H], fill=YELLOW)
    price = ("MEMBERSHIP \u00a310/MONTH   \u00b7   DESK \u00a3210/MONTH   \u00b7   WORKSHOP \u00a372/MONTH   "
             "\u00b7   FLEXI DESK \u00a396/MONTH   \u00b7   DAY PASS \u00a315 \u00b7 HALF \u00a37.50")
    for psize in (21, 20, 19):
        prf = mono(psize, 700)
        prw = spaced_w(d, price, prf, 1)
        if prw <= PAGE_W - 2 * PAD:
            break
    assert prw <= PAGE_W - 2 * PAD, f"price text too wide: {prw}"
    off_pr, prh = ink("MEMBERSHIP", prf)
    draw_spaced(d, (px(PAD) + (PAGE_W - 2 * PAD - prw) // 2, BAND_Y + (BAND_H - prh) // 2 - off_pr),
                price, prf, tracking=1, fill=BLACK)

    # ================= FOOTER (group vertically centred above fine print) =================
    qr = Image.open(os.path.join(ASSETS, "qr.png")).convert("RGBA")
    qsize = qr.size[0]
    rule_y = FY + FOOTER_H - 64
    avail = rule_y - FY
    qtop = FY + max(0, (avail - qsize) // 2)
    paste(img, qr, px(PAD), qtop)
    # The QR image includes a 4-module quiet zone; align the other footer
    # parts with the top of the visible QR pattern, not the white border.
    quiet = int(round(4 * qsize / 33))
    text_top = qtop + quiet

    # left block (scan for prices) — ink tops aligned with the QR pattern top
    scan_f = mono(22, 500)
    off_scan, _ = ink("SCAN FOR PRICES,", scan_f)
    sx = px(PAD) + qsize + 40
    d.text((sx, text_top - off_scan), "SCAN FOR PRICES,", font=scan_f, fill=GRAY)
    d.text((sx, text_top - off_scan + 34), "EVENTS & MORE", font=scan_f, fill=GRAY)
    url_f = font("raoul", 49)
    off_url, _ = ink("doesliverpool.com", url_f)
    d.text((sx, text_top - off_url + 80), "doesliverpool.com", font=url_f, fill=BLACK)

    cx0 = px(PAGE_W - PAD - 600)
    find_f = font("raoul", 33)
    off_find, _ = ink("FIND US", find_f)
    d.text((cx0, text_top - off_find), "FIND US", font=find_f, fill=BLACK)
    cf = arch(27, 400)
    off_cf, _ = ink("1st Floor,", cf)
    c_lines = [
        "1st Floor, The Tapestry,",
        "68\u201376 Kempston Street,",
        "Liverpool L3 8HL",
        "0151 703 0081 \u00b7 hello@doesliverpool.com",
    ]
    ccy = text_top - off_cf + 58
    for ln in c_lines:
        d.text((cx0, ccy), ln, font=cf, fill=(40, 40, 40))
        ccy += 34
    assert_fits("contact col", ccy - 1, rule_y - 10)

    d.rectangle([px(PAD), rule_y, px(PAGE_W - PAD), rule_y + 3], fill=BLACK)
    fine = ("DoES LIVERPOOL CIC \u2014 ALL PROFITS GO BACK INTO THE SPACE   \u00b7   10 MIN WALK FROM LIME STREET STATION")
    ff = mono(20, 400)
    fw = spaced_w(d, fine, ff, 2)
    draw_spaced(d, (px(PAD) + (PAGE_W - 2 * PAD - fw) // 2, rule_y + 14), fine, ff, tracking=2, fill=GRAY)

    # ---------- save ----------
    # Each design iteration is saved as a new version (v2, v3, ...).
    out_png = os.path.join(HERE, "does-liverpool-flyer-v6.png")
    out_pdf = os.path.join(HERE, "does-liverpool-flyer-v6.pdf")
    img.save(out_png)
    img.save(out_pdf, resolution=300.0)
    print("saved:", out_png, img.size)
    print("saved:", out_pdf)
    print("layout nologo: hero", HERO_H, "| white", WY, "-", STRIP_Y, "| strip", STRIP_Y, "-", BY,
          "| black", BY, "-", BAND_Y, "| band", BAND_Y, "-", FY, "| footer", FY, "-", FY + FOOTER_H)

if __name__ == "__main__":
    if NOLOGO:
        build_nologo()
    else:
        build_original()
