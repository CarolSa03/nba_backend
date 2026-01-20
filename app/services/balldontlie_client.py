import requests
import time
from app.config import Config


class BallDontLieClient:
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.headers = {"Authorization": Config.API_KEY}
        self.last_request_time = 0
        self.min_interval = 0.5

    def _rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        self.last_request_time = time.time()

    def get_games(self, params):
        self._rate_limit()
        try:
            response = requests.get(
                f"{self.base_url}/games",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise

    def get_teams(self):
        self._rate_limit()
        try:
            response = requests.get(
                f"{self.base_url}/teams",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Teams API Error: {e}")
            raise
