"""Add a real photo for a dish: python3 src/add_photo.py <photo> "<Dish name>"

Crops to a centred square, resizes to 1200px, strips all metadata (EXIF/GPS),
and saves img/photos/<slug>.jpg, which then replaces the illustration.
"""
import re, sys
from pathlib import Path
from PIL import Image, ImageOps

src, name = Path(sys.argv[1]), sys.argv[2]
slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
out = Path(__file__).resolve().parent.parent / "img" / "photos" / f"{slug}.jpg"
out.parent.mkdir(parents=True, exist_ok=True)
im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
side = min(im.size)
im = im.crop(((im.width - side) // 2, (im.height - side) // 2, (im.width + side) // 2, (im.height + side) // 2))
im.resize((1200, 1200), Image.LANCZOS).save(out, "JPEG", quality=85)  # saved without EXIF
print("saved", out.relative_to(out.parent.parent.parent))
