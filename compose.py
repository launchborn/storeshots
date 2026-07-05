#!/usr/bin/env python3
"""Compose App Store / Play Store screenshots: drop raw device screenshots into
a real device frame, add a caption + accent underline on a styled background.

Driven entirely by a JSON config (see config.example.json). Run:

    python3 compose.py --config path/to/config.json

Frame handling is fully automatic: the interior screen cutout is detected from
the frame PNG's own alpha channel (by flood-filling the *exterior* transparent
region and keeping only the walled-off interior hole), so any frame in frames/
works regardless of its resolution — no per-model coordinates to maintain.
"""
import argparse
import json
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required: pip install Pillow numpy")

try:
    import numpy as np
except ImportError:
    sys.exit("numpy is required: pip install Pillow numpy")

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
FRAMES_DIR = os.path.join(SKILL_DIR, "frames")

# Fonts to try, in order (first that exists wins). Override via config["font"].
DEFAULT_FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def resolve_font(path_hint):
    for p in ([path_hint] if path_hint else []) + DEFAULT_FONTS:
        if p and os.path.exists(p):
            return p
    sys.exit("No usable font found. Set config['font'] to a .ttf/.ttc path.")


def _frame_path(frame_name):
    for c in (frame_name,
              os.path.join(FRAMES_DIR, frame_name),
              os.path.join(FRAMES_DIR, frame_name + ".png")):
        if os.path.exists(c):
            return c
    return None


def load_frame(frame_name):
    # Accept a bare slug (frames/<slug>.png) or an explicit path.
    p = _frame_path(frame_name)
    if p:
        return Image.open(p).convert("RGBA")
    avail = ", ".join(sorted(
        f[:-4] for f in os.listdir(FRAMES_DIR) if f.endswith(".png")
    )) if os.path.isdir(FRAMES_DIR) else "(none)"
    sys.exit(f"Frame '{frame_name}' not found. Available: {avail}")


# Cache of resolved frames: slug -> (frame_img, mask, bbox, cutout_aspect).
_FRAME_CACHE = {}


def get_frame(slug):
    if slug not in _FRAME_CACHE:
        frame = load_frame(slug)
        mask, bbox = interior_mask_and_bbox(frame)
        aspect = (bbox[2] - bbox[0]) / (bbox[3] - bbox[1])
        _FRAME_CACHE[slug] = (frame, mask, bbox, aspect)
    return _FRAME_CACHE[slug]


def list_frame_slugs():
    if not os.path.isdir(FRAMES_DIR):
        return []
    return sorted(f[:-4] for f in os.listdir(FRAMES_DIR) if f.endswith(".png"))


def pick_frame_for(shot_size, color_pref=None):
    """Pick the bundled frame whose screen cutout aspect ratio best matches the
    screenshot. Ties (near-equal aspect) are broken by an optional color-name
    preference (e.g. "black"), then by slug for determinism. Output image size
    is unaffected — only which device frame wraps the shot."""
    slugs = list_frame_slugs()
    if not slugs:
        sys.exit("No frames available in frames/ for auto-selection.")
    target = shot_size[0] / shot_size[1]
    scored = []
    for slug in slugs:
        _, _, _, aspect = get_frame(slug)
        diff = abs(aspect - target)
        color_bonus = 0 if (color_pref and color_pref.lower() in slug.lower()) else 1
        scored.append((round(diff, 4), color_bonus, slug))
    scored.sort()
    return scored[0][2]


def interior_mask_and_bbox(frame, alpha_thresh=40):
    """Return (mask, (x0, y0, x1, y1)) for ONLY the interior screen cutout.

    The frame PNG is transparent both at the screen hole AND outside the phone
    body. We flood-fill the exterior (seeded from every corner) and keep the
    transparent pixels that remain — the screen cutout, walled off by the opaque
    bezel.
    """
    binar = frame.split()[-1].point(lambda a: 255 if a < alpha_thresh else 0).convert("RGB")
    w, h = binar.size
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if binar.getpixel(seed) == (255, 255, 255):
            ImageDraw.floodfill(binar, seed, (255, 0, 0), thresh=10)
    arr = np.asarray(binar)
    interior = (arr[:, :, 0] == 255) & (arr[:, :, 1] == 255) & (arr[:, :, 2] == 255)
    if not interior.any():
        sys.exit("Could not detect an interior screen cutout in the frame.")
    ys, xs = np.where(interior)
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    mask = Image.fromarray((interior * 255).astype("uint8"), "L")
    return mask, bbox


def make_background(size, bg):
    w, h = size
    kind = bg.get("type", "gradient")
    if kind == "solid":
        return Image.new("RGBA", size, tuple(bg.get("color", [0, 0, 0])) + (255,))
    top = tuple(bg.get("top", [22, 25, 32]))
    bottom = tuple(bg.get("bottom", [6, 7, 9]))
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1) if h > 1 else 0
        draw.line(
            [(0, y), (w, y)],
            fill=tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)),
        )
    return img.convert("RGBA")


def draw_caption(canvas, text, cfg, canvas_w):
    if not text:
        return None
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(cfg["_font"], cfg.get("font_size", 82))
    color = tuple(cfg.get("color", [255, 255, 255]))
    shadow = tuple(cfg.get("shadow", [0, 0, 0]))
    line_height = cfg.get("line_height", int(cfg.get("font_size", 82) * 1.27))
    y = cfg.get("top", 180)
    for line in text.split("\n"):
        bb = draw.textbbox((0, 0), line, font=font)
        x = (canvas_w - (bb[2] - bb[0])) // 2
        draw.text((x + 3, y + 4), line, font=font, fill=shadow)
        draw.text((x, y), line, font=font, fill=color)
        y += line_height
    return y


def build_framed_phone(frame, mask, bbox, shot, crop_top, patches):
    for (x0, y0, x1, y1) in patches:
        ImageDraw.Draw(shot).rectangle([x0, y0, x1, y1], fill=(0, 0, 0, 255))
    if crop_top:
        shot = shot.crop((0, crop_top, shot.width, shot.height))

    bx0, by0, bx1, by1 = bbox
    target_w, target_h = bx1 - bx0, by1 - by0
    # Scale-to-COVER the cutout: the screenshot always fills the whole screen
    # hole with no background gap, even when its aspect ratio differs from the
    # frame's (e.g. a 15 Pro screenshot in a 16 Pro Max frame). Overflow is
    # clipped by the mask. Center horizontally, top-align vertically so the
    # status bar / Dynamic Island line up at the top.
    scale = max(target_w / shot.width, target_h / shot.height)
    new_w = max(1, round(shot.width * scale))
    new_h = max(1, round(shot.height * scale))
    resized = shot.resize((new_w, new_h), Image.LANCZOS)

    screen_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    paste_x = bx0 + (target_w - new_w) // 2
    screen_layer.paste(resized, (paste_x, by0))
    screen_layer.putalpha(mask)

    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.alpha_composite(screen_layer)
    out.alpha_composite(frame)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    with open(args.config) as f:
        cfg = json.load(f)

    conf_dir = os.path.dirname(os.path.abspath(args.config))
    src_dir = os.path.join(conf_dir, cfg.get("src_dir", "."))
    out_dir = os.path.join(conf_dir, cfg.get("output_dir", "appstore"))
    os.makedirs(out_dir, exist_ok=True)

    # frame: "auto" (default) picks the best-matching bundled frame per
    # screenshot by aspect ratio; a slug forces one frame for all. Per-item
    # "frame" overrides. Optional "frame_color" biases auto ties (e.g. "black").
    default_frame = cfg.get("frame", "auto")
    color_pref = cfg.get("frame_color")

    # Canvas defaults to a 6.9" App Store size, independent of source device.
    canvas_cfg = cfg.get("canvas", {})
    canvas_w = canvas_cfg.get("width", 1320)
    canvas_h = canvas_cfg.get("height", 2868)

    cap_cfg = dict(cfg.get("caption", {}))
    cap_cfg["_font"] = resolve_font(cfg.get("font"))

    accent = cfg.get("accent")
    bg = cfg.get("background", {"type": "gradient"})
    margins = cfg.get("margins", {})
    side_m = margins.get("side", 60)
    bottom_m = margins.get("bottom", 70)
    gap = margins.get("gap_after_caption", 90)

    for item in cfg["screenshots"]:
        shot = Image.open(os.path.join(src_dir, item["src"])).convert("RGBA")

        frame_choice = item.get("frame", default_frame)
        if frame_choice == "auto":
            frame_choice = pick_frame_for(shot.size, color_pref)
            print(f"  {item['src']}: auto-picked frame '{frame_choice}'")
        frame, mask, bbox, _ = get_frame(frame_choice)

        framed = build_framed_phone(
            frame, mask, bbox, shot,
            item.get("crop_top", 0), item.get("patches", []),
        )

        canvas = make_background((canvas_w, canvas_h), bg)
        cap_bottom = draw_caption(canvas, item.get("caption", ""), cap_cfg, canvas_w)

        if cap_bottom is not None and accent:
            uy = cap_bottom + 26
            uw = cfg.get("accent_width", 110)
            ImageDraw.Draw(canvas).rounded_rectangle(
                [(canvas_w - uw) // 2, uy, (canvas_w + uw) // 2, uy + 8],
                radius=4, fill=tuple(accent),
            )
            top_margin = uy + gap
        else:
            top_margin = (cap_bottom or cap_cfg.get("top", 180)) + gap

        avail_w = canvas_w - 2 * side_m
        avail_h = canvas_h - top_margin - bottom_m
        s = min(avail_w / framed.width, avail_h / framed.height)
        fw, fh = int(framed.width * s), int(framed.height * s)
        framed_r = framed.resize((fw, fh), Image.LANCZOS)

        px = (canvas_w - fw) // 2
        py = top_margin + (avail_h - fh) // 2
        canvas.alpha_composite(framed_r, (px, py))

        out_path = os.path.join(out_dir, item["out"])
        canvas.convert("RGB").save(out_path, "PNG")
        print("Wrote", out_path)


if __name__ == "__main__":
    main()
