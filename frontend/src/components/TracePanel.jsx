import React from 'react';

const TERRAINS = ['plains', 'forest', 'mountain', 'hills', 'coast', 'desert', 'swamp'];

const ACTIONS = [
  { id: 'set_terrain', label: 'Paint Terrain', hint: 'Corrects the terrain type inside your shape.' },
  { id: 'assign_nation', label: 'Assign to Nation', hint: 'Gives the traced land to a chosen realm.' },
  { id: 'carve_water', label: 'Carve Water', hint: 'Turns the traced area into open sea.' },
  { id: 'restore_land', label: 'Restore Land', hint: 'Reclaims sea as land for a chosen realm.' },
];

/**
 * TracePanel — manual correction tool.
 * The user draws a polygon on the map, chooses what it means, and commits.
 */
export default function TracePanel({
  active,            // bool: trace mode on
  onToggle,          // () => void
  action,            // one of ACTIONS ids
  setAction,
  value,             // terrain name or nation id
  setValue,
  nations,           // world.nations
  hasLasso,
  onApply,           // commit trace
  onClearLasso,
  traceCount,        // number of saved traces
  onUndoLast,        // delete most recent trace
}) {
  const needsNation = action === 'assign_nation' || action === 'restore_land';
  const needsTerrain = action === 'set_terrain';
  const current = ACTIONS.find((a) => a.id === action);

  if (!active) {
    return (
      <div className="trace-panel collapsed" data-testid="trace-panel-collapsed">
        <button className="trace-toggle" onClick={onToggle} data-testid="trace-toggle-on">
          ✎ Trace Mode
        </button>
      </div>
    );
  }

  return (
    <div className="trace-panel" data-testid="trace-panel">
      <div className="head">
        <span className="title">Trace &amp; Correct</span>
        <button className="close" onClick={onToggle} data-testid="trace-toggle-off">✕</button>
      </div>

      <label className="lbl">Action</label>
      <select
        className="trace-select"
        value={action}
        onChange={(e) => { setAction(e.target.value); setValue(''); }}
        data-testid="trace-action-select"
      >
        {ACTIONS.map((a) => <option key={a.id} value={a.id}>{a.label}</option>)}
      </select>
      <div className="hint">{current?.hint}</div>

      {needsTerrain && (
        <>
          <label className="lbl">Terrain</label>
          <select
            className="trace-select"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            data-testid="trace-terrain-select"
          >
            <option value="">— choose terrain —</option>
            {TERRAINS.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </>
      )}

      {needsNation && (
        <>
          <label className="lbl">Nation</label>
          <select
            className="trace-select"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            data-testid="trace-nation-select"
          >
            <option value="">— choose nation —</option>
            {[...nations].sort((a, b) => a.name.localeCompare(b.name)).map((n) => (
              <option key={n.id} value={n.id}>{n.name}</option>
            ))}
          </select>
        </>
      )}

      <div className="hint draw-hint">
        {hasLasso
          ? 'Shape captured. Apply it, or draw again to replace.'
          : 'Draw a closed shape on the map with your mouse.'}
      </div>

      <div className="row">
        <button
          className="apply"
          disabled={!hasLasso || (!value && (needsNation || needsTerrain))}
          onClick={onApply}
          data-testid="trace-apply"
        >✓ Apply Trace</button>
        <button className="ghost" disabled={!hasLasso} onClick={onClearLasso} data-testid="trace-clear">
          Clear
        </button>
      </div>

      <div className="row foot">
        <span className="count" data-testid="trace-count">{traceCount} saved</span>
        <button className="ghost" disabled={!traceCount} onClick={onUndoLast} data-testid="trace-undo">
          ↩ Undo Last
        </button>
      </div>
    </div>
  );
}
