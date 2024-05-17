import asyncio

from app.core.database.records import fetch_pb_records
from config import MAP_TIERS

tier_count = {
    7: 24,
    6: 64,
    5: 66,
    4: 151,
    3: 240,
    'total': 938,
}


def get_records_data(rcds):
    count_p1000_tp = sum([1 for rcd in rcds if rcd['points'] == 1000 and rcd['teleports'] > 0])
    count_p1000_pro = sum([1 for rcd in rcds if rcd['points'] == 1000 and rcd['teleports'] == 0])
    count_p900 = sum([1 for rcd in rcds if 1000 > rcd['points'] >= 900])
    count_p800 = sum([1 for rcd in rcds if 900 > rcd['points'] >= 800])

    count = len(set([rcd['map_name'] for rcd in rcds]))
    count_t3 = len(set([rcd['map_name'] for rcd in rcds if MAP_TIERS.get(rcd['map_name']) == 3]))
    count_t4 = len(set([rcd['map_name'] for rcd in rcds if MAP_TIERS.get(rcd['map_name']) == 4]))
    count_t5 = len(set([rcd['map_name'] for rcd in rcds if MAP_TIERS.get(rcd['map_name']) == 5]))
    count_t6 = len(set([rcd['map_name'] for rcd in rcds if MAP_TIERS.get(rcd['map_name']) == 6]))
    count_t7 = len(set([rcd['map_name'] for rcd in rcds if MAP_TIERS.get(rcd['map_name']) == 7]))

    point_avg = sum([rcd['points'] for rcd in rcds]) / len(rcds) if len(rcds) else 0

    for tier in range(3, 8):
        tier_records = [rcd for rcd in rcds if MAP_TIERS.get(rcd['map_name']) == tier]
        if tier_records:
            globals()[f'point_avg_t{tier}'] = sum(rcd['points'] for rcd in tier_records) / len(tier_records)
        else:
            globals()[f'point_avg_t{tier}'] = 0

    count_t567_p900 = len([rcd['id'] for rcd in rcds if MAP_TIERS.get(rcd['map_name']) >= 5 and rcd['points'] > 900])
    count_t567_p800 = len([rcd['id'] for rcd in rcds if MAP_TIERS.get(rcd['map_name']) >= 5 and rcd['points'] > 800])
    count_t567_pro = len([rcd['id'] for rcd in rcds if MAP_TIERS.get(rcd['map_name']) >= 5 and rcd['teleports'] == 0])

    # for rcd in records:
    #     tier = MAP_TIERS.get(rcd['map_name'])
    #
    #     # count p800+
    #     if rcd['points'] == 1000:
    #         if rcd['teleports'] == 0:
    #             count_p1000_pro += 1
    #         else:
    #             count_p1000_tp += 1
    #     elif rcd['points'] > 900:
    #         count_p900 += 1
    #     elif rcd['points'] > 800:
    #         count_p800 += 1

    return {
        'count_p1000_tp': count_p1000_tp,
        'count_p1000_pro': count_p1000_pro,
        'count_p900': count_p900,
        'count_p800': count_p800,
        'count': count,
        'count_t3': count_t3,
        'count_t4': count_t4,
        'count_t5': count_t5,
        'count_t6': count_t6,
        'count_t7': count_t7,
        'point_avg': point_avg,
        'point_avg_t3': point_avg_t3,
        'point_avg_t4': point_avg_t4,
        'point_avg_t5': point_avg_t5,
        'point_avg_t6': point_avg_t6,
        'point_avg_t7': point_avg_t7,
        'count_t567_p900': count_t567_p900,
        'count_t567_p800': count_t567_p800,
        'count_t567_pro': count_t567_pro,
    }


def calc_skill_pts(player_data, count_map=tier_count['total'], count_map5=tier_count[5], count_map6=tier_count[6], count_map7=tier_count[7], count_map567=tier_count[5]+tier_count[6]+tier_count[7]):
    formula = {
        'root': 8,
        'coefficient': 0.91,
        'formula': [
            {'name': 'tpwr', 'key': 'count_p1000_tp', 'denominator': count_map, 'weight': 1.1, 'root': 3.5, 'text': 'tpwr数', 'description': '(tpwr数/总地图数)'},
            {'name': 'prowr', 'key': 'count_p1000_pro', 'denominator': count_map, 'weight': 6, 'root': 2.4, 'text': 'prowr数', 'description': '(prowr数/总地图数)'},
            {'name': '900+', 'key': 'count_p900', 'denominator': count_map, 'weight': .14, 'root': 2, 'text': '900+数', 'description': '(900+数/总地图数)'},
            {'name': '800+', 'key': 'count_p800', 'denominator': count_map, 'weight': .04, 'root': 2, 'text': '800+数', 'description': '(800+数/总地图数)', 'newline': True},

            {'name': 'point', 'key': 'point_avg', 'denominator': 1000, 'weight': .07, 'root': 1, 'text': '均分',  'description': '平均分/1000'},

            {'name': 'point3', 'key': 'point_avg_t3', 'denominator': 1000, 'weight': .01, 'root': 1, 'text': 't3均分',  'description': 't3平均分/1000'},
            {'name': 'point4', 'key': 'point_avg_t4', 'denominator': 1000, 'weight': .02, 'root': 1, 'text': 't4均分',  'description': 't4平均分/1000'},
            {'name': 'point5', 'key': 'point_avg_t5', 'denominator': 1000, 'weight': .1, 'root': 1, 'text': 't5均分',  'description': 't5平均分/1000'},
            {'name': 'point6', 'key': 'point_avg_t6', 'denominator': 1000, 'weight': .12, 'root': 1, 'text': 't6均分', 'description': 't6平均分/1000'},
            {'name': 'point7', 'key': 'point_avg_t7', 'denominator': 1000, 'weight': .17, 'root': 1, 'text': 't7均分', 'description': 't7平均分/1000', 'newline': True},

            {'name': 'count', 'key': 'count', 'denominator': count_map, 'weight': .01, 'root': 1, 'text': '地图数',  'description': '完成地图数/总地图数'},
            # {'name': 'countpro', 'key': 'count_pro', 'denominator': count_map, 'weight': .01, 'root': 1, 'text': 'pro地图数',  'description': 'pro完成地图数/总地图数', 'newline':True},

            # {'name': 'count3', 'key': 'count_t3', 'denominator': count_map3, 'weight': .005, 'root': 1.5, 'text': 't3地图数', 'description': '(t3完成地图数/t3总地图数)'},
            # {'name': 'count4', 'key': 'count_t4', 'denominator': count_map4, 'weight': .005, 'root': 1.5, 'text': 't4地图数', 'description': '(t4完成地图数/t4总地图数)'},
            {'name': 'count5', 'key': 'count_t5', 'denominator': count_map5, 'weight': .05, 'root': 1.5, 'text': 't5地图数', 'description': '(t5完成地图数/t5总地图数)'},
            {'name': 'count6', 'key': 'count_t6', 'denominator': count_map6, 'weight': .15, 'root': 1.5, 'text': 't6地图数', 'description': '(t6完成地图数/t6总地图数)'},
            {'name': 'count7', 'key': 'count_t7', 'denominator': count_map7, 'weight': .24, 'root': 1.5, 'text': 't7地图数', 'description': '(t7完成地图数/t7总地图数)', 'newline': True},

            {'name': 'point*count', 'key': 'point_avg*count', 'denominator': count_map * 1000, 'weight': .01, 'root': 1, 'text': '总分', 'description': '总分/1000/总地图数'},
            # {'name': 'pointpro*countpro', 'key': 'point_avg_pro*count_pro', 'denominator': count_map * 1000, 'weight': .01, 'root': 1, 'text': 'pro总分', 'description': 'pro总分/1000/总地图数', 'newline':True},

            # {'name': 'point3*count3', 'key': 'point_avg_t3*count_t3', 'denominator': count_map3 * 1000, 'weight': .01, 'root': 1, 'text': 't3总分', 'description': 't3总分/1000/t3总地图数'},
            # {'name': 'point4*count4', 'key': 'point_avg_t4*count_t4', 'denominator': count_map4 * 1000, 'weight': .01, 'root': 1, 'text': 't4总分', 'description': 't4总分/1000/t4总地图数'},
            # {'name': 'point5*count5', 'key': 'point_avg_t5*count_t5', 'denominator': count_map5 * 1000, 'weight': .05, 'root': 1, 'text': 't5总分', 'description': 't5总分/1000/t5总地图数'},
            # {'name': 'point6*count6', 'key': 'point_avg_t6*count_t6', 'denominator': count_map6 * 1000, 'weight': .08, 'root': 1, 'text': 't6总分', 'description': 't6总分/1000/t6总地图数'},
            # {'name': 'point7*count7', 'key': 'point_avg_t7*count_t7', 'denominator': count_map7 * 1000, 'weight': .16, 'root': 1, 'text': 't7总分', 'description': 't7总分/1000/t7总地图数', 'newline':True},

            {'name': '900+_count567', 'key': 'count_t567_p900', 'denominator': count_map567, 'weight': .06, 'root': 1, 'text': 't567 900+地图数', 'description': 't567 900+完成地图数/t567总地图数'},
            {'name': '800+_count567', 'key': 'count_t567_p800', 'denominator': count_map567, 'weight': .03, 'root': 1, 'text': 't567 800+地图数', 'description': 't567 800+完成地图数/t567总地图数'},
            {'name': 'count567pro', 'key': 'count_t567_pro', 'denominator': count_map567, 'weight': .06, 'root': 1, 'text': 't567pro地图数', 'description': 't567pro完成地图数/t567总地图数', 'newline': True},
        ]
    }
    formula['weights'] = sum([item['weight'] for item in formula['formula']])
    score = 0
    for item in formula['formula']:
        if '*' in item['key']:
            keys = item['key'].split('*')
            value = player_data[keys[0]]*player_data[keys[1]]
        else:
            value = player_data[item['key']]
        if item['denominator'] != 0:
            score += (value/item['denominator'])**(1/item['root'])*item['weight']

    point_skill = round((score / float(formula['weights'])) ** (1 / formula['root']) / formula['coefficient'] * 10, 4)
    return point_skill
