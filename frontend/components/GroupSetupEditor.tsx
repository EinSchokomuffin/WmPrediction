"use client";

import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";

import { saveAllGroups } from "@/lib/api";
import type { GroupMap } from "@/types/tournament";

interface GroupSetupEditorProps {
  initialGroups: GroupMap;
}

export function GroupSetupEditor({ initialGroups }: GroupSetupEditorProps) {
  const router = useRouter();
  const [groups, setGroups] = useState<GroupMap>(initialGroups);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState("Passe hier deine 12 Gruppen an und speichere sie gesammelt.");

  const orderedGroups = useMemo(() => Object.keys(groups).sort(), [groups]);

  const updateTeam = (group: string, index: number, name: string) => {
    setGroups((current) => ({
      ...current,
      [group]: current[group].map((team, teamIndex) => (teamIndex === index ? { ...team, name } : team)),
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await saveAllGroups(groups);
      setMessage("Gruppen gespeichert. Standings, Bracket und Simulation arbeiten jetzt mit diesen Teams.");
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Gruppen konnten nicht gespeichert werden.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <section className="grid grid-3">
      {orderedGroups.map((group) => (
        <article className="card" key={group}>
          <h2>Gruppe {group}</h2>
          <div style={{ display: "grid", gap: 10 }}>
            {groups[group].map((team, index) => (
              <label key={`${group}-${index}`} style={{ display: "grid", gap: 4 }}>
                <span>Team {index + 1}</span>
                <input
                  value={team.name}
                  onChange={(event) => updateTeam(group, index, event.target.value)}
                  style={{ padding: 8, borderRadius: 8, border: "1px solid #475569", background: "#0f172a", color: "#e2e8f0" }}
                />
              </label>
            ))}
          </div>
        </article>
      ))}

      <article className="card" style={{ gridColumn: "1 / -1" }}>
        <h2>Aktionen</h2>
        <p>{message}</p>
        <button onClick={handleSave} disabled={isSaving}>
          {isSaving ? "Speichert..." : "Alle Gruppen speichern"}
        </button>
      </article>
    </section>
  );
}