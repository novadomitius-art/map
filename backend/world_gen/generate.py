"""
World generator V2 for Kelvaros.

- Dense jittered-lattice Voronoi (~1300 provinces) clipped to the
  pixel-extracted land mask of base_map.webp.
- Nations claim cells via tier-weighted nearest-anchor assignment
  (empires project power further than counties).
- Procedural vassals deepen the feudal hierarchy (realm_gen.py).
- Terrain per province from the pixel-derived terrain grid.
- Settlements: authored anchors + procedural villages/towns/castles.
- Ports snapped to the true land-water boundary.

Run once from /app/backend:
    python -m world_gen.generate
"""
import json
import math
import random
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Polygon, MultiPoint, Point, box
from shapely.ops import voronoi_diagram, unary_union, nearest_points
from shapely.validation import make_valid


from world_gen.catalog import (
    CONTINENT_NAME, CURRENT_YEAR, CONTINENT_LORE,
    RELIGIONS, NATIONS, RELATIONS,
)
from world_gen.realm_gen import gen_vassals, gen_settlements, compute_influence, make_name

EXTRACT_PATH = Path(__file__).parent / "extracted_mask.json"

LATTICE_SPACING = 0.024      # ~1300 land cells
JITTER = 0.38                # fraction of spacing
SIMPLIFY_TOL = 0.0008

TIER_WEIGHT = {
    "empire": 1.75,
    "kingdom": 1.35, "sultanate": 1.35, "theocracy": 1.30, "confederacy": 1.30,
    "khanate": 1.25, "free_kingdom": 1.15, "grand_duchy": 1.12,
    "merchant_republic": 1.10, "tribal_kingdom": 1.10, "federation": 1.10,
}
VASSAL_WEIGHT = 0.72


def load_extracted():
    return json.loads(EXTRACT_PATH.read_text())


def build_land_mask(extracted):
    polys = []
    for rings in extracted["land_polygons"]:
        try:
            p = make_valid(Polygon(rings[0], rings[1:]))
            if not p.is_empty:
                polys.append(p)
        except Exception:
            continue
    return make_valid(unary_union(polys))


class TerrainGrid:
    def __init__(self, extracted):
        tg = extracted["terrain_grid"]
        self.data = tg["data"]
        self.cell = tg["cell"]
        self.map_w = tg["map_w"]
        self.rows = tg["rows"]
        self.cols = tg["cols"]
        self.names = {int(k): v for k, v in extracted["terrain_names"].items()}

    def code_at(self, x, y):
        c = min(self.cols - 1, max(0, int(x * self.map_w // self.cell)))
        r = min(self.rows - 1, max(0, int(y * self.map_w // self.cell)))
        return self.data[r][c]

    def majority_terrain(self, geom):
        from collections import Counter
        step = self.cell / self.map_w
        minx, miny, maxx, maxy = geom.bounds
        r0 = max(0, int(miny / step)); r1 = min(self.rows - 1, int(maxy / step))
        c0 = max(0, int(minx / step)); c1 = min(self.cols - 1, int(maxx / step))
        cnt = Counter()
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                code = self.data[r][c]
                if code == 0:
                    continue
                if geom.contains(Point((c + 0.5) * step, (r + 0.5) * step)):
                    cnt[code] += 1
        if not cnt:
            rp = geom.representative_point()
            code = self.code_at(rp.x, rp.y)
            return self.names.get(code, "coast") if code != 0 else "coast"
        return self.names[cnt.most_common(1)[0][0]]


def poly_to_rings(geom):
    if geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        polys = [geom]
    elif geom.geom_type == "MultiPolygon":
        polys = list(geom.geoms)
    else:
        polys = []
        for g in getattr(geom, "geoms", []):
            if g.geom_type == "Polygon":
                polys.append(g)
            elif g.geom_type == "MultiPolygon":
                polys.extend(list(g.geoms))
    out = []
    for p in polys:
        if p.is_empty or p.area < 1e-8:
            continue
        rings = [[list(c) for c in p.exterior.coords]]
        for interior in p.interiors:
            rings.append([list(c) for c in interior.coords])
        out.append(rings)
    return out


def sample_inside(geom, rng, tries=40):
    minx, miny, maxx, maxy = geom.bounds
    for _ in range(tries):
        x = rng.uniform(minx, maxx)
        y = rng.uniform(miny, maxy)
        if geom.contains(Point(x, y)):
            return (x, y)
    rp = geom.representative_point()
    return (rp.x, rp.y)


def generate_world():
    rng = random.Random(892)
    extracted = load_extracted()
    land = build_land_mask(extracted)
    tgrid = TerrainGrid(extracted)
    land_inner = make_valid(land.buffer(-0.005))
    # True sea/lake boundary EXCLUDING the map frame: the image edges are not
    # water, so ports must never snap there.
    max_y_frame = 1923.0 / 2000.0
    frame_inner = box(0.012, 0.012, 1.0 - 0.012, max_y_frame - 0.012)
    water_edge = land.boundary.intersection(frame_inner)

    # ---- 1) All nations: authored + procedural vassals -------------------
    all_nations = [dict(n) for n in NATIONS] + gen_vassals(NATIONS, rng)

    # Snap every anchor onto land.
    def snap(x, y):
        p = Point(x, y)
        if land_inner.contains(p):
            return (x, y)
        target = land_inner if not land_inner.is_empty else land
        q, _ = nearest_points(target, p)
        return (q.x, q.y)

    anchor_xy = []
    anchor_nation = []
    anchor_weight = []
    for n in all_nations:
        w = VASSAL_WEIGHT if n.get("overlord") else TIER_WEIGHT.get(n["tier"], 1.0)
        snapped = []
        for (sx, sy) in n["seed_points"]:
            sx, sy = snap(sx, sy)
            snapped.append((sx, sy))
            anchor_xy.append((sx, sy))
            anchor_nation.append(n["id"])
            anchor_weight.append(w)
        n["seed_points"] = snapped

    anchor_xy = np.array(anchor_xy)
    anchor_weight = np.array(anchor_weight)

    # ---- 2) Dense jittered lattice over land -----------------------------
    max_y = 1923.0 / 2000.0
    pts = []
    s = LATTICE_SPACING
    row = 0
    y = s / 2
    while y < max_y:
        x = s / 2 + (s / 2 if row % 2 else 0)
        while x < 1.0:
            jx = x + rng.uniform(-JITTER, JITTER) * s
            jy = y + rng.uniform(-JITTER, JITTER) * s
            if land.contains(Point(jx, jy)):
                pts.append((jx, jy))
            x += s
        y += s * 0.93
        row += 1
    print(f"lattice points on land: {len(pts)}")

    # ---- 3) Voronoi + cell->seed matching via KDTree ----------------------
    envelope = box(-0.05, -0.05, 1.05, max_y + 0.05)
    vor = voronoi_diagram(MultiPoint(pts), envelope=envelope)
    kd = cKDTree(np.array(pts))

    # ---- 4) Assign each cell to a nation (tier-weighted nearest anchor) ---
    provinces = []
    prov_geoms = {}
    nation_cells = {n["id"]: [] for n in all_nations}
    cell_of_point = {}
    prov_i = 0
    for cell in vor.geoms:
        cell = make_valid(cell)
        rp = cell.representative_point()
        _, seed_idx = kd.query([rp.x, rp.y])
        cx, cy = pts[seed_idx]
        clipped = make_valid(cell.intersection(land))
        if clipped.is_empty or clipped.area < 1e-6:
            continue
        clipped = make_valid(clipped.simplify(SIMPLIFY_TOL, preserve_topology=True))
        if clipped.is_empty or clipped.area < 1e-6:
            continue
        d = np.sqrt(((anchor_xy - np.array([cx, cy])) ** 2).sum(axis=1))
        scores = d / anchor_weight
        nid = anchor_nation[int(np.argmin(scores))]
        pid = f"p_{prov_i:04d}"
        provinces.append(dict(id=pid, nation_id=nid, terrain=None,
                              seed=[round(cx, 5), round(cy, 5)], polygons=None,
                              _geom=clipped))
        prov_geoms[pid] = clipped
        nation_cells[nid].append(pid)
        cell_of_point[(round(cx, 5), round(cy, 5))] = pid
        prov_i += 1

    # ---- 5) Guarantee every nation owns at least one cell -----------------
    prov_by_id = {p["id"]: p for p in provinces}
    for n in all_nations:
        if nation_cells[n["id"]]:
            continue
        ax, ay = n["seed_points"][0]
        # nearest cells whose owner has >1 cell (never orphan another nation)
        order = sorted(provinces, key=lambda p: (p["seed"][0] - ax) ** 2 + (p["seed"][1] - ay) ** 2)
        for p in order:
            if len(nation_cells[p["nation_id"]]) > 1:
                nation_cells[p["nation_id"]].remove(p["id"])
                p["nation_id"] = n["id"]
                nation_cells[n["id"]].append(p["id"])
                break

    # ---- 6) Terrain + province names --------------------------------------
    used_prov_names = set()
    nation_by_id = {n["id"]: n for n in all_nations}
    for p in provinces:
        p["terrain"] = tgrid.majority_terrain(p["_geom"])
        culture = nation_by_id[p["nation_id"]]["culture"]
        p["name"] = make_name(rng, culture, used_prov_names)
        p["polygons"] = poly_to_rings(p["_geom"])

    # ---- 7) Nation geometries ---------------------------------------------
    nation_geom = {}
    for n in all_nations:
        geoms = [prov_geoms[pid] for pid in nation_cells[n["id"]]]
        nation_geom[n["id"]] = make_valid(unary_union(geoms)) if geoms else None

    # ---- 8) Settlements: authored + procedural ----------------------------
    settlements = []
    used_names = set()
    s_i = 0

    def add_settlement(nid, s, snap_port=False):
        nonlocal s_i
        sx, sy = s["x"], s["y"]
        geom = nation_geom.get(nid)
        if geom is not None and not geom.is_empty:
            pnt = Point(sx, sy)
            if not geom.contains(pnt):
                inner = geom.buffer(-0.003)
                target = inner if not inner.is_empty else geom
                q, _ = nearest_points(target, pnt)
                sx, sy = q.x, q.y
        if snap_port:
            pnt0 = Point(sx, sy)
            if water_edge.is_empty or pnt0.distance(water_edge) > 0.12:
                # No true water nearby (map edges don't count) -> keep as a town
                s = dict(s)
                s["type"] = "town"
            else:
                bp, _ = nearest_points(water_edge, pnt0)
                inland = land.buffer(-0.0022)
                q, _ = nearest_points(inland if not inland.is_empty else land, bp)
                sx, sy = q.x, q.y
        # link province
        pid = None
        pnt = Point(sx, sy)
        for cand in nation_cells.get(nid, []):
            if prov_geoms[cand].contains(pnt):
                pid = cand
                break
        if pid is None and nation_cells.get(nid):
            pid = nation_cells[nid][0]
        settlements.append(dict(
            id=f"s_{s_i:04d}", nation_id=nid, province_id=pid,
            name=s["name"], type=s["type"], x=round(sx, 5), y=round(sy, 5),
            description=s["description"], lore=s.get("lore", s["description"]),
        ))
        s_i += 1

    for n in all_nations:
        for s in n["settlements"]:
            used_names.add(s["name"])
            add_settlement(n["id"], s, snap_port=s["type"] in ("port", "major_port"))

    # procedural minor settlements proportional to territory
    for n in all_nations:
        geom = nation_geom.get(n["id"])
        if geom is None or geom.is_empty:
            continue
        target = int(min(14, max(2, 2 + geom.area * 320)))
        extra = gen_settlements(rng, n, geom, target, used_names, sample_inside)
        for s in extra:
            add_settlement(n["id"], s)
        # coastal nations get a proper port if they lack one
        has_port = any(s["type"] in ("port", "major_port") and s["nation_id"] == n["id"] for s in settlements)
        if not has_port and geom.boundary.distance(water_edge) < 0.002:
            pt = sample_inside(geom, rng)
            name = make_name(rng, n["culture"], used_names)
            add_settlement(n["id"], dict(
                name=name, type="port", x=pt[0], y=pt[1],
                description="A harbour of tarred piers and fish-smoke.",
                lore=f"{name} shelters fishing cogs and the occasional war-galley.",
            ), snap_port=True)

    # ---- 9) Influence + nation records ------------------------------------
    nations_out = []
    for n in all_nations:
        geom = nation_geom.get(n["id"])
        area = geom.area if geom is not None else 0.0
        n_setts = sum(1 for s in settlements if s["nation_id"] == n["id"])
        cap = next((s for s in settlements if s["nation_id"] == n["id"] and s["type"] == "capital"), None)
        if cap is None:
            cap = next((s for s in settlements if s["nation_id"] == n["id"] and s["type"] == "city"), None)
        rec = {k: v for k, v in n.items() if k not in ("seed_points", "settlements")}
        rec["capital_id"] = cap["id"] if cap else None
        rec["influence"] = compute_influence(n, area, len(nation_cells[n["id"]]), n_setts)
        nations_out.append(rec)

    for p in provinces:
        del p["_geom"]

    world = dict(
        continent=CONTINENT_NAME,
        current_year=CURRENT_YEAR,
        lore=CONTINENT_LORE,
        religions=RELIGIONS,
        nations=nations_out,
        provinces=provinces,
        settlements=settlements,
        relations=RELATIONS,
    )
    return world


if __name__ == "__main__":
    out = generate_world()
    root = Path(__file__).parent.parent
    dest = root / "world_data.json"
    dest.write_text(json.dumps(out))
    print(f"Wrote {dest}")
    print(f"  religions={len(out['religions'])}  nations={len(out['nations'])}  "
          f"provinces={len(out['provinces'])}  settlements={len(out['settlements'])}  "
          f"relations={len(out['relations'])}")
