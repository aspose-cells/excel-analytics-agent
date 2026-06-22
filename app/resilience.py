import time
import functools
from typing import Any, Callable, TypeVar

from app.logger import logger

F = TypeVar("F", bound=Callable[..., Any])


class CircuitBreaker:
    STATE_CLOSED = "closed"
    STATE_OPEN = "open"
    STATE_HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = self.STATE_CLOSED

    def call(self, fn: Callable, *args, **kwargs):
        if self.state == self.STATE_OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                logger.info("Circuit breaker transitioning to half-open")
                self.state = self.STATE_HALF_OPEN
            else:
                raise RuntimeError(f"Circuit breaker is OPEN for {fn.__name__}")

        try:
            result = fn(*args, **kwargs)
            if self.state == self.STATE_HALF_OPEN:
                logger.info("Circuit breaker recovering to closed")
                self.state = self.STATE_CLOSED
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            logger.error("Circuit breaker failure %d/%d for %s: %s",
                         self.failure_count, self.failure_threshold, fn.__name__, e)
            if self.failure_count >= self.failure_threshold:
                self.state = self.STATE_OPEN
                logger.warning("Circuit breaker OPEN for %s", fn.__name__)
            raise

    def reset(self):
        self.state = self.STATE_CLOSED
        self.failure_count = 0
        logger.info("Circuit breaker manually reset")


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exc_types: tuple = (Exception,)):
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exc_types as e:
                    last_exc = e
                    if attempt < max_attempts:
                        logger.warning("Retry %d/%d for %s after %.1fs: %s",
                                       attempt, max_attempts, func.__name__, current_delay, e)
                        time.sleep(current_delay)
                        current_delay *= backoff
            if last_exc is None:
                raise RuntimeError(f"Unexpected error in {func.__name__}")
            logger.error("All %d retries failed for %s: %s", max_attempts, func.__name__, last_exc)
            raise last_exc
        return wrapper  # type: ignore
    return decorator


class FallbackRegistry:
    def __init__(self):
        self._fallbacks: dict[str, Callable] = {}

    def register(self, name: str, fallback_fn: Callable):
        self._fallbacks[name] = fallback_fn
        logger.debug("Fallback registered: %s", name)

    def execute(self, name: str, primary: Callable, *args, **kwargs):
        try:
            return primary(*args, **kwargs)
        except Exception as e:
            logger.error("Primary %s failed: %s. Attempting fallback.", name, e)
            if name in self._fallbacks:
                return self._fallbacks[name](*args, **kwargs)
            raise


fallback_registry = FallbackRegistry()
