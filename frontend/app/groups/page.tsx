import { getGroups, getStandings } from "@/lib/api";
import type { GroupMap, GroupStandings } from "@/types/tournament";

export const dynamic = "force-dynamic";

export default async function GroupsPage() {
  const groups: GroupMap = await getGroups().catch(() => ({} as GroupMap));
  const standings: GroupStandings = await getStandings().catch(() => ({} as GroupStandings));

  return (
    <section className="grid grid-3">
      {Object.keys(groups).length === 0 && <article className="card">Keine Daten verfuegbar.</article>}
      {Object.entries(groups).map(([groupName, teams]) => (
        <article className="card" key={groupName}>
          <h2>Gruppe {groupName}</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Team</th>
                <th>Elo</th>
                <th>Pts</th>
              </tr>
            </thead>
            <tbody>
              {teams.map((team) => {
                const standing = standings[groupName]?.find(([name]) => name === team.name);
                return (
                  <tr key={team.name}>
                    <td>{team.name}</td>
                    <td>{Math.round(team.elo)}</td>
                    <td>{standing ? standing[1].Pts : 0}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </article>
      ))}
    </section>
  );
}
