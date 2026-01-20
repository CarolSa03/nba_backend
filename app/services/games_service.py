from datetime import date
from app.services.balldontlie_client import BallDontLieClient
from app.utils.game_processor import process_game, filter_by_view, filter_tied_only

class GamesService:
    def __init__(self):
        self.client = BallDontLieClient()

    def get_games(self, season=None, start_date=None, end_date=None,
                  tied_only=False, view='quarters'):

        if not end_date:
            end_date = date.today().strftime('%Y-%m-%d')

        params = {'per_page': 500 if tied_only else 100}
        if season:
            params['seasons[]'] = season
        if start_date:
            params['start_date'] = start_date
        params['end_date'] = end_date

        print(f"Fetching games: season={season}, start={start_date}, end={end_date}")

        data = self.client.get_games(params)
        games = data.get('data', [])
        print(f"API returned {len(games)} games")

        results = []
        for game in games:
            processed = process_game(game)
            if processed:
                results.append(processed)
        results = filter_by_view(results, view)

        if tied_only:
            results = filter_tied_only(results)

        print(f"Returning {len(results)} processed games")

        return {
            'success': True,
            'season': season,
            'start_date': start_date,
            'end_date': end_date,
            'tied_only': tied_only,
            'api_games': len(games),
            'results': len(results),
            'games': results
        }
