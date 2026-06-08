import { getLatestSimulation, getModelPerformance } from "@/lib/api";
import { RefreshDataCard } from "@/components/RefreshDataCard";

export const dynamic = "force-dynamic";

export default async function SimulationPage() {
  const latest = await getLatestSimulation().catch(() => ({
    created_at: null,
    n_simulations: 0,
    winner_probabilities: {},
  }));
  const performance = await getModelPerformance().catch(() => null);

  const top = Object.entries(latest.winner_probabilities)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 20);

  return (
    <section className="grid">
      <RefreshDataCard />

      <article className="card">
        <h2>Letzte Simulation</h2>
        <p>
          Durchläufe: <strong>{latest.n_simulations}</strong>
        </p>
        <p>
          Zeitstempel: <strong>{latest.created_at ?? "Keine Simulation vorhanden"}</strong>
        </p>
      </article>

      <article className="card">
        <h2>Top 20 Siegerwahrscheinlichkeiten</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Team</th>
              <th>Chance</th>
            </tr>
          </thead>
          <tbody>
            {top.map(([team, prob]) => (
              <tr key={team}>
                <td>{team}</td>
                <td>{(prob * 100).toFixed(2)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>

      {performance && (
        <article className="card">
          <h2>Model Performance</h2>
          <p>Version: {performance.model_version}</p>
          <p>Teams: {performance.tracked_teams}</p>
          <p>Gruppenspiele erfasst: {performance.played_group_matches}</p>
          <p>Log Loss: {performance.log_loss}</p>
          <p>Brier Score: {performance.brier_score}</p>
          <p>Top-1 Accuracy: {(performance.top1_accuracy * 100).toFixed(1)}%</p>
        </article>
      )}
    </section>
  );
}
