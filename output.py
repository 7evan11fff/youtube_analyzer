"""
Output Handlers for YouTube Analyzer.
Handles export to JSON, CSV, Markdown, and visualizations.
"""

import logging
import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class OutputManager:
    """Manages all output generation."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize output manager.
        
        Args:
            output_dir: Directory to save outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    def export_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Export data to JSON.
        
        Args:
            data: Dictionary to export
            filename: Output filename (without extension)
            
        Returns:
            Path to created file
        """
        if filename is None:
            filename = f"analysis_{self.timestamp}"
        
        filepath = self.output_dir / f"{filename}.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"JSON exported to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            return ""
    
    def export_csv(self, videos: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Export video data to CSV.
        
        Args:
            videos: List of video data
            filename: Output filename (without extension)
            
        Returns:
            Path to created file
        """
        if filename is None:
            filename = f"videos_{self.timestamp}"
        
        filepath = self.output_dir / f"{filename}.csv"
        
        try:
            if not videos:
                logger.warning("No videos to export")
                return ""
            
            # Flatten nested data
            flattened = []
            for video in videos:
                # Safely get numeric values with None handling
                duration_seconds = video.get("duration_seconds")
                try:
                    duration_minutes = round(float(duration_seconds) / 60, 2) if duration_seconds else 0
                except (ValueError, TypeError):
                    duration_minutes = 0
                
                view_count = video.get("view_count")
                like_count = video.get("like_count")
                comment_count = video.get("comment_count")
                
                # Convert to numbers safely
                try:
                    views = int(view_count) if view_count is not None and view_count != '' else 0
                except (ValueError, TypeError):
                    views = 0
                
                try:
                    likes = int(like_count) if like_count is not None and like_count != '' else 0
                except (ValueError, TypeError):
                    likes = 0
                
                try:
                    comments = int(comment_count) if comment_count is not None and comment_count != '' else 0
                except (ValueError, TypeError):
                    comments = 0
                
                # Calculate ratios safely (avoid division by zero)
                like_ratio = round((likes / views) * 100, 2) if views > 0 else 0
                comment_ratio = round((comments / views) * 100, 4) if views > 0 else 0
                
                flat = {
                    "id": video.get("id"),
                    "title": video.get("title"),
                    "channel_name": video.get("channel_name"),
                    "upload_date": video.get("upload_date"),
                    "duration_minutes": duration_minutes,
                    "view_count": views,
                    "like_count": likes,
                    "comment_count": comments,
                    "like_ratio_percent": like_ratio,
                    "comment_ratio_percent": comment_ratio,
                    "video_url": f"https://youtube.com/watch?v={video.get('id')}"
                }
                flattened.append(flat)
            
            df = pd.DataFrame(flattened)
            df = df.sort_values("view_count", ascending=False)
            
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"CSV exported to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return ""
    
    def export_markdown_report(self, analysis: Dict[str, Any], blueprint: Dict[str, Any], 
                             videos: List[Dict[str, Any]], niche: str, filename: str = None) -> str:
        """
        Export comprehensive markdown report.
        
        Args:
            analysis: Analysis results
            blueprint: Blueprint data
            videos: Video data
            niche: Niche name
            filename: Output filename (without extension)
            
        Returns:
            Path to created file
        """
        if filename is None:
            filename = f"report_{niche.replace(' ', '_')}_{self.timestamp}"
        
        filepath = self.output_dir / f"{filename}.md"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Header
                f.write(f"# YouTube Niche Analyzer Report\n\n")
                f.write(f"**Niche:** {niche}\n\n")
                f.write(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
                f.write(f"**Videos Analyzed:** {len(videos)}\n\n")
                f.write("---\n\n")
                
                # Executive Summary
                f.write("## Executive Summary\n\n")
                metadata = analysis.get("metadata", {})
                f.write(f"This report analyzes {metadata.get('total_videos_analyzed', 0)} videos ")
                f.write(f"across {metadata.get('unique_channels', 0)} channels in the {niche} niche.\n\n")
                
                # Video Strategy
                f.write("## Recommended Video Strategy\n\n")
                strategy = blueprint.get("video_strategy", {})
                f.write(f"### Optimal Length\n{strategy.get('optimal_video_length', 'N/A')}\n\n")
                f.write(f"**Reasoning:** {strategy.get('length_reasoning', 'N/A')}\n\n")
                f.write(f"### Upload Schedule\n")
                f.write(f"- **Frequency:** {strategy.get('recommended_upload_frequency', 'N/A')}\n")
                f.write(f"- **Best Day:** {strategy.get('best_upload_day', 'N/A')}\n")
                f.write(f"- **Best Time:** {strategy.get('best_upload_time', 'N/A')}\n\n")
                
                f.write(f"### Title Strategy\n")
                f.write(f"{strategy.get('recommended_title_style', 'N/A')}\n\n")
                f.write(f"**Title Recommendations:**\n")
                for tip in strategy.get('title_recommendations', []):
                    f.write(f"- {tip}\n")
                f.write("\n")
                
                # Content Ideas
                f.write("## Top 5 Content Ideas\n\n")
                content_ideas = blueprint.get("content_ideas", [])
                # Ensure content_ideas is a list of dicts
                if isinstance(content_ideas, list):
                    for idea in content_ideas:
                        if isinstance(idea, dict):
                            f.write(f"### Idea #{idea.get('rank', 0)}: {idea.get('title', '')}\n\n")
                            f.write(f"**Type:** {idea.get('type', '')}\n\n")
                            f.write(f"**Rationale:** {idea.get('rationale', '')}\n\n")
                            f.write(f"**Recommended Length:** {idea.get('recommended_length', '')}\n\n")
                            f.write(f"**Title Options:**\n")
                            title_options = idea.get('title_options', [])
                            if isinstance(title_options, list):
                                for title_opt in title_options:
                                    f.write(f"- {title_opt}\n")
                            f.write(f"\n**Hook Strategy:** {idea.get('hook_strategy', '')}\n\n")
                            f.write(f"**Estimated Views:** {idea.get('estimated_views', '')}\n\n")
                            f.write("---\n\n")
                        elif isinstance(idea, str):
                            f.write(f"- {idea}\n\n")
                
                # What Works
                f.write("## What Works in This Niche\n\n")
                works = blueprint.get("what_works", {})
                if not isinstance(works, dict):
                    works = {}
                
                f.write("### Top Engagement Drivers\n")
                engagement_drivers = works.get("top_engagement_drivers", [])
                if isinstance(engagement_drivers, list):
                    for item in engagement_drivers:
                        f.write(f"- {item}\n")
                f.write("\n")
                
                f.write("### Top Title Formulas\n")
                title_formulas = works.get("top_title_formulas", [])
                if isinstance(title_formulas, list):
                    for item in title_formulas:
                        f.write(f"- {item}\n")
                f.write("\n")
                
                f.write("### Best Content Structures\n")
                content_structures = works.get("top_content_structures", [])
                if isinstance(content_structures, list):
                    for item in content_structures:
                        f.write(f"- {item}\n")
                f.write("\n")
                
                # What Doesn't Work
                f.write("## What Doesn't Work - Avoid These Mistakes\n\n")
                doesnt_work = blueprint.get("what_doesnt_work", {})
                if not isinstance(doesnt_work, dict):
                    doesnt_work = {}
                
                f.write("### Engagement Killers\n")
                engagement_killers = doesnt_work.get("engagement_killers", [])
                if isinstance(engagement_killers, list):
                    for item in engagement_killers:
                        f.write(f"- {item}\n")
                f.write("\n")
                
                f.write("### Common Creator Mistakes\n")
                creator_mistakes = doesnt_work.get("common_creator_mistakes", [])
                if isinstance(creator_mistakes, list):
                    for item in creator_mistakes:
                        f.write(f"- {item}\n")
                f.write("\n")
                
                # Competitive Positioning
                f.write("## Competitive Positioning\n\n")
                positioning = blueprint.get("competitive_positioning", {})
                if not isinstance(positioning, dict):
                    positioning = {}
                
                saturation_level = positioning.get('market_saturation_level', 'N/A')
                f.write(f"**Market Saturation:** {saturation_level}\n\n")
                
                saturation_interp = positioning.get('saturation_interpretation', {})
                if isinstance(saturation_interp, dict):
                    interp_text = saturation_interp.get(saturation_level, '')
                else:
                    interp_text = str(saturation_interp) if saturation_interp else ''
                f.write(f"**Interpretation:** {interp_text}\n\n")
                
                f.write("### Differentiation Strategies\n")
                diff_strategies = positioning.get('differentiation_strategies', [])
                if isinstance(diff_strategies, list):
                    for strategy_item in diff_strategies:
                        f.write(f"- {strategy_item}\n")
                f.write("\n")
                
                # Growth Roadmap
                f.write("## 12-Month Growth Roadmap\n\n")
                roadmap = blueprint.get("growth_roadmap", {})
                if not isinstance(roadmap, dict):
                    roadmap = {}

                niche_context = roadmap.get("niche_context", "")
                if niche_context:
                    f.write(f"> {niche_context}\n\n")

                for phase_name in ["phase_1_foundation", "phase_2_scaling", "phase_3_monetization"]:
                    phase_data = roadmap.get(phase_name, {})
                    if not isinstance(phase_data, dict):
                        phase_data = {}
                    phase_title = phase_name.replace("phase_", "").replace("_", " ").title()
                    
                    f.write(f"### {phase_title}\n\n")
                    f.write(f"**Duration:** {phase_data.get('duration', 'N/A')}\n")
                    f.write(f"**Goal:** {phase_data.get('goal', 'N/A')}\n\n")
                    f.write("**Key Focus Areas:**\n")
                    focus_areas = phase_data.get('focus_areas', [])
                    if isinstance(focus_areas, list):
                        for focus in focus_areas:
                            f.write(f"- {focus}\n")

                    key_topics = phase_data.get('key_topics', [])
                    if key_topics:
                        f.write("\n**Key Topics:**\n")
                        for topic in key_topics:
                            f.write(f"- {topic}\n")

                    metrics = phase_data.get('metrics_to_track', [])
                    if metrics:
                        f.write("\n**Metrics to Track:**\n")
                        for metric in metrics:
                            f.write(f"- {metric}\n")

                    f.write(f"\n**Success Criteria:** {phase_data.get('success_criteria', 'N/A')}\n\n")
                
                # Analysis Data
                f.write("## Detailed Analysis\n\n")
                
                # Content Strategy
                f.write("### Content Strategy Analysis\n\n")
                content_strat = analysis.get("content_strategy", {})
                
                f.write("#### Video Length Distribution\n")
                video_len = content_strat.get("video_lengths", {}).get("distribution", {})
                f.write(f"- **Short Form (<10 min):** {video_len.get('short_form_10min_or_less', {}).get('percentage', 0)}%\n")
                f.write(f"- **Medium Form (10-20 min):** {video_len.get('medium_form_10_20min', {}).get('percentage', 0)}%\n")
                f.write(f"- **Long Form (20+ min):** {video_len.get('long_form_20min_plus', {}).get('percentage', 0)}%\n\n")
                
                # Engagement
                f.write("### Engagement Metrics\n\n")
                engagement = analysis.get("engagement", {}).get("engagement_analysis", {})
                benchmarks = engagement.get("engagement_benchmarks", {})

                avg_views = engagement.get('average_views_per_video', 0)
                median_views = engagement.get('median_views', 0)

                f.write(f"- **Median Views per Video:** {median_views:,.0f}\n")
                f.write(f"- **Average Views per Video:** {avg_views:,.0f}")
                if avg_views > 0 and median_views > 0 and avg_views > median_views * 3:
                    f.write(f" *(skewed by viral outliers — median is more representative)*")
                f.write("\n")

                view_dist = engagement.get("view_distribution", {})
                if view_dist:
                    f.write("\n**View Distribution:**\n")
                    f.write(f"- Under 1K views: {view_dist.get('0_1k', 0)} videos\n")
                    f.write(f"- 1K - 10K views: {view_dist.get('1k_10k', 0)} videos\n")
                    f.write(f"- 10K - 100K views: {view_dist.get('10k_100k', 0)} videos\n")
                    f.write(f"- 100K - 1M views: {view_dist.get('100k_1m', 0)} videos\n")
                    f.write(f"- 1M+ views: {view_dist.get('1m_plus', 0)} videos\n")
                f.write("\n")

                f.write("**Engagement Rates:**\n")
                f.write(f"- Like Ratio: {benchmarks.get('average_like_ratio_percent', 0)}% avg / {benchmarks.get('median_like_ratio', 0)}% median\n")
                f.write(f"- Comment Ratio: {benchmarks.get('average_comment_ratio_percent', 0)}% avg / {benchmarks.get('median_comment_ratio', 0)}% median\n")
                f.write(f"- Total Engagement Rate: {benchmarks.get('average_engagement_rate_percent', 0)}%\n\n")
                
                # Competition
                f.write("### Market Competition\n\n")
                competition_data = analysis.get("competition", {})
                if not isinstance(competition_data, dict):
                    competition_data = {}
                competition = competition_data.get("competitive_landscape", {})
                if not isinstance(competition, dict):
                    competition = {}
                    
                f.write(f"- **Unique Channels:** {competition.get('market_saturation', 'N/A')}\n")
                
                market_concentration = competition.get('market_concentration', {})
                if not isinstance(market_concentration, dict):
                    market_concentration = {}
                f.write(f"- **Top 10 Channel Share:** {market_concentration.get('top_10_channel_share_percent', 0)}%\n\n")
                
                f.write("**Top Channels in Niche:**\n")
                top_channels = competition.get('top_channels', [])
                if isinstance(top_channels, list):
                    for channel in top_channels[:5]:
                        if isinstance(channel, dict):
                            f.write(f"- {channel.get('name', 'Unknown')}: {channel.get('videos_in_niche', 0)} videos\n")
                        elif isinstance(channel, str):
                            f.write(f"- {channel}\n")
                f.write("\n")
                
                # Footer
                f.write("---\n\n")
                f.write("*Report generated by YouTube Niche Analyzer*\n")
            
            logger.info(f"Markdown report exported to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error exporting markdown: {e}")
            return ""
    
    def generate_visualizations(self, analysis: Dict[str, Any], videos: List[Dict[str, Any]], 
                              niche: str) -> List[str]:
        """
        Generate matplotlib and plotly visualizations.
        
        Args:
            analysis: Analysis results
            videos: Video data
            niche: Niche name
            
        Returns:
            List of created visualization filepaths
        """
        logger.info("Generating visualizations...")
        
        created_files = []
        
        try:
            # 1. View Distribution Pie Chart
            engagement = analysis.get("engagement", {}).get("engagement_analysis", {})
            view_dist = engagement.get("view_distribution", {})
            
            if view_dist:
                fig = go.Figure(data=[go.Pie(
                    labels=["<1K", "1K-10K", "10K-100K", "100K-1M", "1M+"],
                    values=[
                        view_dist.get("0_1k", 0),
                        view_dist.get("1k_10k", 0),
                        view_dist.get("10k_100k", 0),
                        view_dist.get("100k_1m", 0),
                        view_dist.get("1m_plus", 0)
                    ]
                )])
                fig.update_layout(title=f"View Count Distribution - {niche}")
                
                filepath = self.output_dir / f"view_distribution_{self.timestamp}.html"
                fig.write_html(str(filepath))
                created_files.append(str(filepath))
                logger.info(f"View distribution chart created")
        except Exception as e:
            logger.warning(f"Could not create view distribution chart: {e}")
        
        try:
            # 2. Engagement Metrics Box Plot
            video_data = []
            for video in videos:
                views = video.get("view_count", 0)
                if views > 0:
                    video_data.append({
                        "Title": video.get("title", "Unknown")[:50],
                        "Like Ratio %": (video.get("like_count", 0) / views) * 100,
                        "Comment Ratio %": (video.get("comment_count", 0) / views) * 100,
                    })
            
            if video_data:
                df = pd.DataFrame(video_data)
                
                fig = make_subplots(rows=1, cols=2, 
                                   subplot_titles=("Like Ratio Distribution", "Comment Ratio Distribution"))
                
                fig.add_trace(
                    go.Box(y=df["Like Ratio %"], name="Like Ratio %"),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Box(y=df["Comment Ratio %"], name="Comment Ratio %"),
                    row=1, col=2
                )
                
                fig.update_layout(title=f"Engagement Ratios - {niche}", height=400)
                
                filepath = self.output_dir / f"engagement_distribution_{self.timestamp}.html"
                fig.write_html(str(filepath))
                created_files.append(str(filepath))
                logger.info(f"Engagement distribution chart created")
        except Exception as e:
            logger.warning(f"Could not create engagement distribution chart: {e}")
        
        try:
            # 3. Upload Frequency Timeline
            upload_patterns = analysis.get("content_strategy", {}).get("upload_patterns", {})
            days = upload_patterns.get("day_distribution", {})
            
            if days:
                fig = go.Figure(data=[
                    go.Bar(x=list(days.keys()), y=list(days.values()))
                ])
                fig.update_layout(
                    title=f"Video Upload Distribution by Day - {niche}",
                    xaxis_title="Day of Week",
                    yaxis_title="Number of Videos"
                )
                
                filepath = self.output_dir / f"upload_patterns_{self.timestamp}.html"
                fig.write_html(str(filepath))
                created_files.append(str(filepath))
                logger.info(f"Upload patterns chart created")
        except Exception as e:
            logger.warning(f"Could not create upload patterns chart: {e}")
        
        try:
            # 4. Content Strategy Summary (matplotlib)
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle(f"Content Strategy Overview - {niche}", fontsize=16, fontweight='bold')
            
            # Length distribution
            content_strat = analysis.get("content_strategy", {})
            video_len = content_strat.get("video_lengths", {}).get("distribution", {})
            
            if video_len:
                ax = axes[0, 0]
                lengths = ["Short\n(<10m)", "Medium\n(10-20m)", "Long\n(>20m)"]
                values = [
                    video_len.get("short_form_10min_or_less", {}).get("percentage", 0),
                    video_len.get("medium_form_10_20min", {}).get("percentage", 0),
                    video_len.get("long_form_20min_plus", {}).get("percentage", 0)
                ]
                ax.bar(lengths, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
                ax.set_ylabel("Percentage (%)")
                ax.set_title("Video Length Distribution")
                ax.set_ylim(0, 100)
            
            # Title patterns
            title_analysis = content_strat.get("title_analysis", {})
            patterns = title_analysis.get("patterns", {})
            
            if patterns:
                ax = axes[0, 1]
                pattern_names = ["Questions", "Numbers", "Brackets", "Colons"]
                pattern_values = [
                    patterns.get("question_mark_titles", {}).get("percentage", 0),
                    patterns.get("number_titles", {}).get("percentage", 0),
                    patterns.get("bracket_titles", {}).get("percentage", 0),
                    patterns.get("colon_titles", {}).get("percentage", 0)
                ]
                ax.bar(pattern_names, pattern_values, color=['#95E1D3', '#F38181', '#FECEA8', '#AA96DA'])
                ax.set_ylabel("Percentage (%)")
                ax.set_title("Title Pattern Usage")
                ax.tick_params(axis='x', rotation=45)
            
            # Engagement benchmarks
            engagement = analysis.get("engagement", {}).get("engagement_analysis", {})
            benchmarks = engagement.get("engagement_benchmarks", {})
            
            if benchmarks:
                ax = axes[1, 0]
                engagement_metrics = ["Like\nRatio", "Comment\nRatio", "Total\nEngagement"]
                engagement_values = [
                    benchmarks.get("average_like_ratio_percent", 0),
                    benchmarks.get("average_comment_ratio_percent", 0) * 100,  # Scale up for visibility
                    benchmarks.get("average_engagement_rate_percent", 0)
                ]
                ax.bar(engagement_metrics, engagement_values, color=['#FF9999', '#66B2FF', '#99FF99'])
                ax.set_ylabel("Percentage (%)")
                ax.set_title("Average Engagement Metrics")
            
            # Competition summary
            competition = analysis.get("competition", {}).get("competitive_landscape", {})
            ax = axes[1, 1]
            ax.axis('off')
            
            saturation = competition.get("market_saturation", "Medium")
            concentration = competition.get("market_concentration", {}).get("concentration_level", "Unknown")
            
            info_text = f"""
Market Saturation: {saturation}
Market Concentration: {concentration}
Unique Channels: {competition.get('total_unique_channels', 'N/A')}
Top Channel Share: {competition.get('market_concentration', {}).get('top_10_channel_share_percent', 0)}%
            """
            ax.text(0.1, 0.5, info_text, fontsize=12, verticalalignment='center',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            
            filepath = self.output_dir / f"strategy_overview_{self.timestamp}.png"
            plt.savefig(filepath, dpi=100, bbox_inches='tight')
            plt.close()
            
            created_files.append(str(filepath))
            logger.info(f"Strategy overview chart created")
        except Exception as e:
            logger.warning(f"Could not create strategy overview chart: {e}")
        
        return created_files
