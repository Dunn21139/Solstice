#!/usr/bin/env python3
"""
gen_assets.py - generate the Solstice visual identity in place.

Replaces every branded bitmap in the asset catalog (app icons, alternate
icons, in-app wordmark, theme logo, theme backgrounds) while leaving the
catalog JSON untouched, so the compiled asset catalog stays valid.

    python3 gen_assets.py --root /path/to/solstice --brand Solstice
"""

import argparse
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

# --------------------------------------------------------------------------
# Palettes: (background dark, background light, sun core, sun edge, accent)
# --------------------------------------------------------------------------
PALETTES = {
    "default":  ("#120C33", "#3E2170", "#FFF0C4", "#FFC24B", "#FFB020"),
    "Blue":     ("#05183A", "#12457C", "#E4F2FF", "#63AAFF", "#2E7FE0"),
    "Red":      ("#33080F", "#8A1E2B", "#FFE4DC", "#FF7A63", "#E0432E"),
    "Purple":   ("#1E0C3C", "#5A2A96", "#F4E6FF", "#C08BFF", "#8C4BE0"),
    "ElleKit":  ("#04241D", "#0F6351", "#E2FFF2", "#74FFB6", "#25C98A"),
}

FONT_CANDIDATES = [
    ("/System/Library/Fonts/Avenir Next.ttc", 0),   # Avenir Next Bold
    ("/System/Library/Fonts/HelveticaNeue.ttc", 1), # Helvetica Neue Bold
    ("/System/Library/Fonts/Helvetica.ttc", 1),
]


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_font(px):
    for path, idx in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, px, index=idx)
        except OSError:
            continue
    raise RuntimeError("no usable font found")


# --------------------------------------------------------------------------
# gradient helpers
# --------------------------------------------------------------------------
def diagonal_gradient(size, c0, c1, angle=-45):
    big = Image.linear_gradient("L").resize((size * 2, size * 2), Image.BICUBIC)
    rot = big.rotate(angle, resample=Image.BICUBIC, expand=True)
    w, h = rot.size
    g = rot.crop((w // 2 - size // 2, h // 2 - size // 2,
                  w // 2 + size // 2, h // 2 + size // 2))
    return ImageOps.colorize(g, black=c0, white=c1)


# --------------------------------------------------------------------------
# exact circular falloff (Image.radial_gradient only peaks at the corners,
# which turns a pasted mask into a rounded square)
# --------------------------------------------------------------------------
_FALLOFF = {}
_FALLOFF_N = 512


def _falloff(power):
    key = round(float(power), 3)
    if key not in _FALLOFF:
        n = _FALLOFF_N
        img = Image.new("L", (n, n), 0)
        px = img.load()
        c = (n - 1) / 2.0
        for y in range(n):
            dy = (y - c) / c
            for x in range(n):
                dx = (x - c) / c
                d2 = dx * dx + dy * dy
                px[x, y] = int(255 * (1.0 - math.sqrt(d2)) ** power) if d2 < 1.0 else 0
        _FALLOFF[key] = img
    return _FALLOFF[key]


def radial_mask(size, cx, cy, radius, blur=0.0, power=1.0):
    """L-mode mask, white at (cx, cy) fading to exactly black at `radius`."""
    d = max(2, int(round(radius * 2)))
    m = _falloff(power).resize((d, d), Image.BICUBIC)
    full = Image.new("L", (size, size), 0)
    full.paste(m, (int(round(cx - radius)), int(round(cy - radius))))
    if blur:
        full = full.filter(ImageFilter.GaussianBlur(blur))
    return full


def screen(base, colour, mask):
    layer = Image.new("RGB", base.size, colour)
    return ImageChops.screen(base, Image.composite(layer, Image.new("RGB", base.size, (0, 0, 0)), mask))


# --------------------------------------------------------------------------
# the mark: a radiant sun (disc + tapered rays)
# --------------------------------------------------------------------------
def sun_layer(S, core, edge, accent):
    """Return (rgb, mask) for the sun mark, centred on a black canvas."""
    cx = cy = S * 0.5
    R = S * 0.185
    n_rays = 12
    inner = R * 1.42
    outer_long = R * 1.95
    outer_short = R * 1.62
    base_hw = R * 0.115

    rays = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(rays)
    for i in range(n_rays):
        a = -math.pi / 2 + i * (2 * math.pi / n_rays)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux
        outer = outer_long if i % 2 == 0 else outer_short
        bx, by = cx + inner * ux, cy + inner * uy
        tx, ty = cx + outer * ux, cy + outer * uy
        d.polygon([(bx + base_hw * px, by + base_hw * py),
                   (bx - base_hw * px, by - base_hw * py),
                   (tx, ty)], fill=255)

    disc = radial_mask(S, cx, cy, R, power=0.85)
    mask = ImageChops.lighter(rays, disc).filter(ImageFilter.GaussianBlur(S / 900))

    rgb = ImageOps.colorize(mask, black=accent, white=core)
    rgb = Image.composite(ImageOps.colorize(disc, black=edge, white=core), rgb, disc)
    return rgb, mask


def render_icon(size, palette):
    dark, light, core, edge, accent = (hexrgb(c) for c in palette)
    S = size * 4

    # night sky: bright behind the sun, falling off to the edges
    bg = ImageOps.colorize(
        radial_mask(S, S * 0.5, S * 0.5, S * 0.82, power=1.25),
        black=dark, white=light)

    rnd = random.Random(20260101)
    stars = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(stars)
    for _ in range(170):
        x, y = rnd.uniform(0, S), rnd.uniform(0, S)
        r = rnd.uniform(0.5, 2.1) * (S / 1024)
        d.ellipse((x - r, y - r, x + r, y + r), fill=rnd.randint(70, 220))
    bg = screen(bg, (255, 255, 255), stars.filter(ImageFilter.GaussianBlur(S / 1500)))

    # soft halo, kept well below the sun's own brightness
    halo = radial_mask(S, S * 0.5, S * 0.5, S * 0.46, blur=S * 0.03, power=2.8)
    bg = screen(bg, tuple(int(c * 0.75) for c in accent),
                halo.point(lambda v: int(v * 0.62)))
    sun_rgb, sun_mask = sun_layer(S, core, edge, accent)
    img = Image.composite(sun_rgb, bg, sun_mask)

    # vignette
    vig = radial_mask(S, S * 0.5, S * 0.5, S * 1.0, power=2.2)
    img = Image.composite(Image.new("RGB", (S, S), (0, 0, 0)), img,
                          ImageOps.invert(vig).point(lambda v: int(v * 0.38)))

    return img.resize((size, size), Image.LANCZOS)


def render_mark(size, palette, alpha=0.95):
    """Transparent sun mark used for the boot-logo overlay / PDF."""
    dark, light, core, edge, accent = (hexrgb(c) for c in palette)
    S = size
    rgb, mask = sun_layer(S, core, edge, accent)
    out = ImageOps.colorize(mask, black=edge, white=core).convert("RGBA")
    out.putalpha(mask.point(lambda v: int(v * alpha)))
    return out


def render_wordmark(width, height, brand):
    """White wordmark on transparent, baseline-centred."""
    S = 4
    W, H = width * S, height * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # largest font size that fits inside the box
    lo, hi = 4, H
    while lo < hi:
        mid = (lo + hi + 1) // 2
        f = load_font(mid)
        box = ImageDraw.Draw(img).textbbox((0, 0), brand, font=f)
        if (box[2] - box[0]) <= W * 0.97 and (box[3] - box[1]) <= H * 0.94:
            lo = mid
        else:
            hi = mid - 1

    font = load_font(lo)
    box = ImageDraw.Draw(img).textbbox((0, 0), brand, font=font)
    x = (W - (box[2] - box[0])) / 2 - box[0]
    y = (H - (box[3] - box[1])) / 2 - box[1]
    ImageDraw.Draw(img).text((x, y), brand, font=font, fill=(255, 255, 255, 255))
    return img.resize((width, height), Image.LANCZOS)


def render_background(width, height, palette):
    """Soft aurora field in the brand palette."""
    dark, light, core, edge, accent = (hexrgb(c) for c in palette)
    rnd = random.Random(hash(palette[0]) & 0xFFFF)
    S = 2  # supersample factor for blob smoothness
    W, H = width // S, height // S

    img = diagonal_gradient(max(W, H), dark, light, angle=-25).resize((W, H), Image.BICUBIC)

    tints = [light, accent, edge]
    for _ in range(7):
        cx = rnd.uniform(0, W)
        cy = rnd.uniform(0, H)
        r = rnd.uniform(W * 0.14, W * 0.40)
        col = rnd.choice(tints)
        blobs = Image.new("L", (W, H), 0)
        ImageDraw.Draw(blobs).ellipse((cx - r, cy - r * 0.55, cx + r, cy + r * 0.55), fill=rnd.randint(42, 88))
        blobs = blobs.filter(ImageFilter.GaussianBlur(W * 0.10))
        img = screen(img, col, blobs)

    dust = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(dust)
    for _ in range(260):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        rr = rnd.uniform(0.5, 1.7)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=rnd.randint(55, 170))
    img = screen(img, (255, 255, 255), dust.filter(ImageFilter.GaussianBlur(0.8)))

    return img.resize((width, height), Image.LANCZOS)


# --------------------------------------------------------------------------
def palette_for(name):
    for key, pal in PALETTES.items():
        if key.lower() in name.lower():
            return pal
    return PALETTES["default"]


def build_preview(sheet_path, brand):
    """Contact sheet so the generated identity can be eyeballed."""
    W, H = 1500, 980
    sheet = Image.new("RGB", (W, H), (24, 22, 32))
    d = ImageDraw.Draw(sheet)
    label = load_font(26)

    icons = [512, 180, 120, 76, 40]
    x = 40
    for i, sz in enumerate(icons):
        ic = render_icon(sz, PALETTES["default"])
        d.text((x, 40), f"{sz}px", fill=(170, 170, 190), font=label)
        sheet.paste(ic, (x, 90))
        x += sz + 40

    pal_names = ["Blue", "Red", "Purple", "ElleKit"]
    x = 40
    for pname in pal_names:
        ic = render_icon(150, PALETTES[pname])
        d.text((x, 320), pname, fill=(170, 170, 190), font=label)
        sheet.paste(ic, (x, 365))
        x += 190

    wm = render_wordmark(810, 160, brand)
    d.text((40, 560), "wordmark on dark", fill=(170, 170, 190), font=label)
    dark_bg = Image.new("RGB", (810, 160), (20, 18, 28))
    dark_bg.paste(wm, (0, 0), wm)
    sheet.paste(dark_bg, (40, 600))

    mk = render_mark(320, PALETTES["default"]).resize((320, 320), Image.LANCZOS)
    d.text((900, 560), "logo mark on dark", fill=(170, 170, 190), font=label)
    dark2 = Image.new("RGB", (320, 320), (20, 18, 28))
    dark2.paste(mk, (0, 0), mk)
    sheet.paste(dark2, (900, 600))

    bgp = render_background(480, 320, PALETTES["default"])
    d.text((40, 790), "background", fill=(170, 170, 190), font=label)
    sheet.paste(bgp, (40, 830))
    sheet.save(sheet_path)
    print(f"preview     : {sheet_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--brand", default="Solstice")
    ap.add_argument("--preview", help="write a contact sheet to this PNG path")
    args = ap.parse_args()

    if args.preview:
        build_preview(args.preview, args.brand)
        return

    assets = os.path.join(args.root, "Application", args.brand,
                          "Assets.xcassets")
    if not os.path.isdir(assets):
        sys.exit(f"asset catalog not found: {assets}")

    written = 0

    for dirpath, _, filenames in os.walk(assets):
        name = os.path.basename(dirpath)
        pal = palette_for(dirpath)

        for fn in filenames:
            path = os.path.join(dirpath, fn)
            try:
                with Image.open(path) as im:
                    w, h = im.size
                    fmt = im.format
            except Exception:
                continue

            if name.endswith(".appiconset") and fn.lower().endswith(".png"):
                # full-bleed, opaque app icon
                render_icon(w, pal).convert("RGB").save(path, "PNG", optimize=True)
                written += 1

            elif name == f"{args.brand}.imageset" and fn.lower().endswith(".png"):
                render_wordmark(w, h, args.brand).save(path, "PNG", optimize=True)
                written += 1

            elif name == f"{args.brand}Logo.imageset" and fn.lower().endswith(".pdf"):
                mark = render_mark(w, pal)
                mark.save(path, "PDF", resolution=72.0)
                written += 1

            elif "Background" in name and fn.lower().endswith(".jpg"):
                render_background(w, h, pal).save(path, "JPEG", quality=92)
                written += 1

    print(f"brand       : {args.brand}")
    print(f"images      : {written} written")
    print(f"catalog     : {assets}")


if __name__ == "__main__":
    main()
