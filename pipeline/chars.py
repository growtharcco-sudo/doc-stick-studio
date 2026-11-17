"""Doc Stick characters: Doc Stick (narrator), the boy and the girl. Do not change the look unless James asks.

All characters are drawn with their feet at (x, y), facing right when face=1 and left when face=-1.
Poses: deadpan, point, shocked, wave, think, shrug (all characters); sit_laptop (boy/girl only).
"""
import math
import cairo
from base import INK, RED, stroke, fillstroke

BLUE = (0.20, 0.45, 0.85)
PINK = (0.93, 0.36, 0.58)


def _limbs(c, pose, t, lw, kind):
    if pose == "point":
        c.move_to(0, -157); c.line_to(-24, -128); c.line_to(-6, -110); stroke(c, INK, lw)
        if kind == "doc":
            c.move_to(58, -146); c.line_to(104, -200); stroke(c, (0.54, 0.35, 0.17), 4.5)
            c.move_to(0, -157); c.line_to(58, -146); stroke(c, INK, lw)
        else:
            c.move_to(0, -157); c.line_to(62, -170); stroke(c, INK, lw)
    elif pose == "shocked":
        c.move_to(0, -157); c.line_to(-40, -204); c.move_to(0, -157); c.line_to(40, -204); stroke(c, INK, lw)
    elif pose == "wave":
        c.move_to(0, -157); c.line_to(-26, -100); stroke(c, INK, lw)
        a = math.sin(t * 12) * 0.45; ex, ey = 46, -166
        c.move_to(0, -157); c.line_to(ex, ey); c.line_to(ex + 14 + 46 * math.sin(a), ey - 46 * math.cos(a)); stroke(c, INK, lw)
    elif pose == "think":
        c.move_to(0, -157); c.line_to(-26, -100); stroke(c, INK, lw)
        c.move_to(0, -157); c.line_to(34, -140); c.line_to(16, -192); stroke(c, INK, lw)
    elif pose == "shrug":
        c.move_to(0, -157); c.line_to(-38, -150); c.line_to(-52, -182); c.move_to(0, -157); c.line_to(38, -150); c.line_to(52, -182)
        stroke(c, INK, lw)
    else:
        c.move_to(0, -157); c.line_to(-26, -100); c.move_to(0, -157); c.line_to(26, -100); stroke(c, INK, lw)


def _face(c, pose, blink, mouth, kind):
    if pose == "shocked":
        for ex in (-11, 11):
            c.arc(ex, -213, 8, 0, 2 * math.pi); fillstroke(c, (1, 1, 1), INK, 2.5)
            c.arc(ex, -212, 3, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()
        c.save(); c.translate(0, -195); c.scale(6, 8); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore(); c.set_source_rgb(*INK); c.fill()
        c.move_to(34, -228); c.curve_to(40, -218, 40, -214, 34, -212); c.curve_to(28, -214, 28, -218, 34, -228)
        c.set_source_rgb(0.5, 0.77, 0.91); c.fill()
        return
    for ex in (-10, 10):
        if blink: c.move_to(ex - 5, -210); c.line_to(ex + 5, -210); stroke(c, INK, 3)
        else: c.arc(ex, -209, 3.6, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()
    if kind == "doc":
        if pose == "point":
            c.move_to(-17, -217); c.line_to(-4, -215); c.move_to(5, -222); c.line_to(18, -226); stroke(c, INK, 3)
        else:
            c.move_to(-16, -215); c.line_to(-4, -215); c.move_to(4, -215); c.line_to(16, -215); stroke(c, INK, 3)
    elif pose == "think":
        c.move_to(4, -222); c.line_to(16, -226); stroke(c, INK, 3)
    if mouth:
        ry = 3.2 if mouth == 1 else 6.5; rx = 9 if mouth == 1 else 8.5
        c.save(); c.translate(0, -198); c.scale(rx, ry); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        c.set_source_rgb(0.30, 0.06, 0.06); c.fill_preserve(); stroke(c, INK, 2.5)
    elif kind == "doc" and pose == "point":
        c.move_to(-12, -198); c.curve_to(-4, -195, 4, -195, 12, -200); stroke(c, INK, 3)
    elif kind != "doc" and pose in ("wave", "point"):
        c.move_to(-10, -200); c.curve_to(-4, -194, 4, -194, 10, -200); stroke(c, INK, 3)
    elif pose == "shrug":
        c.move_to(-11, -197); c.line_to(11, -201); stroke(c, INK, 3)
    else:
        c.move_to(-13, -198); c.line_to(13, -198); stroke(c, INK, 3)


def _sit_laptop(c, t, lw):
    c.rectangle(-55, -84, 70, 12); fillstroke(c, (0.75, 0.55, 0.35), INK, 4)
    c.move_to(-48, -72); c.line_to(-48, 0); c.move_to(8, -72); c.line_to(8, 0); stroke(c, INK, 5)
    c.move_to(0, -88); c.line_to(62, -90); c.line_to(66, 0); stroke(c, INK, lw)
    c.move_to(0, -88); c.line_to(0, -182); stroke(c, INK, lw)
    c.move_to(0, -157); c.line_to(48, -104); stroke(c, INK, lw)
    c.move_to(18, -100); c.line_to(86, -100); stroke(c, (0.35, 0.35, 0.40), 9)
    c.move_to(86, -100); c.line_to(100, -160); stroke(c, (0.35, 0.35, 0.40), 9)
    for i in range(3):
        ph = (t + i * 0.33) % 1
        c.move_to(30 + i * 22, -112 - ph * 50); c.rel_curve_to(8, -8, -8, -16, 0, -24)
        c.set_source_rgba(0.90, 0.30, 0.20, 1 - ph); c.set_line_width(4); c.stroke()


def character(c, kind, x, y, s, pose="deadpan", t=0.0, face=1, blink=False, mouth=0, shake=0.0):
    """kind: doc | boy | girl. mouth: 0 closed, 1 half, 2 open (lip sync, doc only)."""
    c.save()
    c.translate(x + math.sin(t * 60) * shake * 6, y); c.scale(s * face, s)
    lw = 5.5
    if pose == "sit_laptop":
        _sit_laptop(c, t, lw); c.translate(0, 0)
    else:
        bob = math.sin(t * 2.2 + (0 if kind == "doc" else 1.7)) * 1.6
        if kind == "girl":
            c.move_to(0, -82 + bob); c.line_to(-22, 0); c.move_to(0, -82 + bob); c.line_to(22, 0); stroke(c, INK, lw)
            c.translate(0, bob)
            c.move_to(0, -150); c.line_to(-30, -78); c.line_to(30, -78); c.close_path(); fillstroke(c, PINK, INK, 4)
            c.move_to(0, -182); c.line_to(0, -148); stroke(c, INK, lw)
        else:
            c.move_to(0, -82 + bob); c.line_to(-22, 0); c.move_to(0, -82 + bob); c.line_to(22, 0); stroke(c, INK, lw)
            c.translate(0, bob)
            c.move_to(0, -182); c.line_to(0, -82); stroke(c, INK, lw)
        _limbs(c, pose, t, lw, kind)
    # head
    if kind == "girl":
        sw = math.sin(t * 3) * 4
        c.move_to(-22, -226); c.curve_to(-44, -222, -50 + sw, -196, -44 + sw, -176); stroke(c, INK, 7)
        c.arc(-26, -226, 7, 0, 2 * math.pi); fillstroke(c, PINK, INK, 2.5)
    c.arc(0, -210, 28, 0, 2 * math.pi); fillstroke(c, (1, 1, 1), INK, lw)
    if kind == "doc":
        c.move_to(-26, -222); c.curve_to(-14, -242, 14, -242, 26, -222); stroke(c, INK, lw)
        c.arc(0, -236, 10, 0, 2 * math.pi); fillstroke(c, (0.79, 0.83, 0.85), INK, 3)
        c.arc(0, -236, 3, 0, 2 * math.pi); c.set_source_rgb(1, 1, 1); c.fill()
    elif kind == "boy":
        c.arc(0, -214, 30, math.pi, 2 * math.pi); c.close_path(); fillstroke(c, BLUE, INK, 3.5)
        c.move_to(20, -214); c.line_to(52, -212); stroke(c, INK, 8); c.move_to(20, -214); c.line_to(50, -212); stroke(c, BLUE, 4)
    else:
        c.move_to(-26, -220); c.curve_to(-20, -240, 20, -244, 27, -214); stroke(c, INK, 6)
    _face(c, pose, blink, mouth if kind == "doc" else 0, kind)
    if kind == "doc" and pose != "sit_laptop":
        c.move_to(0, -172); c.line_to(-15, -181); c.line_to(-15, -163); c.close_path()
        c.move_to(0, -172); c.line_to(15, -181); c.line_to(15, -163); c.close_path()
        fillstroke(c, RED, INK, 1.8)
        c.arc(0, -172, 4, 0, 2 * math.pi); c.set_source_rgb(0.66, 0.12, 0.09); c.fill()
    c.restore()
