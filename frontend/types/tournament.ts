export interface GroupTeam {
  name: string;
  elo: number;
  fifaRanking: number;
}

export type GroupMap = Record<string, GroupTeam[]>;

export interface StandingsRow {
  P: number;
  W: number;
  D: number;
  L: number;
  GF: number;
  GA: number;
  Pts: number;
  R: number;
}

export type GroupStandings = Record<string, [string, StandingsRow][]>;

export interface KnockoutMatch {
  match_number: number;
  stage: string;
  home_team: string | null;
  away_team: string | null;
  home_score: number | null;
  away_score: number | null;
  home_score_et: number | null;
  away_score_et: number | null;
  home_score_pen: number | null;
  away_score_pen: number | null;
}

export interface FullBracketResponse {
  round_of_32: KnockoutMatch[];
  round_of_16: KnockoutMatch[];
  quarter_finals: KnockoutMatch[];
  semi_finals: KnockoutMatch[];
  third_place: KnockoutMatch[];
  final: KnockoutMatch[];
}

export interface SimulationResponse {
  winner_probabilities: Record<string, number>;
}

export interface LatestSimulationResponse {
  created_at: string | null;
  n_simulations: number;
  winner_probabilities: Record<string, number>;
}

export interface ModelPerformanceResponse {
  model_version: string;
  tracked_teams: number;
  played_group_matches: number;
  log_loss: number;
  brier_score: number;
  top1_accuracy: number;
}

export interface RefreshDataResponse {
  status: string;
  updated_groups: number;
  source: string;
  reason: string;
  refreshed_at: string;
}

export interface GroupMatch {
  match_number: number;
  stage: string;
  group: string;
  home: string;
  away: string;
  matchday: number;
  home_goals: number | null;
  away_goals: number | null;
}

export interface TournamentPlayoutResponse {
  standings: GroupStandings;
  group_matches: Record<string, GroupMatch[]>;
  bracket: FullBracketResponse;
}
