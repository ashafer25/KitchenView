"""Flat plate illustrations for the Kitchen View.

Each dish gets img/plates/<slug>.svg (380x380, top-down, flat colours, no text).
Real photos in img/photos/<slug>.jpg take priority over these at build time.

Usage:  python3 src/plates.py            # (re)draw every dish in DISHES
        python3 src/plates.py <slug>     # draw one

To add a dish: write a function that returns a list of SVG strings using the
helpers below, register it in DISHES under the dish's slug (see slug() in
build.py), and run this script. Keep the house style: counter + white plate,
3-6 recognisable components, food covering ~60% of the plate, no text.
"""
import math, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "img" / "plates"


def rot(x, y, deg):
    return f'transform="rotate({deg:.0f} {x:.0f} {y:.0f})"'


def scatter(rng, n, cx, cy, rx, ry, min_gap=18, tries=400):
    """Points inside an ellipse, loosely spaced."""
    pts = []
    for _ in range(tries):
        if len(pts) >= n:
            break
        a, r = rng.uniform(0, 2 * math.pi), math.sqrt(rng.random())
        x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        if all((x - px) ** 2 + (y - py) ** 2 >= min_gap ** 2 for px, py in pts):
            pts.append((x, y))
    return pts


# ---- scene -----------------------------------------------------------------

def canvas(parts, counter="#E7E2D8", speck="#DCD5C8", napkin="#C9B79C", seed=1):
    rng = random.Random(seed)
    dots = "".join(f'<circle cx="{rng.uniform(8,372):.0f}" cy="{rng.uniform(8,372):.0f}" r="{rng.choice([2,2,3])}"/>' for _ in range(14))
    nap = (f'<g {rot(335,310,18)}><rect x="300" y="250" width="70" height="130" rx="8" fill="{napkin}"/>'
           f'<g stroke="#00000018" stroke-width="2"><line x1="308" y1="275" x2="362" y2="275"/><line x1="308" y1="290" x2="362" y2="290"/></g></g>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 380" width="380" height="380">'
            f'<rect width="380" height="380" fill="{counter}"/><g fill="{speck}">{dots}</g>{nap}'
            + "".join(parts) + "</svg>")


def plate(cx=188, cy=190, r=150):
    return (f'<circle cx="{cx+4}" cy="{cy+6}" r="{r+2}" fill="#CFC8BB"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FBFAF6"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.75:.0f}" fill="#F2EFE7"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#E3DED3" stroke-width="2"/>')


def bowl(cx=188, cy=190, r=148, inner="#F4F1EA", rim="#2F3A45"):
    return (f'<circle cx="{cx+4}" cy="{cy+6}" r="{r+2}" fill="#C9C1B3"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{rim}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r-12}" fill="{inner}"/>')


def skillet(cx=180, cy=196, r=140):
    return (f'<rect x="{cx+r-10}" y="{cy-14}" width="80" height="28" rx="12" fill="#2B2B2B" {rot(cx, cy, -35)}/>'
            f'<circle cx="{cx+4}" cy="{cy+6}" r="{r+2}" fill="#B8B0A2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#2E2E2E"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r-12}" fill="#3A3A3A"/>')


def pool(cx, cy, rx, ry, color, opacity=0.55):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{color}" opacity="{opacity}"/>'


# ---- components ------------------------------------------------------------

def penne(x, y, a):
    ridges = "".join(f'<line x1="{x-13+i*9:.0f}" y1="{y-6:.0f}" x2="{x-17+i*9:.0f}" y2="{y+6:.0f}"/>' for i in range(4))
    return (f'<g {rot(x,y,a)} fill="#E7B65C" stroke="#C99234" stroke-width="1">'
            f'<rect x="{x-23:.0f}" y="{y-8:.0f}" width="46" height="16" rx="6"/>{ridges}</g>')


def cube(x, y, a, fill="#E8813A", edge="#C4621F", hi="#F4A867", s=20):
    return (f'<g {rot(x,y,a)}><rect x="{x-s/2:.0f}" y="{y-s/2:.0f}" width="{s}" height="{s*0.92:.0f}" rx="4" fill="{fill}" stroke="{edge}"/>'
            f'<rect x="{x-s/2+4:.0f}" y="{y-s/2+3:.0f}" width="{s*0.35:.0f}" height="4" rx="2" fill="{hi}"/></g>')


def leaf(x, y, a, length=46, fill="#4F6B3A", edge="#33482A"):
    h = length / 2
    return (f'<g {rot(x,y,a)} fill="{fill}" stroke="{edge}" stroke-width="1">'
            f'<path d="M{x-h:.0f} {y:.0f} Q{x:.0f} {y-length*0.35:.0f} {x+h:.0f} {y:.0f} Q{x:.0f} {y+length*0.35:.0f} {x-h:.0f} {y:.0f}Z"/>'
            f'<line x1="{x-h+2:.0f}" y1="{y:.0f}" x2="{x+h-2:.0f}" y2="{y:.0f}"/></g>')


def shaving(x, y, a):
    return f'<path {rot(x,y,a)} d="M{x-5:.0f} {y-2:.0f} l10 -3 l4 6 l-11 3z" fill="#FFF6DA" stroke="#E2D3A6" stroke-width=".8"/>'


def flecks(rng, n, cx, cy, rx, ry, color="#3B3229", r=1.3):
    return "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{color}"/>' for x, y in scatter(rng, n, cx, cy, rx, ry, 8))


def bean(x, y, a, length=58):
    h = length / 2
    return (f'<g {rot(x,y,a)}><rect x="{x-h:.0f}" y="{y-4:.0f}" width="{length}" height="8" rx="4" fill="#4E8A3A" stroke="#36692A"/>'
            f'<line x1="{x-h+6:.0f}" y1="{y-1:.0f}" x2="{x+h-8:.0f}" y2="{y-1:.0f}" stroke="#78B05E" stroke-width="1.5"/></g>')


def potato(x, y, a, r=17):
    return (f'<g {rot(x,y,a)}><ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r}" ry="{r*0.8:.0f}" fill="#D9A441" stroke="#A9741F"/>'
            f'<ellipse cx="{x+2:.0f}" cy="{y+1:.0f}" rx="{r*0.7:.0f}" ry="{r*0.52:.0f}" fill="#F2D27E"/>'
            f'<ellipse cx="{x-r*0.35:.0f}" cy="{y-r*0.25:.0f}" rx="{r*0.25:.0f}" ry="{r*0.12:.0f}" fill="#B9822C" opacity=".6"/></g>')


def fillet(x, y, a, w=118, h=66, top="#F6F0E4", sear="#D9A35A", edge="#B88743", flakes="#E8DCC6"):
    lines = "".join(f'<path d="M{x-w/2+18+i*20:.0f} {y-h/2+8:.0f} q6 {h/2-8:.0f} 0 {h-16:.0f}" fill="none" stroke="{flakes}" stroke-width="2"/>' for i in range(5))
    return (f'<g {rot(x,y,a)}><rect x="{x-w/2:.0f}" y="{y-h/2:.0f}" width="{w}" height="{h}" rx="{h/2.4:.0f}" fill="{sear}" stroke="{edge}"/>'
            f'<rect x="{x-w/2+7:.0f}" y="{y-h/2+6:.0f}" width="{w-14}" height="{h-12}" rx="{h/3:.0f}" fill="{top}"/>{lines}</g>')


def caper(x, y):
    return f'<circle cx="{x:.0f}" cy="{y:.0f}" r="3.2" fill="#7E8B3A" stroke="#5B6628"/>'


def lemon_wedge(x, y, a):
    return (f'<g {rot(x,y,a)}><path d="M{x-24:.0f} {y:.0f} A24 24 0 0 0 {x+24:.0f} {y:.0f}Z" fill="#F2D23A" stroke="#C9A71C"/>'
            f'<path d="M{x-18:.0f} {y+1:.0f} A18 18 0 0 0 {x+18:.0f} {y+1:.0f}Z" fill="#FBEA8A"/>'
            + "".join(f'<line x1="{x:.0f}" y1="{y+1:.0f}" x2="{x+17*math.cos(math.radians(t)):.0f}" y2="{y+1+17*math.sin(math.radians(t)):.0f}" stroke="#F2D23A" stroke-width="1.5"/>' for t in (30, 70, 110, 150))
            + "</g>")


def brat(x, y, a, length=96):
    h = length / 2
    marks = "".join(f'<line x1="{x-h+18+i*18:.0f}" y1="{y-9:.0f}" x2="{x-h+10+i*18:.0f}" y2="{y+9:.0f}" stroke="#5A3A22" stroke-width="3" stroke-linecap="round"/>' for i in range(4))
    return (f'<g {rot(x,y,a)}><rect x="{x-h:.0f}" y="{y-13:.0f}" width="{length}" height="26" rx="13" fill="#A8683C" stroke="#7A4626"/>'
            f'<rect x="{x-h+8:.0f}" y="{y-9:.0f}" width="{length-16}" height="6" rx="3" fill="#C78955"/>{marks}</g>')


def apple_wedge(x, y, a):
    return (f'<g {rot(x,y,a)}><path d="M{x-22:.0f} {y:.0f} Q{x:.0f} {y-22:.0f} {x+22:.0f} {y:.0f}Z" fill="#B8322C"/>'
            f'<path d="M{x-18:.0f} {y-1:.0f} Q{x:.0f} {y-17:.0f} {x+18:.0f} {y-1:.0f}Z" fill="#F3DDA0"/>'
            f'<ellipse cx="{x:.0f}" cy="{y-6:.0f}" rx="5" ry="2.5" fill="#D9B86A"/></g>')


def onion_wedge(x, y, a):
    return (f'<g {rot(x,y,a)} fill="none" stroke-linecap="round">'
            f'<path d="M{x-16:.0f} {y+6:.0f} Q{x:.0f} {y-18:.0f} {x+16:.0f} {y+6:.0f}" stroke="#7B2D5C" stroke-width="5"/>'
            f'<path d="M{x-9:.0f} {y+6:.0f} Q{x:.0f} {y-8:.0f} {x+9:.0f} {y+6:.0f}" stroke="#B66A97" stroke-width="4"/></g>')


def sprout(x, y, a, r=13):
    return (f'<g {rot(x,y,a)}><circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#5E8A35" stroke="#41652A"/>'
            f'<path d="M{x-r+3:.0f} {y:.0f} Q{x:.0f} {y-r+4:.0f} {x+r-3:.0f} {y:.0f} Q{x:.0f} {y+r-4:.0f} {x-r+3:.0f} {y:.0f}Z" fill="#B9D27A"/>'
            f'<path d="M{x+r-6:.0f} {y-r+4:.0f} a{r} {r} 0 0 1 4 8" fill="none" stroke="#3E2A16" stroke-width="3"/></g>')


def thyme(x, y, a):
    leaves = "".join(f'<ellipse cx="{x-14+i*7:.0f}" cy="{y + (-3 if i % 2 else 3):.0f}" rx="3" ry="1.6" fill="#6E8B4E"/>' for i in range(5))
    return f'<g {rot(x,y,a)}><line x1="{x-18:.0f}" y1="{y:.0f}" x2="{x+18:.0f}" y2="{y:.0f}" stroke="#7A6A48" stroke-width="1.2"/>{leaves}</g>'


def rice(rng, cx, cy, rx, ry, n=260):
    grains = "".join(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="4" ry="1.8" fill="#FFFFFF" stroke="#E4DFD3" stroke-width=".6" {rot(x,y,rng.uniform(0,180))}/>' for x, y in scatter(rng, n, cx, cy, rx, ry, 5.5, 4000))
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx+6}" ry="{ry+6}" fill="#F7F4EC"/>{grains}'


def bokchoy(x, y, a):
    return (f'<g {rot(x,y,a)}><path d="M{x-34:.0f} {y:.0f} Q{x:.0f} {y-24:.0f} {x+30:.0f} {y-4:.0f} L{x+30:.0f} {y+4:.0f} Q{x:.0f} {y+24:.0f} {x-34:.0f} {y:.0f}Z" fill="#3F7A36" stroke="#2C5A26"/>'
            f'<path d="M{x-4:.0f} {y:.0f} L{x+34:.0f} {y-5:.0f} L{x+34:.0f} {y+5:.0f}Z" fill="#DDEBC2" stroke="#B9CC97"/></g>')


def cucumber(x, y, r=11):
    return (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#3E6B2E"/><circle cx="{x:.0f}" cy="{y:.0f}" r="{r-2}" fill="#D7EAB6"/>'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r-6}" fill="#C2DB98"/>')


def scallion(x, y):
    return f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4" fill="none" stroke="#5FA041" stroke-width="2.4"/>'


def sesame(rng, n, cx, cy, rx, ry):
    return "".join(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="1.8" ry="1" fill="#F6EBC8" {rot(x,y,rng.uniform(0,180))}/>' for x, y in scatter(rng, n, cx, cy, rx, ry, 6))


# ---- dishes ------------------------------------------------------------------

def halibut():
    rng = random.Random(4)
    p = [plate()]
    p += [potato(x, y, rng.uniform(0, 180)) for x, y in [(110, 150), (132, 120), (100, 186), (128, 205), (148, 170), (160, 140), (122, 238), (155, 228)]]
    p += [bean(240 + rng.uniform(-6, 6), 228 + i * 9, rng.uniform(-24, -12)) for i in range(-3, 5)]
    p.append(fillet(222, 150, -12))
    p.append(pool(222, 150, 50, 22, "#C98A2E", .35))
    p += [caper(x, y) for x, y in [(200, 140), (214, 156), (236, 144), (246, 160), (226, 168), (208, 162)]]
    p.append(flecks(rng, 18, 222, 150, 50, 22, "#3E7A2C", 2))
    p.append(lemon_wedge(178, 268, 15))
    return canvas(p, seed=4)


def butternut_pasta():
    rng = random.Random(2)
    p = [plate(), pool(188, 194, 92, 84, "#E9C27A")]
    p += [penne(x, y, rng.uniform(-90, 90)) for x, y in scatter(rng, 13, 188, 192, 80, 72, 30)]
    p += [cube(x, y, rng.uniform(0, 45)) for x, y in scatter(rng, 10, 190, 192, 78, 70, 26)]
    p += [leaf(x, y, rng.uniform(-90, 90), 40) for x, y in scatter(rng, 5, 188, 192, 60, 56, 34)]
    p += [shaving(x, y, rng.uniform(0, 90)) for x, y in scatter(rng, 8, 190, 190, 70, 64, 18)]
    p.append(flecks(rng, 10, 190, 192, 74, 66))
    return canvas(p, seed=2)


def beyond_brat_sheet_pan():
    rng = random.Random(3)
    p = [plate()]
    p += [brat(200, 150, -18), brat(190, 196, -12)]
    p += [sprout(x, y, rng.uniform(0, 360)) for x, y in [(110, 160), (128, 196), (108, 226), (150, 248), (240, 250), (270, 220), (126, 130)]]
    p += [apple_wedge(x, y, rng.uniform(-40, 40)) for x, y in [(160, 252), (205, 258), (262, 172), (276, 132)]]
    p += [onion_wedge(x, y, rng.uniform(-60, 60)) for x, y in [(118, 262), (232, 112), (290, 196), (175, 108)]]
    p += [thyme(x, y, rng.uniform(0, 180)) for x, y in [(150, 152), (250, 224)]]
    p.append(pool(196, 174, 60, 34, "#C98A2E", .25))
    return canvas(p, seed=3)


def salmon_rice_bowl():
    rng = random.Random(5)
    p = [bowl(), rice(rng, 188, 190, 112, 112)]
    p.append(fillet(196, 150, -20, w=104, h=58, top="#E9895A", sear="#9E4A23", edge="#7A3518", flakes="#F2B08C"))
    p.append(pool(196, 150, 46, 20, "#6B3A1C", .3))
    p += [bokchoy(x, y, a) for x, y, a in [(120, 214, -30), (150, 248, -10)]]
    p += [cucumber(x, y) for x, y in [(240, 216), (262, 236), (236, 244), (258, 206), (214, 236)]]
    p += [scallion(x, y) for x, y in scatter(rng, 9, 196, 160, 60, 36, 12)]
    p.append(sesame(rng, 22, 196, 160, 62, 38))
    return canvas(p, seed=5)


def shepherds_pie():
    rng = random.Random(6)
    p = [skillet()]
    p.append('<circle cx="180" cy="196" r="126" fill="#6B3E2A"/>')
    p += [f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="#7FB04E"/>' for x, y in scatter(rng, 10, 180, 196, 122, 122, 20) if (x - 180) ** 2 + (y - 196) ** 2 > 112 ** 2]
    p.append('<circle cx="180" cy="196" r="112" fill="#F3E3B8"/>')
    for x, y in scatter(rng, 26, 180, 196, 98, 98, 30):
        p.append(f'<path d="M{x-14:.0f} {y+6:.0f} q14 -18 28 0" fill="none" stroke="#D9A64B" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M{x-10:.0f} {y+8:.0f} q10 -12 20 0" fill="none" stroke="#FFF4D6" stroke-width="3" stroke-linecap="round"/>')
    p += [f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="9" ry="5" fill="#C98A2E" opacity=".55"/>' for x, y in scatter(rng, 8, 180, 196, 90, 90, 40)]
    p.append(flecks(rng, 14, 180, 196, 96, 96, "#4E7A34", 1.8))
    return canvas(p, seed=6)


DISHES = {
    "halibut-with-lemon-caper-butter-crispy-potatoes": halibut,
    "butternut-squash-sage-brown-butter-pasta": butternut_pasta,
    "beyond-brat-sheet-pan-with-apples-onions-brussels-sprouts": beyond_brat_sheet_pan,
    "ginger-sesame-salmon-rice-bowls": salmon_rice_bowl,
    "mushroom-lentil-shepherd-s-pie": shepherds_pie,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for s in (sys.argv[1:] or DISHES):
        (OUT / f"{s}.svg").write_text(DISHES[s](), encoding="utf-8")
        print("drew", s)
