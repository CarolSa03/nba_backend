from app.services.balldontlie_client import BallDontLieClient

class TeamsService:
    def __init__(self):
        self.client = BallDontLieClient()

    def get_teams(self):
        try:
            return self.client.get_teams()
        except Exception as e:
            print(f"Teams error: {e}")
            return {'data': []}
