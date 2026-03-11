"""
Core YouTube Analyzer module.
Handles YouTube API integration, data scraping, and transcript fetching.
"""

import logging
import os
import ssl
import time
from typing import Optional, List, Dict, Any, Generator
from datetime import datetime, timedelta
import json
import re

import certifi
import requests
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

# Fix SSL certificate verification for Homebrew Python on macOS
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

from database import get_db

logger = logging.getLogger(__name__)
load_dotenv()


class YouTubeAPIClient:
    """Handles YouTube API operations with rate limiting."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize YouTube API client.
        
        Args:
            api_key: YouTube API key. Falls back to environment variable.
        """
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            logger.warning("No YouTube API key provided. Some features may be limited.")
        
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.requests_made = 0
        self.last_request_time = 0
        self.rate_limit_delay = 0.1  # Seconds between requests
    
    def _apply_rate_limit(self):
        """Apply rate limiting between API requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def search_videos(self, query: str, max_results: int = 50, order: str = "relevance") -> List[Dict[str, Any]]:
        """
        Search for videos using YouTube API.
        
        Args:
            query: Search query
            max_results: Maximum number of results (50-500, default 50)
            order: Sort order (relevance, date, viewCount, etc.)
            
        Returns:
            List of video metadata
        """
        if not self.api_key:
            logger.warning("No API key available, using fallback search")
            return self._search_videos_fallback(query, max_results)
        
        try:
            self._apply_rate_limit()
            
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": min(max_results, 50),
                "key": self.api_key,
                "order": order,
                "relevanceLanguage": "en",
                "videoCategoryId": "0"
            }
            
            response = requests.get(f"{self.base_url}/search", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.requests_made += 1
            
            videos = []
            for item in data.get("items", []):
                if item["id"]["kind"] == "youtube#video":
                    videos.append({
                        "id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "channel_id": item["snippet"]["channelId"],
                        "channel_name": item["snippet"]["channelTitle"],
                        "thumbnail_url": item["snippet"]["thumbnails"].get("high", {}).get("url"),
                        "upload_date": item["snippet"]["publishedAt"]
                    })
            
            logger.info(f"Found {len(videos)} videos for query: {query}")
            return videos
        
        except Exception as e:
            logger.error(f"Error searching videos: {e}")
            return []
    
    def _search_videos_fallback(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Fallback search using yt-dlp when API key is unavailable."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'extract_flat': True,
            }

            logger.info(f"Searching YouTube for up to {max_results} '{query}' videos (this may take a minute)...")

            videos = []
            with YoutubeDL(ydl_opts) as ydl:
                search_url = f"ytsearch{max_results}:{query}"
                results = ydl.extract_info(search_url, download=False)

                entries = results.get("entries", [])
                logger.info(f"Search returned {len(entries)} results, fetching details...")

                for idx, item in enumerate(entries):
                    if item:
                        videos.append({
                            "id": item.get("id"),
                            "title": item.get("title"),
                            "description": item.get("description", ""),
                            "channel_id": item.get("channel_id"),
                            "channel_name": item.get("channel") or item.get("uploader"),
                            "thumbnail_url": item.get("thumbnail"),
                            "upload_date": item.get("upload_date"),
                            "view_count": item.get("view_count"),
                            "duration_seconds": item.get("duration"),
                        })
                    if (idx + 1) % 10 == 0:
                        logger.info(f"  Processed {idx + 1}/{len(entries)} search results")

            logger.info(f"Fallback search complete: {len(videos)} videos found")
            return videos
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return []
    
    def get_video_stats(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed video statistics.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video statistics
        """
        if not self.api_key:
            return self._get_video_stats_fallback(video_id)
        
        try:
            self._apply_rate_limit()
            
            params = {
                "part": "statistics,contentDetails,snippet",
                "id": video_id,
                "key": self.api_key
            }
            
            response = requests.get(f"{self.base_url}/videos", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.requests_made += 1
            
            if not data.get("items"):
                return None
            
            item = data["items"][0]
            stats = item.get("statistics", {})
            details = item.get("contentDetails", {})
            
            # Parse duration (PT format)
            duration = self._parse_duration(details.get("duration", "PT0S"))
            
            return {
                "id": video_id,
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "duration_seconds": duration,
                "made_for_kids": details.get("madeForKids", False),
                "content_rating": details.get("contentRating", {})
            }
        
        except Exception as e:
            logger.error(f"Error getting video stats for {video_id}: {e}")
            return None
    
    def _get_video_stats_fallback(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Fallback video stats using yt-dlp."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'nocheckcertificate': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                
                return {
                    "id": video_id,
                    "view_count": info.get("view_count", 0),
                    "like_count": info.get("like_count", 0),
                    "comment_count": info.get("comment_count", 0),
                    "duration_seconds": info.get("duration", 0),
                    "made_for_kids": False,
                    "content_rating": {}
                }
        except Exception as e:
            logger.error(f"Fallback video stats failed for {video_id}: {e}")
            return None
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get channel statistics."""
        if not self.api_key:
            return None
        
        try:
            self._apply_rate_limit()
            
            params = {
                "part": "statistics,snippet",
                "id": channel_id,
                "key": self.api_key
            }
            
            response = requests.get(f"{self.base_url}/channels", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.requests_made += 1
            
            if not data.get("items"):
                return None
            
            item = data["items"][0]
            stats = item.get("statistics", {})
            
            return {
                "id": channel_id,
                "name": item.get("snippet", {}).get("title"),
                "subscriber_count": int(stats.get("subscriberCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "view_count": int(stats.get("viewCount", 0))
            }
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return None
    
    @staticmethod
    def _parse_duration(duration_str: str) -> int:
        """Parse YouTube duration string (PT format) to seconds."""
        try:
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
            if match:
                hours, minutes, seconds = match.groups()
                return (int(hours or 0) * 3600 + 
                       int(minutes or 0) * 60 + 
                       int(seconds or 0))
        except Exception as e:
            logger.warning(f"Could not parse duration {duration_str}: {e}")
        return 0
    
    def get_video_transcript(self, video_id: str) -> Optional[str]:
        """
        Get video transcript using yt-dlp.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Transcript text or None
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'writesubtitles': True,
                'skip_unavailable_fragments': True,
                'nocheckcertificate': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                
                if not info:
                    return None
                
                # Try to get subtitles
                subtitles = info.get("subtitles", {})
                automatic_captions = info.get("automatic_captions", {})
                
                # Prefer auto-generated English captions
                captions = automatic_captions.get("en", []) or subtitles.get("en", [])
                
                if captions:
                    # Combine caption text
                    transcript = ""
                    for caption in captions[:50]:  # Limit to avoid huge responses
                        transcript += caption.get("text", "") + " "
                    return transcript.strip()
            
            return None
        except Exception as e:
            logger.debug(f"Could not fetch transcript for {video_id}: {e}")
            return None


class NicheDataCollector:
    """Orchestrates data collection for a YouTube niche."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize niche data collector.
        
        Args:
            api_key: YouTube API key
        """
        self.api = YouTubeAPIClient(api_key)
        self.db = get_db()
    
    @staticmethod
    def _build_search_queries(niche: str, num_videos: int) -> List[Dict[str, Any]]:
        """
        Build multiple search queries for broader niche coverage.
        A single query biases toward YouTube's top results; multiple queries
        with different sort orders and variations capture a fuller picture.
        """
        queries = [
            {"query": niche, "order": "relevance"},
        ]
        if num_videos >= 30:
            queries.append({"query": niche, "order": "viewCount"})
        if num_videos >= 50:
            queries.append({"query": f"{niche} tutorial", "order": "relevance"})
        if num_videos >= 75:
            queries.append({"query": f"{niche} for beginners", "order": "relevance"})
        if num_videos >= 100:
            queries.append({"query": f"{niche} tips", "order": "relevance"})
            queries.append({"query": niche, "order": "date"})
        return queries

    def collect_niche_data(self, niche: str, num_videos: int = 50, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Collect comprehensive data for a niche using multiple search strategies
        for broader coverage.
        """
        num_videos = min(max(num_videos, 10), 500)
        
        logger.info(f"Starting data collection for niche: {niche}")
        logger.info(f"Target: {num_videos} videos")
        
        # Check cache
        cached_videos = self.db.get_videos_by_niche(niche, limit=num_videos)
        if cached_videos and not force_refresh:
            if len(cached_videos) >= num_videos * 0.8:
                logger.info(f"Using {len(cached_videos)} cached videos from database")
                return cached_videos

        queries = self._build_search_queries(niche, num_videos)
        seen_ids = set()
        all_videos = []
        per_query = max(10, num_videos // len(queries) + 10)

        for q in queries:
            if len(all_videos) >= num_videos:
                break
            logger.info(f"Searching: '{q['query']}' (sort: {q['order']}, limit: {per_query})")
            results = self.api.search_videos(q["query"], max_results=per_query, order=q["order"])
            for v in results:
                vid_id = v.get("id")
                if vid_id and vid_id not in seen_ids:
                    seen_ids.add(vid_id)
                    all_videos.append(v)

        videos = all_videos[:num_videos]

        if not videos:
            logger.warning(f"No videos found for niche: {niche}")
            return []
        
        logger.info(f"Found {len(videos)} videos, enriching data...")

        enriched_videos = []
        channels_seen = set()
        needs_stats = not self.api.api_key

        for idx, video in enumerate(videos):
            try:
                has_views = video.get("view_count") is not None
                has_duration = video.get("duration_seconds") is not None

                if not has_views or not has_duration:
                    stats = self.api.get_video_stats(video["id"])
                    if stats:
                        video.update(stats)
                    if (idx + 1) % 5 == 0:
                        logger.info(f"Enriched {idx + 1}/{len(videos)} videos (fetching missing stats)")
                elif self.api.api_key:
                    stats = self.api.get_video_stats(video["id"])
                    if stats:
                        video.update(stats)

                # Get channel info (once per unique channel)
                channel_id = video.get("channel_id")
                if channel_id and channel_id not in channels_seen:
                    if self.api.api_key:
                        channel_info = self.api.get_channel_info(channel_id)
                        if channel_info:
                            self.db.add_channel(channel_info, niche)
                    channels_seen.add(channel_id)

                enriched_videos.append(video)

                if (idx + 1) % 10 == 0:
                    logger.info(f"Processed {idx + 1}/{len(videos)} videos")

            except Exception as e:
                logger.warning(f"Error enriching video {video.get('id')}: {e}")
                enriched_videos.append(video)
        
        # Cache all videos
        self.db.add_videos_batch(enriched_videos, niche)
        
        logger.info(f"Data collection complete. Collected {len(enriched_videos)} videos.")
        return enriched_videos
    
    def collect_related_niches(self, niche: str, num_related: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collect data for related niche variations.
        
        Args:
            niche: Base niche name
            num_related: Number of related niches to search
            
        Returns:
            Dictionary mapping niche variations to video lists
        """
        logger.info(f"Collecting related niches for: {niche}")
        
        # Generate related queries
        related_queries = [
            f"{niche} for beginners",
            f"{niche} tutorial",
            f"{niche} tips and tricks"
        ][:num_related]
        
        results = {}
        for query in related_queries:
            logger.info(f"Collecting data for: {query}")
            videos = self.api.search_videos(query, max_results=25)
            if videos:
                results[query] = videos
        
        return results
