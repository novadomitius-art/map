import React from 'react';

const rows = [
  { icon: (
      <svg width="18" height="18" viewBox="-10 -10 20 20">
        <circle r="7" fill="#f6e4a5" stroke="#3b2408" strokeWidth="1.2" />
        <polygon points={pts(4)} fill="#b8873a" stroke="#3b2408" strokeWidth="0.5" />
      </svg>), label: 'Capital City' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <circle r="6" fill="#e2c072" stroke="#2a1808" strokeWidth="1" />
      <circle r="3" fill="#2a1808" />
    </svg>), label: 'City / Major Settlement' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <circle r="5" fill="#3d2a12" stroke="#f2e3c1" strokeWidth="1.2" />
    </svg>), label: 'Town / Settlement' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <circle r="4" fill="#3d2a12" />
    </svg>), label: 'Village' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <polygon points="0,-8 8,6 -8,6" fill="#8a5a2a" stroke="#2a1808" strokeWidth="1.2" />
    </svg>), label: 'Castle / Fortress' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <circle r="6" fill="#7fa5c2" stroke="#2a1808" strokeWidth="1" />
      <line x1="0" y1="-4" x2="0" y2="5" stroke="#0d0704" strokeWidth="1.2"/>
      <path d="M -4 2 Q 0 6 4 2" stroke="#0d0704" fill="none" strokeWidth="1.2"/>
      <line x1="-2" y1="-2" x2="2" y2="-2" stroke="#0d0704" strokeWidth="1.2"/>
    </svg>), label: 'Major Port' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <circle r="5" fill="#a5c0d4" stroke="#2a1808" strokeWidth="1" />
      <line x1="0" y1="-3" x2="0" y2="4" stroke="#0d0704" strokeWidth="1"/>
      <path d="M -3 2 Q 0 5 3 2" stroke="#0d0704" fill="none" strokeWidth="1"/>
    </svg>), label: 'Port' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <circle r="6" fill="#d9b463" stroke="#2a1808" strokeWidth="1" />
      <line x1="0" y1="-5" x2="0" y2="5" stroke="#2a1808" strokeWidth="1.5"/>
      <line x1="-5" y1="0" x2="5" y2="0" stroke="#2a1808" strokeWidth="1.5"/>
    </svg>), label: 'Holy Site' },
];

function pts(size) {
  const arr = [];
  for (let i = 0; i < 10; i++) {
    const a = (Math.PI / 5) * i - Math.PI / 2;
    const r = i % 2 === 0 ? size : size * 0.45;
    arr.push(`${(Math.cos(a) * r).toFixed(1)},${(Math.sin(a) * r).toFixed(1)}`);
  }
  return arr.join(' ');
}

export default function Legend() {
  return (
    <div className="legend">
      <div className="title">SYMBOLS OF THE MAP</div>
      {rows.map((r, i) => (
        <div className="legend-row" key={i}>
          {r.icon} <span>{r.label}</span>
        </div>
      ))}
    </div>
  );
}
