# plan.md — Political Map Game (Foundation Map)

## 1) Objectives
- Deliver an interactive **SVG polygon-based** political map over the uploaded sepia parchment terrain (`/maps/base_map.webp`) as the **canonical playable map**.
- Render **50+ nations** (currently **62**) with organic borders, rich lore, religions, and settlements.
- Ensure **coastlines and terrain classification match the artwork** (pixel-derived), while interior political borders remain editable.
- Provide view modes: **Political / Terrain / Religion / Vassals** and a new **Provinces** mode.
- **Province tiles invisible by default**: political/religion/vassals show smooth merged nation territories; provinces only visible in **Provinces** view.
- Enable freeform editing:
  - **Lasso cut → transfer territory** (persisted)
  - **Trace Mode**: manual correction of water/land, terrain, and nation ownership (persisted)
- Build a stronger “Imperator Rome” aesthetic: softer organic borders, clear hierarchy, dense map symbols.
- Upgrade to deeper **feudal power dynamics**: more vassals, influence rankings, and composition views.
- Increase settlement density and correct placement rules, including **ports on real coastline/river mouths**.
- Keep data model future-ready for treaties and “play as nation”.

---

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation): Lasso Cut → Transfer (must work before full app)
**Goal:** Prove polygon boolean ops + persistence are robust.
1. Web research: best practices for **polygon clipping + multipolygon validity + edge cases** (self-intersections, holes, tiny slivers) using **Shapely**.
2. Backend-only POC (FastAPI route + unit script):
   - Seed 2–3 sample provinces (simple polygons) + 1 lasso polygon.
   - Implement `POST /api/map/transfer` that:
     - Intersects lasso with source provinces
     - Subtracts intersection from source
     - Adds intersection to target (merge/union)
     - Normalizes output (MultiPolygon handling, simplify tiny artifacts)
3. Write a small Python script to call the endpoint and assert:
   - Area conserved (source+target total area stable within epsilon)
   - No invalid geometries
   - Provinces updated as expected
4. Iterate until stable (edge cases: lasso outside, partial overlap, multiple provinces hit, tiny fragments).

**POC User Stories**
1. As a user, I can select a source and target nation and transfer land with a lasso.
2. As a user, if my lasso doesn’t intersect, nothing changes and I get a clear message.
3. As a user, transfers affecting multiple provinces still work in one action.
4. As a user, the server always returns valid polygons after edits.
5. As a user, the transfer persists when I reload.

**Status:** ✅ Done.

---

### Phase 2 — V1 App Development (build around proven core)

#### 2.1 Data + Worldbuilding (hand-authored)
1. Finalize continent name, 6–8 religions, major powers + vassals, minors.
2. Generate initial world state:
   - 62 nations, ~134 provinces via Voronoi
   - Settlements placed and linked to provinces
3. Store world state in `backend/world_data.json` (temporary datastore).

**Status:** ✅ Done.

#### 2.2 Backend (FastAPI + persistence)
1. Implement endpoints:
   - `GET /api/map/state`
   - `GET /api/nation/{id}`
   - `GET /api/settlement/{id}`
   - `POST /api/map/transfer`
   - `POST /api/map/reset`
2. Persistence strategy (current): JSON file (`world_data.json`) + MongoDB audit logs.
3. Future: migrate world state fully to MongoDB.

**Status:** ✅ Done.

#### 2.3 Frontend (React + SVG + d3-zoom)
1. `<MapCanvas>`
   - Background `<image href="/maps/base_map.webp">`
   - Province polygons + nation borders + settlements
   - d3-zoom pan/zoom
2. `<ViewSwitcher>`: Political / Terrain / Religion / Vassals.
3. `<NationPanel>` + `<SettlementDialog>` for lore.
4. `<FreeformEditor>`: pick source → target → draw lasso → commit.

**Notable Fix Completed (P0):**
- ✅ Fixed coordinate-space rendering: SVG now uses pixel viewBox `0..MAP_W x 0..MAP_H`, correct polygon/icon/label scaling.

**Status:** ✅ Done.

---

### Phase 3 — Pixel-Accurate World Rebuild (Status: ✅ Completed)
**Goal:** Make coasts and terrain view match the sepia artwork so that:
- Provinces never appear in ocean.
- Terrain view is aligned with the artwork.
- All land belongs to nations.

#### 3.1 Dependencies + tooling
- Added image-processing deps:
  - `opencv-python-headless`
  - `scipy`

#### 3.2 Land / water segmentation (pixel-derived)
- Implemented `backend/world_gen/extract_mask.py`:
  - Water detection via dark+low-texture threshold
  - Morphology cleanup
  - Contour extraction → polygon-with-holes
- Output: `backend/world_gen/extracted_mask.json`

#### 3.3 Terrain classification (pixel-derived, heuristic)
- Implemented terrain raster grid (cell-based) and a dominant-terrain lookup.

#### 3.4 Regenerate provinces using extracted land + terrain
- Updated `backend/world_gen/generate.py` to:
  - Use extracted land mask
  - Snap seeds/settlements into valid land/nation interiors
  - Assign terrain from the extracted grid
- Regenerated `backend/world_data.json`.

#### 3.5 Visual verification
- Screenshot verification: coastline alignment and terrain view credible.

**Exit criteria met:** ✅

---

### Phase 4 — Trace Mode (Manual Correction Tool) (Status: ✅ Completed)
**Goal:** Allow user to manually fix remaining mismatches by drawing polygons and persisting overrides.

#### 4.1 Overrides model
- `backend/trace_overrides.json` stores overrides.

#### 4.2 Backend endpoints
- ✅ `GET /api/trace/overrides`
- ✅ `POST /api/trace/apply` (set_terrain / assign_nation / carve_water / restore_land)
- ✅ `DELETE /api/trace/overrides/{id}` (rebuild from seed + remaining traces)
- ✅ Reset behavior: `POST /api/map/reset?clear_traces=true|false` (default keeps traces)

#### 4.3 Frontend Trace Tool
- ✅ `TracePanel` UI
- ✅ Reuses lasso drawing in `MapCanvas` with `editorMode='trace-draw'`
- ✅ Apply / Clear / Undo Last

**Exit criteria met:** ✅

---

### Phase 5 — V2 World Upgrade (Power Dynamics + Density + Styling) (Status: 🚧 In Progress)
**Goal:** Make the map feel like the reference (soft borders, dense provinces, deep feudal structure, many settlements) while keeping performance and editability.

#### 5.1 View modes + province visibility
1. Add a new view mode: **Provinces**.
2. Default modes (Political/Religion/Vassals) render **merged nation territories** (no province tile outlines).
3. Province layer renders only in Provinces view.

**Acceptance:**
- Political view looks like a real political map (smooth regions) not a Voronoi tiling.

#### 5.2 Exponentially more provinces
1. Update generator to produce **~1200–1500** Voronoi cells over extracted land mask.
   - Use jittered lattice or Poisson sampling for even distribution.
2. Assign provinces to nations via **tier-weighted nearest-anchor**:
   - Empires/kingdoms project further influence than duchies/counties.
3. Ensure stability:
   - All land assigned
   - Avoid micro-slivers (min area threshold + simplify)

Deliverable: `world_gen/generate_v2.py` (or upgraded `generate.py`) with parameters.

#### 5.3 Deeper feudal power dynamics
1. Procedurally generate **~40–60 additional vassals** under empires/kingdoms.
2. Add an `influence` stat per vassal derived from:
   - army/economy
   - controlled area/province count
   - strategic settlements
3. Update NationPanel:
   - show vassals ranked by influence with bars
4. Update Vassals view:
   - color by overlord composition
   - optionally show “strong vassals” outlines

Implementation: `backend/world_gen/realm_gen.py` (vassal generation + names + influence).

#### 5.4 Soft organic borders like reference
1. Backend computes and serves **nation_shapes**:
   - per-nation merged geometry (`unary_union` of province shapes)
   - optional smoothing (`buffer(+r).buffer(-r)`), simplify
2. Recompute nation_shapes after:
   - transfer
   - trace apply
   - reset
3. Frontend:
   - render nation fills from `nation_shapes`
   - soften border styling (stroke opacity, wider but blurred, subtle inner glow)

Deliverable: `/api/map/state` includes `nation_shapes` (GeoJSON-like rings).

#### 5.5 More settlements + better rules
1. Increase settlements to **~450–600** total:
   - villages/towns/castles proportional to nation area
   - capitals/major cities remain authored anchors
2. Add procedural name generation (culture-based syllables).
3. Performance:
   - zoom-gate labels (villages only show at higher zoom)

#### 5.6 Ports fixed (coast/river validity)
1. Snap `port` and `major_port` settlements to true land-water boundary derived from extracted mask.
2. Prefer:
   - coast adjacency
   - river mouths / wide rivers (heuristic: elongated dark water channels inside land)
3. Pull ports slightly inland so icons sit on land.

---

### Phase 6 — Comprehensive testing + polish (Status: ⏳ Pending)
1. Run `testing_agent_v3` end-to-end:
   - Load map
   - Click nation/settlement
   - Switch view modes incl. Provinces
   - Perform lasso transfer
   - Perform trace apply + undo
   - Reset (keep traces and clear traces)
2. Performance pass:
   - polygon simplification thresholds
   - memoize SVG layers, reduce DOM load
3. Geometry robustness:
   - production-grade MultiPolygon + holes
   - minimum area thresholds; sliver cleanup

---

## 3) Next Actions
1. Implement **nation_shapes** cache in backend and integrate into `/api/map/state`.
2. Add **Provinces** view mode and make province tiles hidden by default.
3. Implement **V2 province generation** (~1200–1500) and tier-weighted assignment.
4. Add **vassal depth + influence UI**.
5. Increase settlement generation and snap ports to coast/river.
6. Run `testing_agent_v3` and fix any regressions.

---

## 4) Success Criteria
- Map renders crisply and interactively (pan/zoom/click) with no timeouts.
- Coastlines are pixel-aligned to `base_map.webp` (no provinces in ocean).
- Terrain mode matches the artwork in the majority of regions.
- Political/Religion/Vassals views show **smooth nation shapes**; provinces visible only in Provinces view.
- Borders look **soft and organic** (reference-like), not harsh tile edges.
- 62 invented nations and lore remain intact; **additional vassals** deepen power dynamics.
- Settlements are dense and believable; **ports are placed on coastline/river mouths**.
- Lasso transfer + Trace Mode both work and persist.
- Testing agent reports core flows passing with no critical UX breakages.
