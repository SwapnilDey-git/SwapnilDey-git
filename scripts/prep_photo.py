"""
prep_photo.py
Prep a source photo for ASCII conversion:
- crop to head/shoulders
- grayscale
- CLAHE local contrast boost
- composite onto pure white
Run once per photo:  python scripts/prep_photo.py source-photo.jpg [x1 y1 x2 y2]
"""
import sys
import cv2
import numpy as np
from PIL import Image

def prep(src_path, box=None, out_path="source-prepped.png"):
    im = Image.open(src_path).convert("RGB")

    if box:
        im = im.crop(box)

    # grayscale
    gray = np.array(im.convert("L"))

    # CLAHE - contrast-limited adaptive histogram equalization
    # gives a flat, evenly-lit face real highlights and shadows
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # slight blur to reduce jpeg noise before ascii bucketing
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)

    out = Image.fromarray(enhanced).convert("L")
    out.save(out_path)
    print(f"wrote {out_path}  size={out.size}")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    box = None
    if len(sys.argv) > 5:
        box = tuple(int(x) for x in sys.argv[2:6])
    prep(src, box)
