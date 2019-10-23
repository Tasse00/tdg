def get(val, dot_expr: str):
    for com in dot_expr.split("."):
        com = com.strip()
        if not com:
            continue
        val = getattr(val, com)
    return val
