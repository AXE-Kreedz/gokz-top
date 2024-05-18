from config import MAP_TIERS


def get_map_tier_str(map_name=None) -> str:
    try:
        map_tier = MAP_TIERS[map_name]
        return "T" + str(map_tier)
    except KeyError:
        return "Unknown"


def get_map_tier(map_name=None) -> int:
    try:
        map_tier = MAP_TIERS[map_name]
        return map_tier
    except KeyError:
        return 0
