import React from 'react';

export default function TopBar({ continent, year, subtitle }) {
  return (
    <div className="top-bar">
      <div className="title">{continent}</div>
      <div className="subtitle">{subtitle}</div>
      <div className="year" data-testid="top-bar-year">{year}</div>
    </div>
  );
}
