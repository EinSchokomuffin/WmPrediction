interface BracketListProps {
  matches: [string, string | null][];
}

export function BracketList({ matches }: BracketListProps) {
  return (
    <div className="card">
      <h2>Round of 32</h2>
      <div className="grid">
        {matches.map(([home, away], idx) => (
          <div key={`${home}-${away ?? "tbd"}-${idx}`} style={{ borderBottom: "1px solid #334155", paddingBottom: 8 }}>
            <span className="badge">S{73 + idx}</span>
            <p>
              {home} vs {away ?? "TBD"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
