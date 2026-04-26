"""Render the social-share preview image (Open Graph card).

Outputs:
    docs/og-image.png  (1200x630, the standard OG/Twitter card size)

Run:
    .venv/bin/python docs/og_image.py

The image uses the same warm cream / terracotta palette as the
benchmark card. It shows the title, tagline, and headline stats so a
shared link to the repo or the Pages site renders with a meaningful
preview instead of a generic GitHub thumbnail.
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
DIVIDER = (233, 223, 206)       # #e9dfce


def _font(size: int, weight: str = "Regular") -> ImageFont.FreeTypeFont:
    """Best-effort font lookup. Falls back to a default if the named
    Helvetica Neue is not present on the system."""
    candidates = []
    if weight == "Bold":
        candidates += [
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Avenir.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        candidates += [
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Avenir.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for path in candidates:
        if Path(path).exists():
            try:
                # For .ttc collections, index 0 is the regular face.
                idx = 1 if weight == "Bold" and path.endswith(".ttc") else 0
                return ImageFont.truetype(path, size, index=idx)
            except (OSError, IndexError):
                continue
    return ImageFont.load_default()


def _vertical_gradient(width: int, height: int) -> Image.Image:
    """Return a vertical gradient from BG_TOP to BG_BOTTOM."""
    base = Image.new("RGB", (width, height), BG_TOP)
    top = BG_TOP
    bot = BG_BOTTOM
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3))
        for x in range(width):
            base.putpixel((x, y), color)
    return base


def _gradient_fast(width: int, height: int) -> Image.Image:
    """Faster gradient using row-fill instead of per-pixel writes."""
    base = Image.new("RGB", (width, height), BG_TOP)
    draw = ImageDraw.Draw(base)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(
            int(BG_TOP[i] * (1 - t) + BG_BOTTOM[i] * t) for i in range(3)
        )
        draw.line([(0, y), (width, y)], fill=color)
    return base


def _rounded_pill(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    fill: tuple[int, int, int],
    radius: int,
) -> None:
    """Draw a rounded-rectangle pill."""
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def _stat_block(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    big: str,
    label: str,
    big_font: ImageFont.FreeTypeFont,
    label_font: ImageFont.FreeTypeFont,
) -> None:
    """Draw a 'stat' element: a large number/short string above a small label."""
    draw.text((x, y), big, fill=INK, font=big_font)
    draw.text((x, y + 70), label, fill=INK_MUTED, font=label_font)


def render() -> None:
    img = _gradient_fast(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)

    # Outer panel frame for visual containment
    draw.rounded_rectangle(
        (32, 32, WIDTH - 32, HEIGHT - 32),
        radius=24,
        fill=(255, 250, 244),
        outline=DIVIDER,
        width=1,
    )

    # Kicker pill
    kicker_text = "v1.0.0"
    kicker_font = _font(20, "Bold")
    kicker_w = draw.textlength(kicker_text, font=kicker_font)
    pill_x0, pill_y0 = 80, 78
    pill_pad_x, pill_pad_y = 16, 8
    _rounded_pill(
        draw,
        (
            pill_x0,
            pill_y0,
            pill_x0 + int(kicker_w) + pill_pad_x * 2,
            pill_y0 + 36,
        ),
        ACCENT_BG,
        18,
    )
    draw.text(
        (pill_x0 + pill_pad_x, pill_y0 + pill_pad_y - 2),
        kicker_text,
        fill=ACCENT,
        font=kicker_font,
    )

    # Title
    title_font = _font(70, "Bold")
    draw.text(
        (80, 138),
        "Wearable Assistant",
        fill=INK,
        font=title_font,
    )
    draw.text(
        (80, 218),
        "Context Benchmark",
        fill=INK,
        font=title_font,
    )

    # Subtitle
    subtitle_font = _font(26)
    subtitle_lines = [
        "Does the model use the camera frame the user is looking at",
        "right now, or stay anchored to an earlier one?",
    ]
    y = 320
    for line in subtitle_lines:
        draw.text((80, y), line, fill=INK_MUTED, font=subtitle_font)
        y += 36

    # Divider
    draw.line([(80, 430), (WIDTH - 80, 430)], fill=DIVIDER, width=2)

    # Stats row
    big_font = _font(48, "Bold")
    label_font = _font(20)
    stats = [
        ("50", "scenarios"),
        ("4", "published runs"),
        ("Reference", "resolution"),
        ("MIT", "license"),
    ]
    col_w = (WIDTH - 160) // len(stats)
    for i, (big, label) in enumerate(stats):
        _stat_block(
            draw,
            80 + i * col_w,
            460,
            big,
            label,
            big_font,
            label_font,
        )

    # Footer attribution (left) and URL (right)
    footer_font = _font(20, "Bold")
    author_text = "by Nate Dryer"
    draw.text(
        (80, HEIGHT - 80),
        author_text,
        fill=INK_MUTED,
        font=footer_font,
    )
    url_text = "n-dryer.github.io/wearable-assistant-context-bench"
    url_w = draw.textlength(url_text, font=footer_font)
    draw.text(
        (WIDTH - 80 - int(url_w), HEIGHT - 80),
        url_text,
        fill=ACCENT,
        font=footer_font,
    )

    img.save(OUT_PATH, "PNG", optimize=True)
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    render()
