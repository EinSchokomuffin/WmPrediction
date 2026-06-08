from __future__ import annotations

import httpx

from core.config import settings


class FootballDataClient:
    def __init__(self) -> None:
        self.base_url = settings.football_data_base_url.rstrip("/")
        self.api_key = settings.football_data_api_key

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            return {}
        return {"X-Auth-Token": self.api_key}

    def fetch_world_cup_standings(self) -> dict:
        url = f"{self.base_url}/v4/competitions/WC/standings"
        with httpx.Client(timeout=20.0) as client:
            response = client.get(url, headers=self._headers())
            response.raise_for_status()
            return response.json()

    def fetch_world_cup_teams(self) -> dict:
        url = f"{self.base_url}/v4/competitions/WC/teams"
        with httpx.Client(timeout=20.0) as client:
            response = client.get(url, headers=self._headers())
            response.raise_for_status()
            return response.json()
