"""
Database and caching layer for YouTube Analyzer.
Provides SQLite storage for video data, analysis results, and cached metrics.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import threading

logger = logging.getLogger(__name__)


class YouTubeAnalyzerDB:
    """SQLite database management for YouTube Analyzer."""

    def __init__(self, db_path: str = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. Defaults to ./data/youtube_analyzer.db
        """
        if db_path is None:
            db_path = "data/youtube_analyzer.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.local = threading.local()
        
        self._initialize_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self.local, 'connection') or self.local.connection is None:
            self.local.connection = sqlite3.connect(str(self.db_path))
            self.local.connection.row_factory = sqlite3.Row
        return self.local.connection
    
    def _initialize_db(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id TEXT PRIMARY KEY,
                niche TEXT NOT NULL,
                title TEXT NOT NULL,
                channel_id TEXT,
                channel_name TEXT,
                description TEXT,
                view_count INTEGER,
                like_count INTEGER,
                comment_count INTEGER,
                upload_date TEXT,
                duration_seconds INTEGER,
                thumbnail_url TEXT,
                video_url TEXT,
                transcript TEXT,
                metadata_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(id, niche)
            )
        """)
        
        # Niche analysis cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS niche_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche TEXT UNIQUE NOT NULL,
                video_count INTEGER,
                analysis_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Channel data cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id TEXT PRIMARY KEY,
                niche TEXT,
                name TEXT,
                subscriber_count INTEGER,
                video_count INTEGER,
                upload_frequency_per_week REAL,
                verified BOOLEAN,
                metadata_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Title/Thumbnail analysis cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE,
                niche TEXT,
                title_features_json TEXT,
                thumbnail_features_json TEXT,
                engagement_metrics_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Timestamped snapshots for trend tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS niche_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche TEXT NOT NULL,
                scraped_at TEXT NOT NULL,
                video_count INTEGER,
                unique_channels INTEGER,
                avg_views REAL,
                median_views REAL,
                avg_engagement REAL,
                avg_like_ratio REAL,
                top_topics_json TEXT,
                analysis_json TEXT,
                blueprint_json TEXT
            )
        """)

        # Auto-scrape schedule config
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scrape_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche TEXT UNIQUE NOT NULL,
                enabled INTEGER DEFAULT 0,
                interval_hours INTEGER DEFAULT 24,
                video_count INTEGER DEFAULT 50,
                last_run TEXT,
                next_run TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def add_video(self, video_data: Dict[str, Any], niche: str) -> bool:
        """
        Add or update a video record.
        
        Args:
            video_data: Dictionary with video information
            niche: Niche category
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO videos (
                    id, niche, title, channel_id, channel_name, description,
                    view_count, like_count, comment_count, upload_date,
                    duration_seconds, thumbnail_url, video_url, transcript,
                    metadata_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video_data.get('id'),
                niche,
                video_data.get('title'),
                video_data.get('channel_id'),
                video_data.get('channel_name'),
                video_data.get('description'),
                video_data.get('view_count'),
                video_data.get('like_count'),
                video_data.get('comment_count'),
                video_data.get('upload_date'),
                video_data.get('duration_seconds'),
                video_data.get('thumbnail_url'),
                video_data.get('video_url'),
                video_data.get('transcript'),
                json.dumps(video_data),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding video to database: {e}")
            return False
    
    def add_videos_batch(self, videos: List[Dict[str, Any]], niche: str) -> int:
        """
        Add multiple videos efficiently.
        
        Args:
            videos: List of video data dictionaries
            niche: Niche category
            
        Returns:
            Number of videos added
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            count = 0
            for video_data in videos:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO videos (
                            id, niche, title, channel_id, channel_name, description,
                            view_count, like_count, comment_count, upload_date,
                            duration_seconds, thumbnail_url, video_url, transcript,
                            metadata_json, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        video_data.get('id'),
                        niche,
                        video_data.get('title'),
                        video_data.get('channel_id'),
                        video_data.get('channel_name'),
                        video_data.get('description'),
                        video_data.get('view_count'),
                        video_data.get('like_count'),
                        video_data.get('comment_count'),
                        video_data.get('upload_date'),
                        video_data.get('duration_seconds'),
                        video_data.get('thumbnail_url'),
                        video_data.get('video_url'),
                        video_data.get('transcript'),
                        json.dumps(video_data),
                        datetime.utcnow().isoformat()
                    ))
                    count += 1
                except Exception as e:
                    logger.warning(f"Error adding individual video: {e}")
                    continue
            
            conn.commit()
            logger.info(f"Added {count} videos to database")
            return count
        except Exception as e:
            logger.error(f"Error in batch add: {e}")
            return 0
    
    def get_videos_by_niche(self, niche: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve all videos for a niche.
        
        Args:
            niche: Niche category
            limit: Maximum number of videos to retrieve
            
        Returns:
            List of video data dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM videos WHERE niche = ? ORDER BY upload_date DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (niche,))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving videos: {e}")
            return []
    
    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get a single video by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
            row = cursor.fetchone()
            
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error retrieving video: {e}")
            return None
    
    def cache_niche_analysis(self, niche: str, analysis_data: Dict[str, Any], video_count: int) -> bool:
        """
        Cache analysis results for a niche.
        
        Args:
            niche: Niche category
            analysis_data: Analysis results dictionary
            video_count: Number of videos analyzed
            
        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO niche_analysis (niche, video_count, analysis_json, updated_at)
                VALUES (?, ?, ?, ?)
            """, (
                niche,
                video_count,
                json.dumps(analysis_data),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error caching niche analysis: {e}")
            return False
    
    def get_cached_analysis(self, niche: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached analysis if it's fresh.
        
        Args:
            niche: Niche category
            max_age_hours: Maximum age of cache in hours
            
        Returns:
            Cached analysis data or None if expired/not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff_time = (datetime.utcnow() - timedelta(hours=max_age_hours)).isoformat()
            
            cursor.execute("""
                SELECT analysis_json FROM niche_analysis
                WHERE niche = ? AND updated_at > ?
            """, (niche, cutoff_time))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['analysis_json'])
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached analysis: {e}")
            return None
    
    def add_channel(self, channel_data: Dict[str, Any], niche: str) -> bool:
        """Add or update channel information."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO channels (
                    id, niche, name, subscriber_count, video_count,
                    upload_frequency_per_week, verified, metadata_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                channel_data.get('id'),
                niche,
                channel_data.get('name'),
                channel_data.get('subscriber_count'),
                channel_data.get('video_count'),
                channel_data.get('upload_frequency_per_week'),
                channel_data.get('verified'),
                json.dumps(channel_data),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding channel: {e}")
            return False
    
    def get_channels_by_niche(self, niche: str) -> List[Dict[str, Any]]:
        """Get all channels for a niche."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM channels WHERE niche = ?
                ORDER BY subscriber_count DESC
            """, (niche,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving channels: {e}")
            return []
    
    # ── Snapshot methods for trend tracking ──

    def save_snapshot(self, niche: str, analysis: Dict[str, Any],
                      blueprint: Dict[str, Any], video_count: int) -> bool:
        """Save a timestamped snapshot of analysis results for trend tracking."""
        try:
            conn = self._get_connection()
            engagement = analysis.get("engagement", {}).get("engagement_analysis", {})
            benchmarks = engagement.get("engagement_benchmarks", {})
            topics = analysis.get("competition", {}).get("niche_topics", [])

            conn.execute("""
                INSERT INTO niche_snapshots
                    (niche, scraped_at, video_count, unique_channels,
                     avg_views, median_views, avg_engagement, avg_like_ratio,
                     top_topics_json, analysis_json, blueprint_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                niche,
                datetime.utcnow().isoformat(),
                video_count,
                analysis.get("metadata", {}).get("unique_channels", 0),
                engagement.get("average_views_per_video", 0),
                engagement.get("median_views", 0),
                benchmarks.get("average_engagement_rate_percent", 0),
                benchmarks.get("average_like_ratio_percent", 0),
                json.dumps(topics[:10]),
                json.dumps(analysis),
                json.dumps(blueprint),
            ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving snapshot: {e}")
            return False

    def get_snapshots(self, niche: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get historical snapshots for a niche, newest first."""
        try:
            conn = self._get_connection()
            rows = conn.execute("""
                SELECT id, niche, scraped_at, video_count, unique_channels,
                       avg_views, median_views, avg_engagement, avg_like_ratio,
                       top_topics_json
                FROM niche_snapshots
                WHERE niche = ?
                ORDER BY scraped_at DESC
                LIMIT ?
            """, (niche, limit)).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Error getting snapshots: {e}")
            return []

    def get_snapshot_detail(self, snapshot_id: int) -> Optional[Dict[str, Any]]:
        """Get full snapshot including analysis and blueprint JSON."""
        try:
            conn = self._get_connection()
            row = conn.execute(
                "SELECT * FROM niche_snapshots WHERE id = ?", (snapshot_id,)
            ).fetchone()
            if row:
                d = dict(row)
                d["analysis"] = json.loads(d.get("analysis_json") or "{}")
                d["blueprint"] = json.loads(d.get("blueprint_json") or "{}")
                d["top_topics"] = json.loads(d.get("top_topics_json") or "[]")
                return d
            return None
        except Exception as e:
            logger.error(f"Error getting snapshot detail: {e}")
            return None

    def get_all_tracked_niches(self) -> List[str]:
        """Get list of niches that have at least one snapshot."""
        try:
            conn = self._get_connection()
            rows = conn.execute(
                "SELECT DISTINCT niche FROM niche_snapshots ORDER BY niche"
            ).fetchall()
            return [r["niche"] for r in rows]
        except Exception as e:
            logger.error(f"Error getting tracked niches: {e}")
            return []

    # ── Schedule methods for auto-scrape ──

    def save_schedule(self, niche: str, enabled: bool,
                      interval_hours: int, video_count: int) -> bool:
        try:
            conn = self._get_connection()
            now = datetime.utcnow()
            next_run = (now + timedelta(hours=interval_hours)).isoformat() if enabled else None
            conn.execute("""
                INSERT OR REPLACE INTO scrape_schedules
                    (niche, enabled, interval_hours, video_count, last_run, next_run)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (niche, int(enabled), interval_hours, video_count, None, next_run))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving schedule: {e}")
            return False

    def get_schedule(self, niche: str) -> Optional[Dict[str, Any]]:
        try:
            conn = self._get_connection()
            row = conn.execute(
                "SELECT * FROM scrape_schedules WHERE niche = ?", (niche,)
            ).fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting schedule: {e}")
            return None

    def get_all_schedules(self) -> List[Dict[str, Any]]:
        try:
            conn = self._get_connection()
            rows = conn.execute(
                "SELECT * FROM scrape_schedules ORDER BY niche"
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Error getting schedules: {e}")
            return []

    def update_schedule_last_run(self, niche: str) -> bool:
        try:
            conn = self._get_connection()
            sched = self.get_schedule(niche)
            if not sched:
                return False
            now = datetime.utcnow()
            next_run = (now + timedelta(hours=sched["interval_hours"])).isoformat()
            conn.execute("""
                UPDATE scrape_schedules
                SET last_run = ?, next_run = ?
                WHERE niche = ?
            """, (now.isoformat(), next_run, niche))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating schedule: {e}")
            return False

    def close(self):
        """Close database connection."""
        if hasattr(self.local, 'connection') and self.local.connection:
            self.local.connection.close()


# Global database instance
_db_instance: Optional[YouTubeAnalyzerDB] = None


def get_db(db_path: str = None) -> YouTubeAnalyzerDB:
    """Get or create global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = YouTubeAnalyzerDB(db_path)
    return _db_instance
