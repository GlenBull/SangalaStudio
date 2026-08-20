"""Trace the PROFILE OUTLINE of each LEGO part a .block design uses, for Studio's importer.

Studio has no LDraw library and must not grow one - shipping 24,000 part files beside an
application that testers update by double-clicking a .cmd is the cost the whole import was designed
to avoid. So the outlines are measured HERE, once, from the library that Sangala Blocks already
bundles, and emitted as a small table of numbers that is pasted into SangalaStudio.html as data.
Nothing is traced at run time and Studio gains no dependency.

WHY AN OUTLINE AND NOT AN ANGLE. A .block design imports with the figure's PROFILE in Studio's plan
and its depth on the extrude axis. In that orientation a slope brick's ramp lies in the page, so the
part simply IS a trapezoid in plan; a wedge is its measured hexagon; an inverted slope is the
mirrored trapezoid. One mechanism covers every part, measured rather than described, and no angle is
parsed out of a part's name.

    set PYTHONUTF8=1
    python "D:\\Code Projects\\Silhouette Tools\\tools\\block_outlines.py" 3040 4286 3665 43712
    python "D:\\Code Projects\\Silhouette Tools\\tools\\block_outlines.py" --from "D:\\...\\Crane.block"
    python "D:\\Code Projects\\Silhouette Tools\\tools\\block_outlines.py" --from ... --js

The projection follows Blocks' own silOf: axis 0 is across, 1 is the part's height (+Y is DOWN in
LDraw, so it is negated here), 2 is its depth. An UPRIGHT part shows its elevation (0,1); a part
turned onto its face shows its plan (0,2). Studs are folded onto the body, exactly as silOf folds
them, because a stud is drawn as its own mark and does not belong to the outline.
"""
import json
import os
import sys

BLOCKS = r"D:\Code Projects\Block Tools"
sys.path.insert(0, os.path.join(BLOCKS, "tools"))
import plan_outline as po                                            # noqa: E402
import ldparts                                                       # noqa: E402

GRID = 400          # cells along the longer side; fine enough to hold a curve
TOL = 2.0           # simplification, in cells - smooths the raster staircase, keeps real corners


def outline(number, iu, iv, flip_v):
    """One part's outline on a chosen plane, normalized to its own box: [0,1] across and down."""
    orig_raster, orig_simplify = po.raster, po.simplify
    po.raster = lambda flat, g=GRID: orig_raster(flat, grid=g)
    po.simplify = lambda loop, t=TOL: orig_simplify(loop, tol=t)
    try:
        loops = po.outline(number, iu=iu, iv=iv, flip_v=flip_v)
    finally:
        po.raster, po.simplify = orig_raster, orig_simplify
    if not loops:
        return None
    return max(loops, key=lambda l: abs(po.area(l)))                 # the body, not a hole


# WHICH PLANE A PART SHOWS DEPENDS ON HOW THE PART ITSELF IS MODELED, not on how it is placed. A
# "Slope Brick 45 2 x 1" measures 8 mm across and 16 deep, so its ramp lies in the z-y plane and the
# elevation that shows it is (2,1), not (0,1). Rather than work a yaw out here and hope, all four
# planes are measured and the importer picks by matching the box it has already computed against the
# part's measured millimeters. Measured, not described - which is the rule this whole table follows.
PLANES = {"01": (0, 1), "21": (2, 1), "02": (0, 2), "20": (2, 0)}


def measure(number):
    """Every plane a placement can need, plus the part's real size in millimeters."""
    path, _, _ = ldparts.resolve(number)
    if not path:
        return None
    x0, x1, y0, y1, z0, z1 = ldparts.bbox(path)
    out = {"mm": [round((x1 - x0) * ldparts.LDU_MM, 3),
                  round((y1 - y0) * ldparts.LDU_MM, 3),
                  round((z1 - z0) * ldparts.LDU_MM, 3)]}
    for key, (iu, iv) in PLANES.items():
        # +Y POINTS DOWN IN LDRAW and down the page in Studio, so a plane carrying the part's HEIGHT
        # already agrees with the page and must NOT be flipped - flipping it stood every slope on its
        # head, putting the thin lip at the top and resting an inverted slope on two studs instead of
        # the one the crown geometry says it stands on. The depth planes are flipped, which is what
        # puts a tipped part's far side away from the viewer.
        lp = outline(number, iu, iv, iv != 1)
        if lp:
            out[key] = [[round(x, 3), round(y, 3)] for x, y in lp]
    return out


def parts_of(block_path):
    d = json.load(open(block_path, encoding="utf-8"))
    seen, order = set(), []
    for b in d.get("bricks", []):
        if b.get("id") not in seen:
            seen.add(b["id"])
            order.append(b["id"])
    return order


def main(argv):
    js = "--js" in argv
    argv = [a for a in argv if a != "--js"]
    if "--from" in argv:
        i = argv.index("--from")
        numbers = parts_of(argv[i + 1])
    else:
        numbers = argv
    if not numbers:
        print(__doc__)
        return 1
    table = {}
    for n in numbers:
        m = measure(n)
        if not m:
            print("  %-8s NOT FOUND" % n, file=sys.stderr)
            continue
        table[n] = m
        if not js:
            print("%-8s mm %-22s %s"
                  % (n, "x".join(str(v) for v in m["mm"]),
                     "  ".join(k + ":" + str(len(m[k])) for k in PLANES if k in m)))
    if js:
        rows = []
        for n in numbers:
            if n not in table:
                continue
            m = table[n]
            bits = ['mm:' + json.dumps(m["mm"], separators=(",", ","))]
            for k in PLANES:
                if k in m:
                    # QUOTED: "01" is a legacy octal literal unquoted, and a syntax error in strict mode
                    bits.append('"' + k + '":' + json.dumps(m[k], separators=(",", ",")))
            rows.append('  "%s":{%s}' % (n, ",".join(bits)))
        print("const BLOCK_SHAPES={\n" + ",\n".join(rows) + "\n};")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
