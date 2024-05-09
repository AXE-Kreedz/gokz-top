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
