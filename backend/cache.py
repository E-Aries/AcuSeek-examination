import json, hashlib
from config import REDIS_URL

_client = None
_available = False

def _get_redis():
    global _client, _available
    if _available:
        return _client
    if _client is None and REDIS_URL:
        try:
            import redis as _redis
            _client = _redis.from_url(REDIS_URL, decode_responses=True)
            _client.ping()
            _available = True
        except Exception:
            _client = None
            _available = False
    return _client if _available else None


def _make_key(prefix, **params):
    raw = str(sorted(params.items())) if params else ""
    h = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f"acuseek:{prefix}:{h}" if params else f"acuseek:{prefix}"


def cache_get(prefix, **params):
    r = _get_redis()
    if not r:
        return None
    try:
        val = r.get(_make_key(prefix, **params))
        return json.loads(val) if val else None
    except Exception:
        return None


def cache_set(prefix, data, ttl=60, **params):
    r = _get_redis()
    if not r:
        return
    try:
        r.setex(_make_key(prefix, **params), ttl, json.dumps(data, ensure_ascii=False, default=str))
    except Exception:
        pass


def cache_del(prefix, **params):
    r = _get_redis()
    if not r:
        return
    try:
        keys = list(r.scan_iter(f"acuseek:{prefix}:*")) if not params else [_make_key(prefix, **params)]
        for k in (keys if isinstance(keys, list) else list(keys)):
            r.delete(k)
    except Exception:
        pass