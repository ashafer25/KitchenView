"""Build the KitchenView GitHub Pages site from the Kitchen View page.

index.html     week overview (jumps to tonight's dinner on weekdays)
<id>.html      one page per dinner, with schema.org Recipe JSON-LD written into
               the page so Safari can offer its own cooking view.

Dish images are keyed by slug(meal name), so a photo or drawing carries over
whenever a dish comes back:
  img/photos/<slug>.jpg   a real photo (wins)            add with src/add_photo.py
  img/plates/<slug>.svg   a flat illustration (fallback) draw with src/plates.py

Usage: python3 build.py template.html out_dir
"""
import html, json, re, sys
from pathlib import Path

BASE_URL = "https://ashafer25.github.io/KitchenView/"

def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def raster(svg, jpg):
    """PNG/JPG copy of an illustration for the recipe data (Safari may not take SVG)."""
    if jpg.exists() and jpg.stat().st_mtime >= svg.stat().st_mtime:
        return True
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 380, "height": 380}, device_scale_factor=3)
            pg.goto(svg.resolve().as_uri())
            pg.screenshot(path=str(jpg), type="jpeg", quality=88)
            b.close()
        return True
    except Exception as e:
        print("could not rasterize", svg.name, "-", e)
        return False

src, out = Path(sys.argv[1]), Path(sys.argv[2])
page = src.read_text(encoding="utf-8")
out.mkdir(parents=True, exist_ok=True)

def swap(text, old, new):
    assert text.count(old) == 1, f"edit point not found once: {old[:60]}"
    return text.replace(old, new)

# Multi-page behavior for the app script.
page = swap(page, "    if (!r) { r = tonight ? tonight.id : 'week'; }",
    "    if (!r && window.KV_PAGES && !window.KV_START && tonight) { location.replace(tonight.id + '.html'); return; }\n"
    "    if (!r) { r = window.KV_START || (tonight ? tonight.id : 'week'); }")
page = swap(page, "    setLD(m || nextUp);", "    if (!window.KV_PAGES) setLD(m || nextUp);")
page = swap(page, "  function go(h){ if (route() === h) render(); else location.hash = h; }",
    "  function go(h){\n"
    "    if (window.KV_PAGES) {\n"
    "      if (h === 'week') { location.href = 'index.html#week'; return; }\n"
    "      if (byId(h) && h !== window.KV_START) { location.href = h + '.html'; return; }\n"
    "    }\n"
    "    if (route() === h) render(); else location.hash = h;\n"
    "  }")
# Drop the claude.ai-only viewport hint and the body-level title (each page gets its own in <head>).
page = page.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
page = swap(page, "<title>Kitchen View</title>\n", "")

plan = json.loads(re.search(r'<script type="application/json" id="plan-data">(.*?)</script>', page, re.S).group(1))

# Pick each dish's image: photo first, then illustration.
for m in plan["meals"]:
    s = slug(m["name"])
    photo, svg, jpg = out / "img/photos" / f"{s}.jpg", out / "img/plates" / f"{s}.svg", out / "img/plates" / f"{s}.jpg"
    m.pop("image", None); m.pop("_ld_image", None)
    if photo.exists():
        m["image"] = m["_ld_image"] = f"img/photos/{s}.jpg"
    elif svg.exists():
        m["image"] = f"img/plates/{s}.svg"
        m["_ld_image"] = f"img/plates/{s}.jpg" if raster(svg, jpg) else m["image"]
    else:
        print("no image yet for", s)
ld_images = {m["id"]: m.pop("_ld_image", None) for m in plan["meals"]}
data_json = json.dumps(plan, ensure_ascii=False, indent=2).replace("</", "<\\/")
page = re.sub(r'(<script type="application/json" id="plan-data">).*?(</script>)',
              lambda mm: mm.group(1) + "\n" + data_json + "\n" + mm.group(2), page, count=1, flags=re.S)

def ld(m):
    def steps():
        for j, s in enumerate(m["steps"]):
            t = s["text"]
            if s.get("timer") and "minute" not in t.lower():
                t += f" (about {s['timer']} minutes)"
            yield {"@type": "HowToStep", "position": j + 1, "text": t}
    return {
        "@context": "https://schema.org", "@type": "Recipe",
        "name": m["name"], "description": m["blurb"],
        "recipeCategory": "Dinner", "recipeCuisine": m["cuisine"],
        "suitableForDiet": "https://schema.org/GlutenFreeDiet",
        "keywords": "gluten-free, weeknight dinner",
        "prepTime": f"PT{m['prep']}M", "cookTime": f"PT{m['cook']}M",
        "totalTime": f"PT{m['prep'] + m['cook']}M",
        "recipeYield": f"{m['serves']} servings",
        "recipeIngredient": [g["qty"] + " " + g["item"] + (", " + g["note"] if g.get("note") else "") for g in m["ingredients"]],
        "recipeInstructions": list(steps()),
        **({"image": [BASE_URL + ld_images[m["id"]]]} if ld_images.get(m["id"]) else {}),
    }

def write(name, title, head_extra, boot):
    doc = page.replace("</head>", f"<title>{html.escape(title)}</title>\n{head_extra}</head>", 1)
    doc = doc.replace('<div id="app"', f"<script>{boot}</script>\n<div id=\"app\"", 1)
    (out / name).write_text(doc, encoding="utf-8")

# Remove last week's dinner pages that aren't in this week's plan.
keep = {"index.html"} | {f"{m['id']}.html" for m in plan["meals"]}
for old in out.glob("*.html"):
    if old.name not in keep:
        old.unlink()

write("index.html", "Kitchen View", "", "window.KV_PAGES=true;")
for m in plan["meals"]:
    data = json.dumps(ld(m), ensure_ascii=False, indent=1).replace("</", "<\\/")
    write(f"{m['id']}.html", m["name"],
          f'<script type="application/ld+json">\n{data}\n</script>\n',
          f"window.KV_PAGES=true;window.KV_START={json.dumps(m['id'])};")
(out / ".nojekyll").write_text("")
print("built", sorted(p.name for p in out.iterdir()))
