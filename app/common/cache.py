import time

class LocalMemoryCache:
    def __init__(self):
        self.cache = {}

    def set(self, key, value, ttl=None):
        """
        Set a key-value pair in the cache with an optional TTL (time-to-live).
        :param key: The key for the cache entry.
        :param value: The value to be cached.
        :param ttl: Time-to-live in seconds. After this time, the cache entry will be invalidated.
        """
        expiration = time.time() + ttl if ttl else None
        self.cache[key] = {'value': value, 'expiration': expiration}

    def get(self, key):
        """
        Retrieve a value from the cache by its key.
        :param key: The key for the cache entry.
        :return: The cached value or None if the key does not exist or the TTL has expired.
        """
        item = self.cache.get(key)
        if item:
            if item['expiration'] is None or item['expiration'] > time.time():
                return item['value']
            else:
                # TTL has expired, remove the item from the cache
                self.cache.pop(key)
        return None

    def delete(self, key):
        """
        Delete a key-value pair from the cache.
        :param key: The key to delete from the cache.
        """
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """
        Clear the entire cache.
        """
        self.cache.clear()

    def __repr__(self):
        return f"LocalMemoryCache({self.cache})"

# # Example usage:
# cache = LocalMemoryCache()
# cache.set("user_id", 12345, ttl=10)  # Set with TTL of 10 seconds
# print(cache.get("user_id"))  # Should print 12345
# time.sleep(11)
# print(cache.get("user_id"))  # Should print None, as TTL has expired

