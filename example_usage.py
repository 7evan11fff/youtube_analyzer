"""
Example usage of YouTube Niche Analyzer as a Python module.

This script demonstrates how to use the analyzer programmatically
instead of via command line.
"""

import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from youtube_analyzer import NicheDataCollector
from analysis import ComprehensiveAnalyzer
from blueprint_generator import BlueprintOrchestrator
from output import OutputManager


def example_1_basic_analysis():
    """
    Example 1: Basic analysis with default settings.
    """
    print("\n" + "="*60)
    print("Example 1: Basic Niche Analysis")
    print("="*60 + "\n")
    
    niche = "Python programming"
    
    # Step 1: Collect data
    print(f"Collecting data for: {niche}")
    collector = NicheDataCollector()  # Uses API key from .env if available
    videos = collector.collect_niche_data(niche, num_videos=50)
    
    if not videos:
        print("No videos found!")
        return
    
    print(f"Collected {len(videos)} videos\n")
    
    # Step 2: Analyze
    print("Analyzing niche...")
    analyzer = ComprehensiveAnalyzer()
    analysis = analyzer.analyze_niche(videos)
    print("Analysis complete\n")
    
    # Step 3: Generate blueprint
    print("Generating content blueprint...")
    orchestrator = BlueprintOrchestrator()
    blueprint = orchestrator.generate_complete_blueprint(analysis, niche)
    print("Blueprint complete\n")
    
    # Step 4: Export
    print("Exporting results...")
    output_mgr = OutputManager(output_dir="output/example1")
    
    output_mgr.export_json({
        "analysis": analysis,
        "blueprint": blueprint
    }, filename="complete_analysis")
    
    output_mgr.export_csv(videos)
    output_mgr.export_markdown_report(analysis, blueprint, videos, niche)
    output_mgr.generate_visualizations(analysis, videos, niche)
    
    print("\n✓ Analysis saved to output/example1/")
    
    # Display summary
    print("\nKey Findings:")
    engagement = analysis.get("engagement", {}).get("engagement_analysis", {})
    print(f"  Average views per video: {engagement.get('average_views_per_video', 'N/A'):,.0f}")
    
    strategy = blueprint.get("video_strategy", {})
    print(f"  Optimal length: {strategy.get('optimal_video_length', 'N/A')}")
    print(f"  Best upload day: {strategy.get('best_upload_day', 'N/A')}")


def example_2_custom_api_key():
    """
    Example 2: Using custom API key.
    """
    print("\n" + "="*60)
    print("Example 2: Analysis with Custom API Key")
    print("="*60 + "\n")
    
    # Replace with your actual API key
    api_key = "YOUR_YOUTUBE_API_KEY_HERE"
    
    if api_key == "YOUR_YOUTUBE_API_KEY_HERE":
        print("⚠️  Please set your API key first!")
        print("Update the api_key variable with your YouTube API key.")
        return
    
    niche = "Machine Learning"
    
    collector = NicheDataCollector(api_key=api_key)
    videos = collector.collect_niche_data(niche, num_videos=50)
    
    print(f"✓ Collected {len(videos)} videos")
    print(f"✓ First video: {videos[0].get('title', 'N/A')[:50]}")


def example_3_analyze_multiple_niches():
    """
    Example 3: Analyze and compare multiple niches.
    """
    print("\n" + "="*60)
    print("Example 3: Comparing Multiple Niches")
    print("="*60 + "\n")
    
    niches = [
        "web development",
        "app development",
        "game development"
    ]
    
    results = {}
    collector = NicheDataCollector()
    analyzer = ComprehensiveAnalyzer()
    
    for niche in niches:
        print(f"Analyzing: {niche}...")
        
        videos = collector.collect_niche_data(niche, num_videos=30)
        if videos:
            analysis = analyzer.analyze_niche(videos)
            results[niche] = {
                "video_count": len(videos),
                "avg_views": analysis.get("engagement", {}).get("engagement_analysis", {}).get("average_views_per_video", 0),
                "engagement_rate": analysis.get("engagement", {}).get("engagement_analysis", {}).get("engagement_benchmarks", {}).get("average_engagement_rate_percent", 0)
            }
    
    print("\nComparison Results:")
    print("-" * 60)
    for niche, data in results.items():
        print(f"\n{niche.upper()}")
        print(f"  Videos analyzed: {data['video_count']}")
        print(f"  Average views: {data['avg_views']:,.0f}")
        print(f"  Engagement rate: {data['engagement_rate']:.3f}%")


def example_4_detailed_analysis():
    """
    Example 4: In-depth analysis with custom processing.
    """
    print("\n" + "="*60)
    print("Example 4: Detailed Analysis with Custom Processing")
    print("="*60 + "\n")
    
    niche = "Data Science"
    
    collector = NicheDataCollector()
    videos = collector.collect_niche_data(niche, num_videos=50)
    
    if not videos:
        print("No videos found!")
        return
    
    # Custom data processing
    print("Custom Analysis:")
    print("-" * 60)
    
    # Calculate engagement stats
    total_views = sum(v.get("view_count", 0) for v in videos)
    total_likes = sum(v.get("like_count", 0) for v in videos)
    total_comments = sum(v.get("comment_count", 0) for v in videos)
    
    print(f"\nOverall Statistics:")
    print(f"  Total views: {total_views:,}")
    print(f"  Total likes: {total_likes:,}")
    print(f"  Total comments: {total_comments:,}")
    
    if total_views > 0:
        print(f"  Overall like ratio: {(total_likes/total_views)*100:.2f}%")
        print(f"  Overall comment ratio: {(total_comments/total_views)*100:.4f}%")
    
    # Top videos
    print(f"\nTop 5 Videos by Views:")
    top_videos = sorted(videos, key=lambda v: v.get("view_count", 0), reverse=True)[:5]
    
    for i, video in enumerate(top_videos, 1):
        title = video.get("title", "Unknown")[:60]
        views = video.get("view_count", 0)
        channel = video.get("channel_name", "Unknown")
        print(f"  {i}. {title}")
        print(f"     Channel: {channel} | Views: {views:,}")
    
    # Full analysis
    print("\nRunning full analysis...")
    analyzer = ComprehensiveAnalyzer()
    analysis = analyzer.analyze_niche(videos)
    
    output_mgr = OutputManager(output_dir="output/example4")
    output_mgr.export_json(analysis, filename="detailed_analysis")
    print("✓ Exported to output/example4/")


def example_5_export_only():
    """
    Example 5: Load cached data and export in different formats.
    """
    print("\n" + "="*60)
    print("Example 5: Export Cached Data")
    print("="*60 + "\n")
    
    from database import get_db
    
    niche = "Python programming"
    
    # Get cached videos
    db = get_db()
    videos = db.get_videos_by_niche(niche)
    
    if not videos:
        print(f"No cached data for: {niche}")
        print("Run an analysis first to cache data.")
        return
    
    print(f"Found {len(videos)} cached videos\n")
    
    # Run analysis on cached data
    analyzer = ComprehensiveAnalyzer()
    analysis = analyzer.analyze_niche(videos)
    
    # Generate blueprint
    orchestrator = BlueprintOrchestrator()
    blueprint = orchestrator.generate_complete_blueprint(analysis, niche)
    
    # Export in multiple formats
    output_mgr = OutputManager(output_dir="output/example5")
    
    print("Exporting formats:")
    
    json_file = output_mgr.export_json({
        "analysis": analysis,
        "blueprint": blueprint
    })
    print(f"  ✓ JSON: {Path(json_file).name}")
    
    csv_file = output_mgr.export_csv(videos)
    print(f"  ✓ CSV: {Path(csv_file).name}")
    
    md_file = output_mgr.export_markdown_report(analysis, blueprint, videos, niche)
    print(f"  ✓ Markdown: {Path(md_file).name}")
    
    viz_files = output_mgr.generate_visualizations(analysis, videos, niche)
    print(f"  ✓ Visualizations: {len(viz_files)} files")


if __name__ == "__main__":
    print("\n🎬 YouTube Niche Analyzer - Usage Examples\n")
    
    print("Available examples:")
    print("  1. Basic analysis")
    print("  2. Custom API key")
    print("  3. Compare multiple niches")
    print("  4. Detailed analysis with custom processing")
    print("  5. Export cached data")
    
    choice = input("\nChoose an example (1-5) or 'all' for all examples: ").strip()
    
    if choice == "1":
        example_1_basic_analysis()
    elif choice == "2":
        example_2_custom_api_key()
    elif choice == "3":
        example_3_analyze_multiple_niches()
    elif choice == "4":
        example_4_detailed_analysis()
    elif choice == "5":
        example_5_export_only()
    elif choice.lower() == "all":
        example_1_basic_analysis()
        example_3_analyze_multiple_niches()
        example_4_detailed_analysis()
        print("\n✓ Examples complete!")
    else:
        print("Invalid choice!")
