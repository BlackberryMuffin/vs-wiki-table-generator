from msgpack import packb, unpackb

def deep_copy(obj):
    return unpackb(packb(obj))
