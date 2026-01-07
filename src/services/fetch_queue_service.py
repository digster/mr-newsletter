"""Fetch queue service for managing newsletter fetch operations."""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class FetchPriority(Enum):
    """Priority levels for fetch operations."""

    HIGH = 1  # Manual refresh
    NORMAL = 2  # Scheduled fetch
    LOW = 3  # Background fetch


class FetchStatus(Enum):
    """Status of a fetch operation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FetchTask:
    """A task in the fetch queue."""

    newsletter_id: int
    priority: FetchPriority
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: FetchStatus = FetchStatus.PENDING
    error: Optional[str] = None
    emails_fetched: int = 0

    def __lt__(self, other: "FetchTask") -> bool:
        """Compare tasks by priority for heap ordering."""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at


@dataclass
class QueueStatus:
    """Status of the fetch queue."""

    is_running: bool
    queue_length: int
    current_task: Optional[int]  # Newsletter ID being fetched
    completed_count: int
    failed_count: int


class FetchQueueService:
    """Service for queuing and processing newsletter fetch operations.

    Features:
    - Priority-based queue (manual refresh gets priority)
    - Configurable delay between fetches to avoid rate limiting
    - Progress tracking
    - Error handling with retry capability
    """

    def __init__(
        self,
        delay_seconds: int = 5,
        fetch_callback: Optional[Callable[[int], int]] = None,
    ):
        """Initialize fetch queue service.

        Args:
            delay_seconds: Delay between processing different newsletters.
            fetch_callback: Async callback to fetch newsletter emails.
                           Takes newsletter_id, returns count of emails fetched.
        """
        self.delay_seconds = delay_seconds
        self.fetch_callback = fetch_callback
        self._queue: list[FetchTask] = []
        self._is_running = False
        self._current_task: Optional[FetchTask] = None
        self._completed_count = 0
        self._failed_count = 0
        self._lock = asyncio.Lock()
        self._process_task: Optional[asyncio.Task] = None

    async def queue_fetch(
        self,
        newsletter_id: int,
        priority: FetchPriority = FetchPriority.NORMAL,
    ) -> bool:
        """Add a newsletter to the fetch queue.

        Args:
            newsletter_id: Newsletter to fetch.
            priority: Priority level.

        Returns:
            True if added, False if already in queue.
        """
        async with self._lock:
            # Check if already in queue
            if any(t.newsletter_id == newsletter_id for t in self._queue):
                logger.debug(f"Newsletter {newsletter_id} already in queue")
                return False

            # Check if currently being processed
            if self._current_task and self._current_task.newsletter_id == newsletter_id:
                logger.debug(f"Newsletter {newsletter_id} is currently being fetched")
                return False

            task = FetchTask(
                newsletter_id=newsletter_id,
                priority=priority,
            )
            self._queue.append(task)
            self._queue.sort()  # Sort by priority

            logger.info(
                f"Queued fetch for newsletter {newsletter_id} "
                f"with priority {priority.name}"
            )

            # Start processing if not already running
            if not self._is_running:
                self._start_processing()

            return True

    async def queue_all_newsletters(
        self,
        newsletter_ids: list[int],
        priority: FetchPriority = FetchPriority.NORMAL,
    ) -> int:
        """Queue multiple newsletters for fetching.

        Args:
            newsletter_ids: List of newsletter IDs.
            priority: Priority level for all.

        Returns:
            Number of newsletters queued.
        """
        queued = 0
        for newsletter_id in newsletter_ids:
            if await self.queue_fetch(newsletter_id, priority):
                queued += 1
        return queued

    def _start_processing(self) -> None:
        """Start the queue processing task."""
        if self._process_task is None or self._process_task.done():
            self._process_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self) -> None:
        """Process tasks in the queue."""
        self._is_running = True
        logger.info("Started fetch queue processing")

        try:
            while True:
                task = await self._get_next_task()
                if not task:
                    break

                self._current_task = task
                task.status = FetchStatus.IN_PROGRESS

                try:
                    if self.fetch_callback:
                        emails_fetched = await self.fetch_callback(task.newsletter_id)
                        task.emails_fetched = emails_fetched
                    task.status = FetchStatus.COMPLETED
                    self._completed_count += 1
                    logger.info(
                        f"Completed fetch for newsletter {task.newsletter_id}: "
                        f"{task.emails_fetched} emails"
                    )
                except Exception as e:
                    task.status = FetchStatus.FAILED
                    task.error = str(e)
                    self._failed_count += 1
                    logger.error(
                        f"Failed fetch for newsletter {task.newsletter_id}: {e}"
                    )

                self._current_task = None

                # Delay before next task
                if self._queue:
                    await asyncio.sleep(self.delay_seconds)

        finally:
            self._is_running = False
            logger.info("Stopped fetch queue processing")

    async def _get_next_task(self) -> Optional[FetchTask]:
        """Get the next task from the queue.

        Returns:
            Next task or None if queue is empty.
        """
        async with self._lock:
            if self._queue:
                return self._queue.pop(0)
            return None

    def get_queue_status(self) -> QueueStatus:
        """Get current queue status.

        Returns:
            Queue status information.
        """
        return QueueStatus(
            is_running=self._is_running,
            queue_length=len(self._queue),
            current_task=(
                self._current_task.newsletter_id if self._current_task else None
            ),
            completed_count=self._completed_count,
            failed_count=self._failed_count,
        )

    async def clear_queue(self) -> None:
        """Clear all pending tasks from the queue."""
        async with self._lock:
            self._queue.clear()
            logger.info("Cleared fetch queue")

    async def stop(self) -> None:
        """Stop queue processing."""
        await self.clear_queue()
        if self._process_task and not self._process_task.done():
            self._process_task.cancel()
            try:
                await self._process_task
            except asyncio.CancelledError:
                pass
        self._is_running = False

    def reset_stats(self) -> None:
        """Reset completion statistics."""
        self._completed_count = 0
        self._failed_count = 0
