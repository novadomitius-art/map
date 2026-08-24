import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import * as d3 from 'd3-selection';
import { zoom as d3zoom, zoomIdentity } from 'd3-zoom';
import { polygonToPath, nationCentroid, pointInPolygons, MAP_W, MAP_H } from '../lib/geom';

/**
 * MapCanvas
 * SVG map: base image + province polygons + nation borders + settlement icons.
 *
 * Props:
 *  world:         full world state
 *  viewMode:      'political' | 'terrain' | 'religion' | 'vassals'
 *  selectedNationId
 *  onSelectNation(id)
 *  onSelectSettlement(id)
 *  editorMode:    null | 'pick-source' | 'pick-target' | 'draw-lasso'
 *  editorSource:  nation id (during edit)
 *  editorTarget:  nation id (during edit)
 *  onEditPick(kind, nationId)   // called on click when editing
 *  onLassoCommit(points)         // called on mouseup when drawing
 *  lassoDraft:    array of [x,y] normalized OR null
 */
export default function MapCanvas({
  world,
  viewMode,
  selectedNationId,
  onSelectNation,
  onSelectSettlement,
  editorMode,
  editorSource,
  editorTarget,
  onEditPick,
  onLassoCommit,
  lassoDraft,
  setLassoDraft,
}) {
  const svgRef = useRef(null);
  const worldGroupRef = useRef(null);
  const [transform, setTransform] = useState({ k: 1, x: 0, y: 0 });
  const [tooltip, setTooltip] = useState(null);
  const [drawing, setDrawing] = useState(false);
  const currentTransformRef = useRef(zoomIdentity);

  // Build lookup maps.
  const nationById = useMemo(() => {
    const m = new Map();
    for (const n of world.nations) m.set(n.id, n);
    return m;
  }, [world.nations]);

  const religionById = useMemo(() => {
    const m = new Map();
    for (const r of world.religions) m.set(r.id, r);
    return m;
  }, [world.religions]);

  const provincesByNation = useMemo(() => {
    const m = new Map();
    for (const p of world.provinces) {
      if (!m.has(p.nation_id)) m.set(p.nation_id, []);
      m.get(p.nation_id).push(p);
    }
    return m;
  }, [world.provinces]);

  const nationLabels = useMemo(() => {
    const arr = [];
    for (const n of world.nations) {
      const provs = provincesByNation.get(n.id) || [];
      const c = nationCentroid(provs);
      if (!c) continue;
      arr.push({ nation: n, cx: c[0], cy: c[1] });
    }
    return arr;
  }, [world.nations, provincesByNation]);

  // Combined fill path per nation: all of a realm's province polygons merged
  // into ONE path so the fill is painted a single time. This removes the faint
  // internal seams you get when many semi-transparent tiles share edges, so a
  // realm reads as one perfectly flat colour (Provinces look, zero grid).
  const nationFillPath = useMemo(() => {
    const m = new Map();
    for (const [nid, provs] of provincesByNation.entries()) {
      const merged = [];
      for (const p of provs) {
        if (p.polygons) for (const poly of p.polygons) merged.push(poly);
      }
      const d = polygonToPath(merged);
      if (d) m.set(nid, d);
    }
    return m;
  }, [provincesByNation]);

  // ---------- d3-zoom ----------
  // The SVG uses a pixel viewBox (0 0 MAP_W MAP_H) with preserveAspectRatio
  // "meet", so on wide screens the map is letter-boxed. d3-zoom by default
  // assumes the viewport equals the viewBox, which lets panning drag the map
  // edge inward and reveal the dark background. To lock the camera to the map
  // we feed d3 the REAL visible viewBox region (computed from the element's
  // pixel size) as its extent, and set translateExtent to the map rectangle.
  // d3 then centres the map when it is smaller than the viewport and clamps
  // panning at the edges when zoomed in -> the void can never slide in.
  useEffect(() => {
    const svgEl = svgRef.current;
    const svg = d3.select(svgEl);
    const worldG = d3.select(worldGroupRef.current);
    const zoomBehav = d3zoom()
      .scaleExtent([1, 14])
      .translateExtent([[0, 0], [MAP_W, MAP_H]])
      .on('zoom', (event) => {
        currentTransformRef.current = event.transform;
        worldG.attr('transform', event.transform);
        setTransform({ k: event.transform.k, x: event.transform.x, y: event.transform.y });
      })
      .filter((event) => {
        // Disable zoom-drag while lasso/trace drawing
        if (editorMode === 'draw-lasso' || editorMode === 'trace-draw') return event.type === 'wheel';
        return !event.button;
      });

    const applyExtent = () => {
      const rect = svgEl.getBoundingClientRect();
      const W = rect.width || MAP_W;
      const H = rect.height || MAP_H;
      // "meet" base scale: viewBox units -> pixels.
      const s0 = Math.min(W / MAP_W, H / MAP_H) || 1;
      // Half of the letter-box gap expressed back in viewBox units.
      const padX = (W - s0 * MAP_W) / 2 / s0;
      const padY = (H - s0 * MAP_H) / 2 / s0;
      zoomBehav.extent([[-padX, -padY], [MAP_W + padX, MAP_H + padY]]);
      svg.call(zoomBehav.transform, currentTransformRef.current);
    };

    svg.call(zoomBehav);
    applyExtent();

    const ro = new ResizeObserver(applyExtent);
    ro.observe(svgEl);
    return () => { ro.disconnect(); svg.on('.zoom', null); };
  }, [editorMode]);

  // ---------- pointer -> normalized world coords helper ----------
  // Returns coordinates normalized 0..1 (map-width units) to match the
  // backend / world_data coordinate space.
  const clientToWorld = useCallback((clientX, clientY) => {
    const svg = svgRef.current;
    const pt = svg.createSVGPoint();
    pt.x = clientX;
    pt.y = clientY;
    const local = pt.matrixTransform(svg.getScreenCTM().inverse());
    const t = currentTransformRef.current;
    const x = (local.x - t.x) / t.k / MAP_W;
    const y = (local.y - t.y) / t.k / MAP_W;
    return [x, y];
  }, []);

  // ---------- lasso drawing ----------
  const isDrawMode = editorMode === 'draw-lasso' || editorMode === 'trace-draw';
  const onSvgMouseDown = (e) => {
    if (!isDrawMode) return;
    if (e.button !== 0) return;
    const [x, y] = clientToWorld(e.clientX, e.clientY);
    setDrawing(true);
    setLassoDraft([[x, y]]);
  };
  const onSvgMouseMove = (e) => {
    if (isDrawMode && drawing) {
      const [x, y] = clientToWorld(e.clientX, e.clientY);
      setLassoDraft((prev) => (prev ? [...prev, [x, y]] : [[x, y]]));
    }
  };
  const onSvgMouseUp = () => {
    if (isDrawMode && drawing) {
      setDrawing(false);
      if (lassoDraft && lassoDraft.length >= 3) {
        onLassoCommit(lassoDraft);
      } else {
        setLassoDraft(null);
      }
    }
  };

  // ---------- fills by view mode ----------
  const nationShapes = world.nation_shapes || {};
  const showNationShapes = viewMode === 'political' || viewMode === 'religion' || viewMode === 'vassals';
  const showNationFill = showNationShapes; // province-based nation colouring (no grid)
  const showProvinceTiles = viewMode === 'provinces';

  function fillForNation(nation) {
    if (viewMode === 'religion') {
      const rel = religionById.get(nation.religion);
      return rel ? rel.color : nation.color;
    }
    if (viewMode === 'vassals') {
      const overlordId = nation.overlord || nation.id;
      const overlord = nationById.get(overlordId) || nation;
      return overlord.color;
    }
    return nation.color;
  }

  function fillFor(nation, province) {
    if (viewMode === 'terrain') {
      // Return a per-terrain semi-transparent tint (or no fill).
      const t = province.terrain;
      const map = {
        mountain: '#5a4a3a',
        forest: '#3a6a3a',
        desert: '#d4b76a',
        plains: '#a89860',
        coast: '#4a6a8a',
        hills: '#8a7050',
        swamp: '#556b2f',
      };
      return map[t] || '#88755a';
    }
    return fillForNation(nation);
  }

  function fillOpacityFor(nation) {
    if (viewMode === 'terrain') return 0.28;
    if (nation.id === selectedNationId) return 0.82;
    if (nation.id === editorSource) return 0.78;
    if (nation.id === editorTarget) return 0.78;
    return 0.66;
  }

  // ---------- click handlers ----------
  function handleNationInteraction(nationId) {
    if (editorMode === 'pick-source') {
      onEditPick('source', nationId);
      return;
    }
    if (editorMode === 'pick-target') {
      onEditPick('target', nationId);
      return;
    }
    onSelectNation(nationId);
  }

  function onNationClick(e, nationId) {
    e.stopPropagation();
    handleNationInteraction(nationId);
  }

  function onNationEnter(e, nation) {
    const parts = [nation.tier.replace(/_/g, ' ')];
    if (nation.overlord) {
      const o = nationById.get(nation.overlord);
      if (o) parts.push(`vassal of ${o.name}`);
      if (typeof nation.influence === 'number') parts.push(`influence ${nation.influence}`);
    }
    setTooltip({
      x: e.clientX, y: e.clientY,
      title: nation.name,
      subtitle: parts.join('  \u00b7  '),
    });
  }

  function onProvinceClick(e, province) {
    e.stopPropagation();
    handleNationInteraction(province.nation_id);
  }

  function onProvinceEnter(e, province) {
    const nation = nationById.get(province.nation_id);
    if (!nation) return;
    setTooltip({
      x: e.clientX, y: e.clientY,
      title: nation.name,
      subtitle: province.name + '  \u00b7  ' + province.terrain,
    });
  }
  function onProvinceLeave() { setTooltip(null); }

  function onSettlementClick(e, s) {
    e.stopPropagation();
    if (editorMode) return;
    onSelectSettlement(s.id);
  }

  function onSettlementEnter(e, s) {
    setTooltip({
      x: e.clientX, y: e.clientY,
      title: s.name,
      subtitle: s.type.replace('_', ' '),
    });
  }

  // ---------- nation borders (outline of union of provinces) ----------
  // We approximate the nation border by rendering each province's exterior
  // ring with a thick stroke; adjacent provinces share edges but the thick
  // stroke gives a bold outer border feel. For vassal sub-borders we draw
  // thin dashed strokes on province exteriors.

  // Sort nations: majors last so they draw label on top.
  const sortedNations = useMemo(() => {
    return [...world.nations].sort((a, b) => {
      const w = (n) => ['empire','kingdom','sultanate','theocracy','confederacy'].includes(n.tier) ? 1 : 0;
      return w(a) - w(b);
    });
  }, [world.nations]);

  const svgClass = 'map-svg' +
    (drawing ? ' grabbing' : '') +
    (editorMode ? ' editing' : '');

  return (
    <div className="map-container">
      <svg
        ref={svgRef}
        className={svgClass}
        viewBox={`0 0 ${MAP_W} ${MAP_H}`}
        preserveAspectRatio="xMidYMid meet"
        onMouseDown={onSvgMouseDown}
        onMouseMove={onSvgMouseMove}
        onMouseUp={onSvgMouseUp}
        onMouseLeave={onSvgMouseUp}
        style={{ background: 'transparent' }}
      >
        <defs>
          <filter id="parchment-vignette">
            <feGaussianBlur in="SourceGraphic" stdDeviation="0"/>
          </filter>
          <filter id="gold-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="1.4" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          {/* Soft blurred dark strokes used for the "recessed" border shadow
              that gives realms depth (province-map feel, no grid). Applied to a
              whole group at once so it stays cheap. */}
          <filter id="border-shadow-blur" x="-10%" y="-10%" width="120%" height="120%">
            <feGaussianBlur stdDeviation="2.2" />
          </filter>
        </defs>

        <g ref={worldGroupRef}>
          {/* Deep-sea backdrop extending well beyond the map so the letter-box
              area around a wide screen reads as open ocean, never a black void.
              It sits inside the zoom group, so it follows the map at all times. */}
          <rect
            x={-MAP_W} y={-MAP_H}
            width={MAP_W * 3} height={MAP_H * 3}
            fill="#0c1218" pointerEvents="none"
          />
          {/* Base map background (pixel coords 0..MAP_W x 0..MAP_H) */}
          <image
            href="/maps/base_map.webp"
            x="0" y="0"
            width={MAP_W} height={MAP_H}
            preserveAspectRatio="none"
          />

          {/* Subtle darkening tint over base map so nation colours read strongly */}
          {viewMode !== 'terrain' && (
            <rect x="0" y="0" width={MAP_W} height={MAP_H}
              fill="rgba(0,0,0,0.18)" pointerEvents="none" />
          )}

          {/* Nation territory FILL.
              Political / religion / vassals are now painted with the actual
              per-province polygons coloured by nation (exactly like the
              Provinces tab) but WITHOUT any grid strokes, so a realm reads as
              one clean solid colour that hugs the coastline. The smoothed
              nation_shapes are still used below only for the outer borders. */}
          {showNationFill && (
            <g>
              {sortedNations.map((n) => {
                const d = nationFillPath.get(n.id);
                if (!d) return null;
                const isSel = n.id === selectedNationId;
                const col = fillForNation(n);
                const op = fillOpacityFor(n);
                return (
                  <path
                    key={'nf-' + n.id}
                    className={'nation-fill' + (isSel ? ' selected' : '')}
                    d={d}
                    fill={col}
                    fillOpacity={op}
                    fillRule="nonzero"
                    onClick={(e) => onNationClick(e, n.id)}
                    onMouseEnter={(e) => onNationEnter(e, n)}
                    onMouseLeave={onProvinceLeave}
                  />
                );
              })}
            </g>
          )}

          {/* Nation borders: two passes over each realm's DISSOLVED outline
              (nation_shapes = the union boundary, so NO internal province grid).
              (1) a soft, blurred dark stroke = recessed "shadow valley" between
                  kingdoms (the shadowy depth of the province map, no grid);
              (2) a thin crisp inked stroke = clean separation between realms. */}
          {showNationShapes && (
            <>
              {/* shadow pass */}
              <g pointerEvents="none" filter="url(#border-shadow-blur)">
                {sortedNations.map((n) => {
                  const rings = nationShapes[n.id];
                  if (!rings || !rings.length) return null;
                  const d = polygonToPath(rings);
                  if (!d) return null;
                  return (
                    <path key={'nsh-' + n.id} className="nation-border-shadow"
                      d={d} vectorEffect="non-scaling-stroke" />
                  );
                })}
              </g>
              {/* crisp ink pass */}
              <g pointerEvents="none">
                {sortedNations.map((n) => {
                  const rings = nationShapes[n.id];
                  if (!rings || !rings.length) return null;
                  const d = polygonToPath(rings);
                  if (!d) return null;
                  if (viewMode === 'vassals' && n.overlord) {
                    const w = 0.7 + (n.influence || 20) / 45;
                    return (
                      <path key={'vb-' + n.id} className="vassal-sub" d={d}
                        vectorEffect="non-scaling-stroke" style={{ strokeWidth: w }} />
                    );
                  }
                  const isSel = n.id === selectedNationId;
                  return (
                    <path key={'nb-' + n.id}
                      className={'nation-border inked' + (isSel ? ' selected' : '')}
                      d={d} vectorEffect="non-scaling-stroke" />
                  );
                })}
              </g>
            </>
          )}

          {/* Province tiles: terrain tints or the dedicated Provinces view */}
          {(viewMode === 'terrain' || showProvinceTiles) && (
            <g>
              {world.provinces.map((p) => {
                const n = nationById.get(p.nation_id);
                if (!n) return null;
                const d = polygonToPath(p.polygons);
                if (!d) return null;
                const isSel = n.id === selectedNationId;
                return (
                  <path
                    key={p.id}
                    className={'province-poly' + (showProvinceTiles ? ' tile' : '') + (isSel ? ' selected' : '')}
                    d={d}
                    fill={fillFor(n, p)}
                    fillOpacity={viewMode === 'terrain' ? 0.30 : 0.5}
                    vectorEffect="non-scaling-stroke"
                    onClick={(e) => onProvinceClick(e, p)}
                    onMouseEnter={(e) => onProvinceEnter(e, p)}
                    onMouseLeave={onProvinceLeave}
                  />
                );
              })}
            </g>
          )}

          {/* Settlement icons (zoom-gated so the map stays readable) */}
          <g>
            {world.settlements.map((s) => {
              const k = transform.k;
              if (s.type === 'village' && k < 2.6) return null;
              if ((s.type === 'town' || s.type === 'castle' || s.type === 'holy_site') && k < 1.7) return null;
              return (
                <SettlementIcon
                  key={s.id}
                  s={s}
                  zoomK={k}
                  onClick={(e) => onSettlementClick(e, s)}
                  onMouseEnter={(e) => onSettlementEnter(e, s)}
                  onMouseLeave={onProvinceLeave}
                />
              );
            })}
          </g>

          {/* Nation labels (only for larger / important tiers) */}
          {viewMode !== 'terrain' && (
            <g>
              {nationLabels.map(({ nation, cx, cy }) => {
                const majorTiers = ['empire', 'kingdom', 'sultanate', 'theocracy', 'confederacy'];
                const isMajor = majorTiers.includes(nation.tier) && !nation.overlord;
                if (nation.overlord && transform.k < 3.2) return null;   // vassals only when zoomed in
                if (!isMajor && transform.k < 2.2) return null;          // minors need some zoom
                const cls = 'nation-label ' + (nation.tier === 'empire' ? 'empire' :
                  isMajor ? 'kingdom' : 'minor');
                // Damp label growth when zooming (grows ~k^0.35 instead of k)
                const damp = 1 / Math.pow(transform.k, 0.65);
                // Fade the huge realm names once vassal labels take over
                const fade = isMajor && transform.k > 4.5
                  ? Math.max(0.25, 1 - (transform.k - 4.5) / 5) : 1;
                return (
                  <text key={nation.id} className={cls}
                    transform={`translate(${cx * MAP_W}, ${cy * MAP_W}) scale(${damp.toFixed(4)})`}
                    opacity={fade}>
                    {nation.name.replace(/^(Empire|Kingdom|Sultanate|Theocracy|Confederacy|Duchy|Free City|Principality|Republic|Margraviate|Barony|Jarldom|Emirate|Beylik|Waziriate|Grand Duchy|Wardenship|Enclave|Grove-Kingdom|Prelacy|Templar-March|Cantonment|Fenlands Domain|Free Kingdom|Ordermarch|Vampiric Duchy|Necrotheocracy|Deep-Hold|Wyrm-Cult|Confederation|Merchant-Republic|Free Republic|Barbarian Confederacy|Isle-Kingdom|County|Sultanate|Theocratic Marches|Demarchy|United Clans|Tribal Kingdom|Broken Kingdom|Technocratic Republic|Plombulate|Prince-Bishopric|Khanate|Tribal Federation) of /, '')}
                  </text>
                );
              })}
            </g>
          )}

          {/* Lasso draft (stored normalized; rendered in pixel space) */}
          {lassoDraft && lassoDraft.length > 1 && (
            <path
              className="lasso-path"
              vectorEffect="non-scaling-stroke"
              d={'M' + lassoDraft.map(([x, y]) => `${(x * MAP_W).toFixed(2)},${(y * MAP_W).toFixed(2)}`).join(' L') + (drawing ? '' : ' Z')}
            />
          )}
        </g>
      </svg>

      {tooltip && (
        <div
          className="map-tooltip"
          style={{ left: tooltip.x + 12, top: tooltip.y + 12 }}
        >
          <div>{tooltip.title}</div>
          <div className="sub">{tooltip.subtitle}</div>
        </div>
      )}
    </div>
  );
}

function SettlementIcon({ s, zoomK, onClick, onMouseEnter, onMouseLeave }) {
  // Map-anchored sizing: symbols should feel like they physically sit on the
  // map. We scale them with the map but damped by sqrt(k) so they clearly GROW
  // as you zoom in (never shrink) without ballooning at deep zoom. baseScale
  // makes every glyph noticeably bigger at the fitted view.
  const k = Math.max(0.0001, zoomK);
  const baseScale = 1.7;
  const S = baseScale / Math.sqrt(k);
  const px = s.x * MAP_W;
  const py = s.y * MAP_W;
  const { type } = s;

  // Only render name label at higher zoom or for capitals
  const showLabel = zoomK >= 3.2 || type === 'capital' || (zoomK >= 2 && (type === 'city' || type === 'major_port'));

  let shape;
  let labelY = 16;
  switch (type) {
    case 'capital':
      labelY = 22;
      shape = (
        <g>
          {/* Seat-of-power crown */}
          <path
            d="M-9,6.5 L-9,-3.2 L-4.4,1.4 L0,-7.2 L4.4,1.4 L9,-3.2 L9,6.5 Z"
            fill="#f2c94c" stroke="#3b2408" strokeWidth={1.5} strokeLinejoin="round"
          />
          <rect x={-9} y={4.2} width={18} height={3.4} rx={0.6}
            fill="#c9992e" stroke="#3b2408" strokeWidth={1.2} />
          <circle cx={-9} cy={-3.2} r={1.7} fill="#f6e4a5" stroke="#3b2408" strokeWidth={1} />
          <circle cx={0} cy={-7.4} r={1.9} fill="#f6e4a5" stroke="#3b2408" strokeWidth={1} />
          <circle cx={9} cy={-3.2} r={1.7} fill="#f6e4a5" stroke="#3b2408" strokeWidth={1} />
          <circle cx={0} cy={5.9} r={1.3} fill="#9c2b2b" />
        </g>
      );
      break;
    case 'city':
      labelY = 19;
      shape = (
        <g>
          <circle r={7} fill="#e2c072" stroke="#2a1808" strokeWidth={1.4} />
          <circle r={3.4} fill="none" stroke="#2a1808" strokeWidth={1.3} />
          <circle r={1.2} fill="#2a1808" />
        </g>
      );
      break;
    case 'major_port':
      labelY = 20;
      shape = (
        <g>
          <circle r={8} fill="#7fa5c2" stroke="#1d3348" strokeWidth={1.5} />
          <AnchorPath r={5.4} color="#0e1c29" />
        </g>
      );
      break;
    case 'port':
      labelY = 18;
      shape = (
        <g>
          <circle r={6.4} fill="#a5c0d4" stroke="#22415c" strokeWidth={1.3} />
          <AnchorPath r={4.2} color="#16293a" />
        </g>
      );
      break;
    case 'castle':
      // Keep with two crenellated towers and a gate
      labelY = 18;
      shape = (
        <g>
          <path
            d="M-8,8 L-8,-3 L-6,-3 L-6,-6.5 L-3.5,-6.5 L-3.5,-3 L-1.2,-3 L-1.2,-6.5 L1.2,-6.5 L1.2,-3 L3.5,-3 L3.5,-6.5 L6,-6.5 L6,-3 L8,-3 L8,8 Z"
            fill="#9a7546" stroke="#2a1808" strokeWidth={1.3} strokeLinejoin="round"
          />
          <path d="M-2.2,8 L-2.2,2.5 A2.2,2.6 0 0 1 2.2,2.5 L2.2,8 Z" fill="#2a1808" />
        </g>
      );
      break;
    case 'town':
      // Small gabled house
      labelY = 16;
      shape = (
        <g>
          <path d="M-5,5.5 L-5,-0.5 L0,-5.5 L5,-0.5 L5,5.5 Z"
            fill="#c9a55e" stroke="#2a1808" strokeWidth={1.2} strokeLinejoin="round" />
          <rect x={-1.4} y={1.2} width={2.8} height={4.3} fill="#2a1808" />
        </g>
      );
      break;
    case 'holy_site':
      // Chapel with a cross
      labelY = 18;
      shape = (
        <g>
          <path d="M-5,6 L-5,-0.5 L0,-5 L5,-0.5 L5,6 Z"
            fill="#e5cd8f" stroke="#2a1808" strokeWidth={1.2} strokeLinejoin="round" />
          <line x1={0} y1={-5.4} x2={0} y2={-10} stroke="#2a1808" strokeWidth={1.4} />
          <line x1={-1.9} y1={-8.2} x2={1.9} y2={-8.2} stroke="#2a1808" strokeWidth={1.4} />
        </g>
      );
      break;
    case 'village':
    default:
      labelY = 13;
      shape = (
        <g>
          <circle r={3.1} fill="#3d2a12" stroke="#e8d5a8" strokeWidth={1.1} />
        </g>
      );
  }

  return (
    <g
      className={`settlement ${type}`}
      transform={`translate(${px.toFixed(2)}, ${py.toFixed(2)}) scale(${S.toFixed(5)})`}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {shape}
      {showLabel && (
        <text y={labelY} textAnchor="middle" className="s-label">
          {s.name}
        </text>
      )}
    </g>
  );
}

function AnchorPath({ r, color = '#0d0704' }) {
  const w = r * 0.42;
  return (
    <g stroke={color} strokeWidth={Math.max(1.1, r * 0.26)} fill="none" strokeLinecap="round">
      <circle cx={0} cy={-r * 0.62} r={r * 0.24} />
      <line x1={0} y1={-r * 0.4} x2={0} y2={r * 0.75} />
      <path d={`M ${-r * 0.75} ${r * 0.2} Q 0 ${r * 1.05} ${r * 0.75} ${r * 0.2}`} />
      <line x1={-w} y1={-r * 0.15} x2={w} y2={-r * 0.15} />
    </g>
  );
}
