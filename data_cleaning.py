"""
Data cleaning and normalization for YouTube video data.
Handles the messy reality of mixed API/scraping sources: None values,
inconsistent date formats, noisy keyword extraction, and missing fields.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

# Words that slip through basic stopword filters but aren't meaningful topics
NOISE_WORDS = frozenset({
    "could", "would", "should", "might", "really", "actually", "just",
    "like", "make", "made", "know", "want", "need", "going", "thing",
    "things", "much", "many", "also", "still", "even", "back", "well",
    "right", "good", "best", "will", "been", "have", "more", "most",
    "every", "some", "them", "than", "what", "when", "your", "this",
    "that", "from", "with", "about", "into", "over", "after", "were",
    "here", "there", "these", "those", "being", "doing", "getting",
    "using", "first", "last", "next", "full", "must", "doesn", "didn",
    "isn", "aren", "won", "don", "can", "does", "very", "part", "come",
    "take", "give", "keep", "help", "start", "stop", "watch", "video",
    "videos", "channel", "subscribe", "link", "below", "check", "free",
})


def safe_int(value: Any, default: int = 0) -> int:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_upload_date(date_value: Any) -> Optional[datetime]:
    """
    Parse upload dates from multiple formats:
    - ISO 8601: "2024-01-15T10:30:00Z"
    - yt-dlp compact: "20240115"
    - Date only: "2024-01-15"
    """
    if not date_value:
        return None

    date_str = str(date_value).strip()

    formats = [
        ("%Y%m%d", 8),
        ("%Y-%m-%dT%H:%M:%SZ", None),
        ("%Y-%m-%dT%H:%M:%S+00:00", None),
        ("%Y-%m-%d", 10),
    ]

    if "T" in date_str and date_str.endswith("Z"):
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            pass

    if "T" in date_str and "+" in date_str:
        try:
            return datetime.fromisoformat(date_str).replace(tzinfo=None)
        except ValueError:
            pass

    for fmt, expected_len in formats:
        if expected_len and len(date_str) != expected_len:
            continue
        try:
            return datetime.strptime(date_str[:len(fmt.replace("%", "X"))], fmt)
        except (ValueError, IndexError):
            pass

    # Last resort: try yt-dlp's YYYYMMDD
    if re.match(r"^\d{8}$", date_str):
        try:
            return datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            pass

    logger.debug(f"Could not parse date: {date_str}")
    return None


def normalize_video(video: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a single video record so all downstream code can rely on
    consistent types and non-None values for numeric fields.
    """
    v = dict(video)

    v["view_count"] = safe_int(v.get("view_count"))
    v["like_count"] = safe_int(v.get("like_count"))
    v["comment_count"] = safe_int(v.get("comment_count"))
    v["duration_seconds"] = safe_int(v.get("duration_seconds"))

    v["title"] = str(v.get("title") or "").strip()
    v["description"] = str(v.get("description") or "").strip()
    v["channel_name"] = str(v.get("channel_name") or v.get("uploader") or "Unknown").strip()
    v["channel_id"] = v.get("channel_id") or ""
    v["id"] = v.get("id") or ""

    parsed_date = parse_upload_date(v.get("upload_date"))
    if parsed_date:
        v["upload_date"] = parsed_date.isoformat()
        v["_parsed_date"] = parsed_date
    else:
        v["_parsed_date"] = None

    if v["view_count"] > 0:
        v["like_ratio"] = (v["like_count"] / v["view_count"]) * 100
        v["comment_ratio"] = (v["comment_count"] / v["view_count"]) * 100
        v["engagement_rate"] = ((v["like_count"] + v["comment_count"]) / v["view_count"]) * 100
    else:
        v["like_ratio"] = 0.0
        v["comment_ratio"] = 0.0
        v["engagement_rate"] = 0.0

    if v["duration_seconds"] > 0:
        minutes = v["duration_seconds"] / 60
        if minutes <= 1:
            v["length_category"] = "Shorts (<1 min)"
        elif minutes <= 10:
            v["length_category"] = "Short-form (<10 min)"
        elif minutes <= 20:
            v["length_category"] = "Medium-form (10-20 min)"
        elif minutes <= 60:
            v["length_category"] = "Long-form (20-60 min)"
        else:
            v["length_category"] = "Extra-long (60+ min)"
    else:
        v["length_category"] = "Unknown"

    return v


def normalize_videos(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize a batch of videos and filter out empty/broken records."""
    cleaned = []
    skipped = 0

    for video in videos:
        v = normalize_video(video)
        if not v["id"] or not v["title"]:
            skipped += 1
            continue
        cleaned.append(v)

    if skipped:
        logger.info(f"Cleaned {len(cleaned)} videos, skipped {skipped} invalid records")

    return cleaned


def is_noise_word(word: str) -> bool:
    """Check if a word is noise that shouldn't be treated as a topic."""
    if len(word) <= 2:
        return True
    if word in NOISE_WORDS:
        return True
    if re.match(r"^\d+$", word):
        return True
    if not re.match(r"^[a-z0-9]+$", word):
        return True
    return False


def extract_clean_keywords(text: str, min_length: int = 4) -> List[str]:
    """Extract meaningful keywords from text, filtering noise."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9]+\b", text.lower())
    return [w for w in words if len(w) >= min_length and not is_noise_word(w)]


def extract_bigrams(text: str) -> List[str]:
    """Extract meaningful two-word phrases from text."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9]+\b", text.lower())
    words = [w for w in words if not is_noise_word(w) and len(w) >= 3]
    bigrams = []
    for i in range(len(words) - 1):
        bigrams.append(f"{words[i]} {words[i+1]}")
    return bigrams


def extract_niche_topics(
    titles: List[str],
    min_count: int = 2,
    max_topics: int = 20,
) -> List[Dict[str, Any]]:
    """
    Extract meaningful niche topics from video titles using both
    unigrams and bigrams, with noise filtering.
    Returns topics sorted by frequency.
    """
    from nltk.corpus import stopwords

    stop_words = set(stopwords.words("english"))

    unigram_counter: Counter = Counter()
    bigram_counter: Counter = Counter()

    for title in titles:
        words = extract_clean_keywords(title)
        words = [w for w in words if w not in stop_words]
        unigram_counter.update(words)
        bigrams = extract_bigrams(title)
        bigram_counter.update(bigrams)

    topics = []

    for phrase, count in bigram_counter.most_common(max_topics):
        if count >= min_count:
            topics.append({
                "topic": phrase,
                "frequency": count,
                "type": "phrase",
            })

    seen_in_bigrams = set()
    for t in topics:
        for word in t["topic"].split():
            seen_in_bigrams.add(word)

    for word, count in unigram_counter.most_common(max_topics * 2):
        if len(topics) >= max_topics:
            break
        if count >= min_count and word not in seen_in_bigrams:
            topics.append({
                "topic": word,
                "frequency": count,
                "type": "keyword",
            })

    topics.sort(key=lambda t: t["frequency"], reverse=True)
    return topics[:max_topics]


def partition_by_performance(
    videos: List[Dict[str, Any]],
    metric: str = "view_count",
    top_pct: float = 0.25,
    bottom_pct: float = 0.25,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Split videos into top-performing, middle, and underperforming groups.
    Used to find what differentiates high-performing content.
    """
    sorted_vids = sorted(videos, key=lambda v: v.get(metric, 0), reverse=True)
    n = len(sorted_vids)
    top_n = max(1, int(n * top_pct))
    bottom_n = max(1, int(n * bottom_pct))

    top = sorted_vids[:top_n]
    bottom = sorted_vids[-bottom_n:]
    middle = sorted_vids[top_n:-bottom_n] if n > top_n + bottom_n else []

    return top, middle, bottom


def compute_percentiles(values: List[float]) -> Dict[str, float]:
    """Compute p10, p25, p50, p75, p90 for a list of values."""
    import numpy as np
    if not values:
        return {}
    arr = np.array(values)
    return {
        "p10": float(np.percentile(arr, 10)),
        "p25": float(np.percentile(arr, 25)),
        "p50": float(np.percentile(arr, 50)),
        "p75": float(np.percentile(arr, 75)),
        "p90": float(np.percentile(arr, 90)),
        "mean": float(np.mean(arr)),
    }
