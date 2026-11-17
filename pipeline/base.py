"""Shared drawing basics for Doc Stick: canvas, colours, font, easing, text."""
import math, os, shutil, subprocess
import cairo

W, H, FPS = 1080, 1920, 30
GROUND = 1560
CAP_Y = 470                     # caption centre; captions use roughly y 330 to 620
CAP_BOTTOM = 640                # nothing else may sit above this line
BG = (0.969, 0.953, 0.918)
FLOOR = (0.90, 0.87, 0.81)
INK = (0.10, 0.10, 0.10)
RED = (0.88, 0.20, 0.17)
FONT = "Inter Display Black"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ensure_font():
    """Install the channel font for fontconfig once (needed on fresh machines and in GitHub Actions)."""
    out = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True).stdout
    if "Inter Display" in out: return
    d = os.path.expanduser("~/.local/share/fonts"); os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(ROOT, "assets", "fonts", "InterDisplay-Black.otf"), d)
    subprocess.run(["fc-cache", "-f"], capture_output=True)


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp(x); return x ** 3
def ease_inout(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def stroke(c, col, w):
    c.set_source_rgb(*col); c.set_line_width(w); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()


def fillstroke(c, fill, col=INK, w=8):
    c.set_source_rgb(*fill); c.fill_preserve(); stroke(c, col, w)


def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path(); c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); c.close_path()


def font(c, size):
    c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)


def text_w(c, s, size):
    font(c, size); return c.text_extents(s).x_advance


def text(c, s, x, y, size, col=INK, align="center", outline=0):
    """Draw text with its baseline at y. Returns the width."""
    font(c, size); e = c.text_extents(s)
    tx = x - e.width / 2 - e.x_bearing if align == "center" else x
    c.move_to(tx, y); c.text_path(s)
    if outline:
        c.set_source_rgb(1, 1, 1); c.set_line_width(outline); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgb(*col); c.fill()
    return e.width


def scaled(c, x, y, s, fn):
    """Run fn() with the origin at (x, y), scaled by s. Does nothing when s is ~0."""
    if abs(s) < 0.002: return
    c.save(); c.translate(x, y); c.scale(s, s); fn(); c.restore()
