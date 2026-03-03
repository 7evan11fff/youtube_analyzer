"""
YouTube Niche Analyzer

A comprehensive Python application that analyzes YouTube niches and generates
strategic content blueprints based on data-driven insights.

Example:
    Basic usage from command line::

        python main.py "AI tutorials" --videos 50

    Or use as a module::

        from youtube_analyzer import NicheDataCollector
        from analysis import ComprehensiveAnalyzer
        from blueprint_generator import BlueprintOrchestrator

        collector = NicheDataCollector(api_key="your_key")
        videos = collector.collect_niche_data("AI tutorials", num_videos=50)

        analyzer = ComprehensiveAnalyzer()
        analysis = analyzer.analyze_niche(videos)

        orchestrator = BlueprintOrchestrator()
        blueprint = orchestrator.generate_complete_blueprint(analysis, "AI tutorials")

Modules:
    youtube_analyzer: YouTube API integration and data collection
    analysis: Deep analysis of video data
    blueprint_generator: Content strategy blueprint generation
    output: Report generation and visualizations
    database: SQLite caching layer
    config: Configuration management
    utils: Utility functions

Version: 1.0.0
"""

__title__ = "YouTube Niche Analyzer"
__description__ = "Analyze YouTube niches and generate content strategy blueprints"
__version__ = "1.0.0"
__author__ = "YouTube Creator Analytics"
__license__ = "MIT"

from youtube_analyzer import NicheDataCollector, YouTubeAPIClient
from analysis import ComprehensiveAnalyzer
from blueprint_generator import BlueprintOrchestrator
from output import OutputManager
from database import get_db

__all__ = [
    "NicheDataCollector",
    "YouTubeAPIClient",
    "ComprehensiveAnalyzer",
    "BlueprintOrchestrator",
    "OutputManager",
    "get_db"
]
