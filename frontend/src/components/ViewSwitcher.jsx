import React from 'react';

const MODES = [
  { id: 'political', label: 'Political', icon: '⚔' },
  { id: 'terrain',   label: 'Terrain',   icon: '▲' },
  { id: 'religion',  label: 'Religion',  icon: '✱' },
  { id: 'vassals',   label: 'Vassals',   icon: '✡' },
  { id: 'provinces', label: 'Provinces', icon: '▦' },
];

export default function ViewSwitcher({ mode, onChange }) {
  return (
    <div className="view-switcher">
      <div className="header">MAP MODE</div>
      {MODES.map((m) => (
        <button
          key={m.id}
          data-testid={`view-btn-${m.id}`}
          className={'view-btn ' + (m.id === mode ? 'active' : '')}
          onClick={() => onChange(m.id)}
        >
          <span className="icon">{m.icon}</span>
          {m.label}
        </button>
      ))}
    </div>
  );
}
