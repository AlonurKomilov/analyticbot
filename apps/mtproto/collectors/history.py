"""History data collector for Telegram channels/chats with repository integration."""

import asyncio
import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from apps.mtproto.config import MTProtoSettings
from core.ports.tg_client import TGClient


class HistoryCollector:
    """Collects message history from Telegram channels and stores in database.

    Implements idempotent history collection with rate limiting and error handling.
    """

    def __init__(self, tg_client: TGClient, repos: Any, settings: MTProtoSettings, user_id: int | None = None):
        """Initialize the history collector.

        Args:
            tg_client: Telegram client implementation
            repos: Repository container with channel_repo, post_repo, metrics_repo, parsers
            settings: MTProto configuration settings
            user_id: User ID for multi-tenant channel ownership (optional)
        """
        self.logger = logging.getLogger(__name__)
        self.tg_client = tg_client
        self.repos = repos
        self.settings = settings
        self.user_id = user_id

        # Get parsers from repos container (provided via DI)
        self.parsers = getattr(repos, "parsers", None)

    async def backfill_history_for_peers(
        self, peers: Sequence[str], limit_per_peer: int | None = None
    ) -> dict[str, Any]:
        """Backfill message history for multiple peers with repository storage.

        Args:
            peers: List of channel usernames or IDs to process
            limit_per_peer: Maximum messages per peer (defaults to settings)

        Returns:
            Dictionary with collection statistics
        """
        if not self.settings.MTPROTO_ENABLED or not self.settings.MTPROTO_HISTORY_ENABLED:
            self.logger.info("History collection disabled by feature flags")
            return {"status": "disabled", "ingested": 0, "updated": 0, "skipped": 0, "errors": 0}

        limit_per_peer = limit_per_peer or self.settings.MTPROTO_HISTORY_LIMIT_PER_RUN
        stats = {"ingested": 0, "updated": 0, "skipped": 0, "errors": 0}

        self.logger.info(f"Starting history backfill for {len(peers)} peers")

        # Process peers with concurrency control
        semaphore = asyncio.Semaphore(self.settings.MTPROTO_CONCURRENCY)

        async def process_peer(peer):
            async with semaphore:
                return await self._process_peer_history(peer, limit_per_peer)

        # Execute concurrent collection
        peer_tasks = [process_peer(peer) for peer in peers]
        peer_results = await asyncio.gather(*peer_tasks, return_exceptions=True)

        # Aggregate results
        for i, result in enumerate(peer_results):
            if isinstance(result, Exception):
                self.logger.error(f"Failed to process peer {peers[i]}: {result}")
                stats["errors"] += 1
            elif isinstance(result, dict):
                for key in ["ingested", "updated", "skipped", "errors"]:
                    stats[key] += result.get(key, 0)

        self.logger.info(f"History backfill complete: {stats}")
        return stats

    async def _process_peer_history(self, peer: str | int, limit: int) -> dict[str, int]:
        """Process history for a single peer.

        Args:
            peer: Channel username or ID (str or int)
            limit: Maximum messages to collect

        Returns:
            Statistics dictionary for this peer
        """
        peer_stats = {"ingested": 0, "updated": 0, "skipped": 0, "errors": 0}

        try:
            self.logger.info(f"Processing history for peer: {peer}")

            # Resolve peer to get channel ID
            try:
                # Handle both string and int peer identifiers
                peer_id = peer
                if isinstance(peer, str) and not peer.lstrip("-").isdigit():
                    # This is a username, we'd need to resolve it
                    # For now, we'll skip username resolution in this stub
                    self.logger.warning(f"Username resolution not implemented: {peer}")
                    return peer_stats

                channel_id = int(peer_id) if str(peer_id).lstrip("-").isdigit() else 0

                if channel_id == 0:
                    self.logger.error(f"Invalid channel ID for peer: {peer}")
                    peer_stats["errors"] += 1
                    return peer_stats

            except (ValueError, TypeError) as e:
                self.logger.error(f"Failed to resolve peer {peer}: {e}")
                peer_stats["errors"] += 1
                return peer_stats

            # Get last processed message ID for incremental sync
            last_msg_id = await self.repos.post_repo.max_msg_id(channel_id)
            offset_id = last_msg_id or 0

            self.logger.debug(f"Starting from message ID {offset_id} for channel {channel_id}")

            # Collect messages in chunks
            messages_processed = 0
            chunk_size = min(200, limit)  # Process in smaller chunks

            while messages_processed < limit:
                try:
                    chunk_limit = min(chunk_size, limit - messages_processed)

                    # Get messages in chunks using proper async iteration (don't await async generators)
                    messages = []
                    async for message in self.tg_client.iter_history(  # type: ignore
                        peer, offset_id=offset_id, limit=chunk_limit
                    ):
                        messages.append(message)

                        # Update offset for next iteration
                        if hasattr(message, "id"):
                            offset_id = max(offset_id, message.id)

                    if not messages:
                        self.logger.debug(f"No more messages for peer {peer}")
                        break

                    # Process messages in this chunk
                    for message in messages:
                        try:
                            # Normalize message to dict format using parser from DI
                            if self.parsers and hasattr(self.parsers, "normalize_message"):
                                normalized = self.parsers.normalize_message(message)
                            else:
                                # Fallback: lazy import if parsers not available via DI
                                from infra.tg.parsers import normalize_message

                                normalized = normalize_message(message)

                            if not normalized or not normalized.get("channel"):
                                peer_stats["skipped"] += 1
                                continue

                            # Ensure channel exists (pass user_id for new channels)
                            self.logger.debug(f"Ensuring channel: {normalized['channel']}")
                            await self.repos.channel_repo.ensure_channel(
                                **normalized["channel"],
                                user_id=self.user_id
                            )
                            self.logger.debug(f"Channel ensured successfully")

                            # Upsert post
                            self.logger.debug(f"Upserting post: channel_id={normalized['post']['channel_id']}, msg_id={normalized['post']['msg_id']}")
                            post_result = await self.repos.post_repo.upsert_post(
                                **normalized["post"]
                            )
                            self.logger.debug(f"Post upsert result: {post_result}")

                            # Add metrics snapshot
                            await self.repos.metrics_repo.add_or_update_snapshot(
                                **normalized["metrics"]
                            )

                            # Update statistics
                            if post_result.get("inserted"):
                                peer_stats["ingested"] += 1
                            elif post_result.get("updated"):
                                peer_stats["updated"] += 1
                            else:
                                peer_stats["skipped"] += 1

                            messages_processed += 1

                            # Rate limiting
                            await asyncio.sleep(self.settings.MTPROTO_SLEEP_THRESHOLD / 1000)

                        except Exception as e:
                            self.logger.error(f"Error processing message in peer {peer}: {e}")
                            peer_stats["errors"] += 1
                            continue

                    # Inter-chunk delay
                    if messages:
                        await asyncio.sleep(self.settings.MTPROTO_SLEEP_THRESHOLD)

                except Exception as e:
                    self.logger.error(f"Error fetching chunk for peer {peer}: {e}")
                    peer_stats["errors"] += 1
                    break

            self.logger.info(f"Completed peer {peer}: {peer_stats}")

        except Exception as e:
            self.logger.error(f"Fatal error processing peer {peer}: {e}")
            peer_stats["errors"] += 1

        return peer_stats

    async def collect_channel_history(
        self, channel_username: str, limit: int = 100, offset_date: datetime | None = None
    ) -> list[dict[str, Any]]:
        """Legacy method for backward compatibility.

        Args:
            channel_username: Username or ID of the channel
            limit: Maximum number of messages to collect
            offset_date: Start collecting from this date (unused in current implementation)

        Returns:
            List of normalized message data
        """
        if not self.settings.MTPROTO_ENABLED:
            self.logger.info("MTProto disabled, returning empty results")
            return []

        try:
            messages = []
            # Get async iterator (don't await async generators)
            async for message in self.tg_client.iter_history(channel_username, limit=limit):  # type: ignore
                # Use parser from DI or fallback to lazy import
                if self.parsers and hasattr(self.parsers, "normalize_message"):
                    normalized = self.parsers.normalize_message(message)
                else:
                    from infra.tg.parsers import normalize_message

                    normalized = normalize_message(message)

                if normalized:
                    messages.append(normalized)

            return messages

        except Exception as e:
            self.logger.error(f"Failed to collect history from {channel_username}: {e}", exc_info=True)
            return []

    async def collect_batch_history(
        self, channels: list[str], limit_per_channel: int = 100
    ) -> dict[str, list[dict[str, Any]]]:
        """Collect history from multiple channels in batch.

        Args:
            channels: List of channel usernames/IDs
            limit_per_channel: Message limit per channel

        Returns:
            Dictionary mapping channel names to their normalized message lists
        """
        results = {}

        for channel in channels:
            try:
                messages = await self.collect_channel_history(channel, limit=limit_per_channel)
                results[channel] = messages
            except Exception as e:
                self.logger.error(f"Failed to collect from {channel}: {e}")
                results[channel] = []

        return results


async def backfill_history_for_peers(
    tg: TGClient, peers: Sequence[str], repos: Any, limit: int
) -> dict:
    """Standalone function for history backfill (matches PR specification).

    Args:
        tg: TGClient instance
        peers: List of peer identifiers
        repos: Repository container
        limit: Message limit per peer

    Returns:
        Statistics dictionary
    """
    from apps.mtproto.config import MTProtoSettings

    settings = MTProtoSettings()
    collector = HistoryCollector(tg, repos, settings)

    return await collector.backfill_history_for_peers(peers, limit)
