import type {
  FullBracketResponse,
  GroupMap,
  GroupStandings,
  LatestSimulationResponse,
  ModelPerformanceResponse,
  RefreshDataResponse,
  SimulationResponse,
} from "@/types/tournament";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export function getGroups(): Promise<GroupMap> {
  return request<GroupMap>("/api/groups");
}

export function getStandings(): Promise<GroupStandings> {
  return request<GroupStandings>("/api/groups/standings");
}

export function getBracket(): Promise<{ round_of_32: [string, string | null][] }> {
  return request<{ round_of_32: [string, string | null][] }>("/api/bracket/r32");
}

export function getSimulation(): Promise<{ winner_probabilities: Record<string, number> }> {
  return fetch(`${API_BASE}/api/simulation/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ n: 1000 }),
  }).then((res) => {
    if (!res.ok) {
      throw new Error(`Simulation request failed: ${res.status}`);
    }
    return res.json() as Promise<{ winner_probabilities: Record<string, number> }>;
  });
}

export function getLatestSimulation(): Promise<LatestSimulationResponse> {
  return request<LatestSimulationResponse>("/api/simulation/latest");
}

export function getFullBracket(): Promise<FullBracketResponse> {
  return request<FullBracketResponse>("/api/bracket");
}

export function getModelPerformance(): Promise<ModelPerformanceResponse> {
  return request<ModelPerformanceResponse>("/api/predictions/performance");
}

export async function runSimulation(n: number): Promise<SimulationResponse> {
  const response = await fetch(`${API_BASE}/api/simulation/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ n }),
  });
  if (!response.ok) {
    throw new Error(`Simulation request failed: ${response.status}`);
  }
  return (await response.json()) as SimulationResponse;
}

export async function refreshData(): Promise<RefreshDataResponse> {
  const response = await fetch(`${API_BASE}/api/data/refresh`, {
    method: "GET",
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Refresh request failed: ${response.status}`);
  }
  return (await response.json()) as RefreshDataResponse;
}
