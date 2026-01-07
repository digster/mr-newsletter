"""Scheduler service for background task management."""

import logging
from typing import Callable, Optional

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, JobExecutionEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing background scheduled tasks.

    Handles periodic email fetching for newsletters.
    """

    def __init__(self):
        """Initialize scheduler service."""
        self.scheduler: Optional[AsyncIOScheduler] = None
        self._fetch_callback: Optional[Callable] = None
        self._is_initialized = False

    def initialize(self, fetch_callback: Optional[Callable] = None) -> None:
        """Initialize the scheduler.

        Args:
            fetch_callback: Async callback for fetching newsletter emails.
        """
        if self._is_initialized:
            return

        self._fetch_callback = fetch_callback

        job_defaults = {
            "coalesce": True,  # Combine missed executions
            "max_instances": 1,  # Only one instance per job
            "misfire_grace_time": 60 * 5,  # 5 minutes grace period
        }

        self.scheduler = AsyncIOScheduler(job_defaults=job_defaults)

        # Add event listeners
        self.scheduler.add_listener(self._on_job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._on_job_error, EVENT_JOB_ERROR)

        self._is_initialized = True
        logger.info("Scheduler initialized")

    def start(self) -> None:
        """Start the scheduler."""
        if not self._is_initialized:
            raise RuntimeError("Scheduler not initialized")

        if self.scheduler and not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self) -> None:
        """Gracefully shutdown the scheduler."""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler shutdown")

    def schedule_newsletter_fetch(
        self,
        newsletter_id: int,
        interval_minutes: int,
    ) -> None:
        """Schedule periodic fetching for a newsletter.

        Args:
            newsletter_id: Newsletter ID.
            interval_minutes: Fetch interval in minutes.
        """
        if not self.scheduler:
            logger.warning("Scheduler not initialized")
            return

        job_id = f"newsletter_fetch_{newsletter_id}"

        # Remove existing job if any
        existing = self.scheduler.get_job(job_id)
        if existing:
            self.scheduler.remove_job(job_id)

        # Add new job
        self.scheduler.add_job(
            self._execute_fetch,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=job_id,
            kwargs={"newsletter_id": newsletter_id},
            replace_existing=True,
        )

        logger.info(
            f"Scheduled fetch for newsletter {newsletter_id} "
            f"every {interval_minutes} minutes"
        )

    def unschedule_newsletter_fetch(self, newsletter_id: int) -> None:
        """Remove scheduled fetch for a newsletter.

        Args:
            newsletter_id: Newsletter ID.
        """
        if not self.scheduler:
            return

        job_id = f"newsletter_fetch_{newsletter_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Unscheduled fetch for newsletter {newsletter_id}")
        except Exception:
            pass

    def update_newsletter_schedule(
        self,
        newsletter_id: int,
        interval_minutes: int,
        enabled: bool,
    ) -> None:
        """Update the schedule for a newsletter.

        Args:
            newsletter_id: Newsletter ID.
            interval_minutes: New interval.
            enabled: Whether auto-fetch is enabled.
        """
        if enabled:
            self.schedule_newsletter_fetch(newsletter_id, interval_minutes)
        else:
            self.unschedule_newsletter_fetch(newsletter_id)

    async def _execute_fetch(self, newsletter_id: int) -> None:
        """Execute the fetch callback for a newsletter.

        Args:
            newsletter_id: Newsletter ID.
        """
        if self._fetch_callback:
            try:
                await self._fetch_callback(newsletter_id)
            except Exception as e:
                logger.error(f"Fetch callback failed for newsletter {newsletter_id}: {e}")

    def _on_job_executed(self, event: JobExecutionEvent) -> None:
        """Handle successful job execution.

        Args:
            event: Job execution event.
        """
        logger.debug(f"Job {event.job_id} executed successfully")

    def _on_job_error(self, event: JobExecutionEvent) -> None:
        """Handle job execution errors.

        Args:
            event: Job execution event.
        """
        logger.error(f"Job {event.job_id} failed: {event.exception}")

    def get_scheduled_jobs(self) -> list[dict]:
        """Get list of scheduled jobs.

        Returns:
            List of job information dicts.
        """
        if not self.scheduler:
            return []

        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append(
                {
                    "id": job.id,
                    "next_run_time": job.next_run_time,
                    "trigger": str(job.trigger),
                }
            )
        return jobs

    def is_running(self) -> bool:
        """Check if scheduler is running.

        Returns:
            True if running.
        """
        return self.scheduler is not None and self.scheduler.running

    def pause(self) -> None:
        """Pause the scheduler."""
        if self.scheduler:
            self.scheduler.pause()
            logger.info("Scheduler paused")

    def resume(self) -> None:
        """Resume the scheduler."""
        if self.scheduler:
            self.scheduler.resume()
            logger.info("Scheduler resumed")

    def run_now(self, newsletter_id: int) -> None:
        """Trigger immediate fetch for a newsletter.

        Args:
            newsletter_id: Newsletter ID.
        """
        if not self.scheduler:
            return

        job_id = f"newsletter_fetch_{newsletter_id}"
        job = self.scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=None)  # Run immediately
            logger.info(f"Triggered immediate fetch for newsletter {newsletter_id}")
