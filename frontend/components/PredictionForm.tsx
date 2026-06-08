"use client";

import { useMemo, useState } from "react";

import { predictMatch } from "@/lib/api";
import type { GroupMap, MatchPredictionResult } from "@/types/tournament";

interface PredictionFormProps {
  groups: GroupMap;
}

export function PredictionForm({ groups }: PredictionFormProps) {
  const teams = useMemo(() => Object.values(groups).flat().map((team) => team.name), [groups]);
  const [homeTeam, setHomeTeam] = useState(teams[0] ?? "");
  const [awayTeam, setAwayTeam] = useState(teams[1] ?? teams[0] ?? "");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("Wähle zwei Teams aus und berechne die Prognose.");
  const [result, setResult] = useState<MatchPredictionResult | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setResult(null);
    try {
      const prediction = await predictMatch(homeTeam, awayTeam);
      setResult(prediction);
      setMessage("Prognose berechnet.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Prediction fehlgeschlagen.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="grid" style={{ maxWidth: 760 }}>
      <article className="card hero-card">
        <h2>Spielprognose</h2>
        <p>{message}</p>

        <form onSubmit={handleSubmit} className="prediction-form">
          <label>
            <span>Heimteam</span>
            <select value={homeTeam} onChange={(event) => setHomeTeam(event.target.value)}>
              {teams.map((team) => (
                <option key={`home-${team}`} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>Auswärtsteam</span>
            <select value={awayTeam} onChange={(event) => setAwayTeam(event.target.value)}>
              {teams.map((team) => (
                <option key={`away-${team}`} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </label>

          <button type="submit" disabled={isLoading || homeTeam === awayTeam}>
            {isLoading ? "Berechnet..." : "Ergebnis prognostizieren"}
          </button>
        </form>

        {homeTeam === awayTeam && <p>Bitte zwei unterschiedliche Teams auswählen.</p>}
      </article>

      {result && (
        <article className="card">
          <h2>
            {homeTeam} vs {awayTeam}
          </h2>
          <div className="prediction-grid">
            <div>
              <strong>Heimsieg</strong>
              <div>{(result.home_win_prob * 100).toFixed(1)}%</div>
            </div>
            <div>
              <strong>Unentschieden</strong>
              <div>{(result.draw_prob * 100).toFixed(1)}%</div>
            </div>
            <div>
              <strong>Auswärtssieg</strong>
              <div>{(result.away_win_prob * 100).toFixed(1)}%</div>
            </div>
            <div>
              <strong>Erwartete Tore {homeTeam}</strong>
              <div>{result.expected_home_goals.toFixed(2)}</div>
            </div>
            <div>
              <strong>Erwartete Tore {awayTeam}</strong>
              <div>{result.expected_away_goals.toFixed(2)}</div>
            </div>
            <div>
              <strong>Modellvertrauen</strong>
              <div>{(result.confidence * 100).toFixed(1)}%</div>
            </div>
          </div>
        </article>
      )}
    </section>
  );
}