# WM 2026 Predictor

Monorepo mit FastAPI-Backend und Next.js-Frontend fuer eine datengetriebene WM-2026-Vorhersageplattform.

## Struktur

- `backend/`: API, Turnierlogik, Prediction-Engine, Monte-Carlo
- `frontend/`: Dashboard, Gruppenansicht, Bracket, Simulation
- `docker-compose.yml`: Lokaler Start beider Services

## Schnellstart (lokal)

### Backend

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -e .[dev]
uvicorn api.main:app --reload --port 6239
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --port 6238
```

Backend (lokal): http://localhost:6239
Frontend (lokal): http://localhost:6238
Tunnel URL (prod): https://wm.wentzek-home.de

## API Endpunkte

- `GET /api/groups`
- `GET /api/groups/standings`
- `GET /api/groups/{group}/schedule`
- `GET /api/groups/{group}/standings`
- `POST /api/groups/setup`
- `POST /api/groups/result`
- `GET /api/standings/third-place`
- `GET /api/bracket`
- `GET /api/bracket/r32`
- `POST /api/bracket/matches/{match_number}/result`
- `GET /api/predictions/match?home=Team+A1&away=Team+B1`
- `GET /api/predictions/teams/{team_name}/tournament-probs`
- `GET /api/predictions/performance`
- `POST /api/simulation/run`
- `GET /api/simulation/latest`
- `GET /api/data/refresh`

## Frontend Seiten

- `/` Dashboard
- `/groups` Gruppen und Standings
- `/bracket` K.O.-Bracket
- `/simulation` Letzte Simulation + Model Performance

## Optionale API-Integration

- `FOOTBALL_DATA_API_KEY` in `.env` setzen, dann zieht `GET /api/data/refresh` echte Gruppenstände von football-data.org.

## Training Workflow (komplett)

1. Historische Daten bereitstellen (CSV mit mindestens den Spalten: `date`, `home_team`, `away_team`, `home_score`, `away_score`).
2. Modell trainieren:

```bash
cd backend
python -m scripts.train_model --csv ..\data\historical\results.csv --output models_artifacts/match_outcome_model.joblib
```

3. Modellstatus prüfen:

```bash
curl http://localhost:6239/api/model/status
```

4. Training direkt per API auslösen:

```bash
curl -X POST http://localhost:6239/api/model/train \
	-H "Content-Type: application/json" \
	-d '{"csvPath":"..\\data\\historical\\results.csv","artifactPath":"models_artifacts/match_outcome_model.joblib"}'
```

5. Modell nach Austausch eines Artefakts neu laden:

```bash
curl -X POST "http://localhost:6239/api/model/reload"
```

Das trainierte Modell wird im Ensemble automatisch genutzt (Elo + Dixon-Coles + ML).

## Testen

```bash
cd backend
pytest
```

## Deployment per Git + Docker

Linux Server:

```bash
bash scripts/deploy.sh
```

Optional mit anderem Zielpfad/Branch:

```bash
APP_DIR=/opt/WmPrediction BRANCH=main bash scripts/deploy.sh
```

Windows Server (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1 -AppDir "C:\deploy\WmPrediction" -Branch "main"
```
