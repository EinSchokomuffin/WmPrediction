import { PredictionForm } from "@/components/PredictionForm";
import { getGroups } from "@/lib/api";
import type { GroupMap } from "@/types/tournament";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const groups: GroupMap = await getGroups().catch(() => ({} as GroupMap));

  if (Object.keys(groups).length === 0) {
    return (
      <section className="grid" style={{ maxWidth: 760 }}>
        <article className="card hero-card">
          <h2>Spielprognose</h2>
          <p>Backend aktuell nicht erreichbar. Prüfe bitte den Backend-Container und lade die Seite danach neu.</p>
        </article>
      </section>
    );
  }

  return <PredictionForm groups={groups} />;
}
