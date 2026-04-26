"""Render the social-share preview image (Open Graph card).

Outputs:
    docs/og-image.png  (1200x630, the standard OG/Twitter card size)

Run:
    .venv/bin/python docs/og_image.py

The image uses the same warm cream and terracotta palette as the
benchmark card. It shows the title, tagline, and four stat badges so
a shared link to the repo or the Pages site renders with a meaningful
preview instead of a generic GitHub thumbnail.

Design choices:
- All text uses Apple's San Francisco (SFNS.ttf), a single-face
  variable TTF. Avoids the .ttc collection indexing fragility that
  bites Helvetica.ttc.
- Hierarchy is by size only, not weight axis (more reliable across
  Pillow versions).
- Stat badges are horizontal pills, matching the hero badges. No
  number-on-top layout that overflows when a label is wide.
- Layout uses textbbox + anchor for clean alignment with no
  hardcoded text widths.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT_PATH = Path(__file__).parent / "og-image.png"

WIDTH = 1200
HEIGHT = 630

# Palette matches the benchmark card
BG_TOP = (255, 250, 244)        # #fffaf4
BG_BOTTOM = (246, 241, 234)     # #f6f1ea
INK = (43, 33, 24)              # #2b2118
INK_MUTED = (91, 74, 61)        # #5b4a3d
ACCENT = (177, 79, 49)          # #b14f31
ACCENT_BG = (244, 223, 213)     # #f4dfd5
PANEL = (240, 232, 221)         # #f0e8dd
PANEL_BORDER = (227, 216, 200)  # #e3d8c8
DIVIDER = (233, 223, 206)       # #e9dfce


# Font discovery: prefer single-face TTFs; avoid .ttc collections
# whose face indices vary across PIL versions.
FONT_CANDIDATES = [
    "/System/Library/Fonts/SFNS.ttf",
    "/System/Library/Fonts/SFNSDisplay.ttf",
    "/System/Library/Fonts/SFNSText.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    """Best-effort font lookup. Returns the first single-face TTF that
    loads. Falls back to Pillow's default if nothing found."""
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _gradient(width: int, height: int) -> Image.Image:
    """Vertical gradient from BG_TOP to BG_BOTTOM, drawn as scanlines."""
    base = Image.new("RGB", (width, height), BG_TOP)
    draw = ImageDraw.Draw(base)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(
            int(BG_TOP[i] * (1 - t) + BG_BOTTOM[i] * t) for i in range(3)
        )
        draw.line([(0, y), (width, y)], fill=color)
    return base


def _draw_pill(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    pad_x: int = 18,
    pad_y: int = 10,
    bg: tuple[int, int, int] = PANEL,
    border: tuple[int, int, int] | None = PANEL_BORDER,
    fg: tuple[int, int, int] = INK_MUTED,
) -> int:
    """Draw a rounded-pill badge containing `text`. Returns the right
    edge x-coordinate of the pill so callers can position the next
    pill flush against it."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pill_w = text_w + pad_x * 2
    pill_h = text_h + pad_y * 2
    radius = pill_h // 2
    if border is not None:
        draw.rounded_rectangle(
            (x, y, x + pill_w, y + pill_h),
            radius=radius,
            fill=bg,
            outline=border,
            width=1,
        )
    else:
        draw.rounded_rectangle(
            (x, y, x + pill_w, y + pill_h),
            radius=radius,
            fill=bg,
        )
    # Center text vertically inside the pill using the bbox y-offset
    draw.text(
        (x + pad_x - bbox[0], y + pad_y - bbox[1]),
        text,
        fill=fg,
        font=font,
    )
    return x + pill_w


def render() -> None:
    img = _gradient(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)

    # Inner card surface for visual containment
    draw.rounded_rectangle(
        (32, 32, WIDTH - 32, HEIGHT - 32),
        radius=24,
        fill=(255, 250, 244),
        outline=DIVIDER,
        width=1,
    )

    # ---- Hero kicker pill ------------------------------------------------
    kicker_font = _font(22)
    _draw_pill(
        draw,
        "v1.0.0",
        kicker_font,
        x=80,
        y=80,
        pad_x=18,
        pad_y=8,
        bg=ACCENT_BG,
        border=None,
        fg=ACCENT,
    )

    # ---- Title (two lines) ----------------------------------------------
    title_font = _font(72)
    draw.text(
        (80, 138),
        "Wearable Assistant",
        fill=INK,
        font=title_font,
    )
    draw.text(
        (80, 220),
        "Context Benchmark",
        fill=INK,
        font=title_font,
    )

    # ---- Subtitle (two lines) -------------------------------------------
    subtitle_font = _font(26)
    subtitle_lines = [
        "Does the model use the camera frame the user is looking at",
        "right now, or stay anchored to an earlier one?",
    ]
    y = 320
    for line in subtitle_lines:
        draw.text((80, y), line, fill=INK_MUTED, font=subtitle_font)
        y += 36

    # ---- Stat badges row -------------------------------------------------
    # Horizontal pill row, consistent with hero. Wraps to next line if
    # they don't fit on one row (they should).
    badge_font = _font(22)
    badges = [
        "50 scenarios",
        "4 published runs",
        "Reference resolution",
        "MIT license",
    ]
    gap = 12
    cursor_x = 80
    badge_y = 460
    for label in badges:
        right = _draw_pill(
            draw,
            label,
            badge_font,
            x=cursor_x,
            y=badge_y,
            pad_x=18,
            pad_y=10,
            bg=PANEL,
            border=PANEL_BORDER,
            fg=INK_MUTED,
        )
        cursor_x = right + gap

    # ---- Footer: author (left) + URL (right) ----------------------------
    footer_font = _font(22)
    author_text = "by Nate Dryer"
    draw.text(
        (80, HEIGHT - 90),
        author_text,
        fill=INK_MUTED,
        font=footer_font,
    )
    url_text = "n-dryer.github.io/wearable-assistant-context-bench"
    bbox = draw.textbbox((0, 0), url_text, font=footer_font)
    url_w = bbox[2] - bbox[0]
    draw.text(
        (WIDTH - 80 - url_w, HEIGHT - 90),
        url_text,
        fill=ACCENT,
        font=footer_font,
    )

    img.save(OUT_PATH, "PNG", optimize=True)
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    render()
