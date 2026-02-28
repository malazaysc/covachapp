import hashlib
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.cache import cache


class GeocodeRateLimiter:
    cache_key = "nominatim:last_call"

    @classmethod
    def throttle(cls):
        last = cache.get(cls.cache_key)
        now = time.monotonic()
        if last and now - last < 1:
            time.sleep(1 - (now - last))
        cache.set(cls.cache_key, time.monotonic(), timeout=2)


def geocode_city(query: str):
    query = (query or "").strip()
    if not query:
        return None

    key = f"geocode:{hashlib.sha1(query.encode()).hexdigest()}"
    cached = cache.get(key)
    if cached:
        return cached

    GeocodeRateLimiter.throttle()
    params = urlencode({"q": query, "format": "json", "limit": 1})
    request = Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": "CovachApp/1.0"},
    )
    try:
        with urlopen(request, timeout=5) as response:
            payload = response.read().decode("utf-8")
    except Exception:
        return None

    import json

    data = json.loads(payload)
    if not data:
        return None

    result = {
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
        "display_name": data[0]["display_name"],
    }
    cache.set(key, result, timeout=60 * 60 * 24)
    return result
