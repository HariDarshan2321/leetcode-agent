"""
Daily Scheduler for the Leetcode Email Agent.
This module handles scheduling and running daily email tasks.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

try:
    from ..config import Config
except ImportError:
    from src.config import Config

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DailyScheduler:
    """
    Scheduler for running daily email tasks.
    Uses APScheduler to manage background job execution.
    """

    def __init__(self, job_function: Callable[[], Dict[str, Any]]):
        """
        Initialize the scheduler.

        Args:
            job_function: Function to call for daily email processing
        """
        self.job_function = job_function
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.last_run_result = None
        self.job_id = "daily_leetcode_emails"

        # Add event listeners
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)

        logger.info("DailyScheduler initialized")

    def start(self) -> bool:
        """
        Start the scheduler.

        Returns:
            True if started successfully, False otherwise
        """
        try:
            if self.is_running:
                logger.warning("Scheduler is already running")
                return True

            # Add the daily job
            self.scheduler.add_job(
                func=self._run_daily_job,
                trigger=CronTrigger(
                    hour=Config.SCHEDULER_HOUR,
                    minute=Config.SCHEDULER_MINUTE,
                    timezone=Config.SCHEDULER_TIMEZONE
                ),
                id=self.job_id,
                name="Daily LeetCode Email Job",
                replace_existing=True,
                max_instances=1  # Prevent overlapping executions
            )

            # Start the scheduler
            self.scheduler.start()
            self.is_running = True

            logger.info(f"Scheduler started - daily emails will be sent at "
                       f"{Config.SCHEDULER_HOUR:02d}:{Config.SCHEDULER_MINUTE:02d} "
                       f"{Config.SCHEDULER_TIMEZONE}")

            return True

        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            return False

    def stop(self) -> bool:
        """
        Stop the scheduler.

        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            if not self.is_running:
                logger.warning("Scheduler is not running")
                return True

            self.scheduler.shutdown(wait=True)
            self.is_running = False

            logger.info("Scheduler stopped")
            return True

        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
            return False

    def run_now(self) -> Dict[str, Any]:
        """
        Run the daily job immediately (for testing purposes).

        Returns:
            Dictionary with job execution results
        """
        logger.info("Running daily job manually")
        return self._run_daily_job()

    def _run_daily_job(self) -> Dict[str, Any]:
        """
        Execute the daily job function.

        Returns:
            Dictionary with job execution results
        """
        try:
            logger.info("Starting daily job execution")
            start_time = datetime.now()

            # Call the job function
            result = self.job_function()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Enhance result with execution metadata
            result.update({
                "job_execution_time": duration,
                "job_start_time": start_time.isoformat(),
                "job_end_time": end_time.isoformat(),
                "job_status": "completed"
            })

            self.last_run_result = result

            logger.info(f"Daily job completed successfully in {duration:.2f} seconds")
            logger.info(f"Emails sent: {result.get('emails_sent', 0)}, "
                       f"Failed: {result.get('emails_failed', 0)}")

            return result

        except Exception as e:
            error_result = {
                "job_status": "failed",
                "error": str(e),
                "job_execution_time": 0,
                "job_start_time": datetime.now().isoformat(),
                "job_end_time": datetime.now().isoformat(),
                "emails_sent": 0,
                "emails_failed": 0,
                "total_users": 0,
                "errors": [str(e)]
            }

            self.last_run_result = error_result
            logger.error(f"Daily job failed: {e}")

            return error_result

    def _job_executed(self, event):
        """Handle job execution event."""
        logger.info(f"Job {event.job_id} executed successfully")

    def _job_error(self, event):
        """Handle job error event."""
        logger.error(f"Job {event.job_id} failed: {event.exception}")

    def get_next_run_time(self) -> Optional[datetime]:
        """
        Get the next scheduled run time.

        Returns:
            Next run time as datetime object, or None if not scheduled
        """
        try:
            if not self.is_running:
                return None

            job = self.scheduler.get_job(self.job_id)
            if job:
                return job.next_run_time
            return None

        except Exception as e:
            logger.error(f"Error getting next run time: {e}")
            return None

    def get_last_run_result(self) -> Optional[Dict[str, Any]]:
        """
        Get the result of the last job execution.

        Returns:
            Dictionary with last run results, or None if no runs yet
        """
        return self.last_run_result

    def get_status(self) -> Dict[str, Any]:
        """
        Get scheduler status information.

        Returns:
            Dictionary with scheduler status
        """
        next_run = self.get_next_run_time()

        status = {
            "is_running": self.is_running,
            "next_run_time": next_run.isoformat() if next_run else None,
            "scheduled_time": f"{Config.SCHEDULER_HOUR:02d}:{Config.SCHEDULER_MINUTE:02d}",
            "timezone": Config.SCHEDULER_TIMEZONE,
            "last_run_result": self.last_run_result,
            "job_id": self.job_id
        }

        return status

    def reschedule(self, hour: int = None, minute: int = None, timezone: str = None) -> bool:
        """
        Reschedule the daily job with new time settings.

        Args:
            hour: New hour (0-23)
            minute: New minute (0-59)
            timezone: New timezone string

        Returns:
            True if rescheduled successfully, False otherwise
        """
        try:
            # Use current config values if not provided
            new_hour = hour if hour is not None else Config.SCHEDULER_HOUR
            new_minute = minute if minute is not None else Config.SCHEDULER_MINUTE
            new_timezone = timezone if timezone is not None else Config.SCHEDULER_TIMEZONE

            # Validate inputs
            if not (0 <= new_hour <= 23):
                logger.error(f"Invalid hour: {new_hour}. Must be 0-23")
                return False

            if not (0 <= new_minute <= 59):
                logger.error(f"Invalid minute: {new_minute}. Must be 0-59")
                return False

            if not self.is_running:
                logger.warning("Scheduler is not running, cannot reschedule")
                return False

            # Remove existing job
            self.scheduler.remove_job(self.job_id)

            # Add job with new schedule
            self.scheduler.add_job(
                func=self._run_daily_job,
                trigger=CronTrigger(
                    hour=new_hour,
                    minute=new_minute,
                    timezone=new_timezone
                ),
                id=self.job_id,
                name="Daily LeetCode Email Job",
                replace_existing=True,
                max_instances=1
            )

            logger.info(f"Rescheduled daily job to {new_hour:02d}:{new_minute:02d} {new_timezone}")
            return True

        except Exception as e:
            logger.error(f"Failed to reschedule job: {e}")
            return False

    def is_job_running(self) -> bool:
        """
        Check if the daily job is currently executing.

        Returns:
            True if job is running, False otherwise
        """
        try:
            if not self.is_running:
                return False

            job = self.scheduler.get_job(self.job_id)
            if job:
                # Check if job is currently running
                running_jobs = self.scheduler.get_jobs()
                for running_job in running_jobs:
                    if running_job.id == self.job_id:
                        # This is a simple check - APScheduler doesn't provide
                        # a direct way to check if a specific job is running
                        return True
            return False

        except Exception as e:
            logger.error(f"Error checking if job is running: {e}")
            return False

    def get_job_history(self, limit: int = 10) -> list[Dict[str, Any]]:
        """
        Get history of job executions.
        Note: This is a simple implementation that only stores the last result.
        For production, you might want to implement persistent job history storage.

        Args:
            limit: Maximum number of history entries to return

        Returns:
            List of job execution history
        """
        history = []

        if self.last_run_result:
            history.append(self.last_run_result)

        return history[:limit]

    def wait_for_completion(self, timeout: int = 300) -> bool:
        """
        Wait for the current job to complete (if running).

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if job completed or wasn't running, False if timeout
        """
        start_time = time.time()

        while self.is_job_running() and (time.time() - start_time) < timeout:
            time.sleep(1)

        return not self.is_job_running()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
