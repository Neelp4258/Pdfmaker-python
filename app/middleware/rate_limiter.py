"""Rate limiting middleware using Redis."""
import time
import logging
from functools import wraps
from flask import request, jsonify, current_app
import redis

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter using Redis."""

    def __init__(self, redis_client, per_minute: int, per_hour: int):
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client instance
            per_minute: Max requests per minute
            per_hour: Max requests per hour
        """
        self.redis = redis_client
        self.per_minute = per_minute
        self.per_hour = per_hour

    def is_allowed(self, key: str) -> tuple[bool, str]:
        """
        Check if request is allowed under rate limits.

        Args:
            key: Rate limit key (e.g., API key or IP)

        Returns:
            Tuple of (allowed, message)
        """
        now = int(time.time())
        minute_key = f"ratelimit:{key}:minute:{now // 60}"
        hour_key = f"ratelimit:{key}:hour:{now // 3600}"

        # Check minute limit
        minute_count = self.redis.incr(minute_key)
        if minute_count == 1:
            self.redis.expire(minute_key, 60)

        if minute_count > self.per_minute:
            return False, f"Rate limit exceeded: {self.per_minute} requests per minute"

        # Check hour limit
        hour_count = self.redis.incr(hour_key)
        if hour_count == 1:
            self.redis.expire(hour_key, 3600)

        if hour_count > self.per_hour:
            return False, f"Rate limit exceeded: {self.per_hour} requests per hour"

        return True, ""

    def get_stats(self, key: str) -> dict:
        """Get current rate limit stats for key."""
        now = int(time.time())
        minute_key = f"ratelimit:{key}:minute:{now // 60}"
        hour_key = f"ratelimit:{key}:hour:{now // 3600}"

        minute_count = int(self.redis.get(minute_key) or 0)
        hour_count = int(self.redis.get(hour_key) or 0)

        return {
            'minute_count': minute_count,
            'minute_limit': self.per_minute,
            'hour_count': hour_count,
            'hour_limit': self.per_hour,
            'minute_remaining': max(0, self.per_minute - minute_count),
            'hour_remaining': max(0, self.per_hour - hour_count),
        }


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter():
    """Get global rate limiter instance."""
    return _rate_limiter


def rate_limit(f):
    """Decorator to apply rate limiting."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config['RATE_LIMIT_ENABLED']:
            return f(*args, **kwargs)

        limiter = get_rate_limiter()
        if not limiter:
            logger.warning("Rate limiter not initialized")
            return f(*args, **kwargs)

        # Use API key or IP as rate limit key
        rate_key = getattr(request, 'api_key', None) or request.remote_addr

        allowed, message = limiter.is_allowed(rate_key)
        if not allowed:
            logger.warning(f"Rate limit exceeded for {rate_key}")
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': message
            }), 429

        # Add rate limit headers
        stats = limiter.get_stats(rate_key)
        response = f(*args, **kwargs)

        if isinstance(response, tuple):
            response_obj, status_code = response[0], response[1]
        else:
            response_obj, status_code = response, 200

        if hasattr(response_obj, 'headers'):
            response_obj.headers['X-RateLimit-Minute-Limit'] = str(stats['minute_limit'])
            response_obj.headers['X-RateLimit-Minute-Remaining'] = str(stats['minute_remaining'])
            response_obj.headers['X-RateLimit-Hour-Limit'] = str(stats['hour_limit'])
            response_obj.headers['X-RateLimit-Hour-Remaining'] = str(stats['hour_remaining'])

        return response_obj, status_code if isinstance(response, tuple) else response_obj

    return decorated_function


def init_rate_limiter(app):
    """Initialize rate limiter for the app."""
    global _rate_limiter

    if not app.config['RATE_LIMIT_ENABLED']:
        logger.info("Rate limiting disabled")
        return

    try:
        redis_client = redis.from_url(
            app.config['REDIS_URL'],
            decode_responses=True,
            socket_connect_timeout=5
        )
        redis_client.ping()

        _rate_limiter = RateLimiter(
            redis_client,
            per_minute=app.config['RATE_LIMIT_PER_MINUTE'],
            per_hour=app.config['RATE_LIMIT_PER_HOUR']
        )

        logger.info(f"Rate limiting enabled: {app.config['RATE_LIMIT_PER_MINUTE']}/min, {app.config['RATE_LIMIT_PER_HOUR']}/hour")

    except Exception as e:
        logger.error(f"Failed to initialize rate limiter: {e}")
        logger.warning("Rate limiting will be disabled")
        _rate_limiter = None
