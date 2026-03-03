"""
Analysis Engine for YouTube Niche Data.
Performs comprehensive analysis on collected video data including:
- Content strategy patterns
- Engagement metrics analysis
- Thumbnail and title strategies
- Competition analysis
- Growth curve patterns
"""

import logging
import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from collections import Counter
import statistics
from urllib.parse import urlparse

import numpy as np
import pandas as pd
from textblob import TextBlob
import nltk

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class ContentStrategyAnalyzer:
    """Analyzes content strategy patterns."""
    
    @staticmethod
    def analyze_video_lengths(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze optimal video length patterns.
        
        Args:
            videos: List of video data
            
        Returns:
            Dictionary with length analysis
        """
        logger.info("Analyzing video lengths...")
        
        durations = [v.get("duration_seconds", 0) for v in videos if v.get("duration_seconds")]
        
        if not durations:
            return {"error": "No duration data available"}
        
        durations_minutes = [d / 60 for d in durations]
        
        # Categorize videos
        short_form = [d for d in durations_minutes if d <= 10]
        medium_form = [d for d in durations_minutes if 10 < d <= 20]
        long_form = [d for d in durations_minutes if d > 20]
        
        return {
            "total_videos": len(durations),
            "average_length_minutes": round(statistics.mean(durations_minutes), 2),
            "median_length_minutes": round(statistics.median(durations_minutes), 2),
            "min_length_minutes": round(min(durations_minutes), 2),
            "max_length_minutes": round(max(durations_minutes), 2),
            "std_dev_minutes": round(statistics.stdev(durations_minutes), 2) if len(durations_minutes) > 1 else 0,
            "distribution": {
                "short_form_10min_or_less": {
                    "count": len(short_form),
                    "percentage": round((len(short_form) / len(durations_minutes)) * 100, 2)
                },
                "medium_form_10_20min": {
                    "count": len(medium_form),
                    "percentage": round((len(medium_form) / len(durations_minutes)) * 100, 2)
                },
                "long_form_20min_plus": {
                    "count": len(long_form),
                    "percentage": round((len(long_form) / len(durations_minutes)) * 100, 2)
                }
            }
        }
    
    @staticmethod
    def analyze_upload_patterns(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze upload timing patterns.
        
        Args:
            videos: List of video data
            
        Returns:
            Dictionary with upload pattern analysis
        """
        logger.info("Analyzing upload patterns...")
        
        days_of_week = []
        hours_of_day = []
        
        for video in videos:
            upload_date = video.get("upload_date")
            if upload_date:
                try:
                    # Parse ISO format date
                    dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    days_of_week.append(dt.strftime("%A"))
                    hours_of_day.append(dt.hour)
                except Exception as e:
                    logger.debug(f"Could not parse date {upload_date}: {e}")
        
        if not days_of_week:
            return {"error": "No upload date data available"}
        
        day_counter = Counter(days_of_week)
        
        # Calculate upload frequency
        dates = sorted([datetime.fromisoformat(v.get("upload_date", "").replace('Z', '+00:00')) 
                       for v in videos if v.get("upload_date")])
        
        frequency_per_week = 0
        if len(dates) > 1:
            days_span = (dates[-1] - dates[0]).days
            if days_span > 0:
                frequency_per_week = round((len(dates) / (days_span / 7)), 2)
        
        return {
            "most_common_upload_days": day_counter.most_common(3),
            "least_common_upload_days": day_counter.most_common()[-3:],
            "average_upload_frequency_per_week": frequency_per_week,
            "total_videos_analyzed": len(days_of_week),
            "peak_upload_hours": Counter(hours_of_day).most_common(3),
            "day_distribution": dict(day_counter)
        }
    
    @staticmethod
    def analyze_titles(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze title patterns and formulas.
        
        Args:
            videos: List of video data
            
        Returns:
            Dictionary with title analysis
        """
        logger.info("Analyzing title patterns...")
        
        titles = [v.get("title", "") for v in videos if v.get("title")]
        
        if not titles:
            return {"error": "No title data"}
        
        # Analyze title characteristics
        title_lengths = [len(t) for t in titles]
        word_counts = [len(t.split()) for t in titles]
        
        # Detect patterns
        question_mark_titles = sum(1 for t in titles if "?" in t)
        number_titles = sum(1 for t in titles if any(c.isdigit() for c in t))
        bracket_titles = sum(1 for t in titles if "[" in t or "]" in t)
        colon_titles = sum(1 for t in titles if ":" in t)
        all_caps_words = sum(1 for t in titles for word in t.split() if word.isupper() and len(word) > 1)
        
        # Extract common words
        stop_words = set(stopwords.words('english'))
        all_words = []
        for title in titles:
            words = [w.lower() for w in title.split() if w.lower() not in stop_words and len(w) > 3]
            all_words.extend(words)
        
        common_words = Counter(all_words).most_common(10)
        
        return {
            "total_titles": len(titles),
            "average_length_chars": round(statistics.mean(title_lengths), 2),
            "average_words": round(statistics.mean(word_counts), 2),
            "min_length": min(title_lengths),
            "max_length": max(title_lengths),
            "optimal_length_range": "50-70 characters (YouTube recommendation)",
            "patterns": {
                "question_mark_titles": {
                    "count": question_mark_titles,
                    "percentage": round((question_mark_titles / len(titles)) * 100, 2)
                },
                "number_titles": {
                    "count": number_titles,
                    "percentage": round((number_titles / len(titles)) * 100, 2)
                },
                "bracket_titles": {
                    "count": bracket_titles,
                    "percentage": round((bracket_titles / len(titles)) * 100, 2)
                },
                "colon_titles": {
                    "count": colon_titles,
                    "percentage": round((colon_titles / len(titles)) * 100, 2)
                }
            },
            "most_common_words": [{"word": word, "count": count} for word, count in common_words],
            "most_common_first_words": Counter([t.split()[0].lower() for t in titles if t.split()]).most_common(5)
        }
    
    @staticmethod
    def analyze_descriptions(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze description patterns."""
        logger.info("Analyzing description patterns...")
        
        descriptions = [v.get("description", "") for v in videos if v.get("description")]
        
        if not descriptions:
            return {"error": "No description data"}
        
        lengths = [len(d) for d in descriptions]
        
        # Check for CTA presence
        cta_patterns = [
            r"subscribe",
            r"like",
            r"comment",
            r"link below",
            r"check out",
            r"follow",
            r"watch next"
        ]
        
        cta_presence = {}
        for pattern in cta_patterns:
            count = sum(1 for d in descriptions if re.search(pattern, d, re.IGNORECASE))
            cta_presence[pattern] = {
                "count": count,
                "percentage": round((count / len(descriptions)) * 100, 2)
            }
        
        return {
            "average_length": round(statistics.mean(lengths), 2),
            "median_length": round(statistics.median(lengths), 2),
            "typical_range": f"{min(lengths)}-{max(lengths)} characters",
            "cta_patterns": cta_presence,
            "contain_timestamps": sum(1 for d in descriptions if re.search(r'\d+:\d+', d)),
            "contain_links": sum(1 for d in descriptions if "http" in d)
        }


class EngagementAnalyzer:
    """Analyzes engagement metrics and patterns."""
    
    @staticmethod
    def analyze_engagement_ratios(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze engagement ratios and benchmarks.
        
        Args:
            videos: List of video data
            
        Returns:
            Dictionary with engagement analysis
        """
        logger.info("Analyzing engagement metrics...")
        
        engagement_data = []
        
        for video in videos:
            # Safely get values with robust None handling
            raw_views = video.get("view_count")
            raw_likes = video.get("like_count")
            raw_comments = video.get("comment_count")
            
            # Convert to int, handling None, empty strings, and other edge cases
            try:
                views = int(raw_views) if raw_views is not None and raw_views != '' else 0
            except (ValueError, TypeError):
                views = 0
            
            try:
                likes = int(raw_likes) if raw_likes is not None and raw_likes != '' else 0
            except (ValueError, TypeError):
                likes = 0
            
            try:
                comments = int(raw_comments) if raw_comments is not None and raw_comments != '' else 0
            except (ValueError, TypeError):
                comments = 0
            
            if views > 0:
                engagement_data.append({
                    "id": video.get("id"),
                    "title": video.get("title"),
                    "views": views,
                    "like_ratio": (likes / views) * 100,
                    "comment_ratio": (comments / views) * 100,
                    "engagement_rate": ((likes + comments) / views) * 100
                })
        
        if not engagement_data:
            return {"error": "No engagement data"}
        
        df = pd.DataFrame(engagement_data)
        
        return {
            "total_videos": len(engagement_data),
            "total_views": int(df["views"].sum()),
            "average_views_per_video": round(df["views"].mean(), 0),
            "median_views": round(df["views"].median(), 0),
            "view_distribution": {
                "0_1k": len(df[df["views"] < 1000]),
                "1k_10k": len(df[(df["views"] >= 1000) & (df["views"] < 10000)]),
                "10k_100k": len(df[(df["views"] >= 10000) & (df["views"] < 100000)]),
                "100k_1m": len(df[(df["views"] >= 100000) & (df["views"] < 1000000)]),
                "1m_plus": len(df[df["views"] >= 1000000])
            },
            "engagement_benchmarks": {
                "average_like_ratio_percent": round(df["like_ratio"].mean(), 2),
                "average_comment_ratio_percent": round(df["comment_ratio"].mean(), 4),
                "average_engagement_rate_percent": round(df["engagement_rate"].mean(), 3),
                "median_like_ratio": round(df["like_ratio"].median(), 2),
                "median_comment_ratio": round(df["comment_ratio"].median(), 4),
                "std_dev_engagement": round(df["engagement_rate"].std(), 3)
            },
            "top_performing_videos": [
                {
                    "title": row["title"],
                    "views": int(row["views"]),
                    "like_ratio": round(row["like_ratio"], 2),
                    "comment_ratio": round(row["comment_ratio"], 4)
                } for _, row in df.nlargest(5, "views").iterrows()
            ]
        }
    
    @staticmethod
    def analyze_sentiment(texts: List[str]) -> Dict[str, Any]:
        """
        Analyze sentiment of comments or descriptions.
        
        Args:
            texts: List of text samples
            
        Returns:
            Dictionary with sentiment analysis
        """
        logger.info("Analyzing sentiment...")
        
        sentiments = []
        
        for text in texts:
            if text:
                try:
                    blob = TextBlob(text)
                    polarity = blob.sentiment.polarity  # -1 to 1
                    
                    if polarity > 0.1:
                        sentiment = "positive"
                    elif polarity < -0.1:
                        sentiment = "negative"
                    else:
                        sentiment = "neutral"
                    
                    sentiments.append({
                        "polarity": polarity,
                        "sentiment": sentiment
                    })
                except Exception as e:
                    logger.debug(f"Could not analyze sentiment: {e}")
        
        if not sentiments:
            return {"error": "No sentiment data"}
        
        df = pd.DataFrame(sentiments)
        
        return {
            "average_polarity": round(df["polarity"].mean(), 3),
            "median_polarity": round(df["polarity"].median(), 3),
            "positive_percent": round((len(df[df["sentiment"] == "positive"]) / len(df)) * 100, 2),
            "negative_percent": round((len(df[df["sentiment"] == "negative"]) / len(df)) * 100, 2),
            "neutral_percent": round((len(df[df["sentiment"] == "neutral"]) / len(df)) * 100, 2),
            "sentiment_distribution": dict(df["sentiment"].value_counts())
        }


class CompetitionAnalyzer:
    """Analyzes competitive landscape."""
    
    @staticmethod
    def analyze_competition(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze competitive landscape and saturation.
        
        Args:
            videos: List of video data
            
        Returns:
            Dictionary with competition analysis
        """
        logger.info("Analyzing competition...")
        
        # Channel distribution
        channels = Counter([v.get("channel_name") for v in videos if v.get("channel_name")])
        
        total_views = sum(int(v.get("view_count") or 0) for v in videos)
        
        top_channels = channels.most_common(10)
        top_channel_share = sum(int(v.get("view_count") or 0)
                               for v in videos 
                               if v.get("channel_name") in [c[0] for c in top_channels]) / total_views if total_views > 0 else 0
        
        return {
            "total_unique_channels": len(channels),
            "market_concentration": {
                "top_10_channel_share_percent": round(top_channel_share * 100, 2),
                "concentration_level": "High" if top_channel_share > 0.5 else "Medium" if top_channel_share > 0.3 else "Low"
            },
            "top_channels": [
                {
                    "name": name,
                    "videos_in_niche": count
                } for name, count in top_channels
            ],
            "market_saturation": "High" if len(channels) > 50 else "Medium" if len(channels) > 20 else "Low"
        }
    
    @staticmethod
    def find_content_gaps(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify underexplored topics and gaps.
        
        Args:
            videos: List of video data
            
        Returns:
            Dictionary with identified gaps
        """
        logger.info("Identifying content gaps...")
        
        titles = [v.get("title", "") for v in videos]
        
        # Extract keywords from all titles
        stop_words = set(stopwords.words('english'))
        all_keywords = Counter()
        
        for title in titles:
            words = [w.lower() for w in title.split() 
                    if w.lower() not in stop_words and len(w) > 3]
            all_keywords.update(words)
        
        # Keywords that appear infrequently might indicate gaps
        gap_indicators = [kw for kw, count in all_keywords.items() if count <= 2]
        
        return {
            "low_frequency_topics": [
                {"topic": kw, "frequency": count} 
                for kw, count in all_keywords.most_common(20)
                if count <= 3
            ],
            "potential_unexplored_angles": gap_indicators[:20],
            "high_saturation_topics": [
                {"topic": kw, "frequency": count} 
                for kw, count in all_keywords.most_common(10)
            ]
        }


class GrowthPatternAnalyzer:
    """Analyzes growth patterns and trends."""
    
    @staticmethod
    def analyze_growth_curves(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze typical growth patterns.
        
        Args:
            videos: List of video data
            
        Returns:
            Dictionary with growth pattern analysis
        """
        logger.info("Analyzing growth patterns...")
        
        # Segment videos by age
        now = datetime.utcnow()
        video_ages = []
        
        for video in videos:
            upload_date = video.get("upload_date")
            if upload_date:
                try:
                    dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    age_days = (now - dt).days
                    views = int(video.get("view_count") or 0)
                    video_ages.append({"age_days": age_days, "views": views})
                except Exception as e:
                    logger.debug(f"Could not parse date: {e}")
        
        if not video_ages:
            return {"error": "No growth data available"}
        
        df = pd.DataFrame(video_ages)
        
        # Group by age ranges
        age_groups = {
            "0-7_days": df[(df["age_days"] <= 7) & (df["age_days"] >= 0)],
            "8-30_days": df[(df["age_days"] > 7) & (df["age_days"] <= 30)],
            "31-90_days": df[(df["age_days"] > 30) & (df["age_days"] <= 90)],
            "90plus_days": df[df["age_days"] > 90]
        }
        
        return {
            "velocity_by_age": {
                name: {
                    "avg_views": round(group["views"].mean(), 0) if len(group) > 0 else 0,
                    "median_views": round(group["views"].median(), 0) if len(group) > 0 else 0,
                    "video_count": len(group)
                }
                for name, group in age_groups.items()
            },
            "typical_growth_trajectory": "Fast initial growth within first 7 days, then plateaus",
            "viral_potential_indicators": {
                "videos_with_100k_views": len(df[df["views"] >= 100000]),
                "percentage_reaching_100k": round((len(df[df["views"] >= 100000]) / len(df)) * 100, 2)
            }
        }
    
    @staticmethod
    def analyze_trending_topics(videos: List[Dict[str, Any]], days_back: int = 30) -> Dict[str, Any]:
        """
        Identify trending topics in recent videos.
        
        Args:
            videos: List of video data
            days_back: How many days back to consider as "recent"
            
        Returns:
            Dictionary with trending topics
        """
        logger.info(f"Analyzing trending topics (last {days_back} days)...")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        recent_videos = []
        
        for video in videos:
            upload_date = video.get("upload_date")
            if upload_date:
                try:
                    dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    if dt >= cutoff_date:
                        recent_videos.append(video)
                except Exception as e:
                    logger.debug(f"Could not parse date: {e}")
        
        if not recent_videos:
            return {"error": f"No videos from last {days_back} days"}
        
        titles = [v.get("title", "") for v in recent_videos]
        stop_words = set(stopwords.words('english'))
        
        all_keywords = Counter()
        for title in titles:
            words = [w.lower() for w in title.split() 
                    if w.lower() not in stop_words and len(w) > 3]
            all_keywords.update(words)
        
        return {
            "recent_videos_count": len(recent_videos),
            "trending_topics": [
                {"topic": kw, "mentions": count} 
                for kw, count in all_keywords.most_common(15)
            ],
            "evergreen_vs_trending": {
                "trending_content_percentage": 40,  # Placeholder
                "evergreen_content_percentage": 60   # Placeholder
            }
        }


class ComprehensiveAnalyzer:
    """Orchestrates all analysis modules."""
    
    def __init__(self):
        """Initialize all analyzers."""
        self.content_strategy = ContentStrategyAnalyzer()
        self.engagement = EngagementAnalyzer()
        self.competition = CompetitionAnalyzer()
        self.growth = GrowthPatternAnalyzer()
    
    def analyze_niche(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run comprehensive analysis on niche data.
        
        Args:
            videos: List of video data
            
        Returns:
            Dictionary with all analysis results
        """
        logger.info(f"Starting comprehensive analysis of {len(videos)} videos...")
        
        results = {
            "metadata": {
                "total_videos_analyzed": len(videos),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "unique_channels": len(set(v.get("channel_name") for v in videos if v.get("channel_name")))
            },
            "content_strategy": {
                "video_lengths": self.content_strategy.analyze_video_lengths(videos),
                "upload_patterns": self.content_strategy.analyze_upload_patterns(videos),
                "title_analysis": self.content_strategy.analyze_titles(videos),
                "description_analysis": self.content_strategy.analyze_descriptions(videos)
            },
            "engagement": {
                "engagement_analysis": self.engagement.analyze_engagement_ratios(videos)
            },
            "competition": {
                "competitive_landscape": self.competition.analyze_competition(videos),
                "content_gaps": self.competition.find_content_gaps(videos)
            },
            "growth": {
                "growth_patterns": self.growth.analyze_growth_curves(videos),
                "trending_topics": self.growth.analyze_trending_topics(videos)
            }
        }
        
        logger.info("Comprehensive analysis complete")
        return results
