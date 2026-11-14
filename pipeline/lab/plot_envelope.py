# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Slide figure of the lunar-habitat envelope, need S1 (branch data-lab, experiment).

Reads data/pipeline/lab/numbers/envelope_lunar_habitat.json (hull, nominal
point, nearest tests) and the counted S1 tests of tests.csv through the
selection of envelope.py (imported, not rewritten). Writes
envelope_lunar_habitat_S1.svg with the standard library only (same inputs,
same bytes) and renders envelope_lunar_habitat_S1.png with the Playwright
Chromium of the machine at device scale factor 2; if rendering fails the SVG
is kept and a message is printed.

Every number drawn comes from the envelope output or tests.csv; tick values
are axis scale marks. Run: python3 pipeline/lab/plot_envelope.py
"""
import json
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import envelope  # noqa: E402
from numlib import ROOT, fail, frac  # noqa: E402

NEED = "S1"
SRC = ROOT / "data" / "pipeline" / "lab" / "numbers" / "envelope_lunar_habitat.json"
OUT_SVG = SRC.parent / "envelope_lunar_habitat_S1.svg"
OUT_PNG = SRC.parent / "envelope_lunar_habitat_S1.png"
W, H = 1600, 900
FONT = "DejaVu Sans, Liberation Sans, Arial, sans-serif"
INK, MUTED, GRID, POINT, HULL, ACCENT = "#1a1a1a", "#555555", "#e3e3e3", "#333333", "#6e6e6e", "#D55E00"
TITLE = "Lunar habitat, extinction conditions: recorded oxygen and pressure of the {n} counted tests"
CAPTION = ["Computed by the team's code from NASA PSI tables (code written with an AI assistant). "
           "All {n} tests are droplet tests of one investigation ({inv}, FLEX).",
           "The region describes where tests exist; it judges nothing. Not a NASA figure."]
# panels: pixel box and axis window (axis window values are scale choices, not data)
LEFT = {"box": (120, 150, 790, 735), "x": (10, 36), "y": (50, 320), "xt": range(10, 36, 5), "yt": range(50, 301, 50)}
ZOOM = {"box": (935, 150, 1545, 735), "x": (16, 36), "y": (69.3, 73.0), "xt": range(16, 37, 4), "yt": (69.5, 70, 70.5, 71, 71.5, 72, 72.5, 73)}


def f2(v):
    return f"{v:.2f}"


def sx(p, v):
    x0, _, x1, _ = p["box"]
    a, b = p["x"]
    return x0 + (float(v) - a) / (b - a) * (x1 - x0)


def sy(p, v):
    _, y0, _, y1 = p["box"]
    a, b = p["y"]
    return y1 - (float(v) - a) / (b - a) * (y1 - y0)


def text(x, y, s, size=18, fill=INK, anchor="start", weight="normal", extra=""):
    return (f'<text x="{f2(x)}" y="{f2(y)}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{extra}>{escape(s)}</text>')


def tick(v):
    return str(v) if not isinstance(v, float) or not v.is_integer() else str(int(v))


def axes(p, name, xlabel, ylabel):
    x0, y0, x1, y1 = p["box"]
    out = [f'<g id="{name}-axes">']
    for v in p["xt"]:
        X = sx(p, v)
        out.append(f'<line x1="{f2(X)}" y1="{y0}" x2="{f2(X)}" y2="{y1}" stroke="{GRID}" stroke-width="1"/>')
        out.append(text(X, y1 + 28, tick(v), 18, MUTED, "middle"))
    for v in p["yt"]:
        Y = sy(p, v)
        out.append(f'<line x1="{x0}" y1="{f2(Y)}" x2="{x1}" y2="{f2(Y)}" stroke="{GRID}" stroke-width="1"/>')
        out.append(text(x0 - 10, Y + 6, tick(v), 18, MUTED, "end"))
    out.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{MUTED}" stroke-width="1.2"/>')
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{MUTED}" stroke-width="1.2"/>')
    out.append(text((x0 + x1) / 2, y1 + 62, xlabel, 20, INK, "middle"))
    yc = (y0 + y1) / 2
    out.append(text(x0 - 72, yc, ylabel, 20, INK, "middle", extra=f' transform="rotate(-90 {f2(x0 - 72)} {f2(yc)})"'))
    out.append("</g>")
    return out


def diamond(x, y, r, fill):
    return (f'<path d="M{f2(x)},{f2(y - r)} L{f2(x + r)},{f2(y)} L{f2(x)},{f2(y + r)} L{f2(x - r)},{f2(y)} Z" '
            f'fill="{fill}" stroke="#ffffff" stroke-width="1.5"/>')


def panel(p, name, pts, hull, nom, r):
    x0, y0, x1, y1 = p["box"]
    out = [f'<clipPath id="{name}-clip"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>',
           f'<g clip-path="url(#{name}-clip)">']
    poly = " ".join(f"{f2(sx(p, a))},{f2(sy(p, b))}" for a, b in hull)
    out.append(f'<polygon points="{poly}" fill="#8a8a8a" fill-opacity="0.08" stroke="{HULL}" stroke-width="2" stroke-linejoin="round"/>')
    for a, b in pts:
        out.append(f'<circle cx="{f2(sx(p, a))}" cy="{f2(sy(p, b))}" r="{r}" fill="{POINT}" fill-opacity="0.38"/>')
    out.append(diamond(sx(p, nom[0]), sy(p, nom[1]), 11, ACCENT))
    out.append("</g>")
    return out


def sign(s):
    return s if s.startswith("-") or s == "0" else "+" + s


def build():
    env = json.loads(SRC.read_text(encoding="utf-8"))
    blk = next(b for b in env["needs"] if b["need_id"] == NEED)
    j = blk["nominal"]["joint"]
    tests = envelope.joint_tests(NEED)
    pts = [(t["o2_pct"], t["pressure_kpa"]) for t in tests]
    distinct = {(frac(a), frac(b)) for a, b in pts}
    if len(tests) != j["tests_with_both_recorded"] or len(distinct) != j["distinct_points"]:
        fail(f"plot: {len(tests)} tests / {len(distinct)} points differ from the envelope output")
    comp = j["composition"]
    if len(comp) != 1 or comp[0]["sample_geometry"] != "droplet" or comp[0]["tests"] != len(tests):
        fail("plot: the caption says all tests are droplet tests of one investigation; the envelope output says otherwise")
    inv = comp[0]["investigation_id"]
    nom_s = (env["scenario"]["nominal"]["o2_pct"], env["scenario"]["nominal"]["pressure_kpa"])
    nom = tuple(float(v) for v in nom_s)
    hull = [(a, b) for a, b in j["hull_vertices_ccw"]]
    hull_pts = {(frac(a), frac(b)) for a, b in hull}
    if not hull_pts <= distinct:
        fail("plot: a hull vertex is not a recorded point")
    n = len(tests)
    pos = j["nominal_position"]

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         text(60, 60, TITLE.format(n=n), 27, INK, weight="bold"),
         text(60, 100, f"Nominal point of the scenario: {nom_s[0]} % oxygen, {nom_s[1]} kPa. Position relative to the region: {pos}.", 20, MUTED)]
    # left panel: all tests
    lx0, ly0, lx1, ly1 = LEFT["box"]
    o.append(text(lx0, ly0 - 14, f"All {n} tests ({j['distinct_points']} distinct points)", 21, INK, weight="bold"))
    o += axes(LEFT, "left", "Ambient oxygen (% by volume)", "Pressure (kPa)")
    o += panel(LEFT, "left", pts, hull, nom, 4.5)
    zx0, zy1 = sx(LEFT, ZOOM["x"][0]), sy(LEFT, ZOOM["y"][0])
    zx1, zy0 = sx(LEFT, ZOOM["x"][1]), sy(LEFT, ZOOM["y"][1])
    o.append(f'<rect x="{f2(zx0)}" y="{f2(zy0 - 4)}" width="{f2(zx1 - zx0)}" height="{f2(zy1 - zy0 + 8)}" fill="none" '
             f'stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    o.append(text(zx1 - 2, zy0 - 14, "zoom at right", 17, INK, "end"))
    # legend (upper right of the left panel, where no test lies)
    lgx, lgy = lx1 - 285, ly0 + 32
    o.append(f'<circle cx="{lgx}" cy="{lgy}" r="6" fill="{POINT}" fill-opacity="0.38"/>')
    o.append(text(lgx + 18, lgy + 6, "recorded test (oxygen, pressure)", 17))
    o.append(f'<rect x="{lgx - 9}" y="{lgy + 22}" width="18" height="14" fill="#8a8a8a" fill-opacity="0.08" stroke="{HULL}" stroke-width="2"/>')
    o.append(text(lgx + 18, lgy + 35, "region (convex hull of the tests)", 17))
    o.append(diamond(lgx, lgy + 60, 9, ACCENT))
    o.append(text(lgx + 18, lgy + 66, "nominal point of the scenario", 17, ACCENT))
    nx, ny = sx(LEFT, nom[0]), sy(LEFT, nom[1])
    # right panel: zoom
    zbx0, zby0, zbx1, zby1 = ZOOM["box"]
    o.append(text(zbx0, zby0 - 14, f"Zoom: {ZOOM['x'][0]} to {ZOOM['x'][1]} % oxygen, {ZOOM['y'][0]} to {tick(ZOOM['y'][1])} kPa", 21, INK, weight="bold"))
    o += axes(ZOOM, "zoom", "Ambient oxygen (% by volume)", "Pressure (kPa)")
    o += panel(ZOOM, "zoom", pts, hull, nom, 5.5)
    znx, zny = sx(ZOOM, nom[0]), sy(ZOOM, nom[1])
    o.append(text(znx + 16, zny - 4, "nominal point", 18, ACCENT, weight="bold"))
    o.append(text(znx + 16, zny + 19, f"{nom_s[0]} %, {nom_s[1]} kPa", 18, ACCENT))
    # nearest tests (Pareto set of the envelope output), labels in the empty band under the region
    near = j["nearest_tests_pareto"]
    o.append(text(zbx0 + 240, zby0 + 50, "Circled: nearest tests, labelled", 16, MUTED))
    o.append(text(zbx0 + 240, zby0 + 72, "test minus nominal (oxygen in", 16, MUTED))
    o.append(text(zbx0 + 240, zby0 + 94, "percentage points, pressure in kPa)", 16, MUTED))
    order = sorted(near, key=lambda t: float(t["o2_pct"]))
    for k, t in enumerate(order):
        px, py = sx(ZOOM, t["o2_pct"]), sy(ZOOM, t["pressure_kpa"])
        ly = zby1 - 18 - 25 * k  # leftmost test on the bottom row: no leader crosses a label
        lab = f"{t['test_id']}: oxygen {sign(t['delta_o2_pct'])}, pressure {sign(t['delta_pressure_kpa'])} kPa"
        tx = max(zbx0 + 12, min(px - 10, zbx1 - 8 - 8.6 * len(lab)))
        o.append(f'<circle cx="{f2(px)}" cy="{f2(py)}" r="7.5" fill="none" stroke="{INK}" stroke-width="1.6"/>')
        o.append(f'<line x1="{f2(px)}" y1="{f2(py + 8)}" x2="{f2(tx + 12)}" y2="{f2(ly - 16)}" stroke="{INK}" stroke-width="1" stroke-opacity="0.6"/>')
        o.append(text(tx, ly, lab, 16, INK))
    # caption
    for k, line in enumerate(CAPTION):
        o.append(text(60, 836 + 30 * k, line.format(n=n, inv=inv), 18, INK))
    o.append("</svg>")
    return "\n".join(o) + "\n", (nx, ny)


RENDER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const [svgPath, pngPath, w, h] = process.argv.slice(1);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 2 });
  await page.goto('file://' + svgPath);
  await page.screenshot({ path: pngPath, clip: { x: 0, y: 0, width: +w, height: +h } });
  await browser.close();
})().catch(e => { console.error(String(e)); process.exit(1); });
"""


def render():
    try:
        r = subprocess.run(["node", "-e", RENDER_JS, str(OUT_SVG), str(OUT_PNG), str(W), str(H)],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        print("plot_envelope: PNG not rendered:", e)
        return False
    if r.returncode != 0:
        print("plot_envelope: PNG not rendered:", (r.stderr or r.stdout).strip()[:500])
        return False
    return True


def main():
    svg, _ = build()
    with open(OUT_SVG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    ok = render()
    print("plot_envelope: wrote", OUT_SVG, "and" if ok else "(no PNG)", OUT_PNG if ok else "")


if __name__ == "__main__":
    main()
