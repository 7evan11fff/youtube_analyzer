"""
Utility functions for YouTube Analyzer.
Provides helper functions for data processing, formatting, and validation.
"""

import logging
import re
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


def format_large_number(num: int) -> str:
    """
    Format large numbers with K/M/B notation.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string (e.g., "1.5M", "234K")
    """
    try:
        num = int(num)
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(num)
    except (ValueError, TypeError):
        return "0"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage with specified decimal places."""
    try:
        return f"{float(value):.{decimals}f}%"
    except (ValueError, TypeError):
        return "0%"


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to HH:MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    except (ValueError, TypeError):
        return "0:00"


def format_date(date_str: str, format: str = "%Y-%m-%d") -> str:
    """
    Parse and format date string.
    
    Args:
        date_str: ISO format date string
        format: Desired output format
        
    Returns:
        Formatted date string
    """
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime(format)
    except (ValueError, AttributeError):
        return date_str


def calculate_engagement_rate(views: int, likes: int, comments: int) -> float:
    """
    Calculate engagement rate as percentage.
    
    Args:
        views: View count
        likes: Like count
        comments: Comment count
        
    Returns:
        Engagement rate as percentage
    """
    try:
        if views <= 0:
            return 0.0
        return ((likes + comments) / views) * 100
    except Exception as e:
        logger.warning(f"Could not calculate engagement rate: {e}")
        return 0.0


def calculate_like_ratio(views: int, likes: int) -> float:
    """Calculate like ratio (likes per 1000 views)."""
    try:
        if views <= 0:
            return 0.0
        return (likes / views) * 100
    except Exception:
        return 0.0


def calculate_comment_ratio(views: int, comments: int) -> float:
    """Calculate comment ratio (comments per 1000 views)."""
    try:
        if views <= 0:
            return 0.0
        return (comments / views) * 100
    except Exception:
        return 0.0


def validate_niche_name(niche: str) -> bool:
    """
    Validate niche name.
    
    Args:
        niche: Niche name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not niche or len(niche.strip()) == 0:
        return False
    if len(niche) > 200:
        return False
    return True


def validate_video_count(count: int) -> bool:
    """Validate video count is within acceptable range."""
    return 10 <= count <= 500


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text: Text to extract from
        min_length: Minimum keyword length
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Remove special characters and split
    words = re.findall(r'\b[a-z0-9]+\b', text.lower())
    
    # Filter by length
    return [w for w in words if len(w) >= min_length]


def get_time_period_description(days_ago: int) -> str:
    """
    Convert days to human-readable period.
    
    Args:
        days_ago: Number of days in the past
        
    Returns:
        Human-readable description
    """
    if days_ago < 1:
        return "Today"
    elif days_ago < 7:
        return f"{days_ago} days ago"
    elif days_ago < 30:
        weeks = days_ago // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif days_ago < 365:
        months = days_ago // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = days_ago // 365
        return f"{years} year{'s' if years > 1 else ''} ago"


def get_video_age_days(upload_date: str) -> int:
    """
    Calculate video age in days.
    
    Args:
        upload_date: ISO format date string
        
    Returns:
        Age in days
    """
    try:
        dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
        age = (datetime.utcnow() - dt).days
        return max(0, age)
    except Exception as e:
        logger.warning(f"Could not calculate age: {e}")
        return 0


def categorize_video_by_views(views: int) -> str:
    """Categorize video by view count."""
    if views < 1000:
        return "Very Low"
    elif views < 10000:
        return "Low"
    elif views < 100000:
        return "Medium"
    elif views < 1000000:
        return "High"
    else:
        return "Very High"


def categorize_video_by_length(seconds: int) -> str:
    """Categorize video by duration."""
    minutes = seconds / 60
    if minutes <= 10:
        return "Short-form"
    elif minutes <= 20:
        return "Medium-form"
    else:
        return "Long-form"


def get_engagement_level(engagement_rate: float) -> str:
    """Categorize engagement level."""
    if engagement_rate < 0.5:
        return "Low"
    elif engagement_rate < 2:
        return "Medium"
    elif engagement_rate < 5:
        return "High"
    else:
        return "Very High"


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], recursive: bool = True) -> Dict[str, Any]:
    """
    Merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        recursive: Whether to recursively merge nested dicts
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and recursive and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value, recursive=True)
        else:
            result[key] = value
    
    return result


def safe_json_dumps(data: Any, indent: int = 2) -> str:
    """
    Safely serialize data to JSON, handling special types.
    
    Args:
        data: Data to serialize
        indent: Indentation level
        
    Returns:
        JSON string
    """
    try:
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error serializing to JSON: {e}")
        return "{}"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def get_file_size_mb(filepath: str) -> float:
    """Get file size in MB."""
    try:
        from pathlib import Path
        return Path(filepath).stat().st_size / (1024 * 1024)
    except Exception as e:
        logger.warning(f"Could not get file size: {e}")
        return 0.0


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file creation.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    return truncate_string(filename, max_length=200, suffix='')


class ProgressBar:
    """Simple progress bar for CLI."""
    
    def __init__(self, total: int, prefix: str = "", width: int = 30):
        """
        Initialize progress bar.
        
        Args:
            total: Total items
            prefix: Prefix text
            width: Bar width in characters
        """
        self.total = total
        self.prefix = prefix
        self.width = width
        self.current = 0
    
    def update(self, amount: int = 1):
        """Update progress."""
        self.current = min(self.current + amount, self.total)
        self._print()
    
    def _print(self):
        """Print progress bar."""
        percent = self.current / self.total
        filled = int(self.width * percent)
        bar = '█' * filled + '░' * (self.width - filled)
        
        print(f'\r{self.prefix} |{bar}| {int(percent * 100)}%', end='', flush=True)
        
        if self.current == self.total:
            print()  # New line when complete
