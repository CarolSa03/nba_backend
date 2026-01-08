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
    season = request.args.get('season', None)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    tied_only = request.args.get('tied_only', 'false').lower() == 'true'
    view = request.args.get('view', 'quarters')


    print(f"Request season={season}, start_date={start_date}, end_date={end_date}, tied_only={tied_only}")

    try:
        params = {'per_page': 100}
        if tied_only:
            params['per_page'] = 500
        if season:
            params['seasons[]'] = season
        if start_date:
            params['start_date'] = start_date
        params['end_date'] = end_date

        headers = {"Authorization": API_KEY}

        print(f"{BASE_URL}/games?{params}")
        response = requests.get(f"{BASE_URL}/games", params=params, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response preview: {response.text[:200]}")

        data = response.json()
        games = data.get('data', [])
        print(f"API: {len(games)} games")

        results = []
        for game in games:
            if game['status'] != 'Final':
                continue

            def safe_gt(score):
                return score is not None and score > 0

            has_ot = any(safe_gt(game.get(f'home_ot{i}')) for i in range(1, 5)) or \
                     any(safe_gt(game.get(f'visitor_ot{i}')) for i in range(1, 5))

            home_scores = [game.get(f'home_q{i}', 0) or 0 for i in range(1, 5)]
            visitor_scores = [game.get(f'visitor_q{i}', 0) or 0 for i in range(1, 5)]

            home_cum = visitor_cum = 0
            tied_quarters = []
            valid_ties = []
            periods = {}

            for q in range(4):
                h_q = home_scores[q]
                v_q = visitor_scores[q]

                home_cum += h_q
                visitor_cum += v_q

                q_score = f"{v_q}-{h_q}"
                cum_score = f"{visitor_cum}-{home_cum}"
                periods[f'Q{q + 1}'] = f"{q_score} ({cum_score})"

                if home_cum == visitor_cum and home_cum > 0:
                    valid_ties.append(f"Q{q + 1} ({home_cum})")

                if home_cum == visitor_cum:
                    if q == 3 and has_ot:
                        tied_quarters.append(f"Q4 ({home_cum})")
                    else:
                        tied_quarters.append(f"Q{q + 1} ({home_cum})")

                regulation_score = f"{visitor_cum}-{home_cum}"

            if has_ot:
                for ot in range(1, 5):
                    h_ot = game.get(f'home_ot{ot}', None) or 0
                    v_ot = game.get(f'visitor_ot{ot}', None) or 0

                    if h_ot == 0 and v_ot == 0:
                        break

                    home_cum += h_ot
                    visitor_cum += v_ot

                    period_label = f'OT{ot}'
                    q_score = f"{v_ot}-{h_ot}"
                    cum_score = f"{visitor_cum}-{home_cum}"
                    periods[period_label] = f"{q_score} ({cum_score})"

                    if home_cum == visitor_cum:
                        tied_quarters.append(f"{period_label} ({home_cum})")
                    if home_cum == visitor_cum and home_cum > 0:
                        valid_ties.append(f"{period_label} ({home_cum})")

            period_order = ['Q1', 'Q2', 'Q3', 'Q4', 'OT1', 'OT2', 'OT3', 'OT4']
            periods = {k: periods[k] for k in period_order if k in periods}

            final_home = game.get('home_team_score') or home_cum
            final_visitor = game.get('visitor_team_score') or visitor_cum

            results.append({
                'date': game['date'][:10],
                'home_team': game['home_team']['full_name'],
                'visitor_team': game['visitor_team']['full_name'],
                'final_score': f"{final_visitor}-{final_home}",
                'regulation_score': regulation_score,
                'has_ot': bool(has_ot),
                'tied_quarters': tied_quarters,
                'valid_ties': valid_ties,
                'periods': periods
            })

        if view == 'regulation':
            results = [g for g in results if g['has_ot']]
            for game in results:
                game['periods'] = {k: v for k, v in game['periods'].items() if not k.startswith('OT')}

        if tied_only:
            results = [g for g in results if g['tied_quarters']]

        print(f"{len(results)} final score")
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
        print(f"FULL ERROR: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/teams', methods=['GET'])
def get_teams():
    try:
        headers = {"Authorization": API_KEY}
        response = requests.get(f"{BASE_URL}/teams", headers=headers)
        print(f"Teams status: {response.status_code}")
        return jsonify(response.json())
    except Exception as e:
        print(f"Teams error: {e}")
        return jsonify({'data': []}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, port=10000)
