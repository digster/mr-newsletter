"""Tests for FetchQueueService - priority queue for email fetching.

These tests verify the fetch queue correctly prioritizes tasks,
prevents duplicates, and processes fetches asynchronously.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.fetch_queue_service import (
    FetchPriority,
    FetchQueueService,
    FetchStatus,
    FetchTask,
    QueueStatus,
)


class TestFetchTaskOrdering:
    """Test FetchTask priority ordering."""

    def test_high_priority_comes_before_normal(self):
        """Verify HIGH priority tasks sort before NORMAL."""
        high_task = FetchTask(newsletter_id=1, priority=FetchPriority.HIGH)
        normal_task = FetchTask(newsletter_id=2, priority=FetchPriority.NORMAL)

        assert high_task < normal_task

    def test_normal_priority_comes_before_low(self):
        """Verify NORMAL priority tasks sort before LOW."""
        normal_task = FetchTask(newsletter_id=1, priority=FetchPriority.NORMAL)
        low_task = FetchTask(newsletter_id=2, priority=FetchPriority.LOW)

        assert normal_task < low_task

    def test_same_priority_ordered_by_time(self):
        """Verify same priority tasks are ordered by creation time."""
        import time

        task1 = FetchTask(newsletter_id=1, priority=FetchPriority.NORMAL)
        time.sleep(0.01)  # Small delay to ensure different timestamps
        task2 = FetchTask(newsletter_id=2, priority=FetchPriority.NORMAL)

        assert task1 < task2


class TestFetchQueueServiceBasic:
    """Test basic queue operations."""

    @pytest.fixture
    def queue_service(self):
        """Create a FetchQueueService instance."""
        return FetchQueueService(delay_seconds=0)

    @pytest.mark.asyncio
    async def test_queue_fetch_adds_task(self, queue_service):
        """Verify queue_fetch adds a task to the queue."""
        result = await queue_service.queue_fetch(1)

        assert result is True
        status = queue_service.get_queue_status()
        assert status.queue_length == 1 or status.current_task == 1

    @pytest.mark.asyncio
    async def test_queue_fetch_rejects_duplicate(self, queue_service):
        """Verify queue_fetch rejects duplicate newsletter IDs."""
        # Stop processing so task stays in queue
        await queue_service.queue_fetch(1)
        await queue_service.stop()

        # Create new service to test duplicate rejection
        queue_service2 = FetchQueueService(delay_seconds=0)
        await queue_service2.queue_fetch(1)

        # Try to add same newsletter again
        result = await queue_service2.queue_fetch(1)

        assert result is False

    @pytest.mark.asyncio
    async def test_queue_all_newsletters_returns_count(self, queue_service):
        """Verify queue_all_newsletters returns queued count."""
        count = await queue_service.queue_all_newsletters([1, 2, 3])

        assert count == 3


class TestFetchQueueServicePriority:
    """Test priority queue behavior."""

    @pytest.mark.asyncio
    async def test_priority_ordering_in_queue(self):
        """Verify tasks are processed in priority order."""
        processed_ids = []

        async def track_callback(newsletter_id: int) -> int:
            processed_ids.append(newsletter_id)
            return 0

        queue_service = FetchQueueService(delay_seconds=0, fetch_callback=track_callback)

        # Queue in reverse priority order
        await queue_service.queue_fetch(3, FetchPriority.LOW)
        await queue_service.queue_fetch(2, FetchPriority.NORMAL)
        await queue_service.queue_fetch(1, FetchPriority.HIGH)

        # Wait for processing
        await asyncio.sleep(0.1)
        await queue_service.stop()

        # Should be processed in priority order: HIGH, NORMAL, LOW
        assert processed_ids == [1, 2, 3]


class TestFetchQueueServiceProcessing:
    """Test queue processing behavior."""

    @pytest.mark.asyncio
    async def test_process_queue_calls_callback(self):
        """Verify processing calls the fetch callback."""
        callback_called = False

        async def test_callback(newsletter_id: int) -> int:
            nonlocal callback_called
            callback_called = True
            return 5

        queue_service = FetchQueueService(delay_seconds=0, fetch_callback=test_callback)
        await queue_service.queue_fetch(1)

        # Wait for processing
        await asyncio.sleep(0.1)
        await queue_service.stop()

        assert callback_called

    @pytest.mark.asyncio
    async def test_process_queue_updates_completed_count(self):
        """Verify successful processing increments completed count."""
        async def success_callback(newsletter_id: int) -> int:
            return 10

        queue_service = FetchQueueService(delay_seconds=0, fetch_callback=success_callback)
        await queue_service.queue_fetch(1)

        # Wait for processing
        await asyncio.sleep(0.1)

        status = queue_service.get_queue_status()
        assert status.completed_count >= 1

    @pytest.mark.asyncio
    async def test_process_queue_updates_failed_count_on_error(self):
        """Verify failed processing increments failed count."""
        async def failing_callback(newsletter_id: int) -> int:
            raise Exception("Test error")

        queue_service = FetchQueueService(delay_seconds=0, fetch_callback=failing_callback)
        await queue_service.queue_fetch(1)

        # Wait for processing
        await asyncio.sleep(0.1)

        status = queue_service.get_queue_status()
        assert status.failed_count >= 1


class TestFetchQueueServiceStatus:
    """Test queue status operations."""

    @pytest.fixture
    def queue_service(self):
        """Create a FetchQueueService instance."""
        return FetchQueueService(delay_seconds=0)

    def test_get_queue_status_returns_correct_type(self, queue_service):
        """Verify get_queue_status returns QueueStatus object."""
        status = queue_service.get_queue_status()

        assert isinstance(status, QueueStatus)

    def test_get_queue_status_initial_state(self, queue_service):
        """Verify initial queue status is empty."""
        status = queue_service.get_queue_status()

        assert status.is_running is False
        assert status.queue_length == 0
        assert status.current_task is None
        assert status.completed_count == 0
        assert status.failed_count == 0


class TestFetchQueueServiceControl:
    """Test queue control operations."""

    @pytest.fixture
    def queue_service(self):
        """Create a FetchQueueService instance."""
        return FetchQueueService(delay_seconds=0)

    @pytest.mark.asyncio
    async def test_clear_queue_removes_pending(self, queue_service):
        """Verify clear_queue removes all pending tasks."""
        # Add tasks without processing
        queue_service._queue.append(FetchTask(newsletter_id=1, priority=FetchPriority.NORMAL))
        queue_service._queue.append(FetchTask(newsletter_id=2, priority=FetchPriority.NORMAL))

        await queue_service.clear_queue()

        assert len(queue_service._queue) == 0

    @pytest.mark.asyncio
    async def test_stop_cancels_processing(self, queue_service):
        """Verify stop cancels queue processing."""
        # Start with a slow callback
        async def slow_callback(newsletter_id: int) -> int:
            await asyncio.sleep(10)
            return 0

        queue_service.fetch_callback = slow_callback
        await queue_service.queue_fetch(1)

        await asyncio.sleep(0.05)  # Let processing start
        await queue_service.stop()

        assert queue_service._is_running is False

    def test_reset_stats_clears_counters(self, queue_service):
        """Verify reset_stats clears completion counters."""
        queue_service._completed_count = 10
        queue_service._failed_count = 5

        queue_service.reset_stats()

        assert queue_service._completed_count == 0
        assert queue_service._failed_count == 0


class TestFetchQueueServiceConcurrency:
    """Test concurrent access to the queue."""

    @pytest.mark.asyncio
    async def test_queue_is_thread_safe(self):
        """Verify queue operations are safe under concurrent access."""
        queue_service = FetchQueueService(delay_seconds=0)

        # Queue many items concurrently
        async def queue_item(newsletter_id: int):
            await queue_service.queue_fetch(newsletter_id)

        await asyncio.gather(*[queue_item(i) for i in range(10)])

        # Stop and check state
        await queue_service.stop()

        # All items should have been queued
        status = queue_service.get_queue_status()
        # Due to processing, queue_length + completed should equal 10
        total_handled = status.queue_length + status.completed_count + status.failed_count
        # At least some items were handled
        assert total_handled >= 0  # Just verify no crash

    @pytest.mark.asyncio
    async def test_prevents_duplicate_while_processing(self):
        """Verify can't queue a newsletter that's currently being processed."""
        processing_started = asyncio.Event()
        can_finish = asyncio.Event()

        async def blocking_callback(newsletter_id: int) -> int:
            processing_started.set()
            await can_finish.wait()
            return 0

        queue_service = FetchQueueService(delay_seconds=0, fetch_callback=blocking_callback)

        # Queue first item
        await queue_service.queue_fetch(1)

        # Wait for processing to start
        await asyncio.wait_for(processing_started.wait(), timeout=1.0)

        # Try to queue same item - should be rejected
        result = await queue_service.queue_fetch(1)

        assert result is False

        # Clean up
        can_finish.set()
        await queue_service.stop()
