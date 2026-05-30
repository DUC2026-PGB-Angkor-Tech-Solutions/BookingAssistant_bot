# Simple In-Memory Cache for temporary bot state tracking
class SimpleDB:
    _cache = {}

    @classmethod
    def set_state(cls, user_id, key, value):
        if user_id not in cls._cache:
            cls._cache[user_id] = {}
        cls._cache[user_id][key] = value

    @classmethod
    def get_state(cls, user_id, key):
        return cls._cache.get(user_id, {}).get(key, None)

    @classmethod
    def clear_state(cls, user_id):
        if user_id in cls._cache:
            cls._cache[user_id].clear()