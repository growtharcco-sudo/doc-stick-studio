"""Doc Stick renderer: spec + voice timing -> frames, captions, lip sync, sound effects, cover.

render(spec, times, total, wav, out_mp4, stills=None)   full video (or PNG stills at the given seconds)
cover(spec, times, total, out_png)                       the cover / thumbnail
"""
import math, os, subprocess, re
from types import SimpleNamespace
import numpy as np
import cairo
from base import (W, H, FPS, GROUND, CAP_Y, BG, FLOOR, INK, RED, ensure_font, clamp, ease_out, ease_in, ease_back,
                  stroke, fillstroke, text, font, scaled, rrect)
import props as P
from chars import character
from kit import caption_chunks

IN_DUR = {"pop": 0.45, "slide_right": 0.7, "slide_left": 0.7, "drop": 0.6, "fade": 0.4, "none": 0.0}
OUT_DUR = {"slide_right": 1.3, "slide_left": 1.3, "pop": 0.3, "none": 0.0}


class Clock:
    def __init__(self, spec, times, total):
        self.spec, self.times = spec, times
        self.end = total + 0.6
        sc = spec["scenes"]
        self.scene_t = [(0.0 if i == 0 else times[s["first"]][0] - 0.05,
                         (times[sc[i + 1]["first"]][0] - 0.05) if i + 1 < len(sc) else self.end) for i, s in enumerate(sc)]

    def at(self, ref):
        """Beat 0 counts from frame 0 (the hook is on screen before the first word)."""
        b, d = ref
        if b == 0: return d
        return (self.times[b][0] if b < len(self.times) else self.end) + d

    def scene(self, t):
        for i, (a, b) in enumerate(self.scene_t):
            if t < b: return i
        return len(self.scene_t) - 1


def _state(clock, states, t, default=None):
    cur, prev, since = default, default, 99.0
    for st in states:
        tt = clock.at(st[:2])
        if t >= tt: prev, cur, since = cur, st[2], t - tt
    return cur, prev, since


class Lips:
    def __init__(self, wav):
        import soundfile as sf
        a, sr = sf.read(wav); hop = sr // FPS
        r = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop + hop // 2] ** 2)) for i in range(len(a) // hop)])
        self.r = np.convolve(r, [0.25, 0.5, 0.25], "same") / max(r.max(), 1e-6)

    def level(self, t):
        i = int(t * FPS)
        if i >= len(self.r): return 0
        v = self.r[i]; return 0 if v < 0.07 else (1 if v < 0.28 else 2)


# ------------------------------------------------------------------ particles and stamps
def particles(c, kind, area, t, age):
    x0, x1 = (440, 1040) if area == "right" else (60, 1040)
    n = 7
    for i in range(n):
        fy = (t * 130 + i * 97) % 650; x = x0 + (i * 149) % (x1 - x0) + 30 * math.sin(t + i); y = 700 + fy; a = (1 - fy / 650) * clamp(age / 0.3)
        if kind == "snow":
            c.save(); c.translate(x, y)
            for k in range(3):
                c.save(); c.rotate(k * math.pi / 3); c.move_to(-16, 0); c.line_to(16, 0); c.set_source_rgba(0.25, 0.55, 0.90, a); c.set_line_width(5); c.stroke(); c.restore()
            c.restore()
        elif kind == "hearts":
            y = 1450 - fy; c.save(); c.translate(x, y); c.scale(0.25, 0.25)
            c.move_to(0, 70); c.curve_to(-90, 10, -80, -70, -35, -70); c.curve_to(-15, -70, 0, -55, 0, -40)
            c.curve_to(0, -55, 15, -70, 35, -70); c.curve_to(80, -70, 90, 10, 0, 70); c.set_source_rgba(*RED, 1 - fy / 650); c.fill(); c.restore()
        elif kind == "sweat":
            c.move_to(x, y); c.curve_to(x + 8, y + 12, x + 8, y + 18, x, y + 22); c.curve_to(x - 8, y + 18, x - 8, y + 12, x, y)
            c.set_source_rgba(0.5, 0.77, 0.91, a); c.fill()
        elif kind == "sparkle":
            s = 10 + 8 * math.sin(t * 6 + i); y = 760 + (i * 113) % 600
            c.move_to(x, y - s); c.line_to(x + s * 0.3, y - s * 0.3); c.line_to(x + s, y); c.line_to(x + s * 0.3, y + s * 0.3)
            c.line_to(x, y + s); c.line_to(x - s * 0.3, y + s * 0.3); c.line_to(x - s, y); c.line_to(x - s * 0.3, y - s * 0.3); c.close_path()
            c.set_source_rgba(0.98, 0.75, 0.15, 0.5 + 0.5 * math.sin(t * 4 + i)); c.fill()


def stamp(c, e, k):
    if k <= 0: return
    color = RED if e["color"] == "red" else INK
    sc = 1 + 0.8 * (1 - ease_out(k)); a = clamp(k * 3); size = e["size"]
    c.save(); c.translate(e["x"], e["y"]); c.rotate(e["rot"]); c.scale(sc, sc)
    font(c, size); ex = c.text_extents(e["text"]); subs = e.get("sub")
    w = ex.width + 60; h = size + 44 + (size * 0.5 if subs else 0)
    c.rectangle(-w / 2, -h / 2, w, h); c.set_source_rgba(*color, a); c.set_line_width(10); c.stroke()
    c.move_to(-ex.width / 2 - ex.x_bearing, (size * 0.36) - (size * 0.25 if subs else 0)); c.set_source_rgba(*color, a); c.show_text(e["text"])
    if subs:
        font(c, size * 0.45); e2 = c.text_extents(subs); c.move_to(-e2.width / 2 - e2.x_bearing, size * 0.62); c.show_text(subs)
    c.restore()


# ------------------------------------------------------------------ captions
def build_captions(spec, clock):
    chunks = []
    for i, p in enumerate(spec["phrases"]):
        parts = caption_chunks(p["cap"]); a, b = clock.times[i]
        tot = sum(max(3, len(x)) for x in parts); acc = 0
        for x in parts:
            chunks.append([x, a + (b - a) * acc / tot, None]); acc += max(3, len(x))
    for i, ch in enumerate(chunks): ch[2] = chunks[i + 1][1] if i + 1 < len(chunks) else clock.end
    return chunks


def caption(c, chunks, t):
    for s, a, b in chunks:
        if not (a <= t < b): continue
        k = ease_back((t - a) / 0.22)
        c.save(); c.translate(W / 2, CAP_Y); sc = 0.82 + 0.18 * k; c.scale(sc, sc); font(c, 96)
        words = s.upper().split(); lines, cur = [], []
        for w in words:
            if cur and c.text_extents(" ".join(cur + [w]).replace("*", "")).x_advance > 900: lines.append(cur); cur = []
            cur.append(w)
        lines.append(cur); sp = c.text_extents(" ").x_advance
        for li, ln in enumerate(lines):
            y = (li - (len(lines) - 1) / 2) * 112 + 34
            tw = sum(c.text_extents(w.replace("*", "")).x_advance for w in ln) + sp * (len(ln) - 1); x = -tw / 2
            for w in ln:
                hl = w.startswith("*") or w.endswith("*") or w.rstrip(".,!?:;").endswith("*"); w2 = w.replace("*", "")
                c.move_to(x, y); c.text_path(w2)
                c.set_source_rgb(1, 1, 1); c.set_line_width(18); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
                c.set_source_rgb(*(RED if hl else INK)); c.fill(); x += c.text_extents(w2).x_advance + sp
        c.restore(); return


# ------------------------------------------------------------------ one frame
def follow_outro(c, clock, sc, t):
    t0 = clock.at([sc["first"], 0.05]); tap = clock.at([sc["first"], 0.35]) + 0.0
    bs = ease_back((t - t0) / 0.45) if t >= t0 else 0
    if bs > 0.002:
        sq = 0.92 if tap <= t < tap + 0.12 else 1.0
        c.save(); c.translate(540, 790); c.scale(bs * sq, bs * sq); w, h = 440, 140
        c.new_sub_path(); c.arc(-w / 2 + h / 2, 0, h / 2, math.pi / 2, 1.5 * math.pi); c.arc(w / 2 - h / 2, 0, h / 2, 1.5 * math.pi, math.pi / 2); c.close_path()
        fillstroke(c, RED, INK, 7); text(c, "FOLLOW", 0, 26, 74, (1, 1, 1)); c.restore()
    k = ease_out((t - t0) / 0.35)
    if t > t0:
        c.save(); c.translate(900 - 230 * k, 1080 - 230 * k); c.rotate(-0.3)
        c.move_to(0, 0); c.line_to(0, 90); c.line_to(22, 70); c.line_to(38, 104); c.line_to(52, 97); c.line_to(36, 63); c.line_to(64, 62); c.close_path()
        fillstroke(c, (1, 1, 1), INK, 6); c.restore()
        if tap <= t < tap + 0.4:
            r = 30 + 160 * (t - tap); c.arc(670, 850, r, 0, 2 * math.pi); c.set_source_rgba(*RED, 1 - (t - tap) / 0.4); c.set_line_width(6); c.stroke()


def draw_prop(c, clock, e, t, s_end):
    t0 = clock.at(e["at"])
    if t < t0: return
    t_out = clock.at(e["until"]) if e.get("until") else None
    if t_out is not None and e["out"] == "none" and t >= t_out: return
    if t_out is not None and t >= t_out + OUT_DUR.get(e["out"], 0): return
    x, y, s, alpha, moving = e["x"], e["y"], e["s"], 1.0, False
    age = t - t0; kin = e["in"]; d = IN_DUR.get(kin, 0)
    if kin == "pop": s *= ease_back(age / d)
    elif kin == "slide_right": x += 950 * (1 - ease_out(age / d)); moving = age < d
    elif kin == "slide_left": x -= 950 * (1 - ease_out(age / d)); moving = age < d
    elif kin == "drop": y -= 900 * (1 - ease_out(age / d))
    elif kin == "fade": alpha = clamp(age / d)
    if t_out is not None and t >= t_out:
        k = (t - t_out) / OUT_DUR[e["out"]]
        if e["out"] == "slide_right": x += 950 * ease_in(k); moving = True
        elif e["out"] == "slide_left": x -= 950 * ease_in(k); moving = True
        elif e["out"] == "pop": s *= 1 - ease_out(k)
    state, prev, since = _state(clock, e.get("states", []), t, e.get("args", {}).get("state"))
    st = SimpleNamespace(t=t, age=age, state=state, prev=prev, since=since, moving=moving, args=e.get("args", {}))
    if abs(s) < 0.002: return
    if alpha < 1: c.push_group()
    c.save(); c.translate(x, y); c.scale(-s if e.get("flip") else s, s); P.draw(c, e["name"], st); c.restore()
    if e.get("label") and age > 0.3:
        x0, y0, x1, y1 = P.PROPS[e["name"]].bbox
        text(c, e["label"], x, y + y1 * e["s"] + 52, 40, INK, outline=12)
    if alpha < 1: c.pop_group_to_source(); c.paint_with_alpha(alpha)


def frame(c, spec, clock, chunks, lips, t, captions=True):
    c.set_source_rgb(*BG); c.paint()
    c.set_source_rgb(*FLOOR); c.rectangle(0, GROUND, W, H - GROUND); c.fill()
    c.move_to(0, GROUND); c.line_to(W, GROUND); stroke(c, (0.80, 0.76, 0.68), 4)
    si = clock.scene(t); sc = spec["scenes"][si]; s_end = clock.scene_t[si][1]
    for e in sc["els"]:
        if e["type"] == "particles":
            t0 = clock.at(e["at"]); t1 = clock.at(e["until"]) if e.get("until") else s_end
            if t0 <= t < t1: particles(c, e["kind"], e["area"], t, t - t0)
    for e in sc["els"]:
        if e["type"] == "prop" and e["name"] not in ("bigx", "qmark"): draw_prop(c, clock, e, t, s_end)
    for p in sc["people"]:
        t0 = clock.at(p["at"])
        if t < t0: continue
        pose, _, since = _state(clock, p["poses"], t, p["poses"][0][2])
        x = p["x"]; s = p["s"]
        if p["in"] == "slide": x += 900 * (1 - ease_out((t - t0) / 0.7)) * (1 if p["face"] < 0 else -1)
        elif p["in"] == "pop": s *= ease_back((t - t0) / 0.45)
        if s > 0.01:
            character(c, p["kind"], x, GROUND, s, pose, t, p["face"], (t + 1.3) % 3.7 < 0.11, 0, 0.6 if pose == "shocked" and since < 2.5 else 0)
    if sc.get("doc"):
        d = sc["doc"]; pose, _, since = _state(clock, d["poses"], t, d["poses"][0][2])
        mouth = 0 if pose == "shocked" else lips.level(t)
        character(c, "doc", d["x"], GROUND, d["s"], pose, t, d["face"], t % 3.7 < 0.11, mouth, 1.0 if pose == "shocked" and since < 2.0 else 0)
    for e in sc["els"]:
        if e["type"] == "prop" and e["name"] in ("bigx", "qmark"): draw_prop(c, clock, e, t, s_end)
        elif e["type"] == "stamp":
            t0 = clock.at(e["at"]); t1 = clock.at(e["until"]) if e.get("until") else s_end
            if t0 <= t < t1: stamp(c, e, (t - t0) / 0.25)
    if sc.get("outro"): follow_outro(c, clock, sc, t)
    if captions: caption(c, chunks, t)


# ------------------------------------------------------------------ sound
def sfx_events(spec, clock):
    ev = [(0.0, "whoosh")]
    for sc in spec["scenes"]:
        for e in sc["els"]:
            t0 = clock.at(e["at"])
            if e["type"] == "prop":
                kind = {"pop": "pop", "slide_right": "whoosh", "slide_left": "whoosh", "drop": "thud", "fade": None}.get(e["in"])
                if e["name"] == "bigx": kind = "thud"
                if kind: ev.append((t0 + (0.45 if kind == "thud" and e["in"] == "drop" else 0), kind))
                if e.get("until") and e["out"] in ("slide_right", "slide_left"): ev.append((clock.at(e["until"]), "whoosh"))
                if e["name"] == "elevator":
                    for s_ in e.get("states", []): ev.append((clock.at(s_[:2]) + 0.3, "whoosh")); ev.append((clock.at(s_[:2]) + 1.1, "ding"))
            elif e["type"] == "stamp": ev.append((t0, "thud"))
        for p in sc["people"]:
            if p["in"] == "slide": ev.append((clock.at(p["at"]), "whoosh"))
            elif p["in"] == "pop": ev.append((clock.at(p["at"]), "pop"))
        if sc.get("outro"): ev += [(clock.at([sc["first"], 0.05]), "pop"), (clock.at([sc["first"], 0.35]), "click")]
    return ev


def mix(spec, clock, wav, out_wav):
    import soundfile as sf
    vo, sr = sf.read(wav); n = int(clock.end * sr) + sr; out = np.zeros(n); out[:len(vo)] += vo
    rng = np.random.default_rng(1)
    def snd(kind):
        if kind == "pop":
            m = int(0.09 * sr); t = np.arange(m) / sr; f = 900 * np.exp(-t * 30) + 250
            return 0.35 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 40)
        if kind == "thud":
            m = int(0.25 * sr); t = np.arange(m) / sr
            return 0.45 * (np.sin(2 * np.pi * 70 * t) + 0.4 * rng.standard_normal(m) * np.exp(-t * 60)) * np.exp(-t * 14)
        if kind == "whoosh":
            m = int(0.6 * sr); w = np.convolve(rng.standard_normal(m), np.ones(30) / 30, "same")
            return 0.25 * w * np.sin(np.pi * np.arange(m) / m) ** 2
        if kind == "click":
            m = int(0.04 * sr); t = np.arange(m) / sr; return 0.4 * np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 120)
        if kind == "ding":
            m = int(0.5 * sr); t = np.arange(m) / sr; return 0.25 * (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t)) * np.exp(-t * 7)
    for t0, kind in sfx_events(spec, clock):
        s = snd(kind); i = int(max(0, t0) * sr)
        if i < n: out[i:i + len(s)] += s[:n - i]
    out = out[:int(clock.end * sr)]; out /= max(1, np.abs(out).max() / 0.95)
    sf.write(out_wav, out, sr)


# ------------------------------------------------------------------ outputs
def render(spec, times, total, wav, out, stills=None):
    ensure_font()
    clock = Clock(spec, times, total); chunks = build_captions(spec, clock); lips = Lips(wav)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(surf)
    if stills is not None:
        for t in stills:
            frame(c, spec, clock, chunks, lips, t); surf.write_to_png(f"{out}.still_{t:05.1f}.png")
        return
    tmp = out[:-4] + ".tmp.mp4"; mixed = out[:-4] + ".mix.wav"
    mix(spec, clock, wav, mixed)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", mixed, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    for n in range(int(clock.end * FPS)):
        frame(c, spec, clock, chunks, lips, n / FPS); surf.flush(); p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    if p.wait() != 0: raise SystemExit("ffmpeg failed")
    os.replace(tmp, out); os.remove(mixed)


def cover(spec, times, total, wav, out_png):
    """The hook scene (end of scene 1, no captions) with the cover headline in the caption zone."""
    ensure_font()
    clock = Clock(spec, times, total); lips = Lips(wav)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(surf)
    t = clock.scene_t[0][1] - 0.3
    lips.level = lambda _t: 0
    frame(c, spec, clock, [], lips, t, captions=False)
    cv = spec.get("cover", {}); big = cv.get("big", [])
    rrect(c, 380, 210, 320, 70, 35); fillstroke(c, RED, INK, 5); text(c, "DOC STICK", 540, 262, 40, (1, 1, 1))
    font(c, 110)
    for i, line in enumerate(big[:2]):
        y = 420 + i * 130; words = line.split(); sp = c.text_extents(" ").x_advance
        tw = sum(c.text_extents(w.replace("*", "")).x_advance for w in words) + sp * (len(words) - 1); x = W / 2 - tw / 2
        for w in words:
            hl = "*" in w; w2 = w.replace("*", "")
            c.move_to(x, y); c.text_path(w2); c.set_source_rgb(1, 1, 1); c.set_line_width(20); c.set_line_join(cairo.LINE_JOIN_ROUND)
            c.stroke_preserve(); c.set_source_rgb(*(RED if hl else INK)); c.fill(); x += c.text_extents(w2).x_advance + sp
    surf.write_to_png(out_png)
