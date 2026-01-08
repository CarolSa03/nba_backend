import os
import requests
from datetime import date
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get('API_KEY')
BASE_URL = 'https://api.balldontlie.io/v1'


@app.route('/api/games', methods=['GET'])
def get_games():
    season = request.args.get('season')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    tied_only = request.args.get('tied_only', 'false').lower() == 'true'
    view = request.args.get('view', 'quarters')

    try:
        params = {'per_page': 100}
        if tied_only:
            params['per_page'] = 500
        if season:
            params['seasons[]'] = season
        if start_date:
            params['start_date'] = start_date
        params['end_date'] = end_date

        headers = {'Authorization': API_KEY}
        response = requests.get(f'{BASE_URL}/games', params=params, headers=headers)

        if response.status_code != 200:
            return jsonify({'error': 'API request failed'}), 500

        data = response.json()
        games = data.get('data', [])

        results = []
        for game in games:
            if game.get('status') != 'Final':
                continue

            def safe_gt(score):
                return score is not None and score != 0

            has_ot = any(game.get(f'home_score_ot{i}') for i in range(1, 5)) or \
                     any(game.get(f'visitor_score_ot{i}') for i in range(1, 5))

            home_scores = [game.get(f'home_score_q{i}', 0) for i in range(1, 5)]
            visitor_scores = [game.get(f'visitor_score_q{i}', 0) for i in range(1, 5)]

            home_cum, visitor_cum = 0, 0
            tied_quarters = []
            valid_ties = []
            periods = {}

            for q in range(4):
                hq = home_scores[q]
                vq = visitor_scores[q]
                home_cum += hq
                visitor_cum += vq
                q_score = f'{vq}-{hq}'
                cum_score = f'{visitor_cum}-{home_cum}'
                label = f'Q{q + 1}'
                periods[label] = f'{q_score} ({cum_score})'

                if home_cum == visitor_cum and home_cum > 0:
                    valid_ties.append(f'{label} {home_cum}')
                if home_cum == visitor_cum:
                    tied_quarters.append(f'{label} {home_cum}')

            regulation_score = f'{visitor_cum}-{home_cum}'
            if has_ot:
                tied_quarters.append(f'Q4 {home_cum}')
                for ot in range(1, 5):
                    hot = game.get(f'home_team_score_ot{ot}', 0)
                    vot = game.get(f'visitor_team_score_ot{ot}', 0)
                    if hot == 0 and vot == 0:
                        break
                    home_cum += hot
                    visitor_cum += vot
                    period_label = f'OT{ot}'
                    q_score = f'{vot}-{hot}'
                    cum_score = f'{visitor_cum}-{home_cum}'
                    periods[period_label] = f'{q_score} ({cum_score})'
                    if home_cum == visitor_cum:
                        tied_quarters.append(f'{period_label} {home_cum}')
                    if home_cum == visitor_cum and home_cum > 0:
                        valid_ties.append(f'{period_label} {home_cum}')

            period_order = ['Q1', 'Q2', 'Q3', 'Q4', 'OT1', 'OT2', 'OT3', 'OT4']
            periods = {k: periods[k] for k in period_order if k in periods}

            final_home = game.get('home_team_score') or home_cum
            final_visitor = game.get('visitor_team_score') or visitor_cum

            result = {
                'date': game['date'][:10],
                'home_team': game['home_team']['full_name'],
                'visitor_team': game['visitor_team']['full_name'],
                'final_score': f'{final_visitor}-{final_home}',
                'regulation_score': regulation_score,
                'has_ot': bool(has_ot),
                'tied_quarters': tied_quarters,
                'periods': periods
            }
            results.append(result)

        if view == 'regulation':
            results = [g for g in results if not g['has_ot']]

        for game in results:
            game['periods'] = {k: v for k, v in game['periods'].items() if not k.startswith('OT')}

        if tied_only:
            results = [g for g in results if g['tied_quarters']]

        return jsonify({
            'success': True,
            'season': season,
            'start_date': start_date,
            'end_date': end_date,
            'tied_only': tied_only,
            'api_games': len(games),
            'results': len(results),
            'games': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/teams', methods=['GET'])
def get_teams():
    try:
        headers = {'Authorization': API_KEY}
        response = requests.get(f'{BASE_URL}/teams', headers=headers)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'data': []}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, port=10000)
