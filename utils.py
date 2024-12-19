def is_any_null_or_empty(*args) -> bool:
    for arg in args:
        if arg is None or arg == "":
            return True
    return False
