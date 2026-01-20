from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.api.games import games_bp
from app.api.teams import teams_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    app.register_blueprint(games_bp, url_prefix='/api')
    app.register_blueprint(teams_bp, url_prefix='/api')

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    return app
