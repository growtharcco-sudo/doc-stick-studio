"""Doc Stick props: every drawable object, drawn at its anchor point (0, 0) at scale 1.

Each prop is registered with @prop(name, bbox, anchor, doc):
  bbox   (x0, y0, x1, y1) around the anchor at scale 1, used by the layout check
  anchor "ground" (bottom-centre stands on the floor) or "center"
The draw function gets (c, st): st.t (seconds into the Reel), st.age (seconds since it appeared),
st.state / st.prev / st.since (current state, previous state, seconds since the change),
st.moving (True while sliding in or out) and st.args (the brief's "args").

Adding a prop for a new topic is allowed (ROUTINE.md step 4): register it here, keep the flat cartoon style
(thick dark outlines, flat fills, no gradients), give an honest bbox, and check it with make_reel.py --sheet.
"""
import math
from types import SimpleNamespace
from base import INK, RED, stroke, fillstroke, rrect, text, ease_out, ease_inout, clamp

PROPS = {}
BLUE = (0.25, 0.55, 0.90); GREEN = (0.38, 0.66, 0.30); DGREEN = (0.16, 0.33, 0.13); LGREEN = (0.74, 0.86, 0.55)
BROWN = (0.55, 0.36, 0.18); DBROWN = (0.33, 0.20, 0.09); PEACH = (0.96, 0.80, 0.66); DPEACH = (0.55, 0.35, 0.25)
YELLOW = (0.99, 0.80, 0.20); TEAL = (0.20, 0.68, 0.75); DTEAL = (0.08, 0.35, 0.40); PINK = (0.95, 0.55, 0.68)
PURPLE = (0.55, 0.40, 0.80); GREY = (0.60, 0.60, 0.62); WHITE = (1, 1, 1); NAVY = (0.10, 0.22, 0.48)
COLORS = {"red": RED, "ink": INK, "blue": BLUE, "green": (0.15, 0.62, 0.45), "teal": TEAL, "pink": PINK,
          "purple": PURPLE, "yellow": (0.95, 0.65, 0.10), "navy": NAVY, "grey": (0.4, 0.4, 0.4)}


def col(name, default=RED): return COLORS.get(name, default) if isinstance(name, str) else (name or default)


def prop(name, bbox, anchor="center", doc=""):
    def reg(fn):
        PROPS[name] = SimpleNamespace(draw=fn, bbox=bbox, anchor=anchor, doc=doc); return fn
    return reg


def ellipse(c, x, y, rx, ry):
    c.save(); c.translate(x, y); c.scale(rx, ry); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()


def wavy_up(c, x, y, t, color, n=3, gap=50, rise=60, w=6, spd=0.8):
    """Rising wavy lines (stink, steam, heat)."""
    for i in range(n):
        ph = (t * spd + i / n) % 1
        c.save(); c.translate(x + (i - (n - 1) / 2) * gap, y - ph * rise); c.move_to(0, 0)
        for k in range(3): c.curve_to(12, -10 - k * 22, -12, -14 - k * 22, 0, -22 - k * 22)
        c.set_source_rgba(*color, (1 - ph) * 0.9); c.set_line_width(w); c.stroke(); c.restore()


# ------------------------------------------------------------------ animals and nature
@prop("crocodile", (-215, -125, 365, 0), "ground", "side-view crocodile facing left. state 'sad' = sad eyes + tear")
def crocodile(c, st):
    t, ow = st.t, 5
    for i, lx in enumerate((-20, 30, 100, 150)):
        ph = math.sin(t * 14 + i * 1.6) * 6 if st.moving else 0
        c.rectangle(lx + ph, -34, 28, 34); fillstroke(c, GREEN, DGREEN, ow)
    tw = math.sin(t * 3) * 10
    c.move_to(150, -95); c.curve_to(240, -95, 300, -50 + tw, 360, -30 + tw); c.curve_to(300, -20, 230, -30, 150, -30); c.close_path()
    fillstroke(c, GREEN, DGREEN, ow)
    ellipse(c, 60, -62, 125, 46); fillstroke(c, GREEN, DGREEN, ow)
    c.save(); c.translate(60, -40); c.scale(100, 16); c.arc(0, 0, 1, 0, math.pi); c.restore(); c.set_source_rgb(*LGREEN); c.fill()
    for rx in range(-10, 170, 30):
        dy = abs(rx - 60) * 0.12
        c.move_to(rx, -100 + dy); c.line_to(rx + 12, -122 + dy); c.line_to(rx + 24, -100 + dy); fillstroke(c, GREEN, DGREEN, 4)
    for i in range(9):
        tx = -205 + i * 17
        c.move_to(tx, -44); c.line_to(tx + 8, -30); c.line_to(tx + 16, -44); c.close_path()
        c.set_source_rgb(1, 1, 1); c.fill_preserve(); stroke(c, DGREEN, 2)
    rrect(c, -215, -88, 200, 46, 22); fillstroke(c, GREEN, DGREEN, ow)
    c.move_to(-205, -60); c.line_to(-30, -60); stroke(c, DGREEN, 3)
    c.arc(-196, -78, 4.5, 0, 2 * math.pi); c.set_source_rgb(*DGREEN); c.fill()
    c.arc(-40, -100, 28, 0, 2 * math.pi); fillstroke(c, GREEN, DGREEN, ow)
    c.arc(-44, -104, 17, 0, 2 * math.pi); fillstroke(c, WHITE, DGREEN, 3)
    if st.state == "sad":
        c.arc(-48, -98, 7, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()
        c.move_to(-63, -112); c.line_to(-26, -120); c.line_to(-26, -122); c.line_to(-63, -122); c.close_path(); c.set_source_rgb(*GREEN); c.fill()
        c.move_to(-64, -110); c.line_to(-24, -124); stroke(c, DGREEN, 5)
        c.move_to(-55, -86); c.curve_to(-57, -78, -53, -74, -55, -70); stroke(c, (0.5, 0.77, 0.91), 5)
    elif (t % 3.3) < 0.12:
        c.move_to(-58, -104); c.line_to(-30, -104); stroke(c, INK, 4)
    else:
        c.arc(-50, -104, 7, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()


@prop("poop", (-62, -125, 62, 0), "ground", "cartoon poop pile with stink lines (args.stink default true)")
def poop(c, st):
    for (cy, rx, ry) in ((-24, 62, 26), (-58, 48, 22), (-86, 32, 17)):
        ellipse(c, 0, cy, rx, ry); fillstroke(c, BROWN, DBROWN, 5)
    c.move_to(-6, -100); c.curve_to(0, -124, 18, -118, 10, -104); fillstroke(c, BROWN, DBROWN, 5)
    ellipse(c, -20, -64, 12, 5); c.set_source_rgba(1, 1, 1, 0.45); c.fill()
    if st.args.get("stink", True): wavy_up(c, 0, -140, st.t, (0.45, 0.55, 0.35))


@prop("sun", (-92, -92, 92, 92), "center", "spinning cartoon sun")
def sun(c, st):
    c.save(); c.rotate(st.t * 0.8)
    for k in range(10):
        c.save(); c.rotate(k * math.pi / 5); c.move_to(62, 0); c.line_to(88, 0); stroke(c, (0.98, 0.62, 0.10), 9); c.restore()
    c.arc(0, 0, 48, 0, 2 * math.pi); fillstroke(c, YELLOW, (0.90, 0.50, 0.05), 6); c.restore()


@prop("flame", (-60, -150, 60, 0), "ground", "flickering flame (heat, fever, burning)")
def flame(c, st):
    f = math.sin(st.t * 14) * 6
    c.move_to(0, -150 - f); c.curve_to(50, -90, 60, -40, 40, -10); c.curve_to(25, 5, -25, 5, -40, -10); c.curve_to(-60, -40, -50, -90, 0, -150 - f)
    fillstroke(c, (0.98, 0.45, 0.12), (0.70, 0.20, 0.05), 5)
    c.move_to(0, -90 + f); c.curve_to(25, -55, 28, -25, 15, -10); c.curve_to(5, -2, -5, -2, -15, -10); c.curve_to(-28, -25, -25, -55, 0, -90 + f)
    c.set_source_rgb(*YELLOW); c.fill()


@prop("drop", (-45, -75, 45, 55), "center", "water drop (sweat, drinking water). args.color")
def drop(c, st):
    c.move_to(0, -75); c.curve_to(30, -30, 45, 0, 45, 15); c.curve_to(45, 40, 25, 55, 0, 55); c.curve_to(-25, 55, -45, 40, -45, 15)
    c.curve_to(-45, 0, -30, -30, 0, -75); fillstroke(c, col(st.args.get("color"), (0.45, 0.75, 0.95)), NAVY, 5)
    ellipse(c, -15, 15, 8, 14); c.set_source_rgba(1, 1, 1, 0.7); c.fill()


# ------------------------------------------------------------------ body and biology (cartoon, never anatomical)
@prop("twins", (-70, -35, 70, 35), "center", "'the twins' (two round friendly faces). state: happy|cold|hot|chill")
def twins(c, st):
    mood = st.state or "happy"
    c.save()
    if mood == "cold": c.translate(math.sin(st.t * 70) * 3, 0)
    fill = {"cold": (0.78, 0.88, 0.98), "hot": (0.98, 0.66, 0.55)}.get(mood, PEACH)
    for cx in (-34, 34):
        c.arc(cx, 0, 32, 0, 2 * math.pi); fillstroke(c, fill, DPEACH, 5)
        if mood == "chill":
            rrect(c, cx - 24, -14, 22, 14, 5); c.set_source_rgb(*INK); c.fill()
            rrect(c, cx + 2, -14, 22, 14, 5); c.set_source_rgb(*INK); c.fill()
            c.move_to(cx - 24, -10); c.line_to(cx + 24, -10); stroke(c, INK, 3)
            c.move_to(cx - 10, 12); c.curve_to(cx - 4, 18, cx + 4, 18, cx + 10, 12); stroke(c, INK, 3.5); continue
        for ex in (-9, 9):
            c.arc(cx + ex, -6, 3.5, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()
        if mood == "cold":
            c.move_to(cx - 10, 12)
            for k in range(5): c.line_to(cx - 10 + (k + 1) * 4, 12 + (-4 if k % 2 == 0 else 0))
            stroke(c, INK, 3)
        elif mood == "hot":
            ellipse(c, cx, 13, 7, 6); c.set_source_rgb(0.4, 0.08, 0.08); c.fill()
            c.move_to(cx + 26, -24); c.curve_to(cx + 32, -14, cx + 32, -10, cx + 26, -8); c.curve_to(cx + 20, -10, cx + 20, -14, cx + 26, -24)
            c.set_source_rgb(0.5, 0.77, 0.91); c.fill()
        else:
            c.move_to(cx - 9, 10); c.curve_to(cx - 3, 17, cx + 3, 17, cx + 9, 10); stroke(c, INK, 3.5)
    c.restore()


@prop("heart", (-80, -75, 80, 75), "center", "beating cartoon heart (love, heartbeat). args.color")
def heart(c, st):
    s = 1 + 0.08 * max(0, math.sin(st.t * 8)) ** 8
    c.save(); c.scale(s, s)
    c.move_to(0, 70); c.curve_to(-90, 10, -80, -70, -35, -70); c.curve_to(-15, -70, 0, -55, 0, -40)
    c.curve_to(0, -55, 15, -70, 35, -70); c.curve_to(80, -70, 90, 10, 0, 70)
    fillstroke(c, col(st.args.get("color"), RED), (0.45, 0.06, 0.05), 6)
    ellipse(c, -42, -38, 14, 9); c.set_source_rgba(1, 1, 1, 0.5); c.fill(); c.restore()


@prop("brain", (-95, -75, 95, 70), "center", "cartoon brain (thinking, hormones, nerves)")
def brain(c, st):
    for (x, y, r) in ((-50, -20, 45), (0, -40, 48), (50, -20, 45), (-30, 25, 42), (30, 25, 42)):
        c.arc(x, y, r, 0, 2 * math.pi); c.set_source_rgb(*PINK); c.fill()
    for (x, y, r) in ((-50, -20, 45), (0, -40, 48), (50, -20, 45), (-30, 25, 42), (30, 25, 42)):
        c.arc(x, y, r, 0, 2 * math.pi); stroke(c, (0.55, 0.20, 0.30), 5)
    c.move_to(0, -80); c.curve_to(10, -40, -10, 0, 0, 60); stroke(c, (0.55, 0.20, 0.30), 5)
    for (x, y) in ((-50, -25), (45, -10), (-25, 30), (25, 25)):
        c.move_to(x - 15, y); c.curve_to(x - 5, y - 12, x + 5, y + 12, x + 15, y); stroke(c, (0.55, 0.20, 0.30), 4)


@prop("virus", (-85, -85, 85, 85), "center", "cartoon germ with spikes and an angry face (infection, flu, fever)")
def virus(c, st):
    c.save(); c.rotate(math.sin(st.t * 2) * 0.15)
    gcol = col(st.args.get("color"), (0.40, 0.75, 0.35))
    for k in range(10):
        a = k * math.pi / 5; x, y = math.cos(a) * 62, math.sin(a) * 62
        c.move_to(x * 0.8, y * 0.8); c.line_to(x * 1.2, y * 1.2); stroke(c, DGREEN, 6)
        c.arc(x * 1.25, y * 1.25, 9, 0, 2 * math.pi); fillstroke(c, gcol, DGREEN, 4)
    c.arc(0, 0, 58, 0, 2 * math.pi); fillstroke(c, gcol, DGREEN, 6)
    for ex in (-18, 18):
        c.arc(ex, -8, 9, 0, 2 * math.pi); fillstroke(c, WHITE, INK, 3); c.arc(ex, -6, 4, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()
    c.move_to(-28, -24); c.line_to(-8, -16); c.move_to(28, -24); c.line_to(8, -16); stroke(c, INK, 5)
    c.move_to(-16, 24); c.curve_to(-6, 14, 6, 14, 16, 24); stroke(c, INK, 5)
    c.restore()


@prop("bacteria", (-80, -40, 80, 40), "center", "friendly rod bacteria (gut, good bacteria). args.color")
def bacteria(c, st):
    w = math.sin(st.t * 5) * 6
    rrect(c, -75, -32, 150, 64, 32); fillstroke(c, col(st.args.get("color"), (0.60, 0.50, 0.90)), (0.30, 0.20, 0.55), 5)
    for k in range(3):
        c.move_to(75, -10 + k * 10); c.curve_to(90, -16 + k * 10 + w, 100, -4 + k * 10 - w, 112, -10 + k * 10); stroke(c, (0.30, 0.20, 0.55), 3)
    for ex in (-25, 5):
        c.arc(ex, -6, 5, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()
    c.move_to(-20, 12); c.curve_to(-12, 20, -2, 20, 6, 12); stroke(c, INK, 4)


@prop("egg_cell", (-95, -95, 95, 95), "center", "the egg cell: big round cell with a glowing edge (fertility topics)")
def egg_cell(c, st):
    c.arc(0, 0, 92, 0, 2 * math.pi); c.set_source_rgb(0.99, 0.88, 0.70); c.fill()
    c.arc(0, 0, 80, 0, 2 * math.pi); fillstroke(c, (1.0, 0.94, 0.82), (0.80, 0.55, 0.30), 6)
    c.arc(-14, -10, 26, 0, 2 * math.pi); c.set_source_rgb(0.95, 0.70, 0.45); c.fill()


@prop("sperm", (-90, -26, 90, 26), "center", "cartoon sperm cell swimming right (tadpole style). args.count 1-5")
def sperm(c, st):
    n = int(st.args.get("count", 1))
    for i in range(n):
        dy = (i - (n - 1) / 2) * 60; dx = ((i * 37) % 50) - 25
        c.save(); c.translate(dx, dy)
        c.move_to(-20, 0)
        for k in range(6):
            x = -20 - (k + 1) * 12; y = math.sin(st.t * 12 + k * 0.9) * 8
            c.line_to(x, y)
        stroke(c, INK, 4)
        ellipse(c, 0, 0, 24, 17); fillstroke(c, WHITE, INK, 4)
        c.arc(8, -4, 3, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()
        c.restore()


# ------------------------------------------------------------------ medical and science objects
@prop("thermometer", (-55, -340, 70, 190), "center",
      "thermometer. args: level 0-1, color, label, value; state 'hot' rises to args.level_hot (red)")
def thermometer(c, st):
    a = st.args; level = a.get("level", 0.6) * ease_out(st.age / 0.8)
    color = col(a.get("color"), BLUE)
    if st.state == "hot":
        k = ease_out(st.since / 0.8); level = a.get("level", 0.6) + (a.get("level_hot", 0.85) - a.get("level", 0.6)) * k
        if st.since > 0.4: color = RED
    rrect(c, -28, -330, 56, 330, 28); fillstroke(c, WHITE, INK, 6)
    c.arc(0, 20, 48, 0, 2 * math.pi); fillstroke(c, color, INK, 6)
    h = 300 * level; rrect(c, -14, -h, 28, h + 20, 14); c.set_source_rgb(*color); c.fill()
    for i in range(6):
        c.move_to(28, -40 - i * 48); c.line_to(44, -40 - i * 48); stroke(c, INK, 4)
    if a.get("label"): text(c, a["label"], 0, 120, 40)
    if a.get("value"): text(c, a["value"], 0, 175, 50, color)


@prop("ring", (-207, -207, 207, 207), "center",
      "percentage ring that counts up. args: value (0-100), suffix ('%'), line1, line2 (small grey text), color")
def ring(c, st):
    a = st.args; r = 190; k = ease_out((st.age - 0.3) / 1.6)
    c.arc(0, 0, r, 0, 2 * math.pi); c.set_source_rgb(1, 1, 1); c.fill_preserve(); stroke(c, (0.85, 0.83, 0.78), 34)
    p = a.get("value", 50) / 100 * k
    if p > 0.001:
        c.arc(0, 0, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * p); stroke(c, col(a.get("color", "green")), 34)
    v = a.get("value", 50) * k
    s = (f"{v:.1f}" if a.get("decimals") else f"{int(round(v))}") + a.get("suffix", "%")
    text(c, s, 0, 40, 128 if len(s) <= 4 else 100)
    if a.get("line1"): text(c, a["line1"], 0, 98, 30, (0.4, 0.4, 0.4))
    if a.get("line2"): text(c, a["line2"], 0, 138, 30, (0.4, 0.4, 0.4))


@prop("big_number", (-260, -110, 260, 40), "center", "a big number that counts up. args: value, prefix, suffix, decimals, color")
def big_number(c, st):
    a = st.args; k = ease_out(st.age / 1.2); v = a.get("value", 0) * k
    d = a.get("decimals", 0)
    s = a.get("prefix", "") + (f"{v:,.{d}f}" if d else f"{int(round(v)):,}") + a.get("suffix", "")
    text(c, s, 0, 0, 150 if len(s) <= 6 else 110, col(a.get("color"), INK), outline=16)


@prop("condom", (-100, -100, 100, 100), "center", "closed condom wrapper (a teal foil square with a ring). Never opened")
def condom(c, st):
    c.save(); c.rotate(-0.12)
    c.move_to(-90, -90)
    for i in range(12): c.line_to(-90 + i * 15 + 7.5, -98 if i % 2 == 0 else -90)
    c.line_to(90, -90)
    for i in range(12): c.line_to(98 if i % 2 == 0 else 90, -90 + i * 15 + 7.5)
    c.line_to(90, 90)
    for i in range(12): c.line_to(90 - i * 15 - 7.5, 98 if i % 2 == 0 else 90)
    c.line_to(-90, 90)
    for i in range(12): c.line_to(-98 if i % 2 == 0 else -90, 90 - i * 15 - 7.5)
    c.close_path(); fillstroke(c, TEAL, DTEAL, 6)
    c.arc(0, 0, 50, 0, 2 * math.pi); stroke(c, DTEAL, 8); c.arc(0, 0, 36, 0, 2 * math.pi); stroke(c, (0.55, 0.85, 0.88), 5)
    c.restore()


@prop("shield", (-90, -105, 90, 105), "center", "blue shield with a white tick (protection)")
def shield(c, st):
    c.move_to(0, -100); c.curve_to(40, -80, 70, -78, 85, -78); c.curve_to(85, 10, 60, 70, 0, 100)
    c.curve_to(-60, 70, -85, 10, -85, -78); c.curve_to(-70, -78, -40, -80, 0, -100); c.close_path()
    fillstroke(c, (0.25, 0.47, 0.85), NAVY, 7)
    c.move_to(-36, 0); c.line_to(-8, 28); c.line_to(40, -28); stroke(c, WHITE, 16)


@prop("warning", (-105, -100, 105, 85), "center", "yellow warning triangle with !")
def warning(c, st):
    c.move_to(0, -95); c.line_to(100, 80); c.line_to(-100, 80); c.close_path(); fillstroke(c, (0.98, 0.78, 0.18), INK, 9)
    text(c, "!", 0, 62, 140)


@prop("check", (-90, -90, 90, 90), "center", "green circle with a white tick (true, healthy, yes)")
def check(c, st):
    c.arc(0, 0, 85, 0, 2 * math.pi); fillstroke(c, (0.20, 0.70, 0.40), (0.05, 0.35, 0.18), 7)
    c.move_to(-40, 0); c.line_to(-10, 32); c.line_to(45, -32); stroke(c, WHITE, 18)


@prop("bigx", (-150, -150, 150, 150), "center", "big red X slammed over something (false, does not work). args.size")
def bigx(c, st):
    s = st.args.get("size", 150)
    c.move_to(-s, -s); c.line_to(s, s); c.move_to(s, -s); c.line_to(-s, s); stroke(c, RED, 30)


@prop("qmark", (-70, -110, 70, 70), "center", "big red question mark")
def qmark(c, st):
    c.save(); c.rotate(math.sin(st.t * 3) * 0.08); text(c, "?", 0, 60, 220, RED); c.restore()


@prop("arrow_down", (-65, -90, 65, 90), "center", "thick down arrow (drop, lower). args.color")
def arrow_down(c, st):
    c.move_to(-30, -90); c.line_to(30, -90); c.line_to(30, 10); c.line_to(65, 10); c.line_to(0, 90); c.line_to(-65, 10); c.line_to(-30, 10); c.close_path()
    fillstroke(c, col(st.args.get("color")), INK, 6)


@prop("arrow_up", (-65, -90, 65, 90), "center", "thick up arrow (rise, more). args.color")
def arrow_up(c, st):
    c.move_to(-30, 90); c.line_to(30, 90); c.line_to(30, -10); c.line_to(65, -10); c.line_to(0, -90); c.line_to(-65, -10); c.line_to(-30, -10); c.close_path()
    fillstroke(c, col(st.args.get("color"), (0.15, 0.62, 0.45)), INK, 6)


@prop("clock", (-90, -90, 90, 90), "center", "wall clock with spinning hands (time, hours). args.fast true = hands race")
def clock(c, st):
    c.arc(0, 0, 85, 0, 2 * math.pi); fillstroke(c, WHITE, INK, 8)
    for k in range(12):
        a = k * math.pi / 6; c.move_to(math.cos(a) * 66, math.sin(a) * 66); c.line_to(math.cos(a) * 74, math.sin(a) * 74); stroke(c, INK, 4)
    sp = 6 if st.args.get("fast") else 0.6
    for L, w, a in ((42, 8, st.t * sp * 0.08), (62, 5, st.t * sp)):
        c.move_to(0, 0); c.line_to(math.sin(a) * L, -math.cos(a) * L); stroke(c, INK, w)
    c.arc(0, 0, 7, 0, 2 * math.pi); c.set_source_rgb(*RED); c.fill()


@prop("calendar", (-100, -110, 100, 100), "center", "calendar page. args: top (month, short), big (day or number)")
def calendar(c, st):
    rrect(c, -95, -100, 190, 195, 16); fillstroke(c, WHITE, INK, 6)
    c.save(); rrect(c, -95, -100, 190, 55, 16); c.clip(); c.rectangle(-95, -100, 190, 55); c.set_source_rgb(*RED); c.fill(); c.restore()
    rrect(c, -95, -100, 190, 195, 16); stroke(c, INK, 6)
    for x in (-50, 50): c.move_to(x, -112); c.line_to(x, -88); stroke(c, INK, 8)
    text(c, st.args.get("top", "DAY"), 0, -60, 34, WHITE)
    text(c, str(st.args.get("big", "1")), 0, 60, 92)


@prop("phone", (-60, -110, 60, 110), "center", "smartphone with a glowing screen. args.text (short)")
def phone(c, st):
    rrect(c, -58, -108, 116, 216, 18); fillstroke(c, (0.15, 0.15, 0.18), INK, 5)
    rrect(c, -48, -92, 96, 176, 8); c.set_source_rgb(0.55, 0.80, 0.98); c.fill()
    if st.args.get("text"): text(c, st.args["text"], 0, 6, 26, NAVY)
    c.arc(0, 96, 6, 0, 2 * math.pi); c.set_source_rgb(0.5, 0.5, 0.5); c.fill()


@prop("book", (-110, -80, 110, 80), "center", "closed book. args.title (short)")
def book(c, st):
    rrect(c, -105, -75, 210, 150, 8); fillstroke(c, col(st.args.get("color"), NAVY), INK, 6)
    c.rectangle(-105, 60, 210, 12); c.set_source_rgb(0.95, 0.92, 0.85); c.fill()
    c.move_to(-80, -75); c.line_to(-80, 75); stroke(c, INK, 4)
    if st.args.get("title"): text(c, st.args["title"], 10, 12, 32, WHITE)


@prop("papyrus", (-320, -206, 320, 206), "center", "ancient Egyptian papyrus scroll that unrolls (history topics)")
def papyrus(c, st):
    k = ease_out(st.age / 0.7); w = 600 * k; h = 380
    if w < 4: return
    c.rectangle(-w / 2, -h / 2, w, h); fillstroke(c, (0.93, 0.84, 0.64), (0.55, 0.42, 0.22), 5)
    for side in (-1, 1):
        x0 = side * w / 2; c.rectangle(x0 - 18, -h / 2 - 16, 36, h + 32); fillstroke(c, (0.84, 0.70, 0.45), (0.55, 0.42, 0.22), 5)
    if k < 0.95: return
    c.save(); c.rectangle(-w / 2 + 20, -h / 2, w - 40, h); c.clip()
    pc = (0.42, 0.28, 0.12); ex, ey = -200, -80
    c.move_to(ex - 60, ey); c.curve_to(ex - 20, ey - 40, ex + 30, ey - 40, ex + 60, ey); c.curve_to(ex + 20, ey + 30, ex - 30, ey + 30, ex - 60, ey); stroke(c, pc, 7)
    c.arc(ex, ey, 14, 0, 2 * math.pi); c.set_source_rgb(*pc); c.fill()
    c.move_to(ex - 10, ey + 22); c.curve_to(ex - 14, ey + 60, ex + 20, ey + 70, ex + 26, ey + 50); stroke(c, pc, 7)
    ellipse(c, -40, -90, 22, 30); stroke(c, pc, 8)
    c.move_to(-78, -44); c.line_to(-2, -44); c.move_to(-40, -60); c.line_to(-40, 40); stroke(c, pc, 8)
    for i in range(3):
        c.move_to(60, 70 + i * 34)
        for j in range(5): c.rel_curve_to(14, -14, 28, -14, 42, 0)
        stroke(c, pc, 5)
        c.move_to(-260, 70 + i * 34); c.line_to(10 - i * 40, 70 + i * 34); stroke(c, pc, 6)
    c.restore()


# ------------------------------------------------------------------ everyday objects and places
@prop("ac_unit", (-155, -65, 155, 120), "center", "wall air conditioner blowing cold air")
def ac_unit(c, st):
    rrect(c, -150, -60, 300, 120, 22); fillstroke(c, WHITE, INK, 7)
    for i in range(5): c.move_to(-110, i * 9); c.line_to(110, i * 9); stroke(c, (0.6, 0.6, 0.6), 4)
    c.arc(118, -32, 8, 0, 2 * math.pi); c.set_source_rgb(0.2, 0.8, 0.4); c.fill()
    for i in range(4):
        ph = (st.t * 1.2 + i * 0.25) % 1
        c.move_to(-90 + i * 60, 70 + ph * 40); c.rel_curve_to(12, 14, -12, 26, 0, 40)
        c.set_source_rgba(*BLUE, 1 - ph); c.set_line_width(7); c.stroke()


@prop("hot_tub", (-150, -200, 150, 0), "ground", "steaming hot tub with bubbles")
def hot_tub(c, st):
    rrect(c, -150, -120, 300, 120, 18); fillstroke(c, (0.55, 0.40, 0.28), INK, 6)
    c.rectangle(-140, -122, 280, 18); c.set_source_rgb(0.45, 0.75, 0.95); c.fill()
    for i in range(6):
        bx = -110 + i * 44 + math.sin(st.t * 3 + i) * 6; by = -134 - (st.t * 40 + i * 13) % 30
        c.arc(bx, by, 7, 0, 2 * math.pi); c.set_source_rgb(0.45, 0.75, 0.95); c.fill()
    wavy_up(c, 0, -160, st.t, (0.6, 0.6, 0.6), gap=60, rise=70, spd=0.7)


@prop("bed", (-170, -150, 170, 0), "ground", "bed with pillow and blanket (sleep). state 'zzz' = floating Zs")
def bed(c, st):
    c.rectangle(-170, -110, 22, 110); fillstroke(c, BROWN, INK, 5)
    c.rectangle(148, -70, 22, 70); fillstroke(c, BROWN, INK, 5)
    rrect(c, -150, -80, 300, 50, 10); fillstroke(c, WHITE, INK, 5)
    rrect(c, -140, -105, 80, 34, 14); fillstroke(c, WHITE, INK, 5)
    rrect(c, -60, -95, 210, 55, 14); fillstroke(c, (0.45, 0.60, 0.90), NAVY, 5)
    if st.state == "zzz":
        for i in range(3):
            ph = (st.t * 0.6 + i / 3) % 1
            text(c, "Z", -60 + ph * 80 + i * 10, -130 - ph * 120, 40 + i * 6, (0.4, 0.4, 0.5))


@prop("sign", (-170, -330, 170, 0), "ground", "wooden sign on a post. args.lines (1 to 3 short lines)")
def sign(c, st):
    c.rectangle(-10, -180, 20, 180); fillstroke(c, BROWN, DBROWN, 4)
    rrect(c, -165, -325, 330, 160, 14); fillstroke(c, (0.93, 0.80, 0.55), DBROWN, 6)
    lines = st.args.get("lines", ["SIGN"]); n = len(lines)
    for i, ln in enumerate(lines):
        text(c, ln, 0, -245 + (i - (n - 1) / 2) * 48 + 16, 40 if n > 1 else 52, DBROWN)


@prop("bubble", (-200, -95, 200, 95), "center",
      "speech bubble. args.lines (1 to 2 short lines), args.tail 'left'|'right' (side of the speaker), color")
def bubble(c, st):
    tail = st.args.get("tail", "left"); tx = -110 if tail == "left" else 110; d = -1 if tail == "left" else 1
    rrect(c, -195, -85, 390, 150, 36)
    c.set_source_rgb(1, 1, 1); c.fill_preserve(); stroke(c, INK, 6)
    c.move_to(tx - 20 * d, 63); c.line_to(tx + 40 * d, 92); c.line_to(tx + 20 * d, 62); c.close_path(); c.set_source_rgb(1, 1, 1); c.fill()
    c.move_to(tx - 20 * d, 64); c.line_to(tx + 40 * d, 92); c.line_to(tx + 22 * d, 64); stroke(c, INK, 6)
    lines = st.args.get("lines", ["..."]); n = len(lines)
    for i, ln in enumerate(lines):
        text(c, ln, 0, -10 + (i - (n - 1) / 2) * 50 + 14, 40, col(st.args.get("color"), INK))


@prop("elevator", (-140, -700, 140, 0), "ground",
      "elevator shaft with a cabin holding the twins. state: mid|up|down (up = cold twins, down = hot twins)")
def elevator(c, st):
    top, bot = -700, 0
    c.rectangle(-140, top, 280, bot - top); fillstroke(c, (0.92, 0.90, 0.86), INK, 7)
    c.move_to(0, top); c.line_to(0, top + 30); stroke(c, INK, 4)
    ys = {"mid": (top + bot) / 2 - 90, "up": top + 40, "down": bot - 220}
    a, b = ys.get(st.prev or "mid", ys["mid"]), ys.get(st.state or "mid", ys["mid"])
    pos = a + (b - a) * ease_inout((st.since - 0.3) / 0.8)
    c.move_to(0, top + 30); c.line_to(0, pos); stroke(c, INK, 4)
    c.rectangle(-110, pos, 220, 180); fillstroke(c, WHITE, INK, 6)
    mood = {"up": "cold", "down": "hot"}.get(st.state, "happy") if st.since > 0.3 else {"up": "cold", "down": "hot"}.get(st.prev, "happy")
    c.save(); c.translate(0, pos + 100); c.scale(1.35, 1.35); twins(c, SimpleNamespace(t=st.t, state=mood)); c.restore()


def draw(c, name, st):
    PROPS[name].draw(c, st)
