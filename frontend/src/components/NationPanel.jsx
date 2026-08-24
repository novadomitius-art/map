import React, { useEffect, useState } from 'react';
import { fetchNation } from '../lib/api';

const TIER_LABEL = {
  empire: 'Empire',  kingdom: 'Kingdom', sultanate: 'Sultanate', theocracy: 'Theocracy',
  confederacy: 'Confederacy', duchy: 'Duchy', principality: 'Principality',
  margraviate: 'Margraviate', barony: 'Barony', jarldom: 'Jarldom', emirate: 'Emirate',
  beylik: 'Beylik', waziriate: 'Waziriate', grand_duchy: 'Grand Duchy',
  wardenship: 'Wardenship', enclave: 'Enclave', grove_kingdom: 'Grove-Kingdom',
  prelacy: 'Prelacy', templar_march: 'Templar-March', cantonment: 'Cantonment',
  domain: 'Fen Domain', free_kingdom: 'Free Kingdom', order_march: 'Order-March',
  necrotheocracy: 'Necrotheocracy', hold: 'Deep-Hold', cult_state: 'Cult-State',
  confederation: 'Confederation', merchant_republic: 'Merchant-Republic',
  republic: 'Republic', khanate: 'Khanate', federation: 'Tribal Federation',
  free_city: 'Free City', county: 'County', prince_bishopric: 'Prince-Bishopric',
  theocratic_march: 'Theocratic March', demarchy: 'Demarchy',
  clan_union: 'Clan Union', tribal_kingdom: 'Tribal Kingdom',
  broken_kingdom: 'Broken Kingdom', technocracy: 'Technocracy',
  plombulate: 'Plombulate',
};

function tierLabel(t) { return TIER_LABEL[t] || t.replace(/_/g, ' '); }

export default function NationPanel({ nationId, world, onSelectNation, onClose, onSelectSettlement }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!nationId) return;
    setLoading(true);
    fetchNation(nationId).then((d) => {
      setDetail(d);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [nationId]);

  if (!nationId) return null;
  const n = detail?.nation;
  const religion = detail?.religion;
  const overlord = detail?.overlord;
  const vassals = detail?.vassals || [];
  const provinces = detail?.provinces || [];
  const settlements = detail?.settlements || [];
  const relations = detail?.relations || [];

  return (
    <div className="nation-panel" data-testid="nation-panel">
      <div className="np-header" style={{ borderBottomColor: n?.color }}>
        <button className="np-close" onClick={onClose} data-testid="nation-panel-close">✕</button>
        <div className="np-crest" style={{ background: `radial-gradient(circle, ${n?.color || '#c9a24a'} 0%, #3d0d0d 100%)` }} />
        <div className="np-title">
          <div className="np-name">{n?.name}</div>
          <div className="np-tier">{n ? tierLabel(n.tier) : ''}{overlord ? `  ·  Vassal of ${overlord.name}` : ''}</div>
        </div>
      </div>

      <div className="np-body">
        {loading && <div style={{ padding: '20px', textAlign: 'center' }}>Loading…</div>}
        {!loading && n && (
          <>
            <div className="np-motto">“{n.motto}”</div>

            <div className="np-section">
              <div className="np-kv">
                <div className="k">Ruler</div><div className="v">{n.ruler}</div>
                <div className="k">Title</div><div className="v">{n.ruler_title}</div>
                <div className="k">Capital</div>
                <div className="v">
                  {(() => {
                    const cap = settlements.find((s) => s.type === 'capital') || settlements.find((s) => s.type === 'city');
                    if (!cap) return '—';
                    return (
                      <a href="#" onClick={(e) => { e.preventDefault(); onSelectSettlement(cap.id); }} style={{ color: '#5c1a1a', textDecoration: 'underline' }}>
                        {cap.name}
                      </a>
                    );
                  })()}
                </div>
                <div className="k">Founded</div><div className="v">{n.founded}</div>
                <div className="k">Culture</div><div className="v">{n.culture}</div>
                <div className="k">Religion</div><div className="v">{religion?.name || '—'}</div>
                <div className="k">Provinces</div><div className="v">{provinces.length}</div>
                <div className="k">Settlements</div><div className="v">{settlements.length}</div>
              </div>
            </div>

            <div className="np-section">
              <div className="np-section-title">Realm Strength</div>
              <div className="np-metric"><div style={{ width: 60, fontSize: 12, fontVariant: 'small-caps', color: '#4a3620' }}>Army</div>
                <div className="bar"><div className="fill" style={{ width: `${n.army}%` }}/></div>
                <div style={{ width: 32, textAlign: 'right' }}>{n.army}</div>
              </div>
              <div className="np-metric"><div style={{ width: 60, fontSize: 12, fontVariant: 'small-caps', color: '#4a3620' }}>Economy</div>
                <div className="bar"><div className="fill" style={{ width: `${n.economy}%` }}/></div>
                <div style={{ width: 32, textAlign: 'right' }}>{n.economy}</div>
              </div>
              {overlord && typeof n.influence === 'number' && (
                <div className="np-metric" data-testid="nation-influence">
                  <div style={{ width: 60, fontSize: 12, fontVariant: 'small-caps', color: '#4a3620' }}>Influence</div>
                  <div className="bar"><div className="fill influence" style={{ width: `${n.influence}%` }}/></div>
                  <div style={{ width: 32, textAlign: 'right' }}>{n.influence}</div>
                </div>
              )}
            </div>

            <div className="np-section">
              <div className="np-section-title">Chronicle</div>
              <div className="np-lore">
                {n.lore.split('\n\n').map((p, i) => <p key={i}>{p}</p>)}
              </div>
            </div>

            {religion && (
              <div className="np-section">
                <div className="np-section-title">Faith</div>
                <div style={{ fontSize: 14 }}>
                  <div style={{ fontFamily: 'Cinzel, serif', fontSize: 13, letterSpacing: 1 }}>{religion.name}</div>
                  <div style={{ fontStyle: 'italic', color: '#5c1a1a', margin: '2px 0 4px' }}>{religion.deity}</div>
                  <div>{religion.lore}</div>
                </div>
              </div>
            )}

            {vassals.length > 0 && (
              <div className="np-section">
                <div className="np-section-title">Sworn Vassals ({vassals.length}) — by Influence</div>
                {[...vassals].sort((a, b) => (b.influence || 0) - (a.influence || 0)).map((v) => (
                  <div key={v.id} className="np-list-item vassal" onClick={() => onSelectNation(v.id)} data-testid={`vassal-row-${v.id}`}>
                    <span className="name">{v.name}</span>
                    <span className="type">{tierLabel(v.tier)}</span>
                    <div className="np-metric small">
                      <div className="bar"><div className="fill influence" style={{ width: `${v.influence || 10}%` }}/></div>
                      <div style={{ width: 26, textAlign: 'right', fontSize: 11 }}>{v.influence ?? '—'}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {relations.length > 0 && (
              <div className="np-section">
                <div className="np-section-title">Foreign Relations</div>
                {relations.map((r, i) => {
                  const otherId = r.a === n.id ? r.b : r.a;
                  const other = world.nations.find((x) => x.id === otherId);
                  if (!other) return null;
                  return (
                    <div key={i} className="np-relation">
                      <span className={`badge ${r.type}`}>{r.type.replace('_', ' ')}</span>
                      <a href="#" onClick={(e) => { e.preventDefault(); onSelectNation(other.id); }}
                         style={{ color: '#2b1b0d', textDecoration: 'underline' }}>
                        {other.name}
                      </a>
                    </div>
                  );
                })}
              </div>
            )}

            <div className="np-section">
              <div className="np-section-title">Notable Settlements</div>
              {settlements.map((s) => (
                <div key={s.id} className="np-list-item" onClick={() => onSelectSettlement(s.id)}>
                  <span className="name">{s.name}</span>
                  <span className="type">{s.type.replace('_', ' ')}</span>
                  <div className="desc">{s.description}</div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
