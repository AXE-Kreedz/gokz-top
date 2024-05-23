from config import MAP_TIERS, VNL_TIERS


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


def get_vnl_map_tier(map_name=None) -> int:
    try:
        map_tier = int(VNL_TIERS[map_name])
        map_tier = 7 if map_tier > 7 else map_tier
        return map_tier
    except KeyError:
        return 0
    except ValueError:
        return 0
