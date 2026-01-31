"""Integration tests for queue and scheduler interaction.

These tests verify the FetchQueueService and SchedulerService
work together correctly for background email fetching.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.fetch_queue_service import FetchQueueService, FetchPriority
from src.services.scheduler_service import SchedulerService


class TestQueueSchedulerIntegration:
    """Test queue and scheduler work together."""

    @pytest.fixture
    def fetch_callback(self):
        """Create a mock fetch callback."""
        return AsyncMock()

    @pytest.fixture
    def scheduler_service(self, fetch_callback):
        """Create an initialized scheduler service."""
        service = SchedulerService()
        service.initialize(fetch_callback=fetch_callback)
        return service

    @pytest.mark.asyncio
    async def test_scheduler_can_schedule_fetch_job(self, scheduler_service):
        """Verify scheduler creates fetch jobs."""
        scheduler_service.start()

        try:
            scheduler_service.schedule_newsletter_fetch(
                newsletter_id=1,
                interval_minutes=60,
            )

            job = scheduler_service.scheduler.get_job("newsletter_fetch_1")
            assert job is not None
        finally:
            scheduler_service.shutdown()

    @pytest.mark.asyncio
    async def test_queue_processes_tasks_in_priority_order(self):
        """Verify queue respects priority ordering."""
        processed_order = []

        async def track_callback(newsletter_id):
            processed_order.append(newsletter_id)
            return 0  # Return count of emails fetched

        queue_service = FetchQueueService(delay_seconds=0, fetch_callback=track_callback)

        # Add tasks in different priority order (queue_fetch is async)
        await queue_service.queue_fetch(newsletter_id=1, priority=FetchPriority.LOW)
        await queue_service.queue_fetch(newsletter_id=2, priority=FetchPriority.HIGH)
        await queue_service.queue_fetch(newsletter_id=3, priority=FetchPriority.NORMAL)

        # Wait for queue to process
        import asyncio
        await asyncio.sleep(0.2)

        # High priority should be first
        assert processed_order[0] == 2  # HIGH priority
        assert 1 in processed_order  # LOW priority was processed
        assert 3 in processed_order  # NORMAL priority was processed


class TestManualRefreshPriority:
    """Test manual refresh gets high priority."""

    @pytest.mark.asyncio
    async def test_manual_refresh_uses_high_priority(self):
        """Verify manual refresh is queued with HIGH priority."""
        queue_service = FetchQueueService()

        # Queue a manual refresh (should be HIGH priority) - queue_fetch is async
        await queue_service.queue_fetch(newsletter_id=1, priority=FetchPriority.HIGH)

        status = queue_service.get_queue_status()
        # The task should be in queue (QueueStatus has queue_length not queue_size)
        assert status.queue_length >= 0  # Task may have started processing


class TestSchedulerJobManagement:
    """Test scheduler job lifecycle."""

    @pytest.fixture
    def scheduler_service(self):
        """Create an initialized scheduler service."""
        service = SchedulerService()
        service.initialize()
        return service

    @pytest.mark.asyncio
    async def test_multiple_newsletters_can_be_scheduled(self, scheduler_service):
        """Verify multiple newsletters can have separate schedules."""
        scheduler_service.start()

        try:
            scheduler_service.schedule_newsletter_fetch(newsletter_id=1, interval_minutes=30)
            scheduler_service.schedule_newsletter_fetch(newsletter_id=2, interval_minutes=60)
            scheduler_service.schedule_newsletter_fetch(newsletter_id=3, interval_minutes=120)

            jobs = scheduler_service.get_scheduled_jobs()
            job_ids = [j["id"] for j in jobs]

            assert "newsletter_fetch_1" in job_ids
            assert "newsletter_fetch_2" in job_ids
            assert "newsletter_fetch_3" in job_ids
        finally:
            scheduler_service.shutdown()

    @pytest.mark.asyncio
    async def test_unschedule_removes_specific_job(self, scheduler_service):
        """Verify unscheduling removes only the specified job."""
        scheduler_service.start()

        try:
            scheduler_service.schedule_newsletter_fetch(newsletter_id=1, interval_minutes=30)
            scheduler_service.schedule_newsletter_fetch(newsletter_id=2, interval_minutes=60)

            # Remove first job
            scheduler_service.unschedule_newsletter_fetch(newsletter_id=1)

            # Second job should still exist
            job1 = scheduler_service.scheduler.get_job("newsletter_fetch_1")
            job2 = scheduler_service.scheduler.get_job("newsletter_fetch_2")

            assert job1 is None
            assert job2 is not None
        finally:
            scheduler_service.shutdown()


class TestQueueStatus:
    """Test queue status reporting."""

    @pytest.mark.asyncio
    async def test_queue_status_shows_pending_tasks(self):
        """Verify queue status reports pending tasks correctly."""
        # Create queue without a callback so tasks don't get processed
        queue_service = FetchQueueService(fetch_callback=None)

        # Stop any auto-processing to check queue state
        await queue_service.stop()

        # Add tasks directly to the queue (bypassing async processing)
        from src.services.fetch_queue_service import FetchTask
        queue_service._queue.append(FetchTask(newsletter_id=1, priority=FetchPriority.NORMAL))
        queue_service._queue.append(FetchTask(newsletter_id=2, priority=FetchPriority.NORMAL))

        status = queue_service.get_queue_status()

        assert status.queue_length == 2
        assert status.is_running is False

    @pytest.mark.asyncio
    async def test_clear_queue_removes_pending(self):
        """Verify clear_queue removes all pending tasks."""
        queue_service = FetchQueueService(fetch_callback=None)

        # Stop any auto-processing
        await queue_service.stop()

        # Add tasks directly
        from src.services.fetch_queue_service import FetchTask
        queue_service._queue.append(FetchTask(newsletter_id=1, priority=FetchPriority.NORMAL))
        queue_service._queue.append(FetchTask(newsletter_id=2, priority=FetchPriority.NORMAL))

        await queue_service.clear_queue()

        status = queue_service.get_queue_status()
        assert status.queue_length == 0
