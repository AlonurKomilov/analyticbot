"""
MTProto Account Pool for horizontal scaling with lease-based management.
Manages multiple Telegram user sessions with health scoring and load balancing.
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncContextManager, Protocol

from infra.common.ratelimit import AccountLimiter

logger = logging.getLogger(__name__)


class AccountStatus(Enum):
    """Account health status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    QUARANTINED = "quarantined"
    OFFLINE = "offline"


@dataclass
class AccountState:
    """State tracking for a single account."""

    name: str
    client: Any  # TGClient interface
    status: AccountStatus = AccountStatus.OFFLINE
    inflight_requests: int = 0
    last_used: float = field(default_factory=time.time)
    fail_count: int = 0
    last_failure: float | None = None
    total_requests: int = 0
    flood_wait_until: float = 0.0

    @property
    def is_available(self) -> bool:
        """Check if account is available for use."""
        if self.status != AccountStatus.HEALTHY:
            return False
        if time.time() < self.flood_wait_until:
            return False
        return True

    @property
    def load_score(self) -> float:
        """Calculate load score for selection (lower is better)."""
        base_score = self.inflight_requests

        # Add penalty for recent failures
        if self.last_failure and (time.time() - self.last_failure) < 300:  # 5 minutes
            base_score += self.fail_count * 0.5

        # Add small penalty for flood wait
        if time.time() < self.flood_wait_until:
            base_score += 10

        # Add randomness to prevent thundering herd
        return base_score + random.uniform(0, 0.1)


class TGClientProtocol(Protocol):
    """Protocol for Telegram client interface."""

    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def is_connected(self) -> bool: ...


class AccountLeaseContext:
    """Context manager for account leases."""

    def __init__(self, pool: "AccountPool", account: AccountState, limiter: AccountLimiter):
        self.pool = pool
        self.account = account
        self.limiter = limiter
        self.client = account.client
        self._entered = False

    async def __aenter__(self):
        """Acquire account lease."""
        if self._entered:
            raise RuntimeError("Account lease context manager is not reentrant")

        self._entered = True

        # Wait for rate limiting
        await self.limiter.acquire_with_delay()

        # Update account state
        self.account.inflight_requests += 1
        self.account.last_used = time.time()
        self.account.total_requests += 1

        logger.debug(
            f"Acquired lease for account {self.account.name} "
            f"(inflight: {self.account.inflight_requests})"
        )

        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release account lease."""
        if not self._entered:
            return

        self.account.inflight_requests = max(0, self.account.inflight_requests - 1)

        # Handle exceptions
        if exc_type is not None:
            await self.pool._handle_account_error(self.account, exc_val)
        else:
            # Reset fail count on success
            self.account.fail_count = 0
            if self.account.status == AccountStatus.UNHEALTHY:
                self.account.status = AccountStatus.HEALTHY
                logger.info(f"Account {self.account.name} recovered to healthy status")

        logger.debug(
            f"Released lease for account {self.account.name} "
            f"(inflight: {self.account.inflight_requests})"
        )


class AccountPool:
    """Pool of Telegram accounts for horizontal scaling."""

    def __init__(
        self,
        factory: callable,  # Factory function to create TGClient
        accounts: list[str],  # Account session names
        rps_per_account: float,
        max_concurrency_per_account: int,
        fail_threshold: int = 3,
        quarantine_duration: float = 300.0,  # 5 minutes
    ):
        self.factory = factory
        self.accounts_config = accounts
        self.rps_per_account = rps_per_account
        self.max_concurrency = max_concurrency_per_account
        self.fail_threshold = fail_threshold
        self.quarantine_duration = quarantine_duration

        self.accounts: list[AccountState] = []
        self.limiters: dict[str, AccountLimiter] = {}
        self._started = False
        self._lock = asyncio.Lock()

        # Initialize accounts
        for account_name in accounts:
            try:
                client = factory(session_name=account_name)
                account = AccountState(name=account_name, client=client)
                self.accounts.append(account)

                # Create rate limiter for account
                self.limiters[account_name] = AccountLimiter(
                    account_name, rps_per_account, max_concurrency_per_account
                )

            except Exception as e:
                logger.error(f"Failed to create client for account {account_name}: {e}")

    async def start(self) -> None:
        """Start all accounts in the pool."""
        if self._started:
            return

        logger.info(f"Starting account pool with {len(self.accounts)} accounts")

        for account in self.accounts:
            try:
                await account.client.start()
                account.status = AccountStatus.HEALTHY
                logger.info(f"Started account {account.name}")
            except Exception as e:
                logger.error(f"Failed to start account {account.name}: {e}")
                account.status = AccountStatus.OFFLINE
                account.fail_count = self.fail_threshold  # Mark as failed

        self._started = True

        # Log pool status
        healthy_count = len([a for a in self.accounts if a.status == AccountStatus.HEALTHY])
        logger.info(f"Account pool started: {healthy_count}/{len(self.accounts)} accounts healthy")

    async def stop(self) -> None:
        """Stop all accounts in the pool."""
        if not self._started:
            return

        logger.info("Stopping account pool")

        # Wait for all inflight requests to complete (with timeout)
        timeout_end = time.time() + 30  # 30 second timeout
        while any(a.inflight_requests > 0 for a in self.accounts) and time.time() < timeout_end:
            await asyncio.sleep(0.1)

        # Force stop all accounts
        for account in self.accounts:
            try:
                await account.client.stop()
                account.status = AccountStatus.OFFLINE
                logger.debug(f"Stopped account {account.name}")
            except Exception as e:
                logger.error(f"Error stopping account {account.name}: {e}")

        self._started = False
        logger.info("Account pool stopped")

    async def lease(self) -> AsyncContextManager[Any]:
        """Lease an account from the pool."""
        if not self._started:
            raise RuntimeError("Account pool not started")

        account = await self._select_best_account()
        if not account:
            raise RuntimeError("No healthy accounts available in pool")

        limiter = self.limiters[account.name]
        return AccountLeaseContext(self, account, limiter)

    async def _select_best_account(self) -> AccountState | None:
        """Select the best available account."""
        available_accounts = []

        # Check for account recovery from quarantine
        await self._check_quarantine_recovery()

        for account in self.accounts:
            if account.is_available:
                available_accounts.append(account)

        if not available_accounts:
            logger.warning("No healthy accounts available")
            return None

        # Sort by load score (lower is better)
        available_accounts.sort(key=lambda a: a.load_score)
        selected = available_accounts[0]

        logger.debug(
            f"Selected account {selected.name} "
            f"(load_score: {selected.load_score:.2f}, "
            f"inflight: {selected.inflight_requests})"
        )

        return selected

    async def _check_quarantine_recovery(self) -> None:
        """Check if any quarantined accounts can be recovered."""
        current_time = time.time()

        for account in self.accounts:
            if (
                account.status == AccountStatus.QUARANTINED
                and account.last_failure
                and current_time - account.last_failure > self.quarantine_duration
            ):
                # Try to reconnect
                try:
                    if await account.client.is_connected():
                        account.status = AccountStatus.HEALTHY
                        account.fail_count = 0
                        logger.info(f"Account {account.name} recovered from quarantine")
                    else:
                        # Try to restart
                        await account.client.start()
                        account.status = AccountStatus.HEALTHY
                        account.fail_count = 0
                        logger.info(f"Account {account.name} restarted and recovered")

                except Exception as e:
                    logger.warning(f"Failed to recover account {account.name}: {e}")
                    # Keep in quarantine, will try again later

    async def _handle_account_error(self, account: AccountState, error: Exception) -> None:
        """Handle error for a specific account."""
        account.fail_count += 1
        account.last_failure = time.time()

        error_str = str(error).lower()

        # Handle flood wait errors
        if "flood" in error_str and "wait" in error_str:
            # Extract wait time if possible
            try:
                import re

                match = re.search(r"(\d+)", error_str)
                if match:
                    wait_seconds = int(match.group(1))
                    account.flood_wait_until = time.time() + wait_seconds
                    logger.warning(f"Account {account.name} flood wait for {wait_seconds}s")
                else:
                    account.flood_wait_until = time.time() + 60  # Default 1 minute
            except:
                account.flood_wait_until = time.time() + 60

        # Mark as unhealthy or quarantine based on fail count
        if account.fail_count >= self.fail_threshold:
            account.status = AccountStatus.QUARANTINED
            logger.error(f"Account {account.name} quarantined after {account.fail_count} failures")
        else:
            account.status = AccountStatus.UNHEALTHY
            logger.warning(
                f"Account {account.name} marked unhealthy "
                f"(failures: {account.fail_count}/{self.fail_threshold})"
            )

    def get_stats(self) -> dict[str, Any]:
        """Get pool statistics."""
        status_counts = {}
        for status in AccountStatus:
            status_counts[status.value] = len([a for a in self.accounts if a.status == status])

        total_inflight = sum(a.inflight_requests for a in self.accounts)
        total_requests = sum(a.total_requests for a in self.accounts)

        account_details = []
        for account in self.accounts:
            account_details.append(
                {
                    "name": account.name,
                    "status": account.status.value,
                    "inflight": account.inflight_requests,
                    "total_requests": account.total_requests,
                    "fail_count": account.fail_count,
                    "flood_wait_remaining": max(0, account.flood_wait_until - time.time()),
                    "load_score": account.load_score,
                    "last_used": account.last_used,
                }
            )

        return {
            "total_accounts": len(self.accounts),
            "status_counts": status_counts,
            "total_inflight_requests": total_inflight,
            "total_requests_processed": total_requests,
            "pool_started": self._started,
            "accounts": account_details,
            "config": {
                "rps_per_account": self.rps_per_account,
                "max_concurrency_per_account": self.max_concurrency,
                "fail_threshold": self.fail_threshold,
                "quarantine_duration": self.quarantine_duration,
            },
        }

    @property
    def healthy_count(self) -> int:
        """Get count of healthy accounts."""
        return len([a for a in self.accounts if a.status == AccountStatus.HEALTHY])

    @property
    def is_ready(self) -> bool:
        """Check if pool is ready (started and has healthy accounts)."""
        return self._started and self.healthy_count > 0
