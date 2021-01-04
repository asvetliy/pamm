def get_from_path(data, path, separator='.'):
    current = data
    path = path.split(separator)[0:]
    while len(path):
        key = path.pop(0)
        current = current.get(key)
        if type(current) is not dict and len(path):
            return None
    return current
