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


def draw_portrait(img):
    d = ImageDraw.Draw(img)

    # hair mass polygon: outer cranium curve, inner edge behind ear/nape
    hair = [
        (118, 292), (134, 272), (152, 262), (172, 258), (192, 264),
        (206, 278), (214, 300), (218, 330), (216, 362), (208, 392),
        (194, 412), (176, 418), (170, 402), (176, 382), (182, 362),
        (182, 336), (176, 312), (164, 296), (146, 290), (128, 290),
    ]
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(hair, fill=255)
    hatch = Image.new("RGB", (W, H), P_BG)
    hd = ImageDraw.Draw(hatch)
    y = 258
    while y <= 424:
        hd.line([(61, y), (297, y)], fill=P_INK, width=1)
        y += 5
    img.paste(hatch, (0, 0), mask)

    d = ImageDraw.Draw(img)
    # face profile, facing left
    prof = [
        (118, 292), (113, 308), (110, 318), (113, 329), (104, 344),
        (102, 348), (110, 354), (108, 360), (113, 366), (109, 372),
        (112, 378), (117, 388), (126, 396), (136, 401), (152, 404), (164, 397),
    ]
    d.line(prof, fill=P_INK, width=2)

    # brow and eye
    d.line([(126, 311), (144, 307)], fill=P_INK, width=2)
    d.line([(129, 321), (145, 319)], fill=P_INK, width=2)
    d.arc((129, 317, 147, 327), start=160, end=360, fill=P_INK, width=1)
    d.ellipse((135, 320, 139, 324), fill=P_INK)
    # nostril and lips
    d.line([(107, 352), (113, 352)], fill=P_INK, width=1)
    d.line([(107, 361), (114, 363)], fill=P_INK, width=2)
    d.line([(108, 372), (114, 370)], fill=P_INK, width=1)
    # ear
    d.arc((166, 342, 186, 374), start=-75, end=75, fill=P_INK, width=2)
    d.arc((171, 349, 181, 367), start=-60, end=60, fill=P_INK, width=1)
    # neck
    d.line([(131, 398), (125, 432)], fill=P_INK, width=2)
    d.line([(157, 402), (163, 432)], fill=P_INK, width=2)
    for x in (135, 141, 147, 153):
        d.line([(x, 402), (x, 428)], fill=P_INK, width=1)
    # collar
    d.line([(96, 446), (128, 434)], fill=P_INK, width=2)
    d.line([(128, 434), (146, 458), (164, 434)], fill=P_INK, width=2)
    d.line([(164, 434), (198, 446)], fill=P_INK, width=2)
    d.line([(98, 452), (126, 441)], fill=P_INK, width=1)
    d.line([(166, 441), (196, 452)], fill=P_INK, width=1)

    # wind-blown strands, flowing left
    strands = [
        [(150, 268), (122, 256), (96, 258), (72, 270), (62, 286)],
        [(168, 260), (132, 250), (102, 252), (68, 262)],
        [(184, 272), (146, 264), (110, 272), (68, 286)],
        [(204, 290), (164, 282), (124, 286), (84, 298)],
        [(210, 300), (170, 296), (130, 300), (92, 312)],
    ]
    for s in strands:
        d.line(s, fill=P_INK, width=2)
    for a, b in [((66, 278), (62, 266)), ((68, 296), (62, 290)), ((70, 316), (62, 318))]:
        d.line([a, b], fill=P_INK, width=1)


def fee_stamp():
    layer = Image.new("RGBA", (190, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = GREEN + (170,)
    d.rectangle((10, 14, 160, 106), outline=c, width=2)   # 150x92
    d.rectangle((16, 20, 154, 100), outline=c, width=1)
    cx = 85
    f1 = fit_font(d, "WIND USE PERMIT", 126, 16, "DejaVuSans-Bold.ttf")
    ctext(d, cx, 32, "WIND USE PERMIT", f1, c)
    f2 = fit_font(d, "FEE PAID: 12 GUSTS", 126, 14)
    ctext(d, cx, 58, "FEE PAID: 12 GUSTS", f2, c)
    f3 = fit_font(d, "SER. 0004831 \u00b7 06 NOV 2026", 126, 12)
    ctext(d, cx, 78, "SER. 0004831 \u00b7 06 NOV 2026", f3, c)
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
    c = BLUE + (170,)
    cx, cy, rx, ry = 115, 80, 95, 60
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=c, width=2)
    d.ellipse((cx - rx + 5, cy - ry + 5, cx + rx - 5, cy + ry - 5), outline=c, width=1)
    arc_text(layer, "PORT GALE \u2014 ZEPHYR", cx, cy, rx, ry, 13, c, -52, 52)
    ctext(d, cx, 68, "ARRIVAL", fnt("DejaVuSans-Bold.ttf", 18), c)
    ctext(d, cx, 94, "VIA FENDRA FERRY", fnt("DejaVuSans.ttf", 9), c)
    ctext(d, cx, 114, "05 JAN 2027", fnt("DejaVuSans-Bold.ttf", 13), c)
    return layer


def stamp_departure():
    layer = Image.new("RGBA", (200, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = RED + (170,)
    d.rectangle((10, 10, 190, 120), outline=c, width=2)   # 180x110
    d.rectangle((15, 15, 185, 115), outline=c, width=1)
    cx = 100
    ctext(d, cx, 30, "DEPARTURE", fnt("DejaVuSans-Bold.ttf", 16), c)
    ctext(d, cx, 57, "PORT GALE", fnt("DejaVuSans.ttf", 14), c)
    ctext(d, cx, 80, "09 JAN 2027", fnt("DejaVuSans.ttf", 14), c)
    return layer


def stamp_admission():
    layer = Image.new("RGBA", (190, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = TEAL + (170,)
    cx, cy, rx, ry = 95, 65, 85, 55
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=c, width=2)
    d.ellipse((cx - rx + 5, cy - ry + 5, cx + rx - 5, cy + ry - 5), outline=c, width=1)
    f1 = fit_font(d, "ISLE OF CALM \u2014 CUSTOMS", 142, 13)
    ctext(d, cx, 28, "ISLE OF CALM \u2014 CUSTOMS", f1, c)
    ctext(d, cx, 52, "ADMISSION", fnt("DejaVuSans-Bold.ttf", 16), c)
    ctext(d, cx, 78, "14 JAN 2027", fnt("DejaVuSans.ttf", 13), c)
    return layer


def paste_rot(main, layer, x, y, deg_cw):
    rot = layer.rotate(-deg_cw, resample=Image.BICUBIC, expand=True)
    ox = (rot.width - layer.width) // 2
    oy = (rot.height - layer.height) // 2
    main.alpha_composite(rot, (x - ox, y - oy))


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

    d = ImageDraw.Draw(img)
    # gutter between the two pages
    d.rectangle((507, 26, 516, 998), fill=GUTTER_C)

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
    fl = fnt("DejaVuSans.ttf", 15)
    fb = fnt("DejaVuSans-Bold.ttf", 15)
    y = 250
    for lab, val in rows:
        d.text((320, y), lab, font=fl, fill=LABEL_C)
        d.text((320, y + 23), val, font=fb, fill=INK)
        y += 44

    # passport block (label above value, compact rows, fits left of gutter)
    fla = fnt("DejaVuSans.ttf", 13)
    fva = fnt("DejaVuSans-Bold.ttf", 12)
    for y, (lab, val) in zip((560, 594, 628),
                             [("PASSPORT NO", "ZP 483 921"),
                              ("DATE OF ISSUE", "04 NOV 2026"),
                              ("EXPIRY", "04 NOV 2031")]):
        d.text((320, y), lab, font=fla, fill=LABEL_C)
        d.text((320, y + 14), val, font=fva, fill=INK)
    fa = fnt("DejaVuSans.ttf", 13)
    fav = fit_font(d, "OFFICE OF WIND & PASSPORTS", 181, 13, "DejaVuSans-Bold.ttf")
    d.text((320, 655), "AUTHORITY", font=fa, fill=LABEL_C)
    d.text((320, 671), "OFFICE OF WIND & PASSPORTS", font=fav, fill=INK)

    # MRZ, two lines, 24px mono bold rendered then scaled to page width
    mrz_lines = [
        "P<ZPR<ZEPHYR<<KESTREL<<A<<<<<<<<<<<<<<<<<<",
        "ZP48392148ZPR6103124F3111049<<<<<<<<<<<8",
    ]
    fm = fnt("DejaVuSansMono-Bold.ttf", 24)
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    y0 = 691
    for s in mrz_lines:
        adv = [probe.textlength(ch, font=fm) + 2 for ch in s]
        sw = int(sum(adv)) + 2
        strip = Image.new("RGBA", (sw, 40), (0, 0, 0, 0))
        sdd = ImageDraw.Draw(strip)
        x = 1.0
        for ch, a in zip(s, adv):
            sdd.text((x, 6), ch, font=fm, fill=INK + (255,))
            x += a
        scale = 0.52
        strip = strip.resize((int(round(sw * scale)), int(round(40 * scale))), Image.LANCZOS)
        img.alpha_composite(strip, (int(round(266 - strip.width / 2)), y0))
        y0 += strip.height + 4

    # page number 1
    d.text((44, 964), "1", font=fnt("DejaVuSans.ttf", 12), fill=LABEL_C)

    # ---------- RIGHT PAGE ----------
    # fee stamp, rotated 6 deg clockwise
    paste_rot(img, fee_stamp(), 790, 210, 6)
    # travel stamps, in ink order a, b, c
    paste_rot(img, stamp_arrival(), 600, 430, -8)
    paste_rot(img, stamp_departure(), 760, 560, 5)
    paste_rot(img, stamp_admission(), 610, 690, -4)

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
