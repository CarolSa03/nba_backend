from flask import Blueprint, jsonify
from app.services.teams_service import TeamsService

teams_bp = Blueprint('teams', __name__)
teams_service = TeamsService()

@teams_bp.route('/teams', methods=['GET'])
def get_teams():
    try:
        result = teams_service.get_teams()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
