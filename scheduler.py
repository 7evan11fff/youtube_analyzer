"""
Background scheduler for automatic niche scraping.
Runs in a daemon thread; the GUI can start/stop it and manage schedules.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from database import get_db

logger = logging.getLogger(__name__)


class ScrapeScheduler:
    """
    Manages periodic background scrapes for tracked niches.
    Each niche can be independently enabled/disabled with its own interval.
    """

    def __init__(self, run_callback: Optional[Callable] = None):
        """
        Args:
            run_callback: function(niche, video_count) called when a scrape
                          is due. The GUI wires this to the analysis pipeline.
        """
        self._run_callback = run_callback
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._poll_interval = 30  # seconds between schedule checks

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        """Start the scheduler loop in a daemon thread."""
        if self.running:
            logger.info("Scheduler already running")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="scrape-scheduler")
        self._thread.start()
        logger.info("Scheduler started")

    def stop(self):
        """Signal the scheduler to stop."""
        self._stop_event.set()
        logger.info("Scheduler stop requested")

    def _loop(self):
        logger.info("Scheduler loop entered")
        while not self._stop_event.is_set():
            try:
                self._tick()
            except Exception as e:
                logger.error(f"Scheduler tick error: {e}")
            self._stop_event.wait(self._poll_interval)
        logger.info("Scheduler loop exited")

    def _tick(self):
        """Check all schedules and run any that are due."""
        db = get_db()
        schedules = db.get_all_schedules()
        now = datetime.utcnow()

        for sched in schedules:
            if not sched.get("enabled"):
                continue
            next_run_str = sched.get("next_run")
            if not next_run_str:
                continue
            try:
                next_run = datetime.fromisoformat(next_run_str)
            except (ValueError, TypeError):
                continue

            if now >= next_run:
                niche = sched["niche"]
                video_count = sched.get("video_count", 50)
                logger.info(f"Auto-scrape triggered for '{niche}' ({video_count} videos)")
                try:
                    if self._run_callback:
                        self._run_callback(niche, video_count)
                    db.update_schedule_last_run(niche)
                except Exception as e:
                    logger.error(f"Auto-scrape failed for '{niche}': {e}")

    # ── Convenience wrappers for the GUI ──

    @staticmethod
    def add_schedule(niche: str, interval_hours: int = 24,
                     video_count: int = 50, enabled: bool = True) -> bool:
        db = get_db()
        return db.save_schedule(niche, enabled, interval_hours, video_count)

    @staticmethod
    def remove_schedule(niche: str) -> bool:
        try:
            db = get_db()
            conn = db._get_connection()
            conn.execute("DELETE FROM scrape_schedules WHERE niche = ?", (niche,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing schedule: {e}")
            return False

    @staticmethod
    def toggle_schedule(niche: str, enabled: bool) -> bool:
        try:
            db = get_db()
            sched = db.get_schedule(niche)
            if not sched:
                return False
            now = datetime.utcnow()
            next_run = (now + timedelta(hours=sched["interval_hours"])).isoformat() if enabled else None
            conn = db._get_connection()
            conn.execute("""
                UPDATE scrape_schedules SET enabled = ?, next_run = ? WHERE niche = ?
            """, (int(enabled), next_run, niche))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error toggling schedule: {e}")
            return False

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return get_db().get_all_schedules()
