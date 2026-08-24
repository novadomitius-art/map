import React, { useEffect, useState, useCallback } from 'react';
import '@/App.css';
import { fetchMapState, transferTerritory, resetWorld, applyTrace, getTraces, deleteTrace } from '@/lib/api';
import MapCanvas from '@/components/MapCanvas';
import TopBar from '@/components/TopBar';
import ViewSwitcher from '@/components/ViewSwitcher';
import NationPanel from '@/components/NationPanel';
import SettlementDialog from '@/components/SettlementDialog';
import FreeformEditor from '@/components/FreeformEditor';
import TracePanel from '@/components/TracePanel';
import Legend from '@/components/Legend';

function App() {
  const [world, setWorld] = useState(null);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('political');
  const [selectedNation, setSelectedNation] = useState(null);
  const [selectedSettlement, setSelectedSettlement] = useState(null);

  // Edit state
  const [editorMode, setEditorMode] = useState(null); // null|'pick-source'|'pick-target'|'draw-lasso'|'trace-draw'
  const [editorSource, setEditorSource] = useState(null);
  const [editorTarget, setEditorTarget] = useState(null);
  const [lassoDraft, setLassoDraft] = useState(null);
  const [toast, setToast] = useState(null);

  // Trace mode state
  const [traceAction, setTraceAction] = useState('set_terrain');
  const [traceValue, setTraceValue] = useState('');
  const [traceCount, setTraceCount] = useState(0);

  useEffect(() => {
    fetchMapState().then(setWorld).catch((e) => setError(e.message));
    getTraces().then((d) => setTraceCount(d.count)).catch(() => {});
  }, []);

  const showToast = useCallback((msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2400);
  }, []);

  const onSelectNation = useCallback((id) => {
    setSelectedNation(id);
    setSelectedSettlement(null);
  }, []);

  const onEditPick = useCallback((kind, nationId) => {
    if (kind === 'source') {
      setEditorSource(nationId);
      setEditorMode('pick-target');
    } else if (kind === 'target') {
      if (nationId === editorSource) {
        showToast('Source and target must differ.');
        return;
      }
      setEditorTarget(nationId);
      setEditorMode('draw-lasso');
    }
  }, [editorSource, showToast]);

  const startEdit = () => {
    setEditorSource(null);
    setEditorTarget(null);
    setLassoDraft(null);
    setEditorMode('pick-source');
    setSelectedNation(null);
  };
  const cancelEdit = () => {
    setEditorMode(null);
    setEditorSource(null);
    setEditorTarget(null);
    setLassoDraft(null);
  };

  const onLassoCommit = (points) => {
    // Called by MapCanvas when the user releases mouse; we just keep the shape
    // as the pending lasso until they hit Commit.
    setLassoDraft(points);
  };

  const confirmTransfer = async () => {
    if (!editorSource || !editorTarget || !lassoDraft || lassoDraft.length < 3) return;
    try {
      const res = await transferTerritory(editorSource, editorTarget, lassoDraft);
      if (res && res.ok) {
        // Refresh the state so nation totals update as well.
        const fresh = await fetchMapState();
        setWorld(fresh);
        const area = (res.transferred_area * 100).toFixed(3);
        showToast(`Territory redrawn — ${area}% of the map ceded.`);
      } else {
        showToast('Nothing was transferred (lasso may not intersect).');
      }
    } catch (e) {
      showToast('Transfer failed: ' + (e.response?.data?.detail || e.message));
    }
    cancelEdit();
  };

  const onReset = async () => {
    await resetWorld();
    const fresh = await fetchMapState();
    setWorld(fresh);
    setSelectedNation(null);
    setSelectedSettlement(null);
    showToast('The map has been restored (your traces were kept).');
  };

  // ---- Trace mode ----
  const traceActive = editorMode === 'trace-draw';
  const toggleTrace = () => {
    if (traceActive) {
      setEditorMode(null);
      setLassoDraft(null);
    } else {
      setEditorSource(null);
      setEditorTarget(null);
      setLassoDraft(null);
      setSelectedNation(null);
      setEditorMode('trace-draw');
    }
  };

  const onApplyTrace = async () => {
    if (!lassoDraft || lassoDraft.length < 3) return;
    try {
      const res = await applyTrace(traceAction, lassoDraft, traceValue || null);
      if (res && res.ok) {
        const fresh = await fetchMapState();
        setWorld(fresh);
        setTraceCount((c) => c + 1);
        const area = (res.affected_area * 100).toFixed(3);
        showToast(`Trace applied — ${area}% of the map corrected.`);
      } else {
        showToast(res?.message || 'Trace had no effect.');
      }
    } catch (e) {
      showToast('Trace failed: ' + (e.response?.data?.detail || e.message));
    }
    setLassoDraft(null);
  };

  const onUndoLastTrace = async () => {
    try {
      const d = await getTraces();
      if (!d.traces.length) return;
      const last = d.traces[d.traces.length - 1];
      await deleteTrace(last.id);
      const fresh = await fetchMapState();
      setWorld(fresh);
      setTraceCount(d.traces.length - 1);
      showToast('Last trace removed.');
    } catch (e) {
      showToast('Undo failed: ' + (e.response?.data?.detail || e.message));
    }
  };

  if (error) return <div style={{ padding: 40, color: '#f2e3c1' }}>Failed to load: {error}</div>;
  if (!world) return <div style={{ padding: 40, color: '#f2e3c1', fontFamily: 'Cinzel, serif', letterSpacing: 2 }}>Loading the world of Kelvaros…</div>;

  const sourceNation = editorSource ? world.nations.find((n) => n.id === editorSource) : null;
  const targetNation = editorTarget ? world.nations.find((n) => n.id === editorTarget) : null;

  return (
    <div className="App">
      <TopBar
        continent={world.continent}
        year={world.current_year}
        subtitle="AND ITS CONSTITUENT REALMS"
      />

      <MapCanvas
        world={world}
        viewMode={viewMode}
        selectedNationId={selectedNation}
        onSelectNation={onSelectNation}
        onSelectSettlement={setSelectedSettlement}
        editorMode={editorMode}
        editorSource={editorSource}
        editorTarget={editorTarget}
        onEditPick={onEditPick}
        onLassoCommit={onLassoCommit}
        lassoDraft={lassoDraft}
        setLassoDraft={setLassoDraft}
      />

      <ViewSwitcher mode={viewMode} onChange={setViewMode} />

      <FreeformEditor
        mode={editorMode === 'trace-draw' ? null : editorMode}
        source={sourceNation}
        target={targetNation}
        onStart={startEdit}
        onCancel={cancelEdit}
        onConfirmTransfer={confirmTransfer}
        hasLasso={lassoDraft && lassoDraft.length >= 3}
        onReset={onReset}
      />

      <TracePanel
        active={traceActive}
        onToggle={toggleTrace}
        action={traceAction}
        setAction={setTraceAction}
        value={traceValue}
        setValue={setTraceValue}
        nations={world.nations}
        hasLasso={lassoDraft && lassoDraft.length >= 3}
        onApply={onApplyTrace}
        onClearLasso={() => setLassoDraft(null)}
        traceCount={traceCount}
        onUndoLast={onUndoLastTrace}
      />

      <Legend />

      {selectedNation && (
        <NationPanel
          nationId={selectedNation}
          world={world}
          onSelectNation={onSelectNation}
          onSelectSettlement={setSelectedSettlement}
          onClose={() => setSelectedNation(null)}
        />
      )}

      {selectedSettlement && (
        <SettlementDialog
          settlementId={selectedSettlement}
          onClose={() => setSelectedSettlement(null)}
          onSelectNation={onSelectNation}
        />
      )}

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

export default App;
