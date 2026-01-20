import requests
from app.config import Config


class BallDontLieClient:
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.headers = {"Authorization": Config.API_KEY}

    def get_games(self, params):
        try:
            response = requests.get(
                f"{self.base_url}/games",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()  # This raises the 401 error
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise

    def get_teams(self):
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
