"""
Trend analysis across historical snapshots.
Compares niche metrics over time to surface growth, decline, and shifts.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from database import get_db

logger = logging.getLogger(__name__)


def get_trend_summary(niche: str, limit: int = 20) -> Dict[str, Any]:
    """
    Build a trend summary for a niche by comparing its historical snapshots.
    Returns deltas, direction arrows, and time-series data for charting.
    """
    db = get_db()
    snapshots = db.get_snapshots(niche, limit=limit)

    if not snapshots:
        return {"error": "No snapshots found", "niche": niche}

    # Newest first from DB – reverse for chronological order
    chronological = list(reversed(snapshots))

    series = {
        "dates": [],
        "avg_views": [],
        "median_views": [],
        "avg_engagement": [],
        "avg_like_ratio": [],
        "video_count": [],
        "unique_channels": [],
    }

    for s in chronological:
        series["dates"].append(s["scraped_at"][:10])
        series["avg_views"].append(s.get("avg_views", 0))
        series["median_views"].append(s.get("median_views", 0))
        series["avg_engagement"].append(s.get("avg_engagement", 0))
        series["avg_like_ratio"].append(s.get("avg_like_ratio", 0))
        series["video_count"].append(s.get("video_count", 0))
        series["unique_channels"].append(s.get("unique_channels", 0))

    latest = chronological[-1]
    deltas = {}

    if len(chronological) >= 2:
        prev = chronological[-2]
        for key in ["avg_views", "median_views", "avg_engagement",
                     "avg_like_ratio", "unique_channels"]:
            old_val = prev.get(key, 0) or 0
            new_val = latest.get(key, 0) or 0
            if old_val > 0:
                pct = ((new_val - old_val) / old_val) * 100
            else:
                pct = 0
            direction = "up" if pct > 1 else "down" if pct < -1 else "flat"
            deltas[key] = {
                "previous": round(old_val, 2),
                "current": round(new_val, 2),
                "change_pct": round(pct, 1),
                "direction": direction,
            }

    return {
        "niche": niche,
        "snapshot_count": len(chronological),
        "first_scraped": chronological[0]["scraped_at"][:10],
        "last_scraped": chronological[-1]["scraped_at"][:10],
        "latest": {
            "avg_views": latest.get("avg_views", 0),
            "median_views": latest.get("median_views", 0),
            "avg_engagement": latest.get("avg_engagement", 0),
            "video_count": latest.get("video_count", 0),
            "unique_channels": latest.get("unique_channels", 0),
        },
        "deltas": deltas,
        "series": series,
    }


def format_trend_report(niche: str) -> str:
    """Build a human-readable trend report string for the GUI."""
    data = get_trend_summary(niche)

    if "error" in data:
        return f"No trend data for '{niche}' yet. Run at least one analysis first."

    lines = [
        f"Trend Report: {niche}",
        f"{'=' * 50}",
        f"Snapshots: {data['snapshot_count']}",
        f"Tracked since: {data['first_scraped']}",
        f"Last scraped:  {data['last_scraped']}",
        "",
        "Latest Metrics:",
        f"  Median Views:    {data['latest']['median_views']:,.0f}",
        f"  Avg Views:       {data['latest']['avg_views']:,.0f}",
        f"  Engagement Rate: {data['latest']['avg_engagement']:.2f}%",
        f"  Videos Sampled:  {data['latest']['video_count']}",
        f"  Unique Channels: {data['latest']['unique_channels']}",
    ]

    if data["deltas"]:
        lines.append("")
        lines.append("Changes Since Previous Scrape:")
        arrows = {"up": "▲", "down": "▼", "flat": "—"}
        labels = {
            "median_views": "Median Views",
            "avg_views": "Avg Views",
            "avg_engagement": "Engagement",
            "avg_like_ratio": "Like Ratio",
            "unique_channels": "Channels",
        }
        for key, label in labels.items():
            d = data["deltas"].get(key)
            if d:
                arrow = arrows[d["direction"]]
                lines.append(
                    f"  {arrow} {label}: {d['change_pct']:+.1f}% "
                    f"({d['previous']:,.1f} → {d['current']:,.1f})"
                )

    return "\n".join(lines)
