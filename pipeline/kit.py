"""Reel kit: brief -> spec. Places everything with named slots and runs the layout check. Never hand-write coordinates.

Usage:  python pipeline/kit.py briefs/<id>.json      (writes specs/<id>.json, exits 1 on LAYOUT PROBLEMS)

Brief:
{
  "id": "003_slug",
  "beats": [                                       # one beat = one spoken phrase
    {"say": "...", "cap": "...", "pause": 0.3,     # cap/pause optional. cap = on-screen caption:
                                                   #   *word* = red highlight, "|" = caption break (else automatic)
     "show": {...scene...}},                       # optional: a new scene starts at this beat. Beat 0 must have one, with the hook image ("at": "0", "in": "none") so frame 0 is never empty.
  ],
  "cover": {"big": ["LINE 1", "*LINE 2*"]},        # 2 short lines, the payoff; *word* = red
  "sources": [...], "math": [...], "post": {...}   # copied as-is (see ROUTINE.md)
}
The outro ("Follow, for the stuff school skipped.") is added automatically. Do not write it.

Scene ("show"): EITHER a kind (see "scene kinds" below: hook, explain, pair, number, patient, stamp, verdict,
exit, solo, censored) with its few fields, OR a custom element-level scene. Times: "n" = beat n of THIS scene (0 = the beat with the show), "n+0.4" = 0.4 s after it starts.
  "doc":    pose name, or {"pose": "deadpan", "poses": {"1": "point", "2+0.3": "shocked"}}, or false (no Doc).
            Doc Stick stands on the left (x 190). Poses: deadpan, point, shocked, wave, think, shrug.
  "person": {"kind": "boy"|"girl", "slot": "right"|"left"|"center", "pose": ..., "poses": {...}, "in": "slide"|"pop"|"none"}
            Extra pose for people: sit_laptop. Default slot: right (facing Doc) or left when there is no Doc.
  "props":  [{"name": <see pipeline/props.py>, "slot": <slot>, "size": 1.0, "at": "0", "until": "3+0.5",
              "in": "pop"|"slide_right"|"slide_left"|"drop"|"fade"|"none", "out": "slide_right"|"slide_left"|"pop"|"none",
              "states": {"2": "sad"}, "args": {...}, "label": "SHORT LABEL"}]
  "stamps": [{"text": "NO EVIDENCE", "sub": "optional", "slot": "high", "at": "1+0.3", "color": "red"|"ink", "rot": -0.12}]
  "particles": [{"kind": "snow"|"hearts"|"sweat"|"sparkle", "area": "right"|"all", "at": "1", "until": "2"}]
Slots:  floor (prop stands on the floor): floor_left 330, floor_mid 470, floor_center 640, floor_right 820, floor_far 940
        air (prop centre): high 660,830  high_left 500,830  high_right 860,830  center 660,1010  left 520,1010
        right 840,1010  low 680,1300  low_left 520,1300  low_right 860,1300
Overlays (bigx, qmark, stamps, particles) may sit on top of other things; everything else must not overlap.
"""
import json, os, sys, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cairo
from base import W, H, GROUND, CAP_BOTTOM, ROOT, font, ensure_font
import props as P

DOC_X = 190
FLOOR = {"floor_left": 330, "floor_mid": 470, "floor_center": 640, "floor_right": 820, "floor_far": 940}
AIR = {"high": (660, 830), "high_left": (500, 830), "high_right": (860, 830), "center": (660, 1010), "left": (520, 1010),
       "right": (840, 1010), "low": (680, 1300), "low_left": (520, 1300), "low_right": (860, 1300)}
PERSON = {"right": (820, -1), "left": (300, 1), "center": (560, -1)}
OVERLAY = {"bigx", "qmark"}
POSES = {"deadpan", "point", "shocked", "wave", "think", "shrug", "sit_laptop"}
OUTRO = [{"say": "Follow,", "cap": "*FOLLOW*", "pause": 0.15},
         {"say": "for the stuff school skipped.", "cap": "FOR THE STUFF | SCHOOL *SKIPPED.*", "pause": 0.5}]


def ref(v, first, default=0.0):
    """'n' / 'n+d' / n (beat of this scene) -> [global beat, delay]."""
    if v is None: return None
    s = str(v).replace(" ", ""); m = re.fullmatch(r"@?(\d+)(?:\+([\d.]+))?", s)
    if not m: raise SystemExit(f"bad time '{v}' (use '2' or '2+0.4')")
    return [first + int(m.group(1)), float(m.group(2)) if m.group(2) else default]


# ------------------------------------------------------------------ scene kinds (short briefs)
# "show": {"kind": "<kind>", ...fields}. Each kind expands to the element-level scene below, with fixed tested slots.
# A prop field is a name ("poop") or a dict {"name", "size", "args", "states", "label", "at", "in", "out", "until"}.
# Every kind also accepts: "poses" (Doc's pose changes, e.g. {"1": "point"}), "add_props", "stamps", "particles".
def _p(v, slot, **dflt):
    if v is None: return None
    d = {"name": v} if isinstance(v, str) else dict(v)
    for k, x in dflt.items(): d.setdefault(k, x)
    d.setdefault("slot", slot); return d


def _doc(pose, f, default_poses=None):
    poses = dict(default_poses or {}); poses.update(f.get("poses", {}))
    return {"pose": f.get("pose", pose), "poses": poses}


def k_hook(f):
    """Frame-0 hook: Doc deadpan (points from beat 1) + the bizarre thing on the floor (+ optional second thing / patient)."""
    props = [_p(f["prop"], "floor_right", **{"in": "none"})]
    if f.get("prop2"): props.append(_p(f["prop2"], "floor_mid"))
    sh = {"doc": _doc("deadpan", f, {"1": "point"}), "props": props}
    if f.get("person"):
        props[0]["slot"] = f.get("prop_slot", "left")
        sh["person"] = {"kind": f["person"], "pose": "deadpan", "poses": f.get("person_poses", {"1+0.3": "shocked"})}
    return sh


def k_explain(f):
    """Doc points at one big object in the middle (+ optional stamp under it)."""
    pr = _p(f["prop"], "center"); pr.setdefault("at", f.get("at", "0"))
    sh = {"doc": _doc("point", f), "props": [pr]}
    if f.get("stamp"): sh["stamps"] = [{"slot": "low", "at": "1+0.6", "size": 54, **({"text": f["stamp"]} if isinstance(f["stamp"], str) else f["stamp"])}]
    return sh


def k_pair(f):
    """Doc points at two things side by side (comparison): left appears first, right one beat later."""
    l = _p(f["left"], "low_left"); r = _p(f["right"], "low_right", at=f.get("right_at", "1"))
    return {"doc": _doc("point", f), "props": [l, r]}


def k_number(f):
    """Big statistic: a ring that counts up (value 0-100) or a big number, + optional small props under it."""
    if "ring" in f: main = {"name": "ring", "slot": "center", "args": f["ring"]}
    else: main = {"name": "big_number", "slot": "center", "args": f["number"]}
    props = [main]
    if f.get("left"): props.append(_p(f["left"], "low_left", size=0.7, at="0+0.6"))
    if f.get("right"): props.append(_p(f["right"], "low_right", size=0.8, at=f.get("right_at", "1+0.5")))
    return {"doc": _doc("point", f), "props": props}


def k_patient(f):
    """A boy or girl asks the awkward question in a speech bubble; Doc answers."""
    lines = f["question"] if isinstance(f["question"], list) else [f["question"]]
    return {"doc": _doc("deadpan", f, {"1": "point"}),
            "person": {"kind": f.get("person", "boy"), "pose": f.get("person_pose", "think"), "in": "slide"},
            "props": [{"name": "bubble", "slot": "high_right", "size": 0.85, "at": "0+0.5", "args": {"lines": lines, "tail": "right"}}]}


def k_stamp(f):
    """One thing on the floor, then a stamp slams on (NO EVIDENCE, MYTH, TRUE...)."""
    st = f["stamp"] if isinstance(f["stamp"], dict) else {"text": f["stamp"]}
    st = {"slot": "center", "at": "1+0.3", "size": 64, **st}
    return {"doc": _doc("deadpan", f), "props": [_p(f["prop"], "floor_right")], "stamps": [st]}


def k_verdict(f):
    """The payoff: 1 or 2 floor props (floor_center, floor_far) + a big red X (false) or a green check ("verdict": "true")."""
    props = [_p(x, s, **{"in": "none"}) for x, s in zip(f["props"], ("floor_center", "floor_far"))]
    mark = "check" if f.get("verdict") == "true" else "bigx"
    if mark == "bigx" and props[0]["name"] == "sign":          # a sign crosses itself out, centred on the board
        props[0]["states"] = {"0+0.7": "crossed"}
    else:
        props.append({"name": mark, "slot": "low" if mark == "bigx" else "high", "at": "0+0.7"})
    return {"doc": _doc("deadpan", f), "props": props}


def k_exit(f):
    """Callback / goodbye: the hook object leaves (slides off right) while Doc waves or goes deadpan."""
    pr = _p(f["prop"], "floor_right", **{"in": "none", "out": "slide_right"}); pr.setdefault("until", f.get("leave_at", "1+0.3"))
    return {"doc": _doc(f.get("pose", "deadpan"), f, {"1": "wave"} if "pose" not in f else {}), "props": [pr]}


def k_solo(f):
    """No Doc: a person (often sit_laptop) on the left and one or two things on the right."""
    props = [_p(f["prop"], "floor_right", at=f.get("prop_at", "0+0.9"))]
    if f.get("prop2"): props.append(_p(f["prop2"], "high_right", at=f.get("prop2_at", "1+0.2")))
    return {"doc": False, "person": {"kind": f.get("person", "boy"), "pose": f.get("person_pose", "deadpan"), "slot": "left"}, "props": props}


def k_censored(f):
    """Implied intimacy, never shown: a bed and a CENSORED stamp. Doc stares, unimpressed."""
    return {"doc": _doc("deadpan", f), "props": [{"name": "bed", "slot": "floor_right", "size": 0.9}],
            "stamps": [{"text": f.get("text", "CENSORED"), "slot": "center", "at": "0+0.6", "color": "ink", "size": 70}]}


KINDS = {"hook": k_hook, "explain": k_explain, "pair": k_pair, "number": k_number, "patient": k_patient, "stamp": k_stamp,
         "verdict": k_verdict, "exit": k_exit, "solo": k_solo, "censored": k_censored}


def expand(show):
    """Kind -> element-level scene. A show without "kind" is already element-level (custom scene)."""
    if "kind" not in show: return show
    f = dict(show); kind = f.pop("kind")
    if kind not in KINDS: raise SystemExit(f"unknown scene kind '{kind}'. Kinds: {', '.join(KINDS)}")
    sh = KINDS[kind](f)
    sh["props"] = sh.get("props", []) + [_p(x, "center") for x in f.get("add_props", [])]
    if f.get("stamps"): sh["stamps"] = sh.get("stamps", []) + f["stamps"]
    if f.get("particles"): sh["particles"] = f["particles"]
    return sh


def build(brief):
    beats = brief["beats"]
    if not beats or "show" not in beats[0]: raise SystemExit("beat 0 needs a 'show' (the hook frame)")
    if beats[0]["show"].get("kind", "hook") not in ("hook", "patient"): print("note: beat 0 is usually kind \"hook\" or \"patient\"")
    if any("school skipped" in b["say"].lower() for b in beats): raise SystemExit("do not write the outro, the kit adds it")
    firsts = [i for i, b in enumerate(beats) if "show" in b]
    phrases = []
    for i, b in enumerate(beats):
        last_of_scene = (i + 1 in firsts) or i == len(beats) - 1
        phrases.append({"say": b["say"], "cap": b.get("cap", b["say"]), "pause": b.get("pause", 0.45 if last_of_scene else 0.2)})
    scenes = []
    for si, first in enumerate(firsts):
        end = firsts[si + 1] if si + 1 < len(firsts) else len(beats)
        sh = expand(beats[first]["show"]); sc = {"first": first, "end": end, "doc": None, "people": [], "els": []}
        d = sh.get("doc", "point")
        if d is not False:
            if isinstance(d, str): d = {"pose": d}
            poses = [[first, 0.0, d.get("pose", "point")]] + [ref(k, first) + [p] for k, p in d.get("poses", {}).items()]
            sc["doc"] = {"x": DOC_X, "s": 2.25, "face": 1, "poses": sorted(poses)}
        ps = sh.get("person"); ps = [ps] if isinstance(ps, dict) else (ps or [])
        for p in ps:
            slot = p.get("slot", "right" if sc["doc"] else "left"); x, face = PERSON[slot]
            poses = [[first, 0.0, p.get("pose", "deadpan")]] + [ref(k, first) + [v] for k, v in p.get("poses", {}).items()]
            sc["people"].append({"kind": p.get("kind", "boy"), "x": x, "s": 2.25, "face": p.get("face", face), "poses": sorted(poses),
                                 "at": ref(p.get("at", "0"), first), "in": p.get("in", "none")})
        for pr in sh.get("props", []):
            name = pr["name"]
            if name not in P.PROPS: raise SystemExit(f"unknown prop '{name}'. Known: {', '.join(sorted(P.PROPS))}")
            info = P.PROPS[name]; slot = pr.get("slot", "floor_right" if info.anchor == "ground" else "center")
            if info.anchor == "ground":
                if slot not in FLOOR: raise SystemExit(f"prop {name} stands on the floor: use a floor_ slot, not '{slot}'")
                x, y = FLOOR[slot], GROUND
            else:
                if slot not in AIR: raise SystemExit(f"prop {name} floats: use an air slot ({', '.join(AIR)}), not '{slot}'")
                x, y = AIR[slot]
            states = sorted(ref(k, first) + [v] for k, v in pr.get("states", {}).items())
            sc["els"].append({"type": "prop", "name": name, "x": x, "y": y, "s": pr.get("size", 1.0), "slot": slot,
                              "at": ref(pr.get("at", "0"), first), "until": ref(pr.get("until"), first),
                              "in": pr.get("in", "pop"), "out": pr.get("out", "none"), "states": states,
                              "args": pr.get("args", {}), "label": pr.get("label"), "flip": pr.get("flip", False)})
        for stp in sh.get("stamps", []):
            x, y = AIR[stp.get("slot", "high")]
            sc["els"].append({"type": "stamp", "text": stp["text"], "sub": stp.get("sub"), "x": x, "y": y,
                              "color": stp.get("color", "red"), "rot": stp.get("rot", -0.12), "size": stp.get("size", 60),
                              "at": ref(stp.get("at", "0+0.3"), first), "until": ref(stp.get("until"), first)})
        for pt in sh.get("particles", []):
            sc["els"].append({"type": "particles", "kind": pt.get("kind", "snow"), "area": pt.get("area", "right"),
                              "at": ref(pt.get("at", "0"), first), "until": ref(pt.get("until"), first)})
        scenes.append(sc)
    n = len(beats)
    phrases += [dict(p) for p in OUTRO]
    scenes.append({"first": n, "end": n + 2, "outro": True, "doc": {"x": 540, "s": 2.4, "face": 1, "poses": [[n, 0.0, "wave"]]},
                   "people": [], "els": []})
    spec = {"id": brief["id"], "voice": "am_michael", "speed": brief.get("speed", 1.0), "phrases": phrases, "scenes": scenes,
            "cover": brief.get("cover", {}), "sources": brief.get("sources", []), "math": brief.get("math", []),
            "post": brief.get("post", {})}
    return spec


# ------------------------------------------------------------------ layout check
_ctx = None
def _tw(s, size):
    global _ctx
    if _ctx is None: ensure_font(); _ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8))
    font(_ctx, size); return _ctx.text_extents(s).x_advance


def boxes(spec):
    """(label, x0, y0, x1, y1, beat_from, beat_to, overlay) for everything placed on screen."""
    out = []
    for sc in spec["scenes"]:
        if sc.get("outro"): continue
        a, b = sc["first"], sc["end"]
        if sc["doc"]:
            x = sc["doc"]["x"]; out.append(("Doc Stick", x - 50, GROUND - 575, x + 50, GROUND, a, b, False))
        for p in sc["people"]:
            x = p["x"]; sit = any(q[2] == "sit_laptop" for q in p["poses"])
            box = (x - 70 * 2.25 / 2.25, GROUND - 260 * 2.25, x + 240, GROUND) if sit else (x - 65, GROUND - 585, x + 65, GROUND)
            if sit and p["face"] < 0: box = (x - 240, GROUND - 585, x + 70, GROUND)
            out.append((f"{p['kind']}", *box, p["at"][0], b, False))
        for e in sc["els"]:
            fr, to = e["at"][0], (e["until"][0] + (1 if e["until"][1] > 0 else 0)) if e.get("until") else b
            if e["type"] == "prop":
                x0, y0, x1, y1 = P.PROPS[e["name"]].bbox; s = e["s"]
                if e.get("flip"): x0, x1 = -x1, -x0
                bx = [e["x"] + x0 * s, e["y"] + y0 * s, e["x"] + x1 * s, e["y"] + y1 * s]
                if e.get("label"): bx[3] += 70; bx[0] = min(bx[0], e["x"] - _tw(e["label"], 40) / 2); bx[2] = max(bx[2], e["x"] + _tw(e["label"], 40) / 2)
                out.append((f"prop {e['name']} ({e['slot']})", *bx, fr, to, e["name"] in OVERLAY))
            elif e["type"] == "stamp":
                w = max(_tw(e["text"], e["size"]), _tw(e.get("sub") or "", e["size"] * 0.45)) + 70
                h = e["size"] + 50 + (e["size"] * 0.5 if e.get("sub") else 0)
                out.append((f"stamp '{e['text']}'", e["x"] - w / 2 - 20, e["y"] - h / 2 - 20, e["x"] + w / 2 + 20, e["y"] + h / 2 + 20, fr, to, True))
    return out


def layout_check(spec):
    probs = []; bx = boxes(spec)
    for (lab, x0, y0, x1, y1, fr, to, ov) in bx:
        if x0 < 10 or x1 > W - 10: probs.append(f"{lab} goes off the side of the screen (x {x0:.0f} to {x1:.0f}): use a smaller size or another slot")
        if y0 < CAP_BOTTOM: probs.append(f"{lab} reaches into the caption zone (top at y {y0:.0f}, must be below {CAP_BOTTOM}): smaller size or a lower slot")
        if y1 > GROUND + 80: probs.append(f"{lab} goes below the floor line: use a higher slot")
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            a, b = bx[i], bx[j]
            if a[7] or b[7]: continue
            if a[5] >= b[6] or b[5] >= a[6]: continue           # not on screen at the same time
            ox = min(a[3], b[3]) - max(a[1], b[1]); oy = min(a[4], b[4]) - max(a[2], b[2])
            if ox > 12 and oy > 12: probs.append(f"{a[0]} overlaps {b[0]} (by {ox:.0f} x {oy:.0f} px): move one to another slot or make it smaller")
    for i, p in enumerate(spec["phrases"]):
        for chunk in caption_chunks(p["cap"]):
            if _tw(chunk.replace("*", ""), 96) > 900 * 2:
                probs.append(f"beat {i}: caption chunk too long: '{chunk}'")
        if len(p["say"].split()) > 22: probs.append(f"beat {i}: phrase too long ({len(p['say'].split())} words, max 22): split it")
    return probs


def caption_chunks(cap):
    """'|' splits by hand; otherwise up to 3 words and about 18 characters per chunk."""
    if "|" in cap: return [c.strip() for c in cap.split("|") if c.strip()]
    words = cap.split(); out = []; cur = []
    for w in words:
        if cur and (len(cur) >= 3 or len(" ".join(cur + [w]).replace("*", "")) > 18): out.append(" ".join(cur)); cur = []
        cur.append(w)
    if cur: out.append(" ".join(cur))
    return out


def main():
    path = sys.argv[1]; brief = json.load(open(path))
    spec = build(brief)
    os.makedirs(os.path.join(ROOT, "specs"), exist_ok=True)
    out = os.path.join(ROOT, "specs", brief["id"] + ".json")
    json.dump(spec, open(out, "w"), indent=1, ensure_ascii=False)
    probs = layout_check(spec)
    if probs:
        print("LAYOUT PROBLEMS:\n- " + "\n- ".join(probs)); sys.exit(1)
    print(f"layout ok: {os.path.relpath(out, ROOT)} ({len(spec['scenes'])} scenes, {len(spec['phrases'])} phrases)")


if __name__ == "__main__":
    main()
