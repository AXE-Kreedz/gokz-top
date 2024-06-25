def ft(seconds, as_colon=True):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60

    if hours > 0:
        if as_colon:
            return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        else:
            return f"{hours}h {minutes}m {seconds:.0f}s"
    else:
        if as_colon:
            return f"{minutes:02d}:{seconds:06.3f}"
        else:
            return f"{minutes}m {seconds:.3f}s"


def format_kzmode(mode, form="full") -> int | str:
    """return kz_timer, kz_simple or kz_vanilla in the specified format"""
    mode_mapping = {
        "v": ("kz_vanilla", "vnl", 0),
        "vnl": ("kz_vanilla", "vnl", 0),
        0: ("kz_vanilla", "vnl", 0),
        "0": ("kz_vanilla", "vnl", 0),
        "kz_vanilla": ("kz_vanilla", "vnl", 0),
        "s": ("kz_simple", "skz", 1),
        "skz": ("kz_simple", "skz", 1),
        1: ("kz_simple", "skz", 1),
        "1": ("kz_simple", "skz", 1),
        "kz_simple": ("kz_simple", "skz", 1),
        "k": ("kz_timer", "kzt", 2),
        "kzt": ("kz_timer", "kzt", 2),
        2: ("kz_timer", "kzt", 2),
        "2": ("kz_timer", "kzt", 2),
        "kz_timer": ("kz_timer", "kzt", 2),
    }

    if mode not in mode_mapping:
        raise ValueError("Invalid mode")

    formatted_mode = mode_mapping[mode]

    formats = {
        "full": formatted_mode[0],
        "f": formatted_mode[0],

        "mid": formatted_mode[1],
        "m": formatted_mode[1],

        "num": formatted_mode[2],
        "n": formatted_mode[2],
        "int": formatted_mode[2],
    }

    if form not in formats:
        raise ValueError("Invalid format type")

    return formats[form]

