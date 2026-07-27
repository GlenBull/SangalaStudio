"""LEGO-kit instruction booklets, rendered from a 3D model of the assembly.

Every illustration comes from ONE model, drawn cumulatively: step N shows every piece placed so far,
with step N's own pieces in full color and the earlier ones pale. Because the pictures are generated
rather than drawn, the steps cannot disagree with one another.

A figure is DATA (see models/crane.py). This file is the engine and knows nothing about any animal.

Units: 1.0 = one stud pitch (8 mm). A brick is 1.2 tall, a plate 0.4 -- the real LEGO ratio, so
3 plates make a brick exactly. Coordinates are (x, y, z) with z up; the figure faces +x.
"""
import os, subprocess, tempfile

U = 14.0        # screen half-step per stud, horizontally
V = 14.0        # screen pixels per unit of height
BH = 1.2        # brick height  (9.6 mm / 8 mm)
PH = 0.4        # plate height  (3.2 mm / 8 mm)

# The LEGO palette these booklets draw from. Add to it freely; the names are what the parts list prints.
COLORS = {
    "white": "#f0f1ee", "black": "#26333d", "red": "#c4281c", "orange": "#fe8a18",
    "yellow": "#f5cd30", "tan": "#d7c59a", "brown": "#694027", "dark brown": "#372115",
    "green": "#3f9b4f", "dark green": "#00522c", "lime": "#a6ca38", "blue": "#0d69ab",
    "dark blue": "#20325a", "light gray": "#a5aaae", "gray": "#75797a", "dark gray": "#4b5054",
    "light green": "#8fce7f", "sand": "#d7c59a", "purple": "#342b75", "pink": "#e891c0",
}

def _hex2rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def _rgb2hex(t): return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in t)
def shade(c, f):
    r, g, b = _hex2rgb(c); return _rgb2hex((r*f, g*f, b*f))
def pale(c, k=0.42):
    """Already-placed pieces ease toward a cool gray so the step's new pieces stand out."""
    r, g, b = _hex2rgb(c); t = (214, 220, 226)
    return _rgb2hex((r+(t[0]-r)*k, g+(t[1]-g)*k, b+(t[2]-b)*k))

def col(name):
    """Accept either a palette name ('dark gray') or a literal '#rrggbb'."""
    return name if str(name).startswith("#") else COLORS[str(name).lower()]

def iso(x, y, z):
    return ((x - y) * U, (x + y) * U * 0.5 - z * V)

def _poly(pts, fill, stroke, sw=0.9):
    d = " ".join("%.2f,%.2f" % iso(*p) for p in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.2f" stroke-linejoin="round"/>'
            % (d, fill, stroke, sw))

# --------------------------------------------------------------------------- pieces
class Piece:
    """One drawable solid. `lo`/`hi` are its 3D bounds, used for the occlusion sort."""
    __slots__ = ("lo", "hi", "draw", "tie")
    def __init__(self, lo, hi, draw):
        self.lo, self.hi, self.draw = lo, hi, draw
        self.tie = (lo[0] + lo[1]) + lo[2]*10      # deterministic fallback ordering

def brick(x, y, z, w, d, h, color, studs=True):
    """A box with studs on top. w, d in studs; h in height units (BH = one brick, PH = one plate).
    Pass studs=False for a smooth-topped piece (a tile, or a decorative prong)."""
    c0 = col(color)
    def draw(on):
        c = c0 if on else pale(c0)
        edge = shade(c, 0.45 if on else 0.72)
        top, rgt, lft = c, shade(c, 0.80), shade(c, 0.62)
        s = [_poly([(x, y, z+h), (x+w, y, z+h), (x+w, y+d, z+h), (x, y+d, z+h)], top, edge),
             _poly([(x+w, y, z), (x+w, y+d, z), (x+w, y+d, z+h), (x+w, y, z+h)], rgt, edge),
             _poly([(x, y+d, z), (x+w, y+d, z), (x+w, y+d, z+h), (x, y+d, z+h)], lft, edge)]
        if studs:
            r = 0.30; rx = r*U*1.4142; ry = r*U*0.7071; sh = 0.22*V
            for i in range(int(round(w))):
                for j in range(int(round(d))):
                    cx, cy = iso(x+i+0.5, y+j+0.5, z+h)
                    s.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="%s" stroke="%s" stroke-width="0.7"/>'
                             % (cx, cy+sh, rx, ry, shade(c, 0.70), edge))
                    s.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
                             % (cx-rx, cy, 2*rx, sh, shade(c, 0.70)))
                    for sx in (cx-rx, cx+rx):
                        s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="0.7"/>'
                                 % (sx, cy, sx, cy+sh, edge))
                    s.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="%s" stroke="%s" stroke-width="0.7"/>'
                             % (cx, cy, rx, ry, top, edge))
        return "".join(s)
    return Piece((x, y, z), (x+w, y+d, z+h), draw)

def slope(x, y, z, w, d, h, dirn, color, inv=False):
    """A slope brick: full height at one edge, ramping to nothing at the opposite one.
    dirn is the direction the ramp FALLS: '+x', '-x', '+y' or '-y'.

    inv=True gives the INVERTED slope (LEGO's 'slope, inverted 45'): the top stays full and flat and
    the UNDERSIDE falls away instead, so the piece fills the underside of an overhang. It carries a
    full set of studs, because its top face is whole. This is the same shape Sangala Studio makes
    with the Invert checkbox on a sloped shape."""
    c0 = col(color)
    if dirn not in ("+x", "-x", "+y", "-y"):
        raise ValueError("slope dirn must be one of '+x', '-x', '+y', '-y' (got %r)" % dirn)
    if inv:
        return _slope_inv(x, y, z, w, d, h, dirn, c0)
    def draw(on):
        c = c0 if on else pale(c0)
        edge = shade(c, 0.45 if on else 0.72)
        ramp, rgt, lft = shade(c, 0.90), shade(c, 0.80), shade(c, 0.62)
        s = []
        if dirn == "-x":            # high at x+w
            s.append(_poly([(x, y, z), (x+w, y, z+h), (x+w, y+d, z+h), (x, y+d, z)], ramp, edge))
            s.append(_poly([(x+w, y, z), (x+w, y+d, z), (x+w, y+d, z+h), (x+w, y, z+h)], rgt, edge))
            s.append(_poly([(x, y+d, z), (x+w, y+d, z), (x+w, y+d, z+h)], lft, edge))
        elif dirn == "+x":          # high at x
            s.append(_poly([(x, y, z+h), (x+w, y, z), (x+w, y+d, z), (x, y+d, z+h)], ramp, edge))
            s.append(_poly([(x, y+d, z), (x+w, y+d, z), (x, y+d, z+h)], lft, edge))
        elif dirn == "-y":          # high at y+d (the face toward the viewer stays tall)
            s.append(_poly([(x, y, z), (x+w, y, z), (x+w, y+d, z+h), (x, y+d, z+h)], ramp, edge))
            s.append(_poly([(x, y+d, z+h), (x+w, y+d, z+h), (x+w, y+d, z), (x, y+d, z)], lft, edge))
            s.append(_poly([(x+w, y, z), (x+w, y+d, z), (x+w, y+d, z+h)], rgt, edge))
        else:                       # '+y': high at y, ramping down toward the viewer
            s.append(_poly([(x, y, z+h), (x+w, y, z+h), (x+w, y+d, z), (x, y+d, z)], ramp, edge))
            s.append(_poly([(x+w, y, z+h), (x+w, y, z), (x+w, y+d, z)], rgt, edge))
        return "".join(s)
    return Piece((x, y, z), (x+w, y+d, z+h), draw)

def cone(x, y, z, w, d, h, color, top=0.55, studs=False):
    """A round piece standing on the grid: a LEGO cone, or a round brick when top=1.

    `top` is the top radius as a fraction of the base -- 1.0 a straight cylinder (a 1 x 1 round
    brick), around 0.55 the familiar cone, 0 a full point. Sangala Studio makes the same shape from
    a circle with its Cone taper field, which is where a model like this one should start."""
    c0 = col(color)
    cx, cy = x + w/2.0, y + d/2.0
    rb = min(w, d) * 0.5 * 0.94              # a round brick is a hair narrower than its stud pitch
    rt = max(0.0, rb * top)
    N = 28
    import math
    def ring(r, zz):
        return [(cx + r*math.cos(2*math.pi*i/N), cy + r*math.sin(2*math.pi*i/N), zz) for i in range(N)]
    def draw(on):
        c = c0 if on else pale(c0)
        edge = shade(c, 0.45 if on else 0.72)
        base, tip = ring(rb, z), ring(rt, z+h)
        s, band = [], []
        for i in range(N):
            j = (i+1) % N
            quad = [base[i], base[j], tip[j], tip[i]]
            p = [iso(*q) for q in quad]
            area = sum(p[k][0]*p[(k+1) % 4][1] - p[(k+1) % 4][0]*p[k][1] for k in range(4))
            if area <= 0:                    # facing away from the camera
                continue
            th = 2*math.pi*(i+0.5)/N
            lit = 0.5 + 0.5*(math.cos(th)*0.80 + math.sin(th)*0.30)
            f = shade(c, 0.52 + 0.36*max(0.0, min(1.0, lit)))
            # stroked in its OWN color: a dark line per facet turns a smooth cone into a beach
            # umbrella. The silhouette below supplies the one outline the piece actually needs.
            s.append(_poly(quad, f, f, sw=0.6))
            band.append((base[i], base[j], tip[i], tip[j]))
        if band:
            ring_pts = [q[0] for q in band] + [band[-1][1]] + [band[-1][3]] \
                       + [q[2] for q in reversed(band)]
            s.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="0.9" stroke-linejoin="round"/>'
                     % (" ".join("%.2f,%.2f" % iso(*q) for q in ring_pts), edge))
        if rt > 1e-6:                        # the flat top, as an ellipse
            tx, ty = iso(cx, cy, z+h)
            s.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="%s" stroke="%s" stroke-width="0.9"/>'
                     % (tx, ty, rt*U*1.4142, rt*U*0.7071, c, edge))
        if studs and rt > 0.18:
            r = 0.30; sh = 0.22*V
            sx_, sy_ = iso(cx, cy, z+h)
            s.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
                     % (sx_-r*U*1.4142, sy_, 2*r*U*1.4142, sh, shade(c, 0.70)))
            s.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="%s" stroke="%s" stroke-width="0.7"/>'
                     % (sx_, sy_, r*U*1.4142, r*U*0.7071, c, edge))
        return "".join(s)
    return Piece((x, y, z), (x+w, y+d, z+h), draw)

def _slope_inv(x, y, z, w, d, h, dirn, c0):
    """The inverted slope. Its top is a whole rectangle (so it takes a full set of studs) and the
    material tapers away underneath toward `dirn`. The undersides face downward and are almost
    edge-on to this camera, so what actually reads is the flat top plus one triangular flank."""
    def draw(on):
        c = c0 if on else pale(c0)
        edge = shade(c, 0.45 if on else 0.72)
        top, rgt, lft, und = c, shade(c, 0.80), shade(c, 0.62), shade(c, 0.52)
        s = [_poly([(x, y, z+h), (x+w, y, z+h), (x+w, y+d, z+h), (x, y+d, z+h)], top, edge)]
        if dirn == "+x":            # solid at x, tapering to nothing at x+w
            s.append(_poly([(x, y, z), (x+w, y, z+h), (x+w, y+d, z+h), (x, y+d, z)], und, edge))
            s.append(_poly([(x, y+d, z), (x+w, y+d, z+h), (x, y+d, z+h)], lft, edge))
        elif dirn == "-x":          # solid at x+w
            s.append(_poly([(x, y, z+h), (x+w, y, z), (x+w, y+d, z), (x, y+d, z+h)], und, edge))
            s.append(_poly([(x+w, y, z), (x+w, y+d, z), (x+w, y+d, z+h), (x+w, y, z+h)], rgt, edge))
            s.append(_poly([(x, y+d, z+h), (x+w, y+d, z), (x+w, y+d, z+h)], lft, edge))
        elif dirn == "+y":          # solid at y, tapering toward the viewer
            s.append(_poly([(x, y, z), (x+w, y, z), (x+w, y+d, z+h), (x, y+d, z+h)], und, edge))
            s.append(_poly([(x+w, y, z), (x+w, y+d, z+h), (x+w, y, z+h)], rgt, edge))
        else:                       # '-y': solid at y+d, the face toward the viewer stays full
            s.append(_poly([(x, y, z+h), (x+w, y, z+h), (x+w, y+d, z), (x, y+d, z)], und, edge))
            s.append(_poly([(x, y+d, z), (x+w, y+d, z), (x+w, y+d, z+h), (x, y+d, z+h)], lft, edge))
            s.append(_poly([(x+w, y, z+h), (x+w, y+d, z), (x+w, y+d, z+h)], rgt, edge))
        r = 0.30; rx = r*U*1.4142; ry = r*U*0.7071; sh = 0.22*V     # the full top carries studs
        for i in range(int(round(w))):
            for j in range(int(round(d))):
                cx, cy = iso(x+i+0.5, y+j+0.5, z+h)
                s.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="%s" stroke="%s" stroke-width="0.7"/>'
                         % (cx, cy+sh, rx, ry, shade(c, 0.70), edge))
                s.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
                         % (cx-rx, cy, 2*rx, sh, shade(c, 0.70)))
                s.append('<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="%s" stroke="%s" stroke-width="0.7"/>'
                         % (cx, cy, rx, ry, top, edge))
        return "".join(s)
    return Piece((x, y, z), (x+w, y+d, z+h), draw)

def decal(x, y, z, a, b, r, color, face="+y"):
    """A round tile (an eye, a spot) lying flat on a vertical face of the piece beneath it.
    (x, y, z) is the face's lower corner; a runs along the face, b runs up it."""
    c0 = col(color)
    def draw(on):
        c = c0 if on else pale(c0)
        ox, oy = iso(x, y, z)
        m = (U, U*0.5, -V) if face == "+y" else (-U, U*0.5, -V)
        return ('<g transform="matrix(%.3f,%.3f,0,%.3f,%.2f,%.2f)">'
                '<circle cx="%.3f" cy="%.3f" r="%.3f" fill="%s" stroke="%s" stroke-width="0.05"/>'
                '<circle cx="%.3f" cy="%.3f" r="%.3f" fill="%s"/></g>'
                % (m[0], m[1], m[2], ox, oy, a, b, r, c, shade(c, 0.5),
                   a, b, r*0.45, shade(c, 0.30) if on else pale("#555555")))
    p = Piece((x, y, z), (x, y, z), draw)
    p.tie += 0.5                       # a decal always paints just after the face it sits on
    return p

# --------------------------------------------------------------------------- draw order
def _screen_box(p):
    xs, ys = [], []
    for X in (p.lo[0], p.hi[0]):
        for Y in (p.lo[1], p.hi[1]):
            for Z in (p.lo[2], p.hi[2]):
                sx, sy = iso(X, Y, Z); xs.append(sx); ys.append(sy)
    return (min(xs), min(ys), max(xs), max(ys))

def _in_front(a, b):
    """True when `a` is wholly on the viewer's side of `b` along one axis. In this projection the
    camera sits at +x, +y, +z, so being entirely beyond a neighbour on ANY of the three means the
    piece can only occlude it, never the reverse."""
    return a.lo[0] >= b.hi[0] - 1e-9 or a.lo[1] >= b.hi[1] - 1e-9 or a.lo[2] >= b.hi[2] - 1e-9

def draw_order(pieces):
    """Painter's order by pairwise occlusion, topologically sorted.

    A plain sort key cannot do this: a wide flat baseplate and a small brick standing on it have no
    single number that orders them correctly against everything else (a center-of-mass key once let
    the baseplate paint straight over a leg). Comparing pieces pairwise, and only where they actually
    overlap on screen, gets it right for figures of any shape -- tall, wide, or sprawling."""
    n = len(pieces)
    if n < 2:
        return list(range(n))
    boxes = [_screen_box(p) for p in pieces]
    after = [[] for _ in range(n)]     # after[i] = pieces that must be drawn AFTER i
    indeg = [0]*n
    for i in range(n):
        for j in range(i+1, n):
            bi, bj = boxes[i], boxes[j]
            if bi[2] < bj[0] or bj[2] < bi[0] or bi[3] < bj[1] or bj[3] < bi[1]:
                continue                                   # disjoint on screen: order is free
            fi, fj = _in_front(pieces[i], pieces[j]), _in_front(pieces[j], pieces[i])
            if fi and not fj:   after[j].append(i); indeg[i] += 1
            elif fj and not fi: after[i].append(j); indeg[j] += 1
    ready = sorted((k for k in range(n) if indeg[k] == 0), key=lambda k: pieces[k].tie)
    out, placed = [], [False]*n
    while len(out) < n:
        if not ready:                                      # interpenetrating pieces can form a cycle;
            rest = [k for k in range(n) if not placed[k]]  # break it on the fallback key
            ready = [min(rest, key=lambda k: pieces[k].tie)]
        k = ready.pop(0); out.append(k); placed[k] = True
        for m in after[k]:
            indeg[m] -= 1
            if indeg[m] == 0 and not placed[m]:
                ready.append(m)
        ready = sorted((m for m in ready if not placed[m]), key=lambda m: pieces[m].tie)
    return out

# --------------------------------------------------------------------------- the booklet
class Book:
    """A figure: its steps, its parts list, and the prose around them."""
    def __init__(self, title, subtitle, note, inventory, steps, closing=None):
        """closing: (heading, text) shown after the last step, or None."""
        self.title, self.subtitle, self.note = title, subtitle, note
        self.inventory, self.steps, self.closing = inventory, steps, closing
        self._frame()

    def _all(self):
        return [p for s in self.steps for p in s["pieces"]]

    def _frame(self, pad=14):
        xs, ys = [], []
        for p in self._all():
            b = _screen_box(p); xs += [b[0], b[2]]; ys += [b[1], b[3]]
        self.vb = (min(xs)-pad, min(ys)-pad, (max(xs)-min(xs))+2*pad, (max(ys)-min(ys))+2*pad)

    def svg(self, upto, width=None):
        """The assembly through step `upto` (0-based), that step's pieces in full color."""
        items = []
        for i, s in enumerate(self.steps[:upto+1]):
            for p in s["pieces"]:
                items.append((p, i == upto))
        order = draw_order([p for p, _ in items])
        body = "".join(items[k][0].draw(items[k][1]) for k in order)
        w = 'width="%d"' % width if width else 'width="100%%" style="max-width:%dpx;height:auto"' % int(self.vb[2]*1.05)
        return ('<svg viewBox="%.1f %.1f %.1f %.1f" %s xmlns="http://www.w3.org/2000/svg">%s</svg>'
                % (self.vb[0], self.vb[1], self.vb[2], self.vb[3], w, body))

    def icon(self, spec, height=34):
        """A small standalone drawing of one piece, for the parts callout beside a step."""
        global U, V
        keep = (U, V); U, V = 9.0, 9.0
        try:
            kind, w, d, h, color = spec
            p = (slope(0, 0, 0, w, d, h, "-x", color) if kind == "slope"
                 else brick(0, 0, 0, w, d, h, color, studs=(kind != "tile")))
            art = p.draw(True)
            b = _screen_box(p)
            vb = "%.1f %.1f %.1f %.1f" % (b[0]-5, b[1]-7, (b[2]-b[0])+10, (b[3]-b[1])+14)
        finally:
            U, V = keep
        return '<svg viewBox="%s" height="%d" xmlns="http://www.w3.org/2000/svg">%s</svg>' % (vb, height, art)

    # ---------------- HTML
    def html(self):
        h = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             "<title>%s</title><style>%s</style></head><body><div class='wrap'>" % (self.title, _CSS)]
        h.append("<h1>%s</h1><p class='lede'>%s</p>" % (self.title, self.subtitle))
        if self.note:
            h.append("<div class='note'>%s</div>" % self.note)
        h.append("<div class='inv'><h2>Pieces you will need</h2><div class='invgrid'>")
        for label, spec in self.inventory:
            h.append("<div class='invrow'>%s<span>%s</span></div>" % (self.icon(spec), label))
        h.append("</div></div>")
        for i, s in enumerate(self.steps):
            h.append("<div class='step'><div class='hd'><div class='num'>%d</div><h3>%s</h3></div><div class='bd'>"
                     % (i+1, s["title"]))
            h.append("<div class='art'>%s</div>" % self.svg(i))
            h.append("<div class='side'><p>%s</p><div class='parts'><b>Add these pieces</b>%s</div></div>"
                     % (s["text"], "".join("<div class='prow'>%s<span>%s</span></div>"
                                           % (self.icon(spec), lab) for lab, spec in s["parts"])))
            h.append("</div></div>")
        if self.closing:
            h.append("<div class='foot'><b>%s.</b> %s</div>" % self.closing)
        h.append("</div></body></html>")
        return "".join(h)

    # ---------------- PNG, via headless Edge (no Python imaging library needed)
    def rasterize(self, outdir, scale=2.6, edge=None):
        """Write one PNG per step. Returns the list of paths, in step order."""
        edge = edge or _find_edge()
        if not edge:
            raise RuntimeError("Microsoft Edge not found - needed to turn the drawings into images. "
                               "The HTML booklet does not need it.")
        outdir = os.path.abspath(outdir)   # Edge resolves --screenshot against ITS cwd, not ours
        os.makedirs(outdir, exist_ok=True)
        w, hgt = int(self.vb[2]*scale), int(self.vb[3]*scale)
        paths = []
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(len(self.steps)):
                page = os.path.join(tmp, "s%02d.html" % (i+1))
                with open(page, "w", encoding="utf-8") as f:
                    f.write("<body style='margin:0;background:#fff'>%s</body>"
                            % self.svg(i, width=w))
                png = os.path.join(outdir, "step%02d.png" % (i+1))
                if os.path.exists(png):
                    os.remove(png)
                subprocess.run([edge, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                                "--screenshot=" + png, "--window-size=%d,%d" % (w, hgt),
                                "file:///" + page.replace("\\", "/")],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
                if not os.path.exists(png):
                    raise RuntimeError("Edge did not write %s" % png)
                paths.append(png)
        return paths

def _find_edge():
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(p):
            return p
    return None

_CSS = """
*{box-sizing:border-box}
body{margin:0;font-family:"Segoe UI",system-ui,sans-serif;color:#26303a;background:#eef2f6}
.wrap{max-width:900px;margin:0 auto;padding:28px 20px 60px}
h1{font-size:1.9rem;margin:0 0 .1rem;letter-spacing:-.01em}
.lede{color:#5b6772;margin:0 0 1.4rem;font-size:1rem;line-height:1.5}
.note{background:#fff8e6;border:1px solid #e6d4a2;border-radius:10px;padding:.7rem .9rem;
      font-size:.88rem;color:#6b5a34;line-height:1.5;margin:0 0 1.6rem}
.inv{background:#fff;border:1px solid #d6dee6;border-radius:12px;padding:1rem 1.1rem;margin:0 0 1.8rem}
.inv h2{font-size:1.05rem;margin:0 0 .6rem}
.invgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:.45rem 1rem}
.invrow{display:flex;align-items:center;gap:.5rem;font-size:.88rem}
.step{background:#fff;border:1px solid #d6dee6;border-radius:14px;margin:0 0 1.1rem;overflow:hidden;
      box-shadow:0 1px 3px rgba(20,40,60,.06)}
.hd{display:flex;align-items:center;gap:.7rem;padding:.75rem 1rem;border-bottom:1px solid #e6ecf2;background:#f7f9fb}
.num{flex:0 0 auto;width:2rem;height:2rem;border-radius:50%;background:#2d6fa8;color:#fff;
     display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1rem}
.hd h3{margin:0;font-size:1.05rem;font-weight:650}
.bd{display:grid;grid-template-columns:1fr 250px;gap:1rem;padding:1rem}
@media(max-width:720px){.bd{grid-template-columns:1fr}}
.art{display:flex;align-items:center;justify-content:center;background:#f4f7fa;border-radius:10px;padding:.5rem}
.side p{margin:0 0 .8rem;font-size:.9rem;line-height:1.55;color:#3d4954}
.parts{border-top:1px dashed #cfd8e0;padding-top:.6rem}
.parts b{display:block;font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:#7c8894;margin-bottom:.35rem}
.prow{display:flex;align-items:center;gap:.5rem;font-size:.86rem;margin-bottom:.2rem}
.foot{color:#5b6772;font-size:.88rem;line-height:1.6;margin-top:1.6rem;border-top:1px solid #d6dee6;padding-top:1rem}
"""
