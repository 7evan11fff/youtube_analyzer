"""
Configuration for YouTube Analyzer.
Manage API keys, settings, and environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_API_QUOTA_PER_DAY = 10000  # YouTube API quota

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/youtube_analyzer.db")
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Output Configuration
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
OUTPUT_FORMATS = ["json", "csv", "markdown"]
GENERATE_VISUALIZATIONS = True

# Analysis Configuration
DEFAULT_VIDEO_COUNT = 50
MIN_VIDEO_COUNT = 10
MAX_VIDEO_COUNT = 500

# Caching Configuration
CACHE_DURATION_HOURS = 24
ENABLE_CACHING = True

# Data Collection Configuration
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "youtube_analyzer.log"

# API Configuration
RATE_LIMIT_DELAY = 0.1  # seconds between API requests

# Analysis Parameters
SENTIMENT_THRESHOLD_POSITIVE = 0.1
SENTIMENT_THRESHOLD_NEGATIVE = -0.1

# Visualization Configuration
VISUALIZATION_DPI = 100
VISUALIZATION_FIGSIZE = (14, 10)

# Feature Flags
ANALYZE_COMMENTS = False  # Can require API quota
EXTRACT_TRANSCRIPTS = True
ANALYZE_THUMBNAILS = True
ANALYZE_TITLES = True
ANALYZE_DESCRIPTIONS = True

# Export Configuration
EXPORT_TO_JSON = True
EXPORT_TO_CSV = True
EXPORT_TO_MARKDOWN = True
CREATE_VISUALIZATIONS = True

# Content Thresholds
ENGAGEMENT_THRESHOLD_LOW = 0.01  # Less than 1% engagement
ENGAGEMENT_THRESHOLD_HIGH = 0.1   # More than 10% engagement

# Trend Configuration
TRENDING_LOOKBACK_DAYS = 30
TRENDING_MIN_MENTIONS = 2

# Database Cleanup
AUTO_CLEANUP_DAYS = 90  # Remove data older than 90 days (disabled by default)
AUTO_CLEANUP_ENABLED = False
