import React, { useEffect, useState } from 'react';
import { fetchSettlement } from '../lib/api';

const TYPE_LABEL = {
  capital: 'Capital City',
  city: 'City',
  town: 'Town',
  village: 'Village',
  castle: 'Castle',
  port: 'Port',
  major_port: 'Major Port',
  holy_site: 'Holy Site',
};

export default function SettlementDialog({ settlementId, onClose, onSelectNation }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!settlementId) { setData(null); return; }
    fetchSettlement(settlementId).then(setData).catch(() => setData(null));
  }, [settlementId]);

  if (!settlementId) return null;
  const s = data?.settlement;
  const n = data?.nation;
  const prov = data?.province;

  return (
    <div className="settlement-dialog" onClick={onClose} data-testid="settlement-dialog">
      <div className="card" onClick={(e) => e.stopPropagation()}>
        <div className="head" style={{ borderBottomColor: n?.color }}>
          <button className="close" onClick={onClose} data-testid="settlement-dialog-close">✕</button>
          <h3>{s?.name || 'Loading…'}</h3>
          <div className="sub">
            {s && TYPE_LABEL[s.type]}
            {n && <> · <a href="#" onClick={(e) => { e.preventDefault(); onSelectNation(n.id); onClose(); }}
              style={{ color: '#5c1a1a', textDecoration: 'underline' }}>{n.name}</a></>}
            {prov && <> · {prov.name}</>}
          </div>
        </div>
        <div className="body">
          {s?.lore}
        </div>
      </div>
    </div>
  );
}
