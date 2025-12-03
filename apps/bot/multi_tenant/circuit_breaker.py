"""
Circuit Breaker Pattern for Bot Management

Prevents cascading failures by stopping requests to failing bots temporarily.

Circuit States:
- CLOSED: Normal operation, all requests allowed
- OPEN: Too many failures, reject requests immediately
- HALF_OPEN: Testing if bot has recovered, allow limited requests

This prevents wasting resources on bots that are consistently failing.
"""

import time
from collections.abc import Callable, Coroutine
from enum import Enum
from typing import Any


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""

    def __init__(self, user_id: int, timeout_remaining: float):
        self.user_id = user_id
        self.timeout_remaining = timeout_remaining
        super().__init__(
            f"Circuit breaker is OPEN for user {user_id}. Retry in {timeout_remaining:.1f} seconds."
        )


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures

    Monitors request failures and temporarily blocks requests when
    failure threshold is exceeded.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: float = 60.0,
        success_threshold: int = 2,
    ):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of consecutive failures before opening
            timeout_seconds: How long to wait before trying again
            success_threshold: Number of successes to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold

        # State tracking
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None
        self.opened_at: float | None = None

    def _should_attempt_reset(self) -> bool:
        """Check if timeout has expired and we should try resetting"""
        if self.state != CircuitState.OPEN:
            return False

        if self.opened_at is None:
            return False

        return time.time() - self.opened_at >= self.timeout_seconds

    async def call(
        self, func: Callable[..., Coroutine[Any, Any, Any]], *args: Any, **kwargs: Any
    ) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception from func if it fails
        """
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                # Timeout expired, try half-open
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                # Still in timeout, reject request
                timeout_remaining = self.timeout_seconds - (time.time() - self.opened_at)
                raise CircuitBreakerOpenError(
                    user_id=kwargs.get("user_id", 0),
                    timeout_remaining=timeout_remaining,
                )

        # Execute function
        try:
            result = await func(*args, **kwargs)

            # Success handling
            self._record_success()
            return result

        except Exception:
            # Failure handling
            self._record_failure()
            raise

    def _record_success(self) -> None:
        """Record successful request"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                # Enough successes, close circuit
                self._close_circuit()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0

    def _record_failure(self) -> None:
        """Record failed request"""
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery test, reopen circuit
            self._open_circuit()
        elif self.state == CircuitState.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                # Too many failures, open circuit
                self._open_circuit()

    def _open_circuit(self) -> None:
        """Open the circuit (block requests)"""
        self.state = CircuitState.OPEN
        self.opened_at = time.time()
        self.failure_count = 0
        self.success_count = 0

    def _close_circuit(self) -> None:
        """Close the circuit (allow requests)"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.opened_at = None

    def reset(self) -> None:
        """Manually reset circuit breaker"""
        self._close_circuit()

    def get_state(self) -> dict[str, Any]:
        """
        Get current circuit breaker state

        Returns:
            Dictionary with state information
        """
        timeout_remaining = 0.0
        if self.state == CircuitState.OPEN and self.opened_at:
            timeout_remaining = max(0, self.timeout_seconds - (time.time() - self.opened_at))

        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_threshold": self.failure_threshold,
            "success_threshold": self.success_threshold,
            "timeout_seconds": self.timeout_seconds,
            "timeout_remaining": timeout_remaining,
            "last_failure_time": self.last_failure_time,
        }


class CircuitBreakerRegistry:
    """
    Registry to manage circuit breakers for multiple users

    Each user bot gets its own circuit breaker.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: float = 60.0,
        success_threshold: int = 2,
    ):
        """
        Initialize registry

        Args:
            failure_threshold: Default failure threshold for new breakers
            timeout_seconds: Default timeout for new breakers
            success_threshold: Default success threshold for new breakers
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold
        self._breakers: dict[int, CircuitBreaker] = {}

    def get_breaker(self, user_id: int) -> CircuitBreaker:
        """
        Get circuit breaker for user (create if needed)

        Args:
            user_id: User ID

        Returns:
            CircuitBreaker instance for the user
        """
        if user_id not in self._breakers:
            self._breakers[user_id] = CircuitBreaker(
                failure_threshold=self.failure_threshold,
                timeout_seconds=self.timeout_seconds,
                success_threshold=self.success_threshold,
            )
        return self._breakers[user_id]

    def reset_breaker(self, user_id: int) -> None:
        """
        Manually reset circuit breaker for user

        Args:
            user_id: User ID
        """
        if user_id in self._breakers:
            self._breakers[user_id].reset()

    def get_all_states(self) -> dict[int, dict[str, Any]]:
        """
        Get states of all circuit breakers

        Returns:
            Dictionary of user_id -> state info
        """
        return {user_id: breaker.get_state() for user_id, breaker in self._breakers.items()}

    def get_open_breakers(self) -> list[int]:
        """
        Get list of user IDs with open circuit breakers

        Returns:
            List of user IDs
        """
        return [
            user_id
            for user_id, breaker in self._breakers.items()
            if breaker.state == CircuitState.OPEN
        ]

    def get_half_open_breakers(self) -> list[int]:
        """
        Get list of user IDs with half-open circuit breakers

        Returns:
            List of user IDs
        """
        return [
            user_id
            for user_id, breaker in self._breakers.items()
            if breaker.state == CircuitState.HALF_OPEN
        ]


# Global registry instance
_circuit_breaker_registry: CircuitBreakerRegistry | None = None


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """
    Get global circuit breaker registry

    Returns:
        Shared CircuitBreakerRegistry instance
    """
    global _circuit_breaker_registry
    if _circuit_breaker_registry is None:
        _circuit_breaker_registry = CircuitBreakerRegistry(
            failure_threshold=5,  # 5 consecutive failures
            timeout_seconds=60.0,  # Wait 60 seconds before retry
            success_threshold=2,  # 2 successes to close
        )
        print("✅ Circuit breaker registry initialized")
    return _circuit_breaker_registry


async def with_circuit_breaker(user_id: int, func: Callable, *args: Any, **kwargs: Any) -> Any:
    """
    Execute function with circuit breaker protection (convenience function)

    Args:
        user_id: User ID for circuit breaker lookup
        func: Async function to execute
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Result from func

    Raises:
        CircuitBreakerOpenError: If circuit is open

    Example:
        result = await with_circuit_breaker(
            user_id=123,
            func=bot.send_message,
            chat_id=456,
            text="Hello"
        )
    """
    registry = get_circuit_breaker_registry()
    breaker = registry.get_breaker(user_id)
    return await breaker.call(func, *args, user_id=user_id, **kwargs)
