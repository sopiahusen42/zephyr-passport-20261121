#!/usr/bin/env python3
"""Render the open passport spread of the Grand Duchy of Zephyr.

Deterministic: fixed math, fixed fonts, no randomness, no time, no network.
Output: entry.png (1024x1024) written next to this file.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

PAPER = (238, 233, 220)
SHADE = (226, 219, 202)
GUTTER_C = (90, 70, 60)
MAROON = (110, 36, 40)
INK = (40, 36, 32)
LABEL_C = (90, 84, 74)
P_INK = (70, 64, 56)
P_BG = (214, 210, 200)
GUILL_C = (200, 190, 168)
BLUE = (60, 90, 170)
RED = (190, 60, 50)
TEAL = (30, 130, 130)
GREEN = (46, 110, 80)

FD = "/usr/share/fonts/truetype/dejavu/"


def fnt(name, size):
    return ImageFont.truetype(FD + name, size)


def tsize(d, s, f):
    return d.textlength(s, font=f)


def ctext(d, cx, y, s, f, fill):
    """Centered horizontal text, y = top."""
    d.text((cx - tsize(d, s, f) / 2, y), s, font=f, fill=fill)


def ltext(d, cx, y, s, f, fill, spacing):
    """Letter-spaced text, centered on cx, y = top."""
    ws = [tsize(d, c, f) for c in s]
    total = sum(ws) + spacing * (len(s) - 1)
    x = cx - total / 2
    for c, w in zip(s, ws):
        d.text((x, y), c, font=f, fill=fill)
        x += w + spacing
    return total


def fit_font(d, s, maxw, start, family="DejaVuSans.ttf"):
    size = start
    while size > 8:
        f = fnt(family, size)
        if tsize(d, s, f) <= maxw:
            return f
        size -= 1
    return fnt(family, 8)


def guilloche(img, x0, x1, y0, y1, n, amp, waves):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    k = 2 * math.pi * waves / (x1 - x0)
    for i in range(n):
        yb = y0 + (y1 - y0) * (i + 0.5) / n
        phase = 0.7 * i
        pts = []
        x = float(x0)
        while x <= x1:
            pts.append((x, yb + amp * math.sin(k * (x - x0) + phase)))
            x += 4
        d.line(pts, fill=GUILL_C + (90,), width=1)
    img.alpha_composite(ov)


def draw_emblem(d):
    cx, cy, r = 266, 96, 34
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=MAROON, width=2)
    r2 = 28
    d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=MAROON, width=1)
    # stylised wind swirl: three concentric arc strokes
    d.arc((cx - 20, cy - 20, cx + 20, cy + 20), start=110, end=300, fill=MAROON, width=2)
    d.arc((cx - 14, cy - 14, cx + 14, cy + 14), start=250, end=80, fill=MAROON, width=2)
    d.arc((cx - 8, cy - 8, cx + 8, cy + 8), start=30, end=200, fill=MAROON, width=2)
    d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=MAROON)
    # tiny wing mark
    for a, b in [((254, 112), (263, 119)), ((257, 108), (264, 115)),
                 ((278, 112), (269, 119)), ((275, 108), (268, 115))]:
        d.line([a, b], fill=MAROON, width=1)


def quad_pts(p0, c, p1, n=12):
    """Sample a quadratic Bezier curve (deterministic)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((u * u * p0[0] + 2 * u * t * c[0] + t * t * p1[0],
                    u * u * p0[1] + 2 * u * t * c[1] + t * t * p1[1]))
    return pts


def hatch_region(img, poly, y0, y1, spacing=3):
    """Horizontal engraving hatch (1 px lines) clipped to poly."""
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(poly, fill=255)
    hatch = Image.new("RGB", (W, H), P_BG)
    hd = ImageDraw.Draw(hatch)
    y = y0
    while y <= y1:
        hd.line([(61, y), (297, y)], fill=P_INK, width=1)
        y += spacing
    img.paste(hatch, (0, 0), mask)


def draw_portrait(img):
    # hair mass: outer cranium curve, inner edge behind ear/nape
    hair = [
        (116, 290), (132, 270), (150, 260), (172, 256), (194, 262),
        (210, 276), (218, 300), (220, 334), (216, 366), (206, 396),
        (192, 416), (174, 422), (168, 404), (174, 384), (180, 364),
        (180, 336), (174, 310), (162, 294), (144, 288), (126, 288),
    ]
    # high-collared windfarmer coat
    collar = [
        (116, 412), (132, 400), (146, 416), (160, 400), (176, 414),
        (184, 448), (150, 466), (108, 448),
    ]
    hatch_region(img, hair, 256, 424, 3)

    d = ImageDraw.Draw(img)
    # face profile, facing left
    prof = [
        (116, 290), (111, 306), (108, 316), (112, 328), (103, 343),
        (101, 348), (109, 354), (107, 360), (112, 366), (108, 372),
        (111, 378), (116, 388), (125, 396), (135, 401), (150, 404), (162, 397),
    ]
    d.line(prof, fill=P_INK, width=2)
    # confident brow and eye
    d.line([(124, 309), (144, 305)], fill=P_INK, width=2)
    d.line([(125, 304), (143, 300)], fill=P_INK, width=1)
    d.line([(128, 320), (144, 318)], fill=P_INK, width=2)
    d.arc((128, 316, 146, 326), start=160, end=360, fill=P_INK, width=1)
    d.ellipse((134, 319, 138, 323), fill=P_INK)
    # nose line, nostril, lips
    d.line([(106, 351), (112, 352)], fill=P_INK, width=1)
    d.line([(106, 360), (113, 362)], fill=P_INK, width=2)
    d.line([(107, 371), (113, 369)], fill=P_INK, width=1)
    # ear
    d.arc((164, 342, 184, 374), start=-75, end=75, fill=P_INK, width=2)
    d.arc((169, 349, 179, 367), start=-60, end=60, fill=P_INK, width=1)
    # jaw-to-collar stubs, then collar hatching over them
    d.line([(130, 398), (130, 402)], fill=P_INK, width=2)
    d.line([(158, 399), (158, 402)], fill=P_INK, width=2)
    hatch_region(img, collar, 400, 466, 3)

    d = ImageDraw.Draw(img)
    # collar outline and coat
    d.line([(116, 412), (132, 400), (146, 416), (160, 400), (176, 414)], fill=P_INK, width=2)
    d.line([(116, 412), (108, 448)], fill=P_INK, width=2)
    d.line([(176, 414), (184, 448)], fill=P_INK, width=2)
    d.line([(108, 448), (132, 464), (150, 466), (168, 464), (184, 448)], fill=P_INK, width=2)
    d.line([(108, 448), (84, 464)], fill=P_INK, width=1)
    d.line([(184, 448), (208, 464)], fill=P_INK, width=1)
    d.line([(112, 454), (130, 466)], fill=P_INK, width=1)
    d.line([(180, 454), (206, 466)], fill=P_INK, width=1)

    # wind-swept hair: 12 curved strands blowing left
    strands = [
        ((168, 260), (118, 244), (62, 258), 2),
        ((182, 268), (124, 252), (62, 272), 2),
        ((194, 280), (132, 264), (64, 286), 2),
        ((202, 296), (140, 280), (66, 300), 2),
        ((208, 314), (148, 298), (70, 316), 2),
        ((212, 334), (156, 318), (76, 334), 2),
        ((212, 354), (162, 340), (84, 352), 1),
        ((208, 374), (168, 362), (92, 372), 1),
        ((200, 392), (170, 384), (100, 392), 1),
        ((190, 408), (168, 404), (110, 412), 1),
        ((150, 254), (104, 240), (62, 248), 1),
        ((128, 252), (92, 242), (62, 246), 1),
    ]
    for p0, c, p1, wd in strands:
        d.line(quad_pts(p0, c, p1), fill=P_INK, width=wd)
    # flyaway wisps
    for a, b in [((64, 262), (62, 250)), ((66, 296), (62, 288)), ((70, 330), (62, 326))]:
        d.line([a, b], fill=P_INK, width=1)


def fee_stamp():
    layer = Image.new("RGBA", (190, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = GREEN + (255,)
    d.rectangle((10, 14, 160, 106), outline=c, width=2)   # 150x92
    d.rectangle((16, 20, 154, 100), outline=c, width=1)
    cx = 85
    f1 = fit_font(d, "WIND USE PERMIT", 134, 16, "DejaVuSans-Bold.ttf")
    ctext(d, cx, 32, "WIND USE PERMIT", f1, c)
    f2 = fit_font(d, "FEE PAID: 12 GUSTS", 134, 14)
    ctext(d, cx, 58, "FEE PAID: 12 GUSTS", f2, c)
    f3 = fit_font(d, "SER. 0004831 \u00b7 06 NOV 2026", 134, 12)
    ctext(d, cx, 78, "SER. 0004831 \u00b7 06 NOV 2026", f3, c)
    speckle_rect(layer, (10, 14, 160, 106), GREEN)
    return layer


def arc_text(layer, s, cx, cy, rx, ry, size, fill, a0, a1):
    """Text along the top arc of an ellipse; a in degrees, 0 = top."""
    f = fnt("DejaVuSans-Bold.ttf", size)
    n = len(s)
    for i, ch in enumerate(s):
        a = a0 + (a1 - a0) * i / max(n - 1, 1)
        rad = math.radians(a)
        px = cx + (rx - 16) * math.sin(rad)
        py = cy - (ry - 12) * math.cos(rad)
        g = Image.new("RGBA", (44, 30), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.text((22 - tsize(gd, ch, f) / 2, 15 - size * 0.7), ch, font=f, fill=fill)
        g = g.rotate(-a, resample=Image.BICUBIC, expand=True)
        layer.alpha_composite(g, (int(round(px - g.width / 2)), int(round(py - g.height / 2))))


def stamp_arrival():
    layer = Image.new("RGBA", (230, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = BLUE + (255,)
    cx, cy, rx, ry = 115, 80, 95, 60
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=c, width=2)
    d.ellipse((cx - rx + 5, cy - ry + 5, cx + rx - 5, cy + ry - 5), outline=c, width=1)
    arc_text(layer, "PORT GALE \u2014 ZEPHYR", cx, cy, rx, ry, 13, c, -52, 52)
    ctext(d, cx, 68, "ARRIVAL", fnt("DejaVuSans-Bold.ttf", 18), c)
    ctext(d, cx, 94, "VIA FENDRA FERRY", fnt("DejaVuSans.ttf", 9), c)
    ctext(d, cx, 114, "05 JAN 2027", fnt("DejaVuSans-Bold.ttf", 13), c)
    speckle_ellipse(layer, cx, cy, rx, ry, BLUE)
    return layer


def stamp_departure():
    layer = Image.new("RGBA", (200, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = RED + (255,)
    d.rectangle((10, 10, 190, 120), outline=c, width=2)   # 180x110
    d.rectangle((15, 15, 185, 115), outline=c, width=1)
    cx = 100
    ctext(d, cx, 30, "DEPARTURE", fnt("DejaVuSans-Bold.ttf", 16), c)
    ctext(d, cx, 57, "PORT GALE", fnt("DejaVuSans.ttf", 14), c)
    ctext(d, cx, 80, "09 JAN 2027", fnt("DejaVuSans.ttf", 14), c)
    speckle_rect(layer, (10, 10, 190, 120), RED)
    return layer


def stamp_admission():
    layer = Image.new("RGBA", (190, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = TEAL + (255,)
    cx, cy, rx, ry = 95, 65, 85, 55
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=c, width=2)
    d.ellipse((cx - rx + 5, cy - ry + 5, cx + rx - 5, cy + ry - 5), outline=c, width=1)
    f1 = fit_font(d, "ISLE OF CALM \u2014 CUSTOMS", 142, 13)
    ctext(d, cx, 28, "ISLE OF CALM \u2014 CUSTOMS", f1, c)
    ctext(d, cx, 52, "ADMISSION", fnt("DejaVuSans-Bold.ttf", 16), c)
    ctext(d, cx, 78, "14 JAN 2027", fnt("DejaVuSans.ttf", 13), c)
    speckle_ellipse(layer, cx, cy, rx, ry, TEAL)
    return layer


def fade_alpha(layer, alpha):
    """Scale a layer's alpha channel to a target ink intensity."""
    r, g, b, a = layer.split()
    a2 = a.point(lambda v: int(round(v * alpha / 255)))
    return Image.merge("RGBA", (r, g, b, a2))


def paste_ink(main, layer, cx, cy, deg_cw):
    """Two-pass stamping: alpha 160, then alpha 80 offset (+1.5, +1.0) px."""
    rot = layer.rotate(-deg_cw, resample=Image.BICUBIC, expand=True)
    x = int(round(cx - rot.width / 2))
    y = int(round(cy - rot.height / 2))
    main.alpha_composite(fade_alpha(rot, 160), (x, y))
    main.alpha_composite(fade_alpha(rot, 80), (x + 2, y + 1))


def speckle_ellipse(layer, cx, cy, rx, ry, color):
    """Deterministic ink speckle ring: 60 dots, alpha (i*37) % 80 + 40."""
    d = ImageDraw.Draw(layer)
    for i in range(60):
        t = 2 * math.pi * i / 60
        m = 1.04 + 0.015 * ((i * 13) % 5)
        px = cx + rx * m * math.cos(t)
        py = cy + ry * m * math.sin(t)
        s = 2 if i % 2 == 0 else 1
        al = (i * 37) % 80 + 40
        d.ellipse((px - s / 2, py - s / 2, px + s / 2, py + s / 2), fill=color + (al,))


def speckle_rect(layer, box, color):
    """Deterministic ink speckle ring around a rect: 60 dots, 1-2 px."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(layer)
    w = x1 - x0
    h = y1 - y0
    per = 2 * (w + h)
    for i in range(60):
        s = per * i / 60
        if s < w:
            px, py, ox, oy = x0 + s, y0, 0, -1
        elif s < w + h:
            px, py, ox, oy = x1, y0 + (s - w), 1, 0
        elif s < 2 * w + h:
            px, py, ox, oy = x1 - (s - w - h), y1, 0, 1
        else:
            px, py, ox, oy = x0, y1 - (s - 2 * w - h), -1, 0
        off = 4 + (i * 11) % 4
        s2 = 2 if i % 2 == 0 else 1
        al = (i * 37) % 80 + 40
        qx, qy = px + ox * off, py + oy * off
        d.ellipse((qx - s2 / 2, qy - s2 / 2, qx + s2 / 2, qy + s2 / 2), fill=color + (al,))


def render():
    img = Image.new("RGB", (W, H), MAROON)
    d = ImageDraw.Draw(img)
    d.rectangle((26, 26, 998, 998), fill=PAPER)

    # faint vertical shading at the outer edges
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for x in range(26, 72):
        a = int(110 * (72 - x) / 46)
        sd.line([(x, 26), (x, 998)], fill=SHADE + (a,))
    for x in range(997, 952, -1):
        a = int(110 * (x - 952) / 46)
        sd.line([(x, 26), (x, 998)], fill=SHADE + (a,))
    img = img.convert("RGBA")
    img.alpha_composite(sh)

    # guilloche texture
    guilloche(img, 26, 507, 26, 998, 40, 6.0, 3.0)
    guilloche(img, 517, 998, 26, 512, 18, 5.0, 2.5)

    # open-book depth: 60 px gutter shadow on each side, darkest at the fold
    gb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdb = ImageDraw.Draw(gb)
    for x in range(447, 507):
        dist = 507 - x
        a = 130 if dist <= 10 else int(130 * (60 - dist) / 50)
        gdb.line([(x, 26), (x, 998)], fill=(100, 82, 72) + (a,))
    for x in range(517, 577):
        dist = x - 517
        a = 130 if dist <= 10 else int(130 * (60 - dist) / 50)
        gdb.line([(x, 26), (x, 998)], fill=(100, 82, 72) + (a,))
    img.alpha_composite(gb)

    d = ImageDraw.Draw(img)
    # gutter between the two pages
    d.rectangle((507, 26, 516, 998), fill=GUTTER_C)
    # 2 px highlight on each outer page edge
    for x in (27, 28, 995, 996):
        d.line([(x, 26), (x, 998)], fill=(248, 244, 234))

    # ---------- LEFT PAGE ----------
    draw_emblem(d)
    ltext(d, 266, 140, "GRAND DUCHY OF ZEPHYR", fnt("DejaVuSerif-Bold.ttf", 20), INK, 3)
    d.line([(156, 166), (376, 166)], fill=MAROON, width=1)
    d.line([(156, 169), (376, 169)], fill=MAROON, width=1)
    ltext(d, 266, 173, "PASSPORT", fnt("DejaVuSans-Bold.ttf", 34), INK, 6)
    ctext(d, 266, 214, "PASSEPORT \u00b7 PASAPORTE", fnt("DejaVuSans.ttf", 12), LABEL_C)

    # portrait box
    d.rectangle((58, 240, 300, 470), outline=MAROON, width=2)
    d.rectangle((61, 243, 297, 467), fill=P_BG)
    draw_portrait(img)
    ctext(d, 179, 478, "PORT OF GALE, ZEPHYR", fnt("DejaVuSans.ttf", 11), LABEL_C)

    # data grid
    rows = [
        ("SURNAME", "ZEPHYR"),
        ("GIVEN NAME", "KESTREL A."),
        ("NATIONALITY", "ZEPHYRIC"),
        ("DATE OF BIRTH", "12 MAR 1986"),
        ("PLACE OF BIRTH", "PORT GALE, Z"),
        ("SEX", "F"),
    ]
    # data grid: strict column x=322, 14 px labels, 15 px bold values +7 px,
    # uniform 44 px pitch, 18 px right margin
    fl = fnt("DejaVuSans.ttf", 14)
    fb = fnt("DejaVuSans-Bold.ttf", 15)
    y = 250
    for lab, val in rows:
        d.text((322, y), lab, font=fl, fill=LABEL_C)
        d.text((322, y + 21), val, font=fb, fill=INK)
        y += 44

    # passport block: same column x=322, compact pitch, two-line authority
    fla = fnt("DejaVuSans.ttf", 13)
    fva = fnt("DejaVuSans-Bold.ttf", 12)
    for y, (lab, val) in zip((560, 590, 620),
                             [("PASSPORT NO", "ZP 483 921"),
                              ("DATE OF ISSUE", "04 NOV 2026"),
                              ("EXPIRY", "04 NOV 2031")]):
        d.text((322, y), lab, font=fla, fill=LABEL_C)
        d.text((322, y + 20), val, font=fva, fill=INK)
    fa = fnt("DejaVuSans.ttf", 13)
    fva2 = fnt("DejaVuSans-Bold.ttf", 13)
    d.text((322, 655), "AUTHORITY", font=fa, fill=LABEL_C)
    d.text((322, 671), "OFFICE OF WIND", font=fva2, fill=INK)
    d.text((322, 686), "& PASSPORTS", font=fva2, fill=INK)

    # MRZ: both lines same size, centred, 20 px above the paper's bottom edge
    mrz_lines = [
        "P<ZPR<ZEPHYR<<KESTREL<<A<<<<<<<<<<<<<<<<<<",
        "ZP48392148ZPR6103124F3111049<<<<<<<<<<<8",
    ]
    fm = fnt("DejaVuSansMono-Bold.ttf", 24)
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    scale = 0.52
    strips = []
    for s in mrz_lines:
        adv = [probe.textlength(ch, font=fm) + 2 for ch in s]
        sw = int(sum(adv)) + 2
        strip = Image.new("RGBA", (sw, 40), (0, 0, 0, 0))
        sdd = ImageDraw.Draw(strip)
        x = 1.0
        for ch, a in zip(s, adv):
            sdd.text((x, 6), ch, font=fm, fill=INK + (255,))
            x += a
        strips.append(strip.resize((int(round(sw * scale)), int(round(40 * scale))), Image.LANCZOS))
    h = strips[0].height
    y0 = 978 - 2 * h - 5
    for st in strips:
        img.alpha_composite(st, (int(round(266 - st.width / 2)), y0))
        y0 += h + 5

    # page number 1
    d.text((44, 964), "1", font=fnt("DejaVuSans.ttf", 12), fill=LABEL_C)

    # ---------- RIGHT PAGE ----------
    # fee stamp, rotated 6 deg clockwise (top-right column)
    paste_ink(img, fee_stamp(), 865, 256, 6)
    # travel stamps: loose 3-column flow, >= 30 px gutters, ink order a, b, c
    paste_ink(img, stamp_arrival(), 632, 460, -8)
    paste_ink(img, stamp_departure(), 866, 615, 5)
    paste_ink(img, stamp_admission(), 675, 775, -4)

    # visa condition line, centred on the right page
    cond = "CONDITION 7 \u2014 BORROWED WIND TO BE RETURNED BY 19:00 LOCAL"
    fc = fnt("DejaVuSans.ttf", 12)
    cx2 = int(round(757 - tsize(d, cond, fc) / 2))
    d.text((cx2, 850), cond, font=fc, fill=INK)
    d.line([(cx2, 867), (cx2 + 140, 867)], fill=INK, width=1)

    # page number 2
    f12 = fnt("DejaVuSans.ttf", 12)
    d.text((990 - tsize(d, "2", f12), 964), "2", font=f12, fill=LABEL_C)

    return img


def main():
    img = render()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.convert("RGB").save(out, optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
