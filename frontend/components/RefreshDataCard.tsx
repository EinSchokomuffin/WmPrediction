"use client";

import { useState } from "react";

import { refreshData } from "@/lib/api";

export function RefreshDataCard() {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("Noch kein Refresh ausgefuehrt.");

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      const result = await refreshData();
      const reasonPart = result.reason ? ` | Hinweis: ${result.reason}` : "";
      setMessage(
        `Status: ${result.status} | Quelle: ${result.source} | Gruppen aktualisiert: ${result.updated_groups} | Zeit: ${result.refreshed_at}${reasonPart}`,
      );
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unbekannter Refresh-Fehler");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <article className="card">
      <h2>Daten-Refresh</h2>
      <p>Ziehe aktuelle Gruppendaten von football-data.org (wenn API-Key gesetzt ist).</p>
      <button onClick={handleRefresh} disabled={isLoading}>
        {isLoading ? "Refresh laeuft..." : "Jetzt refreshen"}
      </button>
      <p style={{ marginTop: 12 }}>{message}</p>
    </article>
  );
}
