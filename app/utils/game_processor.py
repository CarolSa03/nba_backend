def process_game(game):
    if game['status'] != 'Final':
        return None

    has_ot = _has_overtime(game)
    home_scores = [game.get(f'home_q{i}', 0) or 0 for i in range(1, 5)]
    visitor_scores = [game.get(f'visitor_q{i}', 0) or 0 for i in range(1, 5)]

    tied_quarters = []
    valid_ties = []
    periods = {}
    home_cum = visitor_cum = 0

    for q in range(4):
        h_q = home_scores[q]
        v_q = visitor_scores[q]

        home_cum += h_q
        visitor_cum += v_q

        q_score = f"{v_q}-{h_q}"
        cum_score = f"{visitor_cum}-{home_cum}"
        periods[f'Q{q + 1}'] = f"{cum_score} ({q_score})"

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

    return {
        'date': game['date'][:10],
        'home_team': game['home_team']['full_name'],
        'visitor_team': game['visitor_team']['full_name'],
        'final_score': f"{final_visitor}-{final_home}",
        'regulation_score': regulation_score,
        'has_ot': bool(has_ot),
        'tied_quarters': tied_quarters,
        'valid_ties': valid_ties,
        'periods': periods
    }


def _has_overtime(game):
    def safe_gt(score):
        return score is not None and score > 0

    return any(safe_gt(game.get(f'home_ot{i}')) for i in range(1, 5)) or \
        any(safe_gt(game.get(f'visitor_ot{i}')) for i in range(1, 5))


def filter_by_view(games, view):
    if view == 'regulation':
        results = [g for g in games if g['has_ot']]
        for game in results:
            game['periods'] = {
                k: v for k, v in game['periods'].items()
                if not k.startswith('OT')
            }
        return results
    return games


def filter_tied_only(games):
    return [g for g in games if g['tied_quarters']]
