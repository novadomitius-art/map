"""Shapely-based territory transfer for lasso cuts.

Given a lasso polygon and source/target nation ids, compute the intersection
with the source's provinces, subtract from source, and either merge with the
target's nearest province or create a new province owned by the target.

Polygons stored as {polygons: [[[ring1_pt, ...], [hole1_pt, ...], ...], ...]}
where each entry is a polygon-with-holes.
"""
from typing import List, Dict, Tuple
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.validation import make_valid

_MIN_AREA = 1e-6


def rings_to_shape(polygons_rings):
    """[[ring, hole, hole], [ring, ...]] -> shapely (Multi)Polygon."""
    parts = []
    for rings in polygons_rings:
        if not rings:
            continue
        ext = rings[0]
        holes = rings[1:] if len(rings) > 1 else None
        try:
            p = Polygon(ext, holes)
            p = make_valid(p)
            if p.is_empty or p.area < _MIN_AREA:
                continue
            parts.append(p)
        except Exception:
            continue
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    u = unary_union(parts)
    return make_valid(u)


def shape_to_rings(geom):
    """shapely (Multi)Polygon -> [[ring, hole...], [ring, hole...], ...]."""
    if geom is None or geom.is_empty:
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
        if p.is_empty or p.area < _MIN_AREA:
            continue
        rings = [list(map(list, p.exterior.coords))]
        for interior in p.interiors:
            rings.append(list(map(list, interior.coords)))
        out.append(rings)
    return out


def transfer_territory(
    provinces: List[Dict],
    settlements: List[Dict],
    source_nation_id: str,
    target_nation_id: str,
    lasso_polygon: List[Tuple[float, float]],
):
    """Mutate provinces list and return (updated_provinces, updated_settlements, transferred_area).

    - Intersects lasso with every source province, subtracts intersection from source,
      merges intersection into the target's nearest province (or creates one).
    - Settlements whose (x,y) fell inside the transferred region change nation.
    - Preserves holes.
    """
    if len(lasso_polygon) < 3:
        return provinces, settlements, 0.0
    lasso = make_valid(Polygon(lasso_polygon))
    if lasso.is_empty or lasso.area < _MIN_AREA:
        return provinces, settlements, 0.0

    total_transferred_area = 0.0
    transferred_shapes = []

    new_provs = []
    for p in provinces:
        if p.get("nation_id") != source_nation_id:
            new_provs.append(p)
            continue
        shape = rings_to_shape(p.get("polygons", []))
        if shape is None:
            new_provs.append(p)
            continue
        inter = shape.intersection(lasso)
        inter = make_valid(inter)
        if inter.is_empty or inter.area < _MIN_AREA:
            new_provs.append(p)
            continue
        remaining = shape.difference(lasso)
        remaining = make_valid(remaining)
        transferred_shapes.append(inter)
        total_transferred_area += inter.area
        remaining_rings = shape_to_rings(remaining)
        if remaining_rings:
            p2 = dict(p)
            p2["polygons"] = remaining_rings
            new_provs.append(p2)
        # else: province fully absorbed; drop it

    if not transferred_shapes:
        return provinces, settlements, 0.0

    transferred_union = unary_union(transferred_shapes)
    transferred_union = make_valid(transferred_union)

    # Merge into nearest target province if any; else create a new province.
    target_provs = [p for p in new_provs if p.get("nation_id") == target_nation_id]
    if target_provs:
        # merge with the largest target province
        target_provs.sort(key=lambda p: sum(Polygon(r[0]).area for r in p["polygons"] if r), reverse=True)
        anchor = target_provs[0]
        anchor_shape = rings_to_shape(anchor.get("polygons", []))
        merged = unary_union([anchor_shape, transferred_union]) if anchor_shape else transferred_union
        merged = make_valid(merged)
        anchor["polygons"] = shape_to_rings(merged)
    else:
        # create new province owned by target
        import uuid
        new_prov = dict(
            id=f"p_{uuid.uuid4().hex[:8]}",
            nation_id=target_nation_id,
            name="Ceded Territory",
            terrain="plains",
            seed=[transferred_union.centroid.x, transferred_union.centroid.y],
            polygons=shape_to_rings(transferred_union),
        )
        new_provs.append(new_prov)

    # Reassign settlements that fell inside transferred_union.
    new_setts = []
    for s in settlements:
        if s.get("nation_id") == source_nation_id:
            from shapely.geometry import Point
            if transferred_union.contains(Point(s["x"], s["y"])):
                s2 = dict(s)
                s2["nation_id"] = target_nation_id
                # re-link province_id to a target province if any
                # (best-effort: use anchor's id if available)
                if target_provs:
                    s2["province_id"] = target_provs[0]["id"]
                new_setts.append(s2)
                continue
        new_setts.append(s)

    return new_provs, new_setts, total_transferred_area


# ---------------------------------------------------------------------------
# Trace Mode operations (manual correction tool)
# ---------------------------------------------------------------------------

def _largest_province_of(provinces, nation_id):
    provs = [p for p in provinces if p.get("nation_id") == nation_id]
    if not provs:
        return None
    def area_of(p):
        s = rings_to_shape(p.get("polygons", []))
        return s.area if s else 0.0
    return max(provs, key=area_of)


def apply_trace(provinces, settlements, ttype, polygon, value=None):
    """Apply one trace override. Returns (provinces, settlements, affected_area).

    ttype:
      carve_water   -> remove polygon area from every province (becomes sea)
      restore_land  -> add polygon area (minus existing land) to nation `value`
      assign_nation -> transfer polygon area from all owners to nation `value`
      set_terrain   -> paint terrain `value` on polygon area (splits provinces)
    """
    import uuid as _uuid
    from shapely.geometry import Point

    if len(polygon) < 3:
        return provinces, settlements, 0.0
    lasso = make_valid(Polygon([(float(x), float(y)) for x, y in polygon]))
    if lasso.is_empty or lasso.area < _MIN_AREA:
        return provinces, settlements, 0.0

    affected = 0.0

    if ttype == "carve_water":
        out = []
        for p in provinces:
            shape = rings_to_shape(p.get("polygons", []))
            if shape is None:
                continue
            inter = make_valid(shape.intersection(lasso))
            if inter.is_empty or inter.area < _MIN_AREA:
                out.append(p)
                continue
            affected += inter.area
            rem = make_valid(shape.difference(lasso))
            rings = shape_to_rings(rem)
            if rings:
                p2 = dict(p)
                p2["polygons"] = rings
                out.append(p2)
        return out, settlements, affected

    if ttype == "restore_land":
        if not value:
            return provinces, settlements, 0.0
        shapes = [rings_to_shape(p.get("polygons", [])) for p in provinces]
        existing = unary_union([s for s in shapes if s is not None])
        new_land = make_valid(lasso.difference(existing))
        if new_land.is_empty or new_land.area < _MIN_AREA:
            return provinces, settlements, 0.0
        anchor = _largest_province_of(provinces, value)
        if anchor is not None:
            a_shape = rings_to_shape(anchor.get("polygons", []))
            merged = make_valid(unary_union([a_shape, new_land])) if a_shape else new_land
            anchor["polygons"] = shape_to_rings(merged)
        else:
            provinces.append(dict(
                id=f"p_{_uuid.uuid4().hex[:8]}",
                nation_id=value,
                name="Reclaimed Land",
                terrain="coast",
                seed=[new_land.centroid.x, new_land.centroid.y],
                polygons=shape_to_rings(new_land),
            ))
        return provinces, settlements, new_land.area

    if ttype == "assign_nation":
        if not value:
            return provinces, settlements, 0.0
        taken = []
        out = []
        for p in provinces:
            if p.get("nation_id") == value:
                out.append(p)
                continue
            shape = rings_to_shape(p.get("polygons", []))
            if shape is None:
                continue
            inter = make_valid(shape.intersection(lasso))
            if inter.is_empty or inter.area < _MIN_AREA:
                out.append(p)
                continue
            taken.append(inter)
            affected += inter.area
            rem = make_valid(shape.difference(lasso))
            rings = shape_to_rings(rem)
            if rings:
                p2 = dict(p)
                p2["polygons"] = rings
                out.append(p2)
        if not taken:
            return provinces, settlements, 0.0
        gained = make_valid(unary_union(taken))
        anchor = _largest_province_of(out, value)
        if anchor is not None:
            a_shape = rings_to_shape(anchor.get("polygons", []))
            merged = make_valid(unary_union([a_shape, gained])) if a_shape else gained
            anchor["polygons"] = shape_to_rings(merged)
            anchor_id = anchor["id"]
        else:
            new_p = dict(
                id=f"p_{_uuid.uuid4().hex[:8]}",
                nation_id=value,
                name="Annexed Territory",
                terrain="plains",
                seed=[gained.centroid.x, gained.centroid.y],
                polygons=shape_to_rings(gained),
            )
            out.append(new_p)
            anchor_id = new_p["id"]
        new_setts = []
        for s in settlements:
            if s.get("nation_id") != value and gained.contains(Point(s["x"], s["y"])):
                s2 = dict(s)
                s2["nation_id"] = value
                s2["province_id"] = anchor_id
                new_setts.append(s2)
            else:
                new_setts.append(s)
        return out, new_setts, affected

    if ttype == "set_terrain":
        if not value:
            return provinces, settlements, 0.0
        import uuid as _u
        out = []
        for p in provinces:
            shape = rings_to_shape(p.get("polygons", []))
            if shape is None:
                continue
            inter = make_valid(shape.intersection(lasso))
            if inter.is_empty or inter.area < _MIN_AREA:
                out.append(p)
                continue
            affected += inter.area
            if inter.area >= shape.area * 0.9:
                p2 = dict(p)
                p2["terrain"] = value
                out.append(p2)
                continue
            # split: outside keeps old terrain, inside becomes new sibling province
            rem = make_valid(shape.difference(lasso))
            rem_rings = shape_to_rings(rem)
            if rem_rings:
                p_keep = dict(p)
                p_keep["polygons"] = rem_rings
                out.append(p_keep)
            in_rings = shape_to_rings(inter)
            if in_rings:
                out.append(dict(
                    id=f"p_{_u.uuid4().hex[:8]}",
                    nation_id=p["nation_id"],
                    name=p.get("name", "Province") + " (" + value + ")",
                    terrain=value,
                    seed=[inter.centroid.x, inter.centroid.y],
                    polygons=in_rings,
                ))
        return out, settlements, affected

    raise ValueError(f"Unknown trace type: {ttype}")
