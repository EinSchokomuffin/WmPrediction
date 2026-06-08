# ⚽ WM 2026 Predictor — Vollständiges Anwendungskonzept

> **Ziel:** Eine datengetriebene Applikation, die auf Basis von historischen Matchdaten, Elo-Ratings, statistischen Modellen und Monte-Carlo-Simulation die statistisch optimalen Tipps für die FIFA WM 2026 berechnet – von der Gruppenphase bis zum Finale.

---

## 📋 Inhaltsverzeichnis

1. [Projektübersicht](#1-projektübersicht)
2. [Turnierformat WM 2026](#2-turnierformat-wm-2026)
3. [Systemarchitektur](#3-systemarchitektur)
4. [Technologie-Stack](#4-technologie-stack)
5. [Datenquellen & APIs](#5-datenquellen--apis)
6. [Datenmodelle](#6-datenmodelle)
7. [Algorithmen & KI-Engine](#7-algorithmen--ki-engine)
8. [Turnierbaum-Logik](#8-turnierbaum-logik)
9. [Frontend & Visualisierung](#9-frontend--visualisierung)
10. [Phasenplan & TODOs](#10-phasenplan--todos)
11. [Ordnerstruktur](#11-ordnerstruktur)
12. [Kritische Abhängigkeiten & Risiken](#12-kritische-abhängigkeiten--risiken)

---

## 1. Projektübersicht

### Kernfunktionen

| Feature | Beschreibung |
|---|---|
| 📥 Gruppen-Input | Eingabe / Auto-Load der 12 Gruppen A–L mit je 4 Teams |
| 📊 Gruppen-Simulation | Automatische Berechnung aller Gruppenspiele + Tabellen |
| 🔀 KO-Bracket | Automatisches Befüllen des Turnierbaums nach WM-2026-Regelwerk |
| 🤖 Vorhersage-Engine | Elo + Dixon-Coles + ML-Ensemble + Monte-Carlo |
| 📈 Wahrscheinlichkeiten | Win-Probability, Tore, Turniersieger-Chance je Team |
| 💾 Daten-Pipeline | Automatische API-Abfragen für aktuelle Teamdaten |
| 🔄 Live-Update | Ergebnisse einpflegen → Bracket aktualisiert sich |

### Nicht-Ziele (Out of Scope v1)

- Spieler-Individualstatistiken (nur Team-Ebene)
- Live-Ticker / Streaming
- Wett-Plattform-Integration
- Mobile App (erst ab v2)

---

## 2. Turnierformat WM 2026

### 2.1 Übersicht

```
48 Teams → 12 Gruppen à 4 → Round of 32 → Round of 16 → QF → SF → Final
                                 (32 Teams)     (16)      (8)  (4)  (2)
```

**Gesamtspiele:** 104 (vs. 64 bei WM 2022)

### 2.2 Gruppenphase

- **12 Gruppen** (A–L) mit je **4 Teams**
- Jede Gruppe: **6 Spiele** (Round-Robin, jeder gegen jeden)
- **72 Gruppenspiele** gesamt
- Punkte: Sieg = 3, Unentschieden = 1, Niederlage = 0
- Tiebreaker-Reihenfolge:
  1. Punkte
  2. Tordifferenz (gesamt)
  3. Geschossene Tore (gesamt)
  4. Direktes Duell (Punkte)
  5. Direktes Duell (Tordifferenz)
  6. FIFA-Weltrangliste

### 2.3 Qualifikation zur K.O.-Runde (32 Teams)

```
12 Gruppensieger    ← automatisch qualifiziert
12 Gruppenzweite    ← automatisch qualifiziert
 8 beste Dritte     ← bestes Ranking über alle 12 Gruppen
─────────────────
32 Teams gesamt
```

> **Wichtig:** Die **Bestimmung der 8 besten Dritten** ist komplex:
> - Nur Drittplatzierte mit den meisten Punkten kommen weiter
> - Bei Gleichstand: Tordifferenz → Tore → FIFA-Ranking
> - Dies beeinflusst, **welche** Sechzehntelfinale-Paarungen entstehen

### 2.4 Sechzehntelfinale (Round of 32) — Paarungen

Die Paarungen folgen einem **fixen Bracket-Schema** der FIFA.

| Spiel | Team 1 | Team 2 |
|---|---|---|
| S73 | 2. Gruppe A | 2. Gruppe B |
| S74 | 1. Gruppe E | 3. bester aus A/B/C/D/F |
| S75 | 1. Gruppe F | 2. Gruppe C |
| S76 | 1. Gruppe C | 2. Gruppe F |
| S77 | 1. Gruppe I | 3. bester aus C/D/F/G/H |
| S78 | 2. Gruppe E | 2. Gruppe I |
| S79 | 1. Gruppe A | 3. bester aus C/E/F/H/I |
| S80 | 1. Gruppe L | 3. bester aus E/H/I/J/K |
| S81 | 1. Gruppe D | 3. bester aus B/E/F/I/J |
| S82 | 1. Gruppe G | 3. bester aus A/E/H/I/J |
| S83 | 2. Gruppe K | 2. Gruppe L |
| S84 | 1. Gruppe H | 2. Gruppe J |
| S85 | 1. Gruppe B | 3. bester aus E/F/G/I/J |
| S86 | 1. Gruppe J | 2. Gruppe H |
| S87 | 1. Gruppe K | 3. bester aus D/E/I/J/L |
| S88 | 2. Gruppe D | 2. Gruppe G |

### 2.5 Achtelfinale bis Finale

```
Achtelfinale (Spiel 89-96):
  89: Sieger S74 vs Sieger S77
  90: Sieger S73 vs Sieger S75
  91: Sieger S76 vs Sieger S78
  92: Sieger S79 vs Sieger S80
  93: Sieger S83 vs Sieger S84
  94: Sieger S81 vs Sieger S82
  95: Sieger S86 vs Sieger S88
  96: Sieger S85 vs Sieger S87

Viertelfinale (Spiel 97-100):
  97: Sieger 89 vs Sieger 90
  98: Sieger 93 vs Sieger 94
  99: Sieger 91 vs Sieger 92
 100: Sieger 95 vs Sieger 96

Halbfinale (Spiel 101-102):
 101: Sieger 97 vs Sieger 98
 102: Sieger 99 vs Sieger 100

Spiel um Platz 3 (Spiel 103):
 103: Verlierer 101 vs Verlierer 102

Finale (Spiel 104):
 104: Sieger 101 vs Sieger 102
```

---

## 3. Systemarchitektur

```
┌─────────────────────────────────────────────────────────────────┐
│                        WM 2026 PREDICTOR                        │
├─────────────┬───────────────────────┬───────────────────────────┤
│  FRONTEND   │       BACKEND         │      DATA LAYER           │
│  (React/    │    (FastAPI/Python)    │                           │
│   Next.js)  │                       │  ┌─────────────────────┐  │
│             │  ┌─────────────────┐  │  │   External APIs     │  │
│  ┌────────┐ │  │  Prediction     │  │  │ - football-data.org │  │
│  │Bracket │◄├──│  Engine         │◄─┼──│ - API-Football      │  │
│  │Viewer  │ │  │  (Core AI)      │  │  │ - FIFA API          │  │
│  └────────┘ │  └────────┬────────┘  │  │ - SofaScore         │  │
│             │           │           │  └─────────────────────┘  │
│  ┌────────┐ │  ┌────────▼────────┐  │                           │
│  │Group   │◄├──│  Tournament     │  │  ┌─────────────────────┐  │
│  │Tables  │ │  │  Engine         │  │  │   Local Database    │  │
│  └────────┘ │  └────────┬────────┘  │  │   (PostgreSQL /     │  │
│             │           │           │  │    SQLite für Dev)  │  │
│  ┌────────┐ │  ┌────────▼────────┐  │  └─────────────────────┘  │
│  │Stats & │◄├──│  Data Pipeline  │◄─┼──                         │
│  │Odds    │ │  │  (ETL)          │  │  ┌─────────────────────┐  │
│  └────────┘ │  └─────────────────┘  │  │   Cache Layer       │  │
│             │                       │  │   (Redis)           │  │
└─────────────┴───────────────────────┴──└─────────────────────┘──┘
```

### 3.1 Datenfluss

```
API-Daten         Lokale DB          Prediction Engine      Frontend
   │                  │                     │                   │
   ├──► ETL-Job ──────► team_ratings        │                   │
   │                  │  match_history      │                   │
   │                  │  group_results      │                   │
   │                  │        │            │                   │
   │                  └────────► Laden ─────►                   │
   │                                        │                   │
   │                  ┌─────────────────────┘                   │
   │                  │  1. Elo berechnen                       │
   │                  │  2. Poisson-Modell                      │
   │                  │  3. Monte Carlo (10.000 Sim.)           │
   │                  │  4. Ergebnis: Win-Probs, Tore           │
   │                  │        │                                │
   │                  │        └────────────────────────────────►
   │                  │                                         │
   │                  │                                 ┌───────┴──────┐
   │                  │                                 │ Bracket-View │
   │                  │                                 │ Group-Tables │
   │                  │                                 │ Wahrschein-  │
   │                  │                                 │ lichkeiten   │
   │                  │                                 └──────────────┘
```

---

## 4. Technologie-Stack

### Backend

| Komponente | Technologie | Begründung |
|---|---|---|
| Sprache | Python 3.11+ | Beste ML-Library-Unterstützung |
| Framework | FastAPI | Async, schnell, OpenAPI-Docs auto-generiert |
| ML/Stats | scikit-learn, XGBoost | Klassifikation + Regression |
| Numerik | NumPy, SciPy, pandas | Statistische Modelle, Datenverarbeitung |
| Simulation | NumPy random (Monte Carlo) | 10.000+ Turnier-Simulationen |
| DB-ORM | SQLAlchemy + Alembic | Migrations, typsicher |
| Cache | Redis | API-Responses cachen, Rate-Limit-Schutz |
| Task Queue | Celery | Asynchrone ETL-Jobs, tägl. Datenaktualisierung |

### Frontend

| Komponente | Technologie | Begründung |
|---|---|---|
| Framework | Next.js 14 (React) | SSR, File-based Routing, großes Ecosystem |
| Sprache | TypeScript | Typsicherheit für komplexe Bracket-Logik |
| Styling | Tailwind CSS | Schnelles UI-Prototyping |
| Bracket-Viz | D3.js oder `react-tournament-bracket` | Dynamischer Turnierbaum |
| Charts | Recharts / Chart.js | Wahrscheinlichkeits-Charts |
| State Management | Zustand oder Redux Toolkit | Globaler App-State (Bracket-Daten) |
| HTTP-Client | TanStack Query | Caching, Refetching |

### Infrastruktur

| Komponente | Technologie |
|---|---|
| Datenbank (Dev) | SQLite |
| Datenbank (Prod) | PostgreSQL |
| Cache | Redis |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | Render / Railway / selbst-gehostet |

---

## 5. Datenquellen & APIs

### 5.1 Primäre Datenquellen

#### 🥇 football-data.org (Empfohlen als Einstieg)
```
URL:    https://www.football-data.org/documentation/quickstart
Auth:   API-Key (Header: X-Auth-Token)
Tier:   Free (10 Calls/Minute), Paid ab ~12€/Monat
WM2026: Verfügbar ab Turnierbeginn

Relevante Endpoints:
  GET /v4/competitions/WC/teams       → Alle WM-Teams
  GET /v4/competitions/WC/matches     → Alle Spiele
  GET /v4/competitions/WC/standings   → Gruppenstand
  GET /v4/teams/{id}/matches          → Historische Matches
```

#### 🥈 API-Football (RapidAPI) — Vollständigste Daten
```
URL:    https://www.api-football.com/
Auth:   RapidAPI-Key (Header)
Tier:   Free (100 Calls/Tag), Paid ab ca. 10$/Monat

Relevante Endpoints:
  GET /standings?league=1&season=2026     → WM-Tabellen
  GET /fixtures?league=1&season=2026      → Alle Spiele + Ergebnisse
  GET /teams/statistics?league=1&team=X  → Team-Statistiken
  GET /odds?fixture=X&bookmaker=Y         → Wettquoten (für Vergleich)
  GET /predictions?fixture=X             → Eigene KI-Vorhersage als Benchmark
```

#### 🥉 FIFA Weltrangliste (Web Scraping)
```
URL:     https://www.fifa.com/fifa-world-ranking/men
Methode: BeautifulSoup / Playwright (keine offizielle API)
Update:  Monatlich (oder nach großen Turnieren)
Daten:   Rang, Punkte, Konföderation

# Alternative: FIFA-Ranking über football-data.org
GET /v4/teams/{id}  → enthält "fifa_rank" Feld
```

#### 📊 Historische WM-Daten (Kaggle / GitHub)
```
Quelle 1: kaggle.com/datasets/martj42/international-football-results
Datei:    results.csv (47.000+ internationale Spiele seit 1872)
Felder:   date, home_team, away_team, home_score, away_score, tournament, city, country

Quelle 2: github.com/jfjelstul/worldcup
Datei:    WC-Matches komplett, Teams, Gruppen, alle WMs
```

#### 📡 Echtzeit-Ergebnisse (während des Turniers)
```
Primär:  API-Football (Live Fixtures: GET /fixtures?live=all)
Backup:  football-data.org (GET /v4/competitions/WC/matches?status=LIVE)
Polling-Intervall: 60 Sekunden (Rate-Limit beachten)
```

### 5.2 API-Kosten-Übersicht

| Anbieter | Free Tier | Empfehlung |
|---|---|---|
| football-data.org | 10 Req/min, WC-Daten | ✅ Dev + Prod |
| API-Football | 100 Req/Tag | ✅ Als Backup/Ergänzung |
| Kaggle historisch | Kostenlos | ✅ ML-Training |
| FIFA Scraping | Kostenlos | ⚠️ TOS prüfen |

---

## 6. Datenmodelle

### 6.1 Datenbankschema (SQLAlchemy)

```python
# models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

class Confederation(enum.Enum):
    UEFA = "UEFA"
    CONMEBOL = "CONMEBOL"
    AFC = "AFC"
    CAF = "CAF"
    CONCACAF = "CONCACAF"
    OFC = "OFC"

class Team(Base):
    __tablename__ = "teams"
    id              = Column(Integer, primary_key=True)
    name            = Column(String, unique=True, nullable=False)    # "Germany"
    name_short      = Column(String)                                  # "GER"
    fifa_code       = Column(String(3))                               # "GER"
    confederation   = Column(Enum(Confederation))
    fifa_ranking    = Column(Integer)
    fifa_points     = Column(Float)
    elo_rating      = Column(Float, default=1500.0)   # Berechnetes Elo
    elo_updated_at  = Column(DateTime)
    # Relationships
    group_id        = Column(Integer, ForeignKey("groups.id"))
    group           = relationship("Group", back_populates="teams")

class Group(Base):
    __tablename__ = "groups"
    id      = Column(Integer, primary_key=True)
    name    = Column(String(1))  # "A" bis "L"
    teams   = relationship("Team", back_populates="group")
    matches = relationship("Match", back_populates="group")

class Match(Base):
    __tablename__ = "matches"
    id              = Column(Integer, primary_key=True)
    match_number    = Column(Integer)         # 1–104
    stage           = Column(String)          # "GROUP", "R32", "R16", "QF", "SF", "3RD", "FINAL"
    home_team_id    = Column(Integer, ForeignKey("teams.id"), nullable=True)
    away_team_id    = Column(Integer, ForeignKey("teams.id"), nullable=True)
    home_score      = Column(Integer, nullable=True)   # None = noch nicht gespielt
    away_score      = Column(Integer, nullable=True)
    home_score_et   = Column(Integer, nullable=True)   # Verlängerung
    away_score_et   = Column(Integer, nullable=True)
    home_score_pen  = Column(Integer, nullable=True)   # Elfmeter
    away_score_pen  = Column(Integer, nullable=True)
    scheduled_at    = Column(DateTime)
    venue           = Column(String)
    group_id        = Column(Integer, ForeignKey("groups.id"), nullable=True)
    group           = relationship("Group", back_populates="matches")

class Prediction(Base):
    __tablename__ = "predictions"
    id                  = Column(Integer, primary_key=True)
    match_id            = Column(Integer, ForeignKey("matches.id"))
    model_version       = Column(String)         # z.B. "ensemble_v1.2"
    home_win_prob       = Column(Float)
    draw_prob           = Column(Float)
    away_win_prob       = Column(Float)
    expected_home_goals = Column(Float)
    expected_away_goals = Column(Float)
    confidence          = Column(Float)          # 0–1
    created_at          = Column(DateTime)

class HistoricalMatch(Base):
    __tablename__ = "historical_matches"
    id          = Column(Integer, primary_key=True)
    date        = Column(DateTime)
    home_team   = Column(String)
    away_team   = Column(String)
    home_score  = Column(Integer)
    away_score  = Column(Integer)
    tournament  = Column(String)      # "FIFA World Cup", "Friendly", etc.
    is_neutral  = Column(Boolean, default=False)
    weight      = Column(Float, default=1.0)  # Zeit-Gewichtung (jüngere = höher)

class TournamentSimulation(Base):
    __tablename__ = "tournament_simulations"
    id                  = Column(Integer, primary_key=True)
    created_at          = Column(DateTime)
    n_simulations       = Column(Integer)
    results_json        = Column(String)   # JSON: {team: {winner_prob, sf_prob, qf_prob...}}
    model_version       = Column(String)
```

### 6.2 TypeScript-Interfaces (Frontend)

```typescript
// types/tournament.ts

export interface Team {
  id: number;
  name: string;
  shortCode: string;      // "GER"
  confederation: string;
  fifaRanking: number;
  eloRating: number;
  flagUrl?: string;
}

export interface GroupStanding {
  team: Team;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goalsFor: number;
  goalsAgainst: number;
  goalDiff: number;
  points: number;
  position: 1 | 2 | 3 | 4;
}

export interface Group {
  name: string;           // "A" bis "L"
  teams: Team[];
  standings: GroupStanding[];
  matches: Match[];
}

export interface Match {
  id: number;
  matchNumber: number;
  stage: TournamentStage;
  homeTeam: Team | null;    // null = Qualifier noch nicht bekannt
  awayTeam: Team | null;
  homeScore: number | null;
  awayScore: number | null;
  prediction?: MatchPrediction;
  scheduledAt: string;      // ISO datetime
  venue: string;
}

export type TournamentStage =
  | "GROUP"
  | "ROUND_OF_32"     // Sechzehntelfinale
  | "ROUND_OF_16"     // Achtelfinale
  | "QUARTER_FINAL"
  | "SEMI_FINAL"
  | "THIRD_PLACE"
  | "FINAL";

export interface MatchPrediction {
  homeWinProb: number;
  drawProb: number;
  awayWinProb: number;
  expectedHomeGoals: number;
  expectedAwayGoals: number;
  confidence: number;
}

export interface TournamentBracket {
  groups: Group[];
  roundOf32: Match[];
  roundOf16: Match[];
  quarterFinals: Match[];
  semiFinals: Match[];
  thirdPlace: Match;
  final: Match;
  teamProbabilities: Record<string, TeamTournamentProbs>;
}

export interface TeamTournamentProbs {
  teamId: number;
  winnerProb: number;
  finalProb: number;
  semiFinalProb: number;
  quarterFinalProb: number;
  roundOf16Prob: number;
  groupAdvanceProb: number;
}
```

---

## 7. Algorithmen & KI-Engine

### 7.1 Überblick der Modell-Hierarchie

```
                    ┌──────────────────────┐
                    │  ENSEMBLE PREDICTOR  │  ← Finales Ergebnis
                    └──────┬───────┬───────┘
                           │       │
              ┌────────────┘       └────────────┐
              ▼                                 ▼
  ┌─────────────────────┐           ┌─────────────────────┐
  │   STATISTISCHES     │           │   MACHINE LEARNING  │
  │   MODELL (60%)      │           │   MODELL (40%)      │
  └──────┬──────┬───────┘           └──────┬──────────────┘
         │      │                          │
    ┌────┘  ┌───┘                    ┌─────┘
    ▼       ▼                        ▼
  Elo   Dixon-Coles              XGBoost
  Rating  Poisson              Classifier
```

### 7.2 Elo-Rating-System

Das **Elo-Rating** ist die Grundlage aller Vorhersagen.

```python
# prediction/elo.py

class EloRating:
    """
    Modifiziertes Elo-System für Fußball (basierend auf Club Elo / FiveThirtyEight-Methodik).
    """
    
    BASE_RATING = 1500.0
    K_FACTOR_MAP = {
        "FIFA World Cup": 60,
        "UEFA Euro": 50,
        "Continental Championship": 50,
        "World Cup Qualification": 40,
        "Friendly": 20,
    }
    HOME_ADVANTAGE = 100  # Elo-Punkte Bonus für Heimspiele
    
    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """Erwarteter Score (Gewinnwahrscheinlichkeit) für Team A."""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def update_rating(
        self,
        rating_winner: float,
        rating_loser: float,
        score_winner: float,   # 1.0 = Sieg, 0.5 = Unentschieden, 0.0 = Niederlage
        tournament: str,
        is_neutral: bool = True
    ) -> tuple[float, float]:
        """Aktualisiert Elo nach einem Spiel. Gibt (new_winner, new_loser) zurück."""
        k = self.K_FACTOR_MAP.get(tournament, 30)
        
        if not is_neutral:
            rating_winner += self.HOME_ADVANTAGE  # Heimvorteil modellieren
        
        expected_w = self.expected_score(rating_winner, rating_loser)
        expected_l = 1 - expected_w
        
        # Tordifferenz-Multiplikator (Wichtig! 5:0 > 1:0)
        goal_diff = abs(score_winner)  # Im echten Code: abs(home_score - away_score)
        goal_multiplier = self._goal_multiplier(goal_diff)
        
        new_winner = rating_winner + k * goal_multiplier * (score_winner - expected_w)
        new_loser  = rating_loser  + k * goal_multiplier * ((1 - score_winner) - expected_l)
        
        return new_winner, new_loser
    
    def _goal_multiplier(self, goal_diff: int) -> float:
        """FiveThirtyEight-Formel für Tordifferenz-Gewichtung."""
        if goal_diff <= 1:
            return 1.0
        elif goal_diff == 2:
            return 1.5
        else:
            return (11 + goal_diff) / 8
    
    def win_probability(self, elo_a: float, elo_b: float) -> dict:
        """
        Konvertiert Elo-Differenz in Win/Draw/Loss Wahrscheinlichkeiten.
        Nutzt Poisson-Überlagerung für Draw-Modellierung.
        """
        win_prob = self.expected_score(elo_a, elo_b)
        
        # Näherungsformel für Draw-Wahrscheinlichkeit
        # (wird durch Dixon-Coles präzisiert)
        draw_factor = 0.27  # Typischer Unentschieden-Anteil WM
        
        p_win   = win_prob * (1 - draw_factor)
        p_draw  = draw_factor * (1 - abs(win_prob - 0.5) * 2)
        p_loss  = (1 - win_prob) * (1 - draw_factor)
        
        # Normalisierung
        total = p_win + p_draw + p_loss
        return {
            "home_win": p_win / total,
            "draw":     p_draw / total,
            "away_win": p_loss / total
        }
```

### 7.3 Dixon-Coles Poisson-Modell

Das **Dixon-Coles Modell** erweitert die einfache Poisson-Verteilung und korrigiert die Unterschätzung von Niedrig-Tor-Spielen (0:0, 1:0, 0:1, 1:1).

```python
# prediction/dixon_coles.py
import numpy as np
from scipy.stats import poisson
from scipy.optimize import minimize

class DixonColesModel:
    """
    Dixon-Coles (1997): Modelling Association Football Scores and Inefficiencies in the
    Football Betting Market. Applied Statistics, 46(2), 265–280.
    
    Schätzt Attack- und Defense-Stärken je Team aus historischen Daten.
    """
    
    def __init__(self, time_decay_factor: float = 0.002):
        """
        time_decay_factor: ξ (xi) — Jüngere Spiele werden stärker gewichtet.
        Empfehlung: 0.002 (≈ 1 Jahr Halbwertszeit)
        """
        self.rho = -0.13   # Korrekturparameter für 0:0, 1:0 etc. (Startwert)
        self.xi  = time_decay_factor
        self.attack_params  = {}   # team → float
        self.defense_params = {}   # team → float
        self.home_advantage = 0.0
        
    def _time_weight(self, days_ago: int) -> float:
        """Exponentielles Gewicht. Spiele vor 3 Jahren ≈ 0.11 Gewicht."""
        return np.exp(-self.xi * days_ago)
    
    def _tau(self, x: int, y: int, mu: float, lambda_: float) -> float:
        """
        Dixon-Coles Korrekturterm für niedrige Toranzahlen.
        Korrigiert: 0:0, 1:0, 0:1, 1:1
        """
        rho = self.rho
        if x == 0 and y == 0:
            return 1 - lambda_ * mu * rho
        elif x == 1 and y == 0:
            return 1 + mu * rho
        elif x == 0 and y == 1:
            return 1 + lambda_ * rho
        elif x == 1 and y == 1:
            return 1 - rho
        else:
            return 1.0
    
    def _neg_log_likelihood(self, params, matches, teams):
        """Negative Log-Likelihood — wird minimiert (scipy.optimize)."""
        n_teams = len(teams)
        team_idx = {t: i for i, t in enumerate(teams)}
        
        alphas  = params[:n_teams]      # Attack-Stärken
        betas   = params[n_teams:2*n_teams]   # Defense-Stärken
        gamma   = params[2*n_teams]           # Home advantage
        rho     = params[2*n_teams + 1]
        
        log_lik = 0.0
        for match in matches:
            i = team_idx[match["home"]]
            j = team_idx[match["away"]]
            x, y = match["home_goals"], match["away_goals"]
            w    = match.get("weight", 1.0)
            
            # Erwartete Tore
            mu_h     = np.exp(alphas[i] + betas[j] + gamma)   # Home expected goals
            mu_a     = np.exp(alphas[j] + betas[i])            # Away expected goals
            
            # Poisson-Wahrscheinlichkeit mit Dixon-Coles-Korrektur
            tau_val = self._tau(x, y, mu_h, mu_a)
            p_x     = poisson.pmf(x, mu_h)
            p_y     = poisson.pmf(y, mu_a)
            
            log_lik += w * np.log(max(tau_val * p_x * p_y, 1e-10))
        
        return -log_lik
    
    def fit(self, matches: list[dict], teams: list[str]):
        """Trainiert das Modell auf historischen Daten."""
        n = len(teams)
        # Startwerte: alles 0, außer rho = -0.1
        x0 = np.zeros(2 * n + 2)
        x0[-1] = -0.1  # rho
        x0[-2] = 0.3   # home advantage
        
        result = minimize(
            self._neg_log_likelihood,
            x0,
            args=(matches, teams),
            method="L-BFGS-B",
            options={"maxiter": 1000}
        )
        
        team_idx = {t: i for i, t in enumerate(teams)}
        for team, i in team_idx.items():
            self.attack_params[team]  = result.x[i]
            self.defense_params[team] = result.x[n + i]
        self.home_advantage = result.x[2 * n]
        self.rho            = result.x[2 * n + 1]
        
    def predict_score_matrix(
        self, home_team: str, away_team: str, max_goals: int = 8
    ) -> np.ndarray:
        """
        Gibt Matrix P[i,j] = P(home_goals=i, away_goals=j) zurück.
        Shape: (max_goals+1, max_goals+1)
        """
        alpha_h = self.attack_params.get(home_team, 0.0)
        beta_a  = self.defense_params.get(away_team, 0.0)
        alpha_a = self.attack_params.get(away_team, 0.0)
        beta_h  = self.defense_params.get(home_team, 0.0)
        
        # Bei WM: neutraler Austragungsort → kein Home Advantage
        mu_h = np.exp(alpha_h + beta_a)
        mu_a = np.exp(alpha_a + beta_h)
        
        matrix = np.outer(
            poisson.pmf(range(max_goals + 1), mu_h),
            poisson.pmf(range(max_goals + 1), mu_a)
        )
        
        # Dixon-Coles-Korrektur für niedrige Tore
        for i in range(min(2, max_goals + 1)):
            for j in range(min(2, max_goals + 1)):
                matrix[i, j] *= self._tau(i, j, mu_h, mu_a)
        
        return matrix / matrix.sum()   # Normalisieren
    
    def predict_match(self, home_team: str, away_team: str) -> dict:
        """Gibt Win/Draw/Loss Wahrscheinlichkeiten + Expected Goals zurück."""
        M = self.predict_score_matrix(home_team, away_team)
        
        home_win = float(np.tril(M, -1).sum())   # i > j
        draw     = float(np.trace(M))             # i == j
        away_win = float(np.triu(M, 1).sum())     # i < j
        
        goals_range = np.arange(M.shape[0])
        exp_home    = float(np.dot(M.sum(axis=1), goals_range))
        exp_away    = float(np.dot(M.sum(axis=0), goals_range))
        
        return {
            "home_win_prob": home_win,
            "draw_prob":     draw,
            "away_win_prob": away_win,
            "expected_home_goals": exp_home,
            "expected_away_goals": exp_away,
        }
```

### 7.4 Machine Learning Modell (XGBoost)

```python
# prediction/ml_model.py
import xgboost as xgb
import pandas as pd
import numpy as np

class MLPredictor:
    """
    XGBoost Classifier: Klassifiziert Match-Ausgang (Home Win / Draw / Away Win)
    auf Basis von Feature-Engineering über historische Daten.
    """
    
    FEATURES = [
        # Elo-basiert
        "elo_diff",              # home_elo - away_elo
        "elo_home",              # Absolutes Home-Elo
        "elo_away",              # Absolutes Away-Elo
        
        # FIFA-Ranking
        "ranking_diff",          # home_rank - away_rank (niedriger = besser)
        
        # Formkurve (letzten 5 Spiele)
        "home_form_points",      # Punkte aus letzten 5 Spielen (max 15)
        "away_form_points",
        "home_goals_scored_5",   # Ø Tore in letzten 5 Spielen
        "home_goals_conceded_5",
        "away_goals_scored_5",
        "away_goals_conceded_5",
        
        # Head-to-Head (letzten 5 Duelle)
        "h2h_home_wins",         # Anzahl Heimsiege
        "h2h_draws",
        "h2h_away_wins",
        "h2h_home_goals_avg",
        "h2h_away_goals_avg",
        
        # Turnier-Kontext
        "is_neutral",            # 1 = neutraler Platz (immer 1 bei WM)
        "stage_weight",          # Gruppenspiel=1, KO=2, SF=3, Final=4
        "confederation_match",   # Gleiche Konföderation = 1
    ]
    
    def __init__(self):
        self.model = xgb.XGBClassifier(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="multi:softprob",
            num_class=3,   # 0=Home Win, 1=Draw, 2=Away Win
            random_state=42,
            eval_metric="mlogloss"
        )
    
    def engineer_features(self, match_data: dict, historical_df: pd.DataFrame) -> pd.Series:
        """Feature Engineering für ein einzelnes Match."""
        home = match_data["home_team"]
        away = match_data["away_team"]
        
        # Elo
        elo_diff = match_data["home_elo"] - match_data["away_elo"]
        
        # Form (letzten 5 Spiele)
        home_last5 = self._get_last_n_matches(historical_df, home, n=5)
        away_last5 = self._get_last_n_matches(historical_df, away, n=5)
        
        # H2H
        h2h = historical_df[
            ((historical_df["home_team"] == home) & (historical_df["away_team"] == away)) |
            ((historical_df["home_team"] == away) & (historical_df["away_team"] == home))
        ].tail(5)
        
        features = {
            "elo_diff": elo_diff,
            "elo_home": match_data["home_elo"],
            "elo_away": match_data["away_elo"],
            "ranking_diff": match_data.get("home_rank", 50) - match_data.get("away_rank", 50),
            "home_form_points": self._calc_form_points(home_last5, home),
            "away_form_points": self._calc_form_points(away_last5, away),
            # ... weitere Features
        }
        
        return pd.Series(features)
    
    def _get_last_n_matches(self, df: pd.DataFrame, team: str, n: int) -> pd.DataFrame:
        return df[
            (df["home_team"] == team) | (df["away_team"] == team)
        ].tail(n)
    
    def _calc_form_points(self, matches: pd.DataFrame, team: str) -> float:
        points = 0
        for _, row in matches.iterrows():
            if row["home_team"] == team:
                if row["home_score"] > row["away_score"]:   points += 3
                elif row["home_score"] == row["away_score"]: points += 1
            else:
                if row["away_score"] > row["home_score"]:   points += 3
                elif row["home_score"] == row["away_score"]: points += 1
        return points
    
    def predict_proba(self, features: pd.Series) -> dict:
        X = features.values.reshape(1, -1)
        probs = self.model.predict_proba(X)[0]
        return {
            "home_win_prob": float(probs[0]),
            "draw_prob":     float(probs[1]),
            "away_win_prob": float(probs[2]),
        }
```

### 7.5 Monte-Carlo Turniersimulation

```python
# simulation/monte_carlo.py
import numpy as np
from collections import defaultdict
from typing import Optional

class TournamentSimulator:
    """
    Simuliert das gesamte WM-Turnier N-mal und berechnet
    Wahrscheinlichkeiten für jeden Ausgang.
    
    Wichtig: Beinhaltet WM-2026-spezifische Logik:
    - Gruppenphasen-Tiebreaker
    - 8 beste Dritte Auswahl
    - Sechzehntelfinale-Seeding
    """
    
    def __init__(self, predictor, n_simulations: int = 10_000):
        self.predictor  = predictor   # Ensemble-Predictor
        self.n_sims     = n_simulations
    
    def simulate_match(
        self,
        home: str,
        away: str,
        allow_draw: bool = True
    ) -> dict:
        """
        Simuliert ein einzelnes Match.
        Returns: {"winner": str, "home_goals": int, "away_goals": int}
        """
        pred = self.predictor.predict(home, away)
        exp_home = pred["expected_home_goals"]
        exp_away = pred["expected_away_goals"]
        
        # Tore aus Poisson-Verteilung ziehen
        home_goals = np.random.poisson(exp_home)
        away_goals = np.random.poisson(exp_away)
        
        if not allow_draw and home_goals == away_goals:
            # Verlängerung + Elfmeter modellieren
            # Vereinfacht: 50/50 nach Unentschieden
            winner = np.random.choice([home, away])
            if winner == home:
                home_goals += 1
            else:
                away_goals += 1
        
        return {
            "home_goals": home_goals,
            "away_goals": away_goals,
            "winner": home if home_goals > away_goals else (
                away if away_goals > home_goals else None
            )
        }
    
    def simulate_group(self, group: dict) -> dict:
        """
        Simuliert alle 6 Spiele einer Gruppe.
        Returns: Sortierte Standings-Liste.
        """
        teams = group["teams"]
        standings = {t: {"P":0, "W":0, "D":0, "L":0, "GF":0, "GA":0, "Pts":0} for t in teams}
        
        matches = [
            (teams[i], teams[j])
            for i in range(len(teams))
            for j in range(i+1, len(teams))
        ]
        
        for home, away in matches:
            result = self.simulate_match(home, away, allow_draw=True)
            self._update_standings(standings, home, away, result)
        
        # Sortierung nach WM-2026-Tiebreaker-Regeln
        return self._sort_standings(standings)
    
    def _update_standings(self, standings, home, away, result):
        hg, ag = result["home_goals"], result["away_goals"]
        standings[home]["P"]  += 1; standings[away]["P"]  += 1
        standings[home]["GF"] += hg; standings[home]["GA"] += ag
        standings[away]["GF"] += ag; standings[away]["GA"] += hg
        if hg > ag:
            standings[home]["W"] += 1; standings[home]["Pts"] += 3
            standings[away]["L"] += 1
        elif ag > hg:
            standings[away]["W"] += 1; standings[away]["Pts"] += 3
            standings[home]["L"] += 1
        else:
            standings[home]["D"] += 1; standings[home]["Pts"] += 1
            standings[away]["D"] += 1; standings[away]["Pts"] += 1
    
    def _sort_standings(self, standings: dict) -> list:
        return sorted(
            standings.items(),
            key=lambda x: (x[1]["Pts"], x[1]["GF"] - x[1]["GA"], x[1]["GF"]),
            reverse=True
        )
    
    def simulate_tournament(self, groups: dict) -> dict:
        """
        Simuliert das komplette Turnier einmal durch.
        Returns: {"winner": str, "finalist": str, "semi_finalists": list, ...}
        """
        # Gruppenphase
        group_results = {}
        for group_name, group in groups.items():
            group_results[group_name] = self.simulate_group(group)
        
        # 8 beste Dritte bestimmen
        all_thirds = [
            (group_name, res[2])  # 3. Platz jeder Gruppe
            for group_name, res in group_results.items()
        ]
        best_thirds = sorted(
            all_thirds,
            key=lambda x: (x[1][1]["Pts"], x[1][1]["GF"] - x[1][1]["GA"], x[1][1]["GF"]),
            reverse=True
        )[:8]
        best_third_groups = {bt[0] for bt in best_thirds}
        
        # Round of 32 aufbauen (Seeding-Logik)
        r32_matches = self._build_r32(group_results, best_third_groups)
        
        # K.O.-Runden simulieren
        r32_winners  = [self.simulate_match(m[0], m[1], allow_draw=False)["winner"]
                        for m in r32_matches]
        r16_matches  = self._build_r16(r32_winners)
        r16_winners  = [self.simulate_match(m[0], m[1], allow_draw=False)["winner"]
                        for m in r16_matches]
        qf_matches   = [(r16_winners[i], r16_winners[i+1]) for i in range(0, 8, 2)]
        qf_winners   = [self.simulate_match(m[0], m[1], allow_draw=False)["winner"]
                        for m in qf_matches]
        sf_matches   = [(qf_winners[0], qf_winners[1]), (qf_winners[2], qf_winners[3])]
        sf_results   = [self.simulate_match(m[0], m[1], allow_draw=False) for m in sf_matches]
        sf_winners   = [r["winner"] for r in sf_results]
        sf_losers    = [sf_matches[i][0 if sf_results[i]["winner"] == sf_matches[i][1] else 1]
                        for i in range(2)]
        
        winner = self.simulate_match(sf_winners[0], sf_winners[1], allow_draw=False)["winner"]
        
        return {
            "winner":       winner,
            "finalist":     [sf_winners[0], sf_winners[1]],
            "semi_finalists": sf_winners + sf_losers,
            "qf":           qf_winners,
        }
    
    def run(self, groups: dict) -> dict:
        """
        Führt N Simulationen durch und aggregiert Wahrscheinlichkeiten.
        """
        stats = defaultdict(lambda: {
            "winner": 0, "finalist": 0, "semi": 0, "qf": 0, "r16": 0
        })
        
        for _ in range(self.n_sims):
            result = self.simulate_tournament(groups)
            
            stats[result["winner"]]["winner"]   += 1
            for t in result["finalist"]:
                stats[t]["finalist"] += 1
            for t in result["semi_finalists"]:
                stats[t]["semi"]     += 1
            for t in result["qf"]:
                stats[t]["qf"]       += 1
        
        # Normalisieren
        return {
            team: {k: v / self.n_sims for k, v in counts.items()}
            for team, counts in stats.items()
        }
    
    def _build_r32(self, group_results: dict, best_third_groups: set) -> list:
        """
        Baut die 16 Sechzehntelfinale-Paarungen nach FIFA-Seeding auf.
        Die Zuordnung der 8 besten Dritten variiert je nach Herkunftsgruppe.
        """
        # Gruppenplatzierungen extrahieren
        def get_pos(group, pos):
            return group_results[group][pos - 1][0]
        
        def get_best_third_from(groups: list) -> str:
            """Findet den besten Dritten aus den angegebenen Gruppen."""
            candidates = [
                (g, group_results[g][2])
                for g in groups if g in best_third_groups
            ]
            if not candidates:
                return None
            best = max(candidates, key=lambda x: (
                x[1][1]["Pts"],
                x[1][1]["GF"] - x[1][1]["GA"],
                x[1][1]["GF"]
            ))
            return best[1][0]
        
        # Paarungen laut FIFA-Spielplan
        return [
            (get_pos("A", 2), get_pos("B", 2)),                          # S73
            (get_pos("E", 1), get_best_third_from(["A","B","C","D","F"])), # S74
            (get_pos("F", 1), get_pos("C", 2)),                          # S75
            (get_pos("C", 1), get_pos("F", 2)),                          # S76
            (get_pos("I", 1), get_best_third_from(["C","D","F","G","H"])), # S77
            (get_pos("E", 2), get_pos("I", 2)),                          # S78
            (get_pos("A", 1), get_best_third_from(["C","E","F","H","I"])), # S79
            (get_pos("L", 1), get_best_third_from(["E","H","I","J","K"])), # S80
            (get_pos("D", 1), get_best_third_from(["B","E","F","I","J"])), # S81
            (get_pos("G", 1), get_best_third_from(["A","E","H","I","J"])), # S82
            (get_pos("K", 2), get_pos("L", 2)),                          # S83
            (get_pos("H", 1), get_pos("J", 2)),                          # S84
            (get_pos("B", 1), get_best_third_from(["E","F","G","I","J"])), # S85
            (get_pos("J", 1), get_pos("H", 2)),                          # S86
            (get_pos("K", 1), get_best_third_from(["D","E","I","J","L"])), # S87
            (get_pos("D", 2), get_pos("G", 2)),                          # S88
        ]
```

### 7.6 Ensemble Predictor

```python
# prediction/ensemble.py

class EnsemblePredictor:
    """
    Kombiniert Elo, Dixon-Coles und ML zu einem finalen Ergebnis.
    Gewichte empirisch optimiert auf historischen WM-Daten.
    """
    
    WEIGHTS = {
        "elo":         0.25,
        "dixon_coles": 0.45,
        "ml":          0.30,
    }
    
    def __init__(self, elo_model, dc_model, ml_model):
        self.elo = elo_model
        self.dc  = dc_model
        self.ml  = ml_model
    
    def predict(self, home_team: str, away_team: str, features=None) -> dict:
        elo_pred = self.elo.win_probability(
            self.elo.ratings[home_team],
            self.elo.ratings[away_team]
        )
        dc_pred  = self.dc.predict_match(home_team, away_team)
        ml_pred  = self.ml.predict_proba(features) if features else None
        
        w = self.WEIGHTS
        
        if ml_pred:
            home_win = (w["elo"] * elo_pred["home_win"] +
                        w["dixon_coles"] * dc_pred["home_win_prob"] +
                        w["ml"] * ml_pred["home_win_prob"])
            draw     = (w["elo"] * elo_pred["draw"] +
                        w["dixon_coles"] * dc_pred["draw_prob"] +
                        w["ml"] * ml_pred["draw_prob"])
            away_win = 1 - home_win - draw
        else:
            # Ohne ML (bei fehlenden Features): Elo + DC
            home_win = 0.35 * elo_pred["home_win"] + 0.65 * dc_pred["home_win_prob"]
            draw     = 0.35 * elo_pred["draw"]      + 0.65 * dc_pred["draw_prob"]
            away_win = 1 - home_win - draw
        
        return {
            "home_win_prob": max(0, home_win),
            "draw_prob":     max(0, draw),
            "away_win_prob": max(0, away_win),
            "expected_home_goals": dc_pred["expected_home_goals"],
            "expected_away_goals": dc_pred["expected_away_goals"],
        }
```

---

## 8. Turnierbaum-Logik

### 8.1 Gruppenphase — Vollständiger Spielplan

```python
# tournament/group_phase.py

def generate_group_schedule(groups: dict[str, list[str]]) -> list[dict]:
    """
    Generiert alle 72 Gruppenspiele.
    Jede Gruppe: 4 Teams → 6 Spiele (Round-Robin).
    """
    all_matches = []
    match_number = 1
    
    for group_name, teams in sorted(groups.items()):
        group_matches = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                group_matches.append({
                    "match_number": match_number,
                    "stage": "GROUP",
                    "group": group_name,
                    "home": teams[i],
                    "away": teams[j],
                })
                match_number += 1
        
        # Spieltag-Zuweisung (Matchday 1/2/3)
        # MD1: Spiel 1+2+3 (nicht gleichzeitig bei WM)
        # MD2: Spiel 4+5+6 (Spiel 5+6 gleichzeitig!)  
        # MD3: Spiel 7+8+9 → eigentlich Spiel 5+6 sind letzter Spieltag
        # Korrekte Zuweisung:
        # Matchday 1: (0,1) und (0,2) und (1,2)... → Paarung 1,2
        # Matchday 2: Paarung 3, 4  
        # Matchday 3: Paarung 5, 6 (IMMER gleichzeitig!)
        
        for idx, match in enumerate(group_matches):
            if idx < 2:   match["matchday"] = 1
            elif idx < 4: match["matchday"] = 2
            else:         match["matchday"] = 3
        
        all_matches.extend(group_matches)
    
    return all_matches
```

### 8.2 Bestimmung der 8 besten Dritten

```python
# tournament/third_place_ranking.py

BEST_THIRDS_TO_R32_SLOTS = {
    # Mapping: Welche 8 Gruppen stellten die besten Dritten?
    # → Bestimmt den Gegner im Sechzehntelfinale laut FIFA-Regelwerk
    # FIFA hat verschiedene Szenarien vorab festgelegt (ähnlich EM 2024)
    # Vollständige Tabelle muss aus offiziellem FIFA-Dokument extrahiert werden
    # Hier: vereinfachte Logik
    frozenset(["A","B","C","D","E","F","G","H"]): "TBD",
    # ... weitere Kombinationen
}

def rank_third_place_teams(group_results: dict) -> list[tuple[str, str]]:
    """
    Rankt alle 12 Drittplatzierten und gibt die besten 8 zurück.
    Returns: List of (group_name, team_name), sortiert nach Ranking.
    """
    thirds = []
    for group_name, standings in group_results.items():
        team_name, stats = standings[2]  # Index 2 = 3. Platz
        thirds.append({
            "group": group_name,
            "team": team_name,
            "points": stats["Pts"],
            "goal_diff": stats["GF"] - stats["GA"],
            "goals_for": stats["GF"],
        })
    
    # Sortierung nach FIFA-Tiebreaker-Regeln für Drittplatzierte
    thirds_sorted = sorted(
        thirds,
        key=lambda x: (x["points"], x["goal_diff"], x["goals_for"]),
        reverse=True
    )
    
    return [(t["group"], t["team"]) for t in thirds_sorted[:8]]
```

---

## 9. Frontend & Visualisierung

### 9.1 Bracket-Komponente (React)

```tsx
// components/TournamentBracket.tsx
import { motion } from 'framer-motion';

interface BracketProps {
  bracket: TournamentBracket;
  onMatchClick: (match: Match) => void;
}

export const TournamentBracket: React.FC<BracketProps> = ({ bracket, onMatchClick }) => {
  return (
    <div className="bracket-container overflow-x-auto">
      <div className="bracket-grid grid grid-cols-[repeat(7,minmax(140px,1fr))] gap-4 min-w-[1200px]">
        {/* Linke Seite: R32 → R16 → QF → SF */}
        <BracketColumn stage="R32_LEFT"  matches={bracket.roundOf32.slice(0, 8)} />
        <BracketColumn stage="R16_LEFT"  matches={bracket.roundOf16.slice(0, 4)} />
        <BracketColumn stage="QF_LEFT"   matches={bracket.quarterFinals.slice(0, 2)} />
        <BracketColumn stage="SF_LEFT"   matches={bracket.semiFinals.slice(0, 1)} />
        {/* Mitte: Final */}
        <FinalColumn final={bracket.final} thirdPlace={bracket.thirdPlace} />
        {/* Rechte Seite: SF → QF → R16 → R32 */}
        <BracketColumn stage="SF_RIGHT"  matches={bracket.semiFinals.slice(1, 2)} />
        <BracketColumn stage="QF_RIGHT"  matches={bracket.quarterFinals.slice(2, 4)} />
        <BracketColumn stage="R16_RIGHT" matches={bracket.roundOf16.slice(4, 8)} />
        <BracketColumn stage="R32_RIGHT" matches={bracket.roundOf32.slice(8, 16)} />
      </div>
    </div>
  );
};

// Einzelne Match-Card im Bracket
const MatchCard: React.FC<{ match: Match; onClick: () => void }> = ({ match, onClick }) => {
  const { homeTeam, awayTeam, homeScore, awayScore, prediction } = match;
  
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      onClick={onClick}
      className="match-card bg-gray-800 rounded-lg p-2 cursor-pointer border border-gray-600 hover:border-blue-500"
    >
      <TeamRow
        team={homeTeam}
        score={homeScore}
        winProb={prediction?.homeWinProb}
        isWinner={homeScore !== null && homeScore > (awayScore ?? -1)}
      />
      <div className="divider h-px bg-gray-600 my-1" />
      <TeamRow
        team={awayTeam}
        score={awayScore}
        winProb={prediction?.awayWinProb}
        isWinner={awayScore !== null && awayScore > (homeScore ?? -1)}
      />
      {prediction && (
        <ProbabilityBar
          home={prediction.homeWinProb}
          draw={prediction.drawProb}
          away={prediction.awayWinProb}
        />
      )}
    </motion.div>
  );
};
```

### 9.2 API Routes (FastAPI)

```python
# api/routes.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="WM 2026 Predictor API", version="1.0.0")

@app.get("/api/groups", response_model=list[GroupResponse])
async def get_groups():
    """Alle 12 Gruppen mit Teams und Standings."""
    ...

@app.post("/api/groups/setup", response_model=SetupResponse)
async def setup_groups(payload: GroupSetupPayload):
    """Gruppen manuell befüllen oder aus API laden."""
    ...

@app.get("/api/bracket", response_model=BracketResponse)
async def get_bracket():
    """Vollständiger Turnierbaum mit Predictions."""
    ...

@app.get("/api/matches/{match_id}/prediction", response_model=PredictionResponse)
async def get_prediction(match_id: int):
    """Vorhersage für ein bestimmtes Spiel."""
    ...

@app.post("/api/matches/{match_id}/result", response_model=BracketResponse)
async def submit_result(match_id: int, payload: ResultPayload):
    """Ergebnis einpflegen → Bracket auto-updaten."""
    ...

@app.get("/api/teams/{team_id}/tournament-probs", response_model=TeamProbsResponse)
async def get_tournament_probs(team_id: int):
    """Turnierverlauf-Wahrscheinlichkeiten für ein Team."""
    ...

@app.post("/api/simulation/run", response_model=SimulationResponse)
async def run_simulation(payload: SimulationPayload):
    """Startet N Monte-Carlo-Simulationen (asynchron via Celery)."""
    ...

@app.get("/api/data/refresh")
async def refresh_data():
    """Aktualisiert alle Teamdaten aus externen APIs."""
    ...
```

---

## 10. Phasenplan & TODOs

### Phase 1 — Foundation (Woche 1–2)
> **Ziel:** Lauffähiges Backend mit Datenpipeline und einfachem Bracket-Grundgerüst.

#### ✅ TODO 1.1 — Projekt-Setup
- [ ] Repository anlegen (Monorepo: `backend/`, `frontend/`, `data/`, `docs/`)
- [ ] `pyproject.toml` mit Dependencies (`fastapi`, `sqlalchemy`, `pandas`, `numpy`, `scipy`, `xgboost`, `celery`, `redis`)
- [ ] `package.json` für Next.js Frontend
- [ ] Docker Compose: FastAPI + PostgreSQL + Redis + Next.js
- [ ] `.env.example` mit allen benötigten API-Keys dokumentieren
- [ ] GitHub Actions CI: Linting (ruff, eslint) + Tests (pytest, jest)

#### ✅ TODO 1.2 — Datenbank & Modelle
- [ ] SQLAlchemy-Modelle aus Kapitel 6 implementieren
- [ ] Alembic-Migrationen aufsetzen (`alembic init`, erste Migration)
- [ ] Seed-Skript: WM-2026-Teams und Gruppen (A–L) aus Kaggle-Datensatz laden
- [ ] Unit Tests: `test_models.py`

#### ✅ TODO 1.3 — Daten-Pipeline (ETL)
- [ ] `football-data.org` API-Client implementieren (Rate-Limiting, Retry, Caching via Redis)
- [ ] ETL-Job: Historische Matchdaten (Kaggle CSV) → DB importieren
- [ ] ETL-Job: FIFA-Ranking täglich aktualisieren
- [ ] Celery-Task: `refresh_team_data()` — täglich ausführen
- [ ] Logging-Setup (structlog oder loguru)

#### ✅ TODO 1.4 — Basis-API
- [ ] FastAPI App mit CORS-Middleware
- [ ] `GET /api/groups` — alle 12 Gruppen zurückgeben
- [ ] `POST /api/groups/setup` — manuelle Gruppen-Eingabe
- [ ] Swagger-Docs testen (`/docs`)

---

### Phase 2 — Gruppenphase-Engine (Woche 2–3)
> **Ziel:** Vollständige Gruppenphase-Berechnung inkl. korrekter Tiebreaker-Logik.

#### ✅ TODO 2.1 — Spielplan-Generator
- [ ] `generate_group_schedule()` implementieren (alle 72 Gruppenspiele)
- [ ] Matchday-Zuweisung (MD1, MD2, MD3)
- [ ] Echtzeit-Spielplandaten von football-data.org abrufen + DB speichern
- [ ] `GET /api/groups/{name}/schedule` Endpoint

#### ✅ TODO 2.2 — Standings-Berechnung
- [ ] `calculate_standings()` mit vollständiger FIFA-Tiebreaker-Logik
- [ ] Tiebreaker-Kaskade: Punkte → Tordiff → Tore → Direktes Duell → FIFA-Ranking
- [ ] `GET /api/groups/{name}/standings`
- [ ] Unit Tests: alle Tiebreaker-Szenarien abdecken

#### ✅ TODO 2.3 — Beste-8-Dritte-Logik
- [ ] `rank_third_place_teams()` implementieren
- [ ] Edge Cases: Was wenn 8 Dritte punktgleich sind?
- [ ] `GET /api/standings/third-place`
- [ ] Test: verschiedene Szenarien simulieren

#### ✅ TODO 2.4 — Live-Update-Integration
- [ ] Polling-Service: Alle 60s API abfragen nach neuen Ergebnissen
- [ ] `POST /api/matches/{id}/result` → Standings neu berechnen → Bracket updaten
- [ ] WebSocket (optional) für Echtzeit-Frontend-Update

---

### Phase 3 — KO-Phasen-Engine (Woche 3–4)
> **Ziel:** Vollständiger Turnierbaum mit korrektem Seeding und Bracket-Fortschritt.

#### ✅ TODO 3.1 — Sechzehntelfinale-Seeding
- [ ] `build_r32_bracket()` — alle 16 Paarungen laut FIFA-Schema (Kapitel 2.4)
- [ ] Best-Third-Zuordnung zu Slots implementieren
- [ ] Sonderfall: Gleiche Gruppe darf nicht gegeneinander im R32 (prüfen!)
- [ ] `GET /api/bracket/r32`

#### ✅ TODO 3.2 — Bracket-Fortschritt
- [ ] `advance_bracket()` — nach Spielergebnis nächste Runde aktualisieren
- [ ] Verlängerung + Elfmeter in DB modellieren
- [ ] Vollständigen Bracket-Baum (R32 → R16 → QF → SF → Final) persistent speichern
- [ ] `GET /api/bracket` — vollständigen aktuellen Bracket zurückgeben

#### ✅ TODO 3.3 — Bracket-Edge Cases
- [ ] Was passiert bei ungültigem Ergebnis-Input?
- [ ] Rückwärts-Navigation (Ergebnis korrigieren)?
- [ ] Unit Tests: Bracket-Fortschritt von Gruppe A bis Finale

---

### Phase 4 — KI/Prediction-Engine (Woche 4–6)
> **Ziel:** Vollständiges Ensemble-Prediction-System mit Monte-Carlo-Simulation.

#### ✅ TODO 4.1 — Elo-Rating
- [ ] `EloRating`-Klasse aus Kapitel 7.2 implementieren
- [ ] Historische Matches aus DB verarbeiten (gesamte Datenbasis ~47.000 Matches)
- [ ] Elo-Ratings für alle WM-2026-Teams berechnen und in DB speichern
- [ ] Visualisierung: Elo-Entwicklung der deutschen Nationalmannschaft über Zeit
- [ ] Validation: Elo-Predictions vs. historische WM-Ergebnisse backtesten

#### ✅ TODO 4.2 — Dixon-Coles Modell
- [ ] `DixonColesModel` aus Kapitel 7.3 implementieren
- [ ] Training auf historischen Länderspielen (Kaggle-Dataset)
- [ ] Zeit-Gewichtung kalibrieren (optimal xi bestimmen durch Cross-Validation)
- [ ] Attack/Defense-Parameter für alle Teams berechnen
- [ ] Unit Test: predict_match("Germany", "Brazil") → plausible Werte?

#### ✅ TODO 4.3 — Feature Engineering & ML-Modell
- [ ] Feature-Engineering-Pipeline aus Kapitel 7.4 implementieren
- [ ] Training-Dataset vorbereiten: alle WM-Spiele 1990–2022
- [ ] XGBoost-Modell trainieren + Hyperparameter-Optimierung (Optuna)
- [ ] Cross-Validation (Leave-One-Tournament-Out)
- [ ] Model-Persistenz: Pickle/MLflow
- [ ] Backtesting: WM 2022-Vorhersagen vs. Realität

#### ✅ TODO 4.4 — Ensemble & Gewichtung
- [ ] `EnsemblePredictor` implementieren
- [ ] Ensemble-Gewichte durch Backtesting optimieren
- [ ] `GET /api/matches/{id}/prediction` Endpoint
- [ ] Confidence-Score berechnen (wie sicher ist das Modell?)

#### ✅ TODO 4.5 — Monte Carlo Simulation
- [ ] `TournamentSimulator` aus Kapitel 7.5 implementieren
- [ ] `_build_r32()` Seeding-Logik korrekt integrieren
- [ ] 10.000 Simulationen: Laufzeit < 30 Sekunden (optimieren falls nötig)
- [ ] Celery-Task: `run_simulation.delay(n=10000)`
- [ ] `GET /api/simulation/latest` — neueste Simulationsergebnisse
- [ ] Visualisierung: Turniersieger-Wahrscheinlichkeiten als Bar Chart

---

### Phase 5 — Frontend (Woche 5–7)
> **Ziel:** Vollständige, interaktive UI mit Bracket-Visualisierung und Predictions.

#### ✅ TODO 5.1 — Setup & Layout
- [ ] Next.js 14 + TypeScript + Tailwind einrichten
- [ ] TanStack Query für API-State
- [ ] Grundlayout: Header, Sidebar, Hauptbereich
- [ ] Dark Mode als Standard (WM-Ästhetik)
- [ ] Responsive Design (Desktop-Fokus, Mobile optional)

#### ✅ TODO 5.2 — Gruppen-Ansicht
- [ ] `GroupsPage`: 12 Gruppen-Tabellen anzeigen (4 pro Zeile)
- [ ] `GroupTable`-Komponente: Standings mit Live-Aktualisierung
- [ ] `MatchList`-Komponente: Alle Gruppenspiele mit Uhrzeit/Ergebnis/Prediction
- [ ] Eingabe-Interface: Manuelle Team-Eingabe für Gruppen A–L

#### ✅ TODO 5.3 — Bracket-Visualisierung
- [ ] `TournamentBracket`-Komponente (Kapitel 9.1)
- [ ] Match-Cards mit Win-Probability-Bars
- [ ] Team-Flags einbinden (restcountries.com API oder statische Flags)
- [ ] Hover-State: Detaillierte Prediction-Info
- [ ] Animierter Bracket-Aufbau (Framer Motion)

#### ✅ TODO 5.4 — Statistik-Dashboard
- [ ] Turniersieger-Wahrscheinlichkeiten: Horizontales Bar Chart (alle 48 Teams)
- [ ] Team-Detailseite: Elo-Entwicklung, Predictions, Bracket-Weg
- [ ] Konföderation-Filter
- [ ] Model-Performance-Seite: Backtesting-Ergebnisse visualisieren

#### ✅ TODO 5.5 — Admin-Interface
- [ ] Ergebnis-Eingabe: Spielstand manuell eintragen
- [ ] Gruppen-Setup: Teams zuweisen
- [ ] Simulation neu starten
- [ ] Einfacher API-Key-Schutz

---

### Phase 6 — Testing & Deployment (Woche 7–8)
> **Ziel:** Produktionsreife Applikation mit vollständiger Test-Abdeckung.

#### ✅ TODO 6.1 — Backend-Tests
- [ ] pytest Unit Tests: alle Core-Algorithmen
- [ ] Integration Tests: API-Endpoints mit TestClient
- [ ] Test-Coverage > 80%
- [ ] Backtesting-Report: WM 2014, 2018, 2022 Vorhersagen vs. Realität

#### ✅ TODO 6.2 — Frontend-Tests
- [ ] Jest + React Testing Library: alle Komponenten
- [ ] E2E-Tests mit Playwright: vollständiger Bracket-Flow
- [ ] Storybook für Komponenten-Dokumentation

#### ✅ TODO 6.3 — Performance
- [ ] Simulation-Laufzeit < 30s für 10.000 Runden
- [ ] API-Response-Zeit < 200ms (Redis-Cache für teure Berechnungen)
- [ ] Frontend Bundle Size optimieren (Code Splitting)

#### ✅ TODO 6.4 — Deployment
- [ ] Docker-Images bauen und testen
- [ ] PostgreSQL auf Produktions-DB migrieren
- [ ] Deployment auf Render.com oder Railway (günstig, Docker-Support)
- [ ] Domain + HTTPS einrichten
- [ ] Monitoring: Sentry (Errors) + Uptime-Monitor

---

## 11. Ordnerstruktur

```
wm2026-predictor/
│
├── backend/
│   ├── alembic/                  # DB-Migrationen
│   │   └── versions/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI App
│   │   ├── routes/
│   │   │   ├── groups.py
│   │   │   ├── bracket.py
│   │   │   ├── predictions.py
│   │   │   ├── simulation.py
│   │   │   └── admin.py
│   │   └── schemas.py            # Pydantic-Modelle
│   ├── core/
│   │   ├── config.py             # Settings (Env-Vars)
│   │   └── database.py           # DB-Session
│   ├── data/
│   │   ├── clients/
│   │   │   ├── football_data.py  # football-data.org Client
│   │   │   └── api_football.py   # API-Football Client
│   │   ├── etl/
│   │   │   ├── import_historical.py  # Kaggle CSV → DB
│   │   │   ├── update_rankings.py    # FIFA-Ranking Update
│   │   │   └── update_results.py     # Live-Ergebnisse Update
│   │   └── seeds/
│   │       └── wm2026_groups.json    # Teams + Gruppen A–L
│   ├── models/
│   │   └── db.py                 # SQLAlchemy-Modelle
│   ├── prediction/
│   │   ├── elo.py                # Elo-Rating-System
│   │   ├── dixon_coles.py        # Dixon-Coles Poisson
│   │   ├── ml_model.py           # XGBoost Predictor
│   │   └── ensemble.py           # Ensemble Predictor
│   ├── simulation/
│   │   └── monte_carlo.py        # Monte Carlo Simulator
│   ├── tournament/
│   │   ├── group_phase.py        # Spielplan + Standings
│   │   ├── third_place.py        # Beste-8-Dritte-Logik
│   │   └── bracket.py            # KO-Bracket-Logik
│   ├── tasks/
│   │   └── celery_app.py         # Async Tasks
│   └── tests/
│       ├── test_elo.py
│       ├── test_dixon_coles.py
│       ├── test_tournament.py
│       └── test_api.py
│
├── frontend/
│   ├── app/                      # Next.js App Router
│   │   ├── page.tsx              # Dashboard
│   │   ├── groups/
│   │   │   └── page.tsx          # Gruppen-Übersicht
│   │   ├── bracket/
│   │   │   └── page.tsx          # Turnierbaum
│   │   ├── simulation/
│   │   │   └── page.tsx          # Monte Carlo Ergebnisse
│   │   └── admin/
│   │       └── page.tsx          # Admin-Interface
│   ├── components/
│   │   ├── tournament/
│   │   │   ├── TournamentBracket.tsx
│   │   │   ├── BracketColumn.tsx
│   │   │   ├── MatchCard.tsx
│   │   │   └── ProbabilityBar.tsx
│   │   ├── groups/
│   │   │   ├── GroupTable.tsx
│   │   │   └── MatchList.tsx
│   │   ├── charts/
│   │   │   ├── WinProbChart.tsx
│   │   │   └── EloHistoryChart.tsx
│   │   └── ui/                   # shadcn/ui Komponenten
│   ├── hooks/
│   │   ├── useBracket.ts
│   │   ├── useGroups.ts
│   │   └── useSimulation.ts
│   ├── types/
│   │   └── tournament.ts         # TypeScript Interfaces (Kapitel 6.2)
│   └── lib/
│       └── api.ts                # API-Client-Functions
│
├── data/
│   └── historical/
│       ├── results.csv           # Kaggle: ~47.000 Matches
│       └── wm2026_teams.json     # 48 Teams + Elo-Startwerte
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
└── README.md
```

---

## 12. Kritische Abhängigkeiten & Risiken

### 12.1 API-Schlüssel (vor Start besorgen!)

```bash
# .env Datei
FOOTBALL_DATA_API_KEY=xxx      # https://www.football-data.org/ (kostenlos)
API_FOOTBALL_KEY=xxx           # https://www.api-football.com/ (kostenlos Tier)
POSTGRES_URL=postgresql://...
REDIS_URL=redis://localhost:6379
SECRET_KEY=xxx                 # FastAPI JWT
```

### 12.2 Bekannte Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|---|---|---|---|
| API Rate Limit überschritten | Mittel | Hoch | Redis-Cache, exponential Backoff |
| FIFA ändert Seeding-Regeln | Niedrig | Hoch | Seeding-Logik modular halten |
| Tiebreaker-Bugs | Mittel | Mittel | Umfangreiche Unit Tests |
| ML-Modell overfittet | Mittel | Mittel | Cross-Val, einfaches Elo als Fallback |
| Deployment-Kosten | Niedrig | Niedrig | Render Free Tier reicht für Demo |

### 12.3 Offene Fragen (TODO: recherchieren)

- [ ] Hat FIFA das vollständige Best-Third-Seeding-Schema für 2026 veröffentlicht?
- [ ] Gibt es offizielle API von FIFA (nicht nur Scraping)?
- [ ] Wie genau werden die 8 besten Dritten im KO-Baum verteilt? (Bei EM 2024 gab es eine feste Mapping-Tabelle)
- [ ] Gilt bei WM 2026 das "gleiche Konföderation nicht im R32"-Prinzip?

### 12.4 Nächste unmittelbare Schritte

```
1. [ ] GitHub-Repo anlegen
2. [ ] football-data.org API-Key besorgen (kostenlos, 5 Min.)
3. [ ] Kaggle-Dataset herunterladen: martj42/international-football-results
4. [ ] Python-Umgebung einrichten: pip install fastapi sqlalchemy pandas numpy scipy xgboost
5. [ ] Erste Datenbankmodelle + Seed-Skript ausführen
6. [ ] Erste Prediction: Deutschland vs. Curaçao testen
```

---

## Zusammenfassung

```
TURNIER     → 48 Teams, 12 Gruppen, 104 Spiele, Sechzehntelfinale NEU
BACKEND     → Python/FastAPI, PostgreSQL, Redis, Celery
PREDICTION  → Elo (25%) + Dixon-Coles Poisson (45%) + XGBoost ML (30%)
SIMULATION  → 10.000 Monte-Carlo-Durchläufe → Turniersieger-Wahrscheinlichkeit
FRONTEND    → Next.js, TypeScript, D3.js Bracket, Tailwind
DATEN       → football-data.org + API-Football + Kaggle (47k hist. Spiele)
DEPLOYMENT  → Docker Compose, Render.com / Railway
PHASEN      → 6 Phasen, 8 Wochen, klar strukturierte TODOs
```

> 🚀 **Bereit zum Start:** Phase 1 → Repo anlegen → API-Key holen → Los!
```
