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

    def __init__(
        self,
        tg_client: TGClient,
        repos: Any,
        settings: MTProtoSettings,
        user_id: int | None = None,
    ):
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

    async def _detect_and_mark_deleted_messages(
        self, channel_id: int, fetched_message_ids: list[int]
    ) -> int:
        """Detect messages that exist in DB but not in Telegram (deleted messages).

        Mark them as deleted with soft delete (is_deleted=TRUE, deleted_at=NOW).

        Args:
            channel_id: Channel ID to check
            fetched_message_ids: List of message IDs that currently exist in Telegram

        Returns:
            Count of messages marked as deleted
        """
        if not fetched_message_ids or not self.user_id:
            return 0

        try:
            from apps.di import get_container

            container = get_container()
            pool = await container.database.asyncpg_pool()

            async with pool.acquire() as conn:
                # Find messages in DB that weren't in the fetched list and aren't already marked deleted
                result = await conn.execute(
                    """
                    UPDATE posts
                    SET is_deleted = TRUE,
                        deleted_at = NOW(),
                        updated_at = NOW()
                    WHERE channel_id = $1
                        AND msg_id NOT IN (SELECT unnest($2::bigint[]))
                        AND is_deleted = FALSE
                    """,
                    abs(channel_id),
                    fetched_message_ids,
                )

                # Extract count from result (format: "UPDATE 5")
                deleted_count = (
                    int(result.split()[-1]) if result and result.startswith("UPDATE") else 0
                )

                return deleted_count

        except Exception as e:
            self.logger.warning(f"Failed to detect deleted messages: {e}")
            return 0

    async def _log_collection_progress(
        self,
        channel_id: int,
        phase: str,
        current: int,
        total: int,
        session_num: int = None,
        total_sessions: int = None,
        messages_in_session: int = None,
        session_limit: int = None,
        speed_msgs_per_sec: float = None,
        eta_seconds: int = None,
        channel_name: str = None,
    ):
        """Log detailed collection progress to audit log for frontend tracking.

        Args:
            channel_id: Channel being collected
            phase: Collection phase ('fetching', 'processing', 'complete')
            current: Current message count
            total: Total messages expected
            session_num: Current session number (for multi-session collections)
            total_sessions: Total sessions needed
            messages_in_session: Messages collected in current session
            session_limit: Message limit per session
            speed_msgs_per_sec: Collection speed
            eta_seconds: Estimated time to completion
            channel_name: Optional channel name for display
        """
        if not self.user_id:
            return

        try:
            from apps.mtproto.audit import log_mtproto_event

            metadata = {
                "channel_id": channel_id,
                "phase": phase,
                "messages_current": current,
                "messages_total": total,
                "progress_percent": round((current / total * 100) if total > 0 else 0, 2),
            }

            # Add channel name if provided
            if channel_name:
                metadata["channel_name"] = channel_name

            # Add session tracking if provided
            if session_num is not None and total_sessions is not None:
                metadata["session_current"] = session_num
                metadata["session_total"] = total_sessions
                metadata["session_progress_percent"] = round(
                    (session_num / total_sessions * 100) if total_sessions > 0 else 0, 2
                )

            # Add current session details
            if messages_in_session is not None and session_limit is not None:
                metadata["session_messages_current"] = messages_in_session
                metadata["session_messages_limit"] = session_limit
                metadata["session_messages_percent"] = round(
                    ((messages_in_session / session_limit * 100) if session_limit > 0 else 0),
                    2,
                )

            # Add performance metrics
            if speed_msgs_per_sec is not None:
                metadata["speed_messages_per_second"] = round(speed_msgs_per_sec, 2)

            if eta_seconds is not None:
                metadata["eta_seconds"] = eta_seconds
                metadata["eta_minutes"] = round(eta_seconds / 60, 1)

            await log_mtproto_event(
                user_id=self.user_id,
                action="collection_progress_detail",
                channel_id=channel_id,
                metadata=metadata,
            )
        except Exception as e:
            self.logger.warning(f"Failed to log progress: {e}")

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
            return {
                "status": "disabled",
                "ingested": 0,
                "updated": 0,
                "skipped": 0,
                "errors": 0,
            }

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

    async def _update_channel_metadata(self, channel_id: int) -> None:
        """Update channel metadata (subscriber count, title, etc.) from Telegram.

        Args:
            channel_id: Telegram channel ID to update
        """
        try:
            self.logger.info(f"📊 Fetching channel metadata for {channel_id}...")

            # Get full channel info from Telegram
            full_channel_response = await self.tg_client.get_full_channel(channel_id)

            if full_channel_response:
                # Telethon returns a messages.ChatFull object with full_chat attribute
                full_chat = getattr(full_channel_response, "full_chat", None)
                if full_chat:
                    subscriber_count = getattr(full_chat, "participants_count", 0)

                    self.logger.info(
                        f"✅ Channel {channel_id} has {subscriber_count:,} subscribers"
                    )

                    # Update channel in database using repository pool
                    pool = self.repos.channel_repo.pool

                    async with pool.acquire() as conn:
                        await conn.execute(
                            """
                            UPDATE channels
                            SET subscriber_count = $1,
                                updated_at = NOW()
                            WHERE id = $2
                            """,
                            subscriber_count,
                            abs(channel_id),  # Use absolute value for DB
                        )
                    self.logger.info(
                        f"💾 Updated subscriber_count={subscriber_count:,} in database for channel {abs(channel_id)}"
                    )
                else:
                    self.logger.warning(f"No full_chat data in response for {channel_id}")
            else:
                self.logger.warning(f"Could not fetch full channel info for {channel_id}")

        except Exception as e:
            self.logger.warning(f"Failed to update channel metadata for {channel_id}: {e}")
            # Don't fail collection if metadata update fails

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

            # Update channel metadata (subscriber count, etc.) before collecting messages
            await self._update_channel_metadata(channel_id)

            # For full collection, iter_history starts from newest and goes to oldest
            self.logger.info(f"Starting full collection for channel {channel_id} (limit={limit})")

            # Get channel name for progress tracking
            channel_name = f"Channel {channel_id}"
            try:
                # Query channel name from database
                from apps.di import get_container

                container = get_container()
                pool = await container.database.asyncpg_pool()
                async with pool.acquire() as conn:
                    result = await conn.fetchrow(
                        "SELECT title FROM channels WHERE id = $1", abs(channel_id)
                    )
                    if result and result["title"]:
                        channel_name = result["title"]
            except Exception as e:
                self.logger.debug(f"Could not fetch channel name: {e}")

            # Get total message count from channel for better progress tracking
            # First, let's estimate total messages by checking database
            try:
                existing_count = (
                    await self.repos.post_repo.count_posts_by_channel(channel_id)
                    if hasattr(self.repos.post_repo, "count_posts_by_channel")
                    else 0
                )
            except:
                existing_count = 0

            # Estimate sessions needed (limit is per session)
            estimated_total = max(existing_count, limit)  # Use existing count as baseline
            estimated_sessions = max(1, (estimated_total + limit - 1) // limit)  # Ceiling division
            current_session = 1

            # Use iter_history to get all messages from newest to oldest
            # Don't use offset_id manipulation - let iter_history handle pagination naturally
            messages = []
            message_count = 0
            fetch_start_time = datetime.now()

            self.logger.info(
                f"📥 Fetching up to {limit:,} messages from Telegram (Session {current_session}/{estimated_sessions})..."
            )

            # Log initial progress
            await self._log_collection_progress(
                channel_id=channel_id,
                phase="fetching",
                current=0,
                total=limit,
                session_num=current_session,
                total_sessions=estimated_sessions,
                messages_in_session=0,
                session_limit=limit,
                channel_name=channel_name,
            )

            async for message in self.tg_client.iter_history(peer, limit=limit):  # type: ignore
                messages.append(message)
                message_count += 1

                # Log progress every 500 messages for better granularity
                if message_count % 500 == 0:
                    elapsed = (datetime.now() - fetch_start_time).total_seconds()
                    speed = message_count / elapsed if elapsed > 0 else 0
                    eta = int((limit - message_count) / speed) if speed > 0 else 0

                    self.logger.info(
                        f"  📊 Fetched {message_count:,}/{limit:,} messages ({message_count / limit * 100:.1f}%) - {speed:.1f} msg/s"
                    )

                    # Log detailed progress
                    await self._log_collection_progress(
                        channel_id=channel_id,
                        phase="fetching",
                        current=message_count,
                        total=limit,
                        session_num=current_session,
                        total_sessions=estimated_sessions,
                        messages_in_session=message_count,
                        session_limit=limit,
                        speed_msgs_per_sec=speed,
                        eta_seconds=eta,
                        channel_name=channel_name,
                    )

            fetch_duration = (datetime.now() - fetch_start_time).total_seconds()
            fetch_speed = len(messages) / fetch_duration if fetch_duration > 0 else 0

            self.logger.info(
                f"✅ Fetched {len(messages):,} total messages in {fetch_duration:.1f}s ({fetch_speed:.1f} msg/s)"
            )

            if not messages:
                self.logger.info(f"No messages found for peer {peer}")
                return peer_stats

            # Log message ID range
            msg_ids = [m.id for m in messages if hasattr(m, "id")]
            if msg_ids:
                self.logger.info(f"  Message ID range: {min(msg_ids):,} to {max(msg_ids):,}")

            # Process all fetched messages with progress tracking
            self.logger.info(f"💾 Processing {len(messages):,} messages to database...")
            process_start_time = datetime.now()
            messages_processed = 0
            total_to_process = len(messages)

            # Log initial processing progress
            await self._log_collection_progress(
                channel_id=channel_id,
                phase="processing",
                current=0,
                total=total_to_process,
                session_num=current_session,
                total_sessions=estimated_sessions,
                channel_name=channel_name,
            )

            for message in messages:
                try:
                    # Normalize message to dict format using parser from DI
                    if self.parsers and hasattr(self.parsers, "normalize_message"):
                        normalized = self.parsers.normalize_message(message)
                    else:
                        # Fallback: lazy import if parsers not available via DI
                        from infra.tg.parsers import normalize_message

                        normalized = normalize_message(message)

                    # Check if normalization failed (returns None on error)
                    if normalized is None:
                        self.logger.warning("Failed to normalize message, skipping")
                        peer_stats["skipped"] += 1
                        continue

                    if not normalized.get("channel"):
                        peer_stats["skipped"] += 1
                        continue

                    # Ensure channel exists (pass user_id for new channels)
                    self.logger.debug(f"Ensuring channel: {normalized['channel']}")
                    await self.repos.channel_repo.ensure_channel(
                        **normalized["channel"], user_id=self.user_id
                    )
                    self.logger.debug("Channel ensured successfully")

                    # Upsert post
                    self.logger.debug(
                        f"Upserting post: channel_id={normalized['post']['channel_id']}, msg_id={normalized['post']['msg_id']}"
                    )

                    # Add is_deleted=FALSE to restore if message was previously marked deleted
                    normalized["post"]["is_deleted"] = False
                    normalized["post"]["deleted_at"] = None

                    post_result = await self.repos.post_repo.upsert_post(**normalized["post"])
                    self.logger.debug(f"Post upsert result: {post_result}")

                    # Add metrics snapshot
                    await self.repos.metrics_repo.add_or_update_snapshot(**normalized["metrics"])

                    # Update statistics
                    if post_result.get("inserted"):
                        peer_stats["ingested"] += 1
                    elif post_result.get("updated"):
                        peer_stats["updated"] += 1
                    else:
                        peer_stats["skipped"] += 1

                    messages_processed += 1

                    # Log progress every 500 messages during processing
                    if messages_processed % 500 == 0:
                        elapsed = (datetime.now() - process_start_time).total_seconds()
                        speed = messages_processed / elapsed if elapsed > 0 else 0
                        eta = (
                            int((total_to_process - messages_processed) / speed) if speed > 0 else 0
                        )

                        self.logger.info(
                            f"  💾 Processed {messages_processed:,}/{total_to_process:,} "
                            f"({messages_processed / total_to_process * 100:.1f}%) - {speed:.1f} msg/s"
                        )

                        # Log detailed processing progress
                        await self._log_collection_progress(
                            channel_id=channel_id,
                            phase="processing",
                            current=messages_processed,
                            total=total_to_process,
                            session_num=current_session,
                            total_sessions=estimated_sessions,
                            speed_msgs_per_sec=speed,
                            eta_seconds=eta,
                            channel_name=channel_name,
                        )

                    # Rate limiting
                    await asyncio.sleep(self.settings.MTPROTO_SLEEP_THRESHOLD / 1000)

                except Exception as e:
                    self.logger.error(f"Error processing message in peer {peer}: {e}")
                    peer_stats["errors"] += 1
                    continue

            # Log final processing stats
            process_duration = (datetime.now() - process_start_time).total_seconds()
            process_speed = messages_processed / process_duration if process_duration > 0 else 0
            total_duration = fetch_duration + process_duration

            self.logger.info(
                f"✅ Processing complete: {messages_processed:,} messages in {process_duration:.1f}s "
                f"({process_speed:.1f} msg/s)"
            )
            self.logger.info(
                f"📊 Total session time: {total_duration:.1f}s (fetch: {fetch_duration:.1f}s, process: {process_duration:.1f}s)"
            )

            # Log completion progress
            await self._log_collection_progress(
                channel_id=channel_id,
                phase="complete",
                current=messages_processed,
                total=messages_processed,
                session_num=current_session,
                total_sessions=estimated_sessions,
                speed_msgs_per_sec=process_speed,
                eta_seconds=0,
                channel_name=channel_name,
            )

            # Detect deleted messages (soft delete)
            deleted_count = await self._detect_and_mark_deleted_messages(
                channel_id=channel_id, fetched_message_ids=msg_ids
            )
            if deleted_count > 0:
                self.logger.info(
                    f"🗑️ Marked {deleted_count} deleted messages for channel {channel_id}"
                )
                peer_stats["deleted"] = deleted_count

            self.logger.info(f"Completed peer {peer}: {peer_stats}")

        except Exception as e:
            self.logger.error(f"Fatal error processing peer {peer}: {e}")
            peer_stats["errors"] += 1

        return peer_stats

    async def collect_channel_history(
        self,
        channel_username: str,
        limit: int = 100,
        offset_date: datetime | None = None,
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
            self.logger.error(
                f"Failed to collect history from {channel_username}: {e}", exc_info=True
            )
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
