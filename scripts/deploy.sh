#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/EinSchokomuffin/WmPrediction.git"
APP_DIR="${APP_DIR:-/opt/WmPrediction}"
BRANCH="${BRANCH:-main}"

if [ ! -d "$APP_DIR/.git" ]; then
  echo "Cloning repository into $APP_DIR..."
  mkdir -p "$APP_DIR"
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

echo "Updating source code..."
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

echo "Restarting Docker services..."
docker compose down
docker compose up -d --build

echo "Deployment complete."
