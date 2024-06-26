from collections import Counter

from app.core.utils.kreedz import get_map_tier, get_vnl_map_tier

map_count = {
    'kz_timer': {
        7: 24,
        6: 64,
        5: 66,
        4: 151,
        3: 240,
        'total': 938,
    },
    'kz_simple': {
        7: 23,
        6: 61,
        5: 65,
        4: 143,
        3: 236,
        'total': 922,
    },
    'kz_vanilla': {
        7: 54,
        6: 49,
        5: 66,
        4: 109,
        3: 118,
        'total': 531,
    },
}


def calc_player_data(rcds):
    player_data = {'name': rcds[-1]['player_name'], 'steamid': rcds[-1]['steam_id'], 'avatar_hash': ''}
    pts_avgs = {}
    counts = {}

    server_counts = Counter(rcd['server_name'] for rcd in rcds)
    most_played_server = server_counts.most_common(1)[0][0]
    player_data['most_played_server'] = most_played_server

    get_map_tier_func = get_vnl_map_tier if rcds[0]['mode'] == 'kz_vanilla' else get_map_tier

    for tier in range(0, 8):
        tier_records = [rcd for rcd in rcds if get_map_tier_func(rcd['map_name']) == tier]
        pts_avgs[f'pts_avg_t{tier}'] = int(
            sum(rcd['points'] for rcd in tier_records) / len(tier_records) if tier_records else 0)
        counts[f'count_t{tier}'] = len(set(rcd['map_name'] for rcd in tier_records))

    counts.update({
        'count_p1000_tp': sum(1 for rcd in rcds if rcd['points'] == 1000 and rcd['teleports'] > 0),
        'count_p1000_pro': sum(1 for rcd in rcds if rcd['points'] == 1000 and rcd['teleports'] == 0),
        'count_p900': sum(1 for rcd in rcds if 1000 > rcd['points'] >= 900),
        'count_p800': sum(1 for rcd in rcds if 900 > rcd['points'] >= 800),
        'count': len(set(rcd['map_name'] for rcd in rcds)),
        'count_t567_p900': len(
            [rcd['id'] for rcd in rcds if get_map_tier_func(rcd['map_name']) >= 5 and rcd['points'] > 900]),
        'count_t567_p800': len(
            [rcd['id'] for rcd in rcds if get_map_tier_func(rcd['map_name']) >= 5 and rcd['points'] > 800]),
        'count_t567_pro': len(
            [rcd['id'] for rcd in rcds if get_map_tier_func(rcd['map_name']) >= 5 and rcd['teleports'] == 0]),
    })

    pts_avgs['pts_avg'] = int(sum(rcd['points'] for rcd in rcds) / len(rcds) if rcds else 0)
    counts['count_pro'] = sum(1 for rcd in rcds if rcd['teleports'] == 0)
    counts['count_tp'] = sum(1 for rcd in rcds if rcd['teleports'] > 0)
    pts_avgs['pts_avg_pro'] = int(sum(rcd['points'] for rcd in rcds if rcd['teleports'] == 0) / counts['count_pro']) if \
        counts['count_pro'] else 0
    pts_avgs['pts_avg_tp'] = int(sum(rcd['points'] for rcd in rcds if rcd['teleports'] > 0) / counts['count_tp']) if \
        counts['count_tp'] else 0
    pts_avgs['total_points'] = sum(rcd['points'] for rcd in rcds)

    return {**player_data, **pts_avgs, **counts}


def calc_skill_pts(rcds):

    mode = rcds[0]['mode']
    tier_count = map_count[mode]
    total_count_map = tier_count['total']
    total_count_map5 = tier_count[5]
    total_count_map6 = tier_count[6]
    total_count_map7 = tier_count[7]
    total_count_map567 = tier_count[5] + tier_count[6] + tier_count[7]

    player_data = calc_player_data(rcds)
    formula = {
        'root': 8,
        'coefficient': 0.91,
        'formula': [
            {'name': 'tpwr', 'key': 'count_p1000_tp', 'denominator': total_count_map, 'weight': 1.1, 'root': 3.5,
             'text': 'tpwr count', 'description': '(tpwr count / total map count)'},
            {'name': 'prowr', 'key': 'count_p1000_pro', 'denominator': total_count_map, 'weight': 6, 'root': 2.4,
             'text': 'prowr count', 'description': '(prowr count / total map count)'},
            {'name': '900+', 'key': 'count_p900', 'denominator': total_count_map, 'weight': 0.14, 'root': 2,
             'text': '900+ count', 'description': '(900+ count / total map count)'},
            {'name': '800+', 'key': 'count_p800', 'denominator': total_count_map, 'weight': 0.04, 'root': 2,
             'text': '800+ count', 'description': '(800+ count / total map count)', 'newline': True},

            {'name': 'point', 'key': 'pts_avg', 'denominator': 1000, 'weight': 0.07, 'root': 1, 'text': 'avg pts',
             'description': 'average points / 1000'},

            {'name': 'point3', 'key': 'pts_avg_t3', 'denominator': 1000, 'weight': 0.01, 'root': 1, 'text': 't3 avg',
             'description': 't3 average points / 1000'},
            {'name': 'point4', 'key': 'pts_avg_t4', 'denominator': 1000, 'weight': 0.02, 'root': 1, 'text': 't4 avg',
             'description': 't4 average points / 1000'},
            {'name': 'point5', 'key': 'pts_avg_t5', 'denominator': 1000, 'weight': 0.1, 'root': 1, 'text': 't5 avg',
             'description': 't5 average points / 1000'},
            {'name': 'point6', 'key': 'pts_avg_t6', 'denominator': 1000, 'weight': 0.12, 'root': 1, 'text': 't6 avg',
             'description': 't6 average points / 1000'},
            {'name': 'point7', 'key': 'pts_avg_t7', 'denominator': 1000, 'weight': 0.17, 'root': 1, 'text': 't7 avg',
             'description': 't7 average points / 1000', 'newline': True},

            {'name': 'count', 'key': 'count', 'denominator': total_count_map, 'weight': 0.01, 'root': 1,
             'text': 'finished maps', 'description': 'finished maps count / total map count'},
            # {'name': 'countpro', 'key': 'count_pro', 'denominator': count_map, 'weight': 0.01, 'root': 1, 'text': 'pro maps count', 'description': 'pro finished maps count / total maps count', 'newline': True},

            # {'name': 'count3', 'key': 'count_t3', 'denominator': count_map3, 'weight': 0.005, 'root': 1.5, 'text': 't3 maps count', 'description': '(t3 finished maps count / t3 total maps count)'},
            # {'name': 'count4', 'key': 'count_t4', 'denominator': count_map4, 'weight': 0.005, 'root': 1.5, 'text': 't4 maps count', 'description': '(t4 finished maps count / t4 total maps count)'},
            {'name': 'count5', 'key': 'count_t5', 'denominator': total_count_map5, 'weight': 0.05, 'root': 1.5,
             'text': 'finished t5', 'description': '(t5 finished maps count / t5 total maps count)'},
            {'name': 'count6', 'key': 'count_t6', 'denominator': total_count_map6, 'weight': 0.15, 'root': 1.5,
             'text': 'finished t6', 'description': '(t6 finished maps count / t6 total maps count)'},
            {'name': 'count7', 'key': 'count_t7', 'denominator': total_count_map7, 'weight': 0.24, 'root': 1.5,
             'text': 'finished t7', 'description': '(t7 finished maps count / t7 total maps count)', 'newline': True},

            {'name': 'point*count', 'key': 'pts_avg*count', 'denominator': total_count_map * 1000, 'weight': 0.01,
             'root': 1, 'text': 'total points', 'description': 'total points / 1000 / total maps count'},
            # {'name': 'pointpro*countpro', 'key': 'pts_avg_pro*count_pro', 'denominator': count_map * 1000, 'weight': 0.01, 'root': 1, 'text': 'pro total points', 'description': 'pro total points / 1000 / total maps count', 'newline': True},

            # {'name': 'point3*count3', 'key': 'pts_avg_t3*count_t3', 'denominator': count_map3 * 1000, 'weight': 0.01, 'root': 1, 'text': 't3 total points', 'description': 't3 total points / 1000 / t3 total maps count'},
            # {'name': 'point4*count4', 'key': 'pts_avg_t4*count_t4', 'denominator': count_map4 * 1000, 'weight': 0.01, 'root': 1, 'text': 't4 total points', 'description': 't4 total points / 1000 / t4 total maps count'},
            # {'name': 'point5*count5', 'key': 'pts_avg_t5*count_t5', 'denominator': count_map5 * 1000, 'weight': 0.05, 'root': 1, 'text': 't5 total points', 'description': 't5 total points / 1000 / t5 total maps count'},
            # {'name': 'point6*count6', 'key': 'pts_avg_t6*count_t6', 'denominator': count_map6 * 1000, 'weight': 0.08, 'root': 1, 'text': 't6 total points', 'description': 't6 total points / 1000 / t6 total maps count'},
            # {'name': 'point7*count7', 'key': 'pts_avg_t7*count_t7', 'denominator': count_map7 * 1000, 'weight': 0.16, 'root': 1, 'text': 't7 total points', 'description': 't7 total points / 1000 / t7 total maps count', 'newline': True},

            {'name': '900+_count567', 'key': 'count_t567_p900', 'denominator': total_count_map567, 'weight': 0.06,
             'root': 1, 'text': 't567 900+ maps count',
             'description': 't567 900+ finished maps count / t567 total maps count'},
            {'name': '800+_count567', 'key': 'count_t567_p800', 'denominator': total_count_map567, 'weight': 0.03,
             'root': 1, 'text': 't567 800+ maps count',
             'description': 't567 800+ finished maps count / t567 total maps count'},
            {'name': 'count567pro', 'key': 'count_t567_pro', 'denominator': total_count_map567, 'weight': 0.06,
             'root': 1, 'text': 't567 pro maps count',
             'description': 't567 pro finished maps count / t567 total maps count', 'newline': True},
        ]

    }
    formula['weights'] = sum([item['weight'] for item in formula['formula']])

    score = 0
    for item in formula['formula']:
        if '*' in item['key']:
            keys = item['key'].split('*')
            value = player_data[keys[0]] * player_data[keys[1]]
        else:
            value = player_data[item['key']]
        if item['denominator'] != 0:
            score += (value / item['denominator']) ** (1 / item['root']) * item['weight']

    player_data['pts_skill'] = round(
        (score / float(formula['weights'])) ** (1 / formula['root']) / formula['coefficient'] * 10, 4)
    player_data['rank_name'] = get_rank_name(player_data['pts_skill'])

    return player_data


def get_rank_name(skill_pts):
    rank_names = {
        9.0: 'Legend',
        8.0: 'Master',
        7.0: 'Pro',
        6.0: 'Expert',
        5.5: 'Skilled',
        5.2: 'Regular',
        4.8: 'Casual',
        4.5: 'Beginner',
    }

    for pts, rank in rank_names.items():
        if skill_pts >= pts:
            return rank

    return 'New'


"""
10% percentile: 3.8958
20% percentile: 4.2781
30% percentile: 4.5188
40% percentile: 4.6960
50% percentile: 4.8428
60% percentile: 4.9817
70% percentile: 5.1206
80% percentile: 5.2737
90% percentile: 5.4775
"""
