from flask import Blueprint, request, jsonify
from app.services.games_service import GamesService

games_bp = Blueprint('games', __name__)
games_service = GamesService()

@games_bp.route('/games', methods=['GET'])
def get_games():
    try:
        season = request.args.get('season', None)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        tied_only = request.args.get('tied_only', 'false').lower() == 'true'
        view = request.args.get('view', 'quarters')

        result = games_service.get_games(
            season=season,
            start_date=start_date,
            end_date=end_date,
            tied_only=tied_only,
            view=view
        )

        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
