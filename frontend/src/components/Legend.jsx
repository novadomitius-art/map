import React from 'react';

const rows = [
  { icon: (
      <svg width="18" height="18" viewBox="-10 -10 20 20">
        <path d="M-8,6 L-8,-3 L-3.9,1 L0,-6.4 L3.9,1 L8,-3 L8,6 Z"
          fill="#f2c94c" stroke="#3b2408" strokeWidth="1.2" strokeLinejoin="round" />
        <rect x="-8" y="4" width="16" height="2.8" fill="#c9992e" stroke="#3b2408" strokeWidth="0.9" />
      </svg>), label: 'Capital City' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <circle r="6.5" fill="#e2c072" stroke="#2a1808" strokeWidth="1.3" />
      <circle r="3.1" fill="none" stroke="#2a1808" strokeWidth="1.2" />
      <circle r="1.1" fill="#2a1808" />
    </svg>), label: 'City / Major Settlement' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <path d="M-6,6.5 L-6,-0.6 L0,-6.6 L6,-0.6 L6,6.5 Z"
        fill="#c9a55e" stroke="#2a1808" strokeWidth="1.2" strokeLinejoin="round" />
      <rect x="-1.7" y="1.4" width="3.4" height="5.1" fill="#2a1808" />
    </svg>), label: 'Town / Settlement' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <circle r="3.4" fill="#3d2a12" stroke="#e8d5a8" strokeWidth="1.2" />
    </svg>), label: 'Village' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <path d="M-8,8 L-8,-3 L-6,-3 L-6,-6.5 L-3.5,-6.5 L-3.5,-3 L-1.2,-3 L-1.2,-6.5 L1.2,-6.5 L1.2,-3 L3.5,-3 L3.5,-6.5 L6,-6.5 L6,-3 L8,-3 L8,8 Z"
        fill="#9a7546" stroke="#2a1808" strokeWidth="1.2" strokeLinejoin="round" />
      <path d="M-2.2,8 L-2.2,2.5 A2.2,2.6 0 0 1 2.2,2.5 L2.2,8 Z" fill="#2a1808" />
    </svg>), label: 'Castle / Fortress' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <circle r="6.6" fill="#7fa5c2" stroke="#1d3348" strokeWidth="1.4" />
      <circle cx="0" cy="-3.4" r="1.3" fill="none" stroke="#0e1c29" strokeWidth="1.2" />
      <line x1="0" y1="-2.2" x2="0" y2="4" stroke="#0e1c29" strokeWidth="1.3" strokeLinecap="round"/>
      <path d="M -4 1 Q 0 6 4 1" stroke="#0e1c29" fill="none" strokeWidth="1.3" strokeLinecap="round"/>
      <line x1="-2.2" y1="-0.8" x2="2.2" y2="-0.8" stroke="#0e1c29" strokeWidth="1.3" strokeLinecap="round"/>
    </svg>), label: 'Major Port' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <circle r="5.6" fill="#a5c0d4" stroke="#22415c" strokeWidth="1.2" />
      <circle cx="0" cy="-2.8" r="1.1" fill="none" stroke="#16293a" strokeWidth="1.1" />
      <line x1="0" y1="-1.8" x2="0" y2="3.3" stroke="#16293a" strokeWidth="1.1" strokeLinecap="round"/>
      <path d="M -3.2 0.8 Q 0 4.6 3.2 0.8" stroke="#16293a" fill="none" strokeWidth="1.1" strokeLinecap="round"/>
    </svg>), label: 'Port' },
  { icon: (<svg width="18" height="18" viewBox="-10 -10 20 20">
      <path d="M-6,7 L-6,-0.6 L0,-6 L6,-0.6 L6,7 Z"
        fill="#e5cd8f" stroke="#2a1808" strokeWidth="1.2" strokeLinejoin="round" />
      <line x1="0" y1="-6.4" x2="0" y2="-9.6" stroke="#2a1808" strokeWidth="1.5"/>
      <line x1="-2.2" y1="-8.2" x2="2.2" y2="-8.2" stroke="#2a1808" strokeWidth="1.5"/>
    </svg>), label: 'Holy Site' },
];

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
