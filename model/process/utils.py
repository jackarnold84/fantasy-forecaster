def safe_round(x, n):
    try:
        return round(x, n)
    except:
        return None
