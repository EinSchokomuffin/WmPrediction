import Link from "next/link";

import { getSimulation } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const simulation = await getSimulation().catch(() => ({ winner_probabilities: {} }));
  const top = Object.entries(simulation.winner_probabilities)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  return (
    <section className="grid">
      <div className="card">
        <h2>Top 10 Turniersieger-Wahrscheinlichkeiten</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Team</th>
              <th>Wahrscheinlichkeit</th>
            </tr>
          </thead>
          <tbody>
            {top.length > 0 ? (
              top.map(([team, prob]) => (
                <tr key={team}>
                  <td>{team}</td>
                  <td>{(prob * 100).toFixed(2)}%</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={2}>Backend nicht erreichbar - pruefe Container und API-Verbindung.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Navigation</h2>
        <p>Gruppenphase und Bracket sind bereits implementiert.</p>
        <ul>
          <li>
            <Link href="/groups">Gruppen und Standings</Link>
          </li>
          <li>
            <Link href="/bracket">Round of 32 Bracket</Link>
          </li>
          <li>
            <Link href="/simulation">Simulation & Model Performance</Link>
          </li>
        </ul>
      </div>
    </section>
  );
}
