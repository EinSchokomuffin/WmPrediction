"use client";

import { useState } from "react";

import { runTournamentPlayout } from "@/lib/api";
import type { GroupMatch, KnockoutMatch, TournamentPlayoutResponse } from "@/types/tournament";

const STAGE_LABELS: Record<string, string> = {
  round_of_32: "Round of 32",
  round_of_16: "Achtelfinale",
  quarter_finals: "Viertelfinale",
  semi_finals: "Halbfinale",
  third_place: "Spiel um Platz 3",
  final: "Finale",
};

function renderScore(match: KnockoutMatch) {
  if (match.home_score === null || match.away_score === null) {
    return "offen";
  }
  const base = `${match.home_score}:${match.away_score}`;
  if (match.home_score_et !== null && match.away_score_et !== null) {
    const et = ` n.V. ${match.home_score_et}:${match.away_score_et}`;
    if (match.home_score_pen !== null && match.away_score_pen !== null) {
      return `${base}${et} i.E. ${match.home_score_pen}:${match.away_score_pen}`;
    }
    return `${base}${et}`;
  }
  return base;
}

export function TournamentPlayoutCard() {
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState("Starte hier eine komplette Turniersimulation mit Gruppenphase und K.o.-Baum.");
  const [result, setResult] = useState<TournamentPlayoutResponse | null>(null);

  const handleRun = async () => {
    setIsRunning(true);
    try {
      const response = await runTournamentPlayout();
      setResult(response);
      setMessage("Turnier komplett simuliert. Alle Resultate stehen unten.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Simulation fehlgeschlagen.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <section className="grid">
      <article className="card">
        <h2>Komplettsimulation</h2>
        <p>{message}</p>
        <button onClick={handleRun} disabled={isRunning}>
          {isRunning ? "Simulation laeuft..." : "Turnier komplett simulieren"}
        </button>
      </article>

      {result && (
        <>
          {Object.entries(result.group_matches).map(([group, matches]) => (
            <article className="card" key={group}>
              <h2>Gruppe {group} Ergebnisse</h2>
              <div style={{ display: "grid", gap: 8 }}>
                {(matches as GroupMatch[]).map((match) => (
                  <div key={match.match_number} style={{ borderBottom: "1px solid #334155", paddingBottom: 8 }}>
                    <strong>MD {match.matchday}</strong>: {match.home} {match.home_goals ?? "-"}:{match.away_goals ?? "-"} {match.away}
                  </div>
                ))}
              </div>
            </article>
          ))}

          {Object.entries(result.bracket).map(([stage, matches]) => (
            <article className="card" key={stage}>
              <h2>{STAGE_LABELS[stage] ?? stage}</h2>
              <div style={{ display: "grid", gap: 8 }}>
                {(matches as KnockoutMatch[]).map((match) => (
                  <div key={match.match_number} style={{ borderBottom: "1px solid #334155", paddingBottom: 8 }}>
                    <span className="badge">S{match.match_number}</span>
                    <div>
                      {match.home_team} vs {match.away_team}
                    </div>
                    <div>{renderScore(match)}</div>
                  </div>
                ))}
              </div>
            </article>
          ))}
        </>
      )}
    </section>
  );
}