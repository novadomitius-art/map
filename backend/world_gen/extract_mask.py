"""
Pixel-accurate land/water + terrain extraction from base_map.webp.

Outputs:
  backend/world_gen/extracted_mask.json
    {
      "land_polygons": [ [ [exterior ring], [hole], ... ], ... ]   # normalized 0..1 (by MAP_W)
      "terrain_grid":  { "cols": C, "rows": R, "cell": px, "data": [[...]] }  # terrain code per cell
    }
  backend/world_gen/debug_overlay.png   # visual verification

Terrain codes: 0=water 1=plains 2=forest 3=mountain 4=hills 5=coast 6=desert

Run from /app/backend:  python -m world_gen.extract_mask
"""
import json
import os
from pathlib import Path

import cv2
import numpy as np

MAP_PATH = "/app/frontend/public/maps/base_map.webp"
OUT_DIR = Path(__file__).parent
MAP_W = 2000.0

TERRAIN_NAMES = {0: "water", 1: "plains", 2: "forest", 3: "mountain", 4: "hills", 5: "coast", 6: "desert"}


def build_water_mask(gray):
    """Uniformly-dark, low-texture areas = ocean/lakes. Textured dark strokes on land are excluded."""
    h, w = gray.shape

    # Local standard deviation (texture measure)
    g32 = gray.astype(np.float32)
    mean = cv2.boxFilter(g32, -1, (15, 15))
    sq_mean = cv2.boxFilter(g32 * g32, -1, (15, 15))
    std = np.sqrt(np.maximum(sq_mean - mean * mean, 0))

    # Water candidate: dark AND locally smooth
    water = ((gray < 78) & (std < 26)).astype(np.uint8) * 255

    # Morphology: remove thin strokes (rivers/linework), then close gaps in open water
    water = cv2.morphologyEx(water, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    water = cv2.morphologyEx(water, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))

    # Keep only significant water bodies (drop residual dark forest blobs)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(water, connectivity=8)
    keep = np.zeros_like(water)
    min_area = 0.0006 * h * w  # ~2300 px
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            keep[labels == i] = 255

    # Remove tiny land specks fully inside water (noise) by inverting & filtering
    land = cv2.bitwise_not(keep)
    n2, l2, s2, _ = cv2.connectedComponentsWithStats(land, connectivity=8)
    min_land = 0.0004 * h * w
    for i in range(1, n2):
        if s2[i, cv2.CC_STAT_AREA] < min_land:
            keep[l2 == i] = 255  # absorb speck into water

    return keep


def land_polygons_from_mask(water):
    """Land = NOT water. Extract contours with holes, normalized by MAP_W."""
    land = cv2.bitwise_not(water)
    contours, hierarchy = cv2.findContours(land, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    hierarchy = hierarchy[0] if hierarchy is not None else []

    polys = []  # list of [exterior, hole, hole...]
    idx_map = {}
    for i, cnt in enumerate(contours):
        if hierarchy[i][3] == -1:  # top-level: exterior ring of a land blob
            if cv2.contourArea(cnt) < 400:
                continue
            approx = cv2.approxPolyDP(cnt, 1.8, True)
            if len(approx) < 3:
                continue
            ring = [[float(p[0][0]) / MAP_W, float(p[0][1]) / MAP_W] for p in approx]
            idx_map[i] = len(polys)
            polys.append([ring])
    for i, cnt in enumerate(contours):
        parent = hierarchy[i][3]
        if parent != -1 and parent in idx_map:  # hole (inland sea / lake)
            if cv2.contourArea(cnt) < 900:
                continue
            approx = cv2.approxPolyDP(cnt, 1.8, True)
            if len(approx) < 3:
                continue
            ring = [[float(p[0][0]) / MAP_W, float(p[0][1]) / MAP_W] for p in approx]
            polys[idx_map[parent]].append(ring)
    return polys


def classify_terrain(gray, water, cell=60):
    """Grid classification calibrated on this artwork:
    - mountain: dark line-art WITH large bright faces between strokes
    - forest:   uniform dense dark canopy texture, no big bright patches
    - plains:   mostly light open parchment
    - hills:    scattered glyphs on open ground
    - desert:   very light + smooth
    """
    h, w = gray.shape
    dark = (gray < 105).astype(np.uint8)
    bright = (gray > 115).astype(np.uint8)
    nb, lb, sb, _ = cv2.connectedComponentsWithStats(bright, connectivity=8)
    big_bright = np.zeros_like(bright)
    for i in range(1, nb):
        if sb[i, cv2.CC_STAT_AREA] > 400:
            big_bright[lb == i] = 1

    rows = h // cell
    cols = w // cell
    grid = np.zeros((rows, cols), np.uint8)
    strong = np.zeros((rows, cols), np.uint8)  # 1 = high-confidence, exempt from smoothing
    g32 = gray.astype(np.float32)

    for r in range(rows):
        for c in range(cols):
            ys, xs = r * cell, c * cell
            wblk = water[ys:ys + cell, xs:xs + cell]
            if np.count_nonzero(wblk) / wblk.size > 0.5:
                grid[r, c] = 0
                strong[r, c] = 1
                continue
            d = dark[ys:ys + cell, xs:xs + cell].mean()
            fb = big_bright[ys:ys + cell, xs:xs + cell].mean()
            mean_l = g32[ys:ys + cell, xs:xs + cell].mean()
            score = 2.5 * fb - d

            if d < 0.07:
                grid[r, c] = 6 if (mean_l > 150 and fb > 0.8) else 1  # desert / plains
                strong[r, c] = 1 if d < 0.04 else 0
            elif d < 0.16:
                grid[r, c] = 4  # hills (scattered glyphs on open ground)
            elif score > -0.25:
                grid[r, c] = 3  # mountain (bright faces amid dark strokes)
                strong[r, c] = 1 if score > 0.0 else 0
            else:
                grid[r, c] = 2  # forest (uniform dense canopy)
                strong[r, c] = 1 if score < -0.45 else 0

    # conservative smoothing: flip a cell only when neighbors strongly agree,
    # never flip high-confidence cells
    for _ in range(2):
        out = grid.copy()
        for r in range(rows):
            for c in range(cols):
                if grid[r, c] == 0 or strong[r, c]:
                    continue
                r0, r1 = max(0, r - 1), min(rows, r + 2)
                c0, c1 = max(0, c - 1), min(cols, c + 2)
                blk = grid[r0:r1, c0:c1]
                vals, counts = np.unique(blk[blk != 0], return_counts=True)
                if len(vals):
                    best = vals[np.argmax(counts)]
                    # require >= 60% consensus to overwrite current value
                    if best != grid[r, c] and counts.max() >= 0.6 * (blk != 0).sum():
                        out[r, c] = best
        grid = out

    # coast pass: land cell adjacent to water (and not mountain) -> coast
    water_cells = grid == 0
    dil = cv2.dilate(water_cells.astype(np.uint8), np.ones((3, 3), np.uint8))
    coast = (dil == 1) & (grid != 0) & (grid != 3)
    grid[coast] = 5

    return grid, cell


def render_debug(img, water, land_polys, grid, cell):
    dbg = img.copy()
    tint = {1: (60, 160, 190), 2: (60, 140, 60), 3: (140, 100, 160), 4: (60, 190, 230), 6: (80, 210, 240), 5: (200, 160, 60)}
    overlay = dbg.copy()
    rows, cols = grid.shape
    for r in range(rows):
        for c in range(cols):
            t = grid[r, c]
            if t in tint:
                cv2.rectangle(overlay, (c * cell, r * cell), ((c + 1) * cell, (r + 1) * cell), tint[t], -1)
    dbg = cv2.addWeighted(overlay, 0.35, dbg, 0.65, 0)
    # land contours in red
    for poly in land_polys:
        for ring in poly:
            pts = np.array([[int(x * MAP_W), int(y * MAP_W)] for x, y in ring], np.int32)
            cv2.polylines(dbg, [pts], True, (0, 0, 255), 3)
    cv2.imwrite(str(OUT_DIR / "debug_overlay.png"), dbg, [cv2.IMWRITE_PNG_COMPRESSION, 7])


def main():
    img = cv2.imread(MAP_PATH)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    water = build_water_mask(gray)
    land_polys = land_polygons_from_mask(water)
    grid, cell = classify_terrain(gray, water)

    out = {
        "land_polygons": land_polys,
        "terrain_grid": {"rows": int(grid.shape[0]), "cols": int(grid.shape[1]), "cell": cell,
                          "map_w": int(MAP_W), "data": grid.tolist()},
        "terrain_names": TERRAIN_NAMES,
    }
    (OUT_DIR / "extracted_mask.json").write_text(json.dumps(out))
    render_debug(img, water, land_polys, grid, cell)

    land_frac = 1 - np.count_nonzero(water) / water.size
    from collections import Counter
    cnt = Counter(int(x) for x in grid.flatten())
    print(f"land fraction: {land_frac:.3f}, polygons: {len(land_polys)}")
    print("terrain cells:", {TERRAIN_NAMES[k]: v for k, v in sorted(cnt.items())})


if __name__ == "__main__":
    main()
