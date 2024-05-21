
def get_formula():
    formula = {
        'root': 8,
        'coefficient': 0.91,
        'formula': [
            {'name': 'tpwr', 'key': 'count_p1000_tp', 'weight': 1.1, 'root': 3.5, 'text': 'tpwr count', 'description': '(tpwr count / total map count)'},
            {'name': 'prowr', 'key': 'count_p1000_pro', 'weight': 6, 'root': 2.4,
             'text': 'prowr count', 'description': '(prowr count / total map count)'},
            {'name': '900+', 'key': 'count_p900', 'weight': 0.14, 'root': 2,
             'text': '900+ count', 'description': '(900+ count / total map count)'},
            {'name': '800+', 'key': 'count_p800', 'weight': 0.04, 'root': 2,
             'text': '800+ count', 'description': '(800+ count / total map count)', 'newline': True},

            {'name': 'point', 'key': 'pts_avg',  'weight': 0.07, 'root': 1, 'text': 'avg pts',
             'description': 'average points / 1000'},

            {'name': 'point3', 'key': 'pts_avg_t3', 'weight': 0.01, 'root': 1, 'text': 't3 avg',
             'description': 't3 average points / 1000'},
            {'name': 'point4', 'key': 'pts_avg_t4',  'weight': 0.02, 'root': 1, 'text': 't4 avg',
             'description': 't4 average points / 1000'},
            {'name': 'point5', 'key': 'pts_avg_t5', 'weight': 0.1, 'root': 1, 'text': 't5 avg',
             'description': 't5 average points / 1000'},
            {'name': 'point6', 'key': 'pts_avg_t6', 'weight': 0.12, 'root': 1, 'text': 't6 avg',
             'description': 't6 average points / 1000'},
            {'name': 'point7', 'key': 'pts_avg_t7',  'weight': 0.17, 'root': 1, 'text': 't7 avg',
             'description': 't7 average points / 1000', 'newline': True},
            {'name': 'count', 'key': 'count', 'weight': 0.01, 'root': 1,
             'text': 'finished maps', 'description': 'finished maps count / total map count'},
            {'name': 'count5', 'key': 'count_t5',  'weight': 0.05, 'root': 1.5,
             'text': 'finished t5', 'description': '(t5 finished maps count / t5 total maps count)'},
            {'name': 'count6', 'key': 'count_t6',  'weight': 0.15, 'root': 1.5,
             'text': 'finished t6', 'description': '(t6 finished maps count / t6 total maps count)'},
            {'name': 'count7', 'key': 'count_t7', 'weight': 0.24, 'root': 1.5,
             'text': 'finished t7', 'description': '(t7 finished maps count / t7 total maps count)', 'newline': True},
            {'name': 'point*count', 'key': 'pts_avg*count', 'weight': 0.01,
             'root': 1, 'text': 'total points', 'description': 'total points / 1000 / total maps count'},
            {'name': '900+_count567', 'key': 'count_t567_p900', 'weight': 0.06,
             'root': 1, 'text': 't567 900+ maps count',
             'description': 't567 900+ finished maps count / t567 total maps count'},
            {'name': '800+_count567', 'key': 'count_t567_p800', 'weight': 0.03,
             'root': 1, 'text': 't567 800+ maps count',
             'description': 't567 800+ finished maps count / t567 total maps count'},
            {'name': 'count567pro', 'key': 'count_t567_pro', 'weight': 0.06,
             'root': 1, 'text': 't567 pro maps count',
             'description': 't567 pro finished maps count / t567 total maps count', 'newline': True},
        ]
    }
    formula['weights'] = sum([item['weight'] for item in formula['formula']])
    return formula
