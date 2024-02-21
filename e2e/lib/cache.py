import os
import tempfile
from pathlib import Path
from typing import Optional

# system temp directory plus a fixed random string to reduce the chance of collision
TEMP_DIR = f"{tempfile.gettempdir()}/KDvAXGESBZ"


class Cache:
    """Key-value persistent cache. `cache_id` is relative to the `base_dir`
    The value of cache_id depends on how often you want to invalidate your cache
    NOTE:There is no invalidation or cleanup at runtime
    """

    def __init__(self, cache_id: str, base_dir: str = f"{TEMP_DIR}/.cache"):
        self.dir = f"{base_dir}/{cache_id}"
        os.makedirs(self.dir, exist_ok=True)
        self.cache = {}

    def put(self, key: str, value: str):
        with open(f"{self.dir}/{key}", "w+") as f:
            f.write(value)
            self.cache[key] = value

    def get(self, key: str) -> Optional[str]:
        if value := self.cache.get(key, None):
            return value
        path = f"{self.dir}/{key}"
        if Path(path).is_file():
            with open(path, "r") as f:
                return f.read()

    def delete(self, key: str):
        if key not in self.cache:
            return
        del self.cache[key]
