from json import loads, dumps

def deep_copy(obj):
    return loads(dumps(obj))
