// Geometry helpers for the Kelvaros map.
// Coordinates are normalized 0..1 across the base map image (2000 x 1923).
// SVG viewBox is 0..1 (normalized) so polygons render 1:1.

export const MAP_W = 2000;
export const MAP_H = 1923;
export const ASPECT = MAP_W / MAP_H;

// Convert a polygon-with-holes ([[ring], [hole], ...]) to an SVG path string.
// Data coords are normalized (0..1 across map width); we scale to pixel space
// (0..MAP_W) so the SVG viewBox works with sane px-based font/stroke sizes.
export function polygonToPath(polygons) {
  if (!polygons || !polygons.length) return '';
  const parts = [];
  for (const polyRings of polygons) {
    for (const ring of polyRings) {
      if (!ring || ring.length < 3) continue;
      const [x0, y0] = ring[0];
      let d = `M${(x0 * MAP_W).toFixed(2)},${(y0 * MAP_W).toFixed(2)}`;
      for (let i = 1; i < ring.length; i++) {
        d += ` L${(ring[i][0] * MAP_W).toFixed(2)},${(ring[i][1] * MAP_W).toFixed(2)}`;
      }
      d += ' Z';
      parts.push(d);
    }
  }
  return parts.join(' ');
}

// Centroid of first polygon of a province (used for label positioning).
export function polygonCentroid(polygons) {
  if (!polygons || !polygons.length || !polygons[0].length) return [0, 0];
  const ring = polygons[0][0];
  let cx = 0, cy = 0, n = 0;
  for (const [x, y] of ring) { cx += x; cy += y; n++; }
  if (!n) return [0, 0];
  return [cx / n, cy / n];
}

// Compute the visual centroid of a nation given all its provinces.
export function nationCentroid(provinces) {
  let cx = 0, cy = 0, totalArea = 0;
  for (const p of provinces) {
    if (!p.polygons || !p.polygons.length) continue;
    for (const rings of p.polygons) {
      const ring = rings[0];
      if (!ring || ring.length < 3) continue;
      // shoelace area + centroid
      let a = 0, x = 0, y = 0;
      for (let i = 0; i < ring.length; i++) {
        const [x1, y1] = ring[i];
        const [x2, y2] = ring[(i + 1) % ring.length];
        const cross = x1 * y2 - x2 * y1;
        a += cross;
        x += (x1 + x2) * cross;
        y += (y1 + y2) * cross;
      }
      a *= 0.5;
      if (Math.abs(a) < 1e-9) continue;
      x /= (6 * a); y /= (6 * a);
      const w = Math.abs(a);
      cx += x * w;
      cy += y * w;
      totalArea += w;
    }
  }
  if (totalArea === 0) return null;
  return [cx / totalArea, cy / totalArea];
}

// Point-in-polygon (single ring) test.
export function pointInRing(x, y, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    const intersect = ((yi > y) !== (yj > y)) &&
      (x < ((xj - xi) * (y - yi)) / ((yj - yi) || 1e-12) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

// Point in polygon-with-holes.
export function pointInPolygons(x, y, polygons) {
  for (const rings of polygons) {
    if (!rings.length) continue;
    if (pointInRing(x, y, rings[0])) {
      // check holes
      let inHole = false;
      for (let i = 1; i < rings.length; i++) {
        if (pointInRing(x, y, rings[i])) { inHole = true; break; }
      }
      if (!inHole) return true;
    }
  }
  return false;
}

// Compress a screen-space lasso path into normalized coords (dedupe nearby).
export function compressLasso(points, minSep = 0.003) {
  if (points.length < 2) return points;
  const out = [points[0]];
  for (let i = 1; i < points.length; i++) {
    const [x, y] = points[i];
    const [px, py] = out[out.length - 1];
    const dx = x - px, dy = y - py;
    if (dx * dx + dy * dy > minSep * minSep) out.push([x, y]);
  }
  // ensure closed
  const [fx, fy] = out[0];
  const [lx, ly] = out[out.length - 1];
  if (Math.abs(lx - fx) > 1e-6 || Math.abs(ly - fy) > 1e-6) out.push([fx, fy]);
  return out;
}
