import React from 'react';

/**
 * FreeformEditor
 * Shows a step-by-step toolbar for lasso-transfer.
 *
 * Props:
 *  mode:         null | 'pick-source' | 'pick-target' | 'draw-lasso'
 *  source, target: nation objects
 *  onStart(): begins pick-source flow
 *  onCancel()
 *  onConfirmTransfer(): commit the drawn lasso to backend
 *  hasLasso:  boolean (whether the user has drawn a lasso)
 *  onReset(): reset entire world back to seed
 */
export default function FreeformEditor({
  mode, source, target, onStart, onCancel, onConfirmTransfer, hasLasso, onReset,
}) {
  if (!mode) {
    return (
      <div className="editor-bar" data-testid="editor-bar-idle">
        <span className="step">EDIT</span>
        <span className="instr">Redraw the borders of Kelvaros.</span>
        <button onClick={onStart} data-testid="editor-start">◆ Begin Border Edit</button>
        <button onClick={onReset} data-testid="editor-reset" className="danger">↻ Reset Map</button>
      </div>
    );
  }
  return (
    <div className="editor-bar" data-testid="editor-bar-active">
      {mode === 'pick-source' && (
        <>
          <span className="step">STEP 1</span>
          <span className="instr">Click the <b>source</b> nation — the realm you will cut from.</span>
        </>
      )}
      {mode === 'pick-target' && (
        <>
          <span className="step">STEP 2</span>
          <span className="instr">Source: <b>{source?.name}</b>. Now click the <b>target</b> nation to receive the land.</span>
        </>
      )}
      {mode === 'draw-lasso' && (
        <>
          <span className="step">STEP 3</span>
          <span className="instr">
            <b>{source?.name}</b> → <b>{target?.name}</b>. Now draw a lasso across the border to redraw it.
          </span>
          <button
            disabled={!hasLasso}
            onClick={onConfirmTransfer}
            data-testid="editor-confirm"
            style={{ opacity: hasLasso ? 1 : 0.5, cursor: hasLasso ? 'pointer' : 'not-allowed' }}
          >✓ Commit Transfer</button>
        </>
      )}
      <button onClick={onCancel} className="danger" data-testid="editor-cancel">✕ Cancel</button>
    </div>
  );
}
