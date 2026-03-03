"""
YouTube Niche Analyzer - Main CLI/GUI Interface
Orchestrates the complete analysis pipeline from data collection to report generation.
Supports both command-line and graphical user interface modes.
"""

import sys
import logging
from pathlib import Path
from typing import Optional
import click
from datetime import datetime

from youtube_analyzer import NicheDataCollector
from analysis import ComprehensiveAnalyzer
from blueprint_generator import BlueprintOrchestrator
from output import OutputManager
from database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_analyzer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AnalysisProgressTracker:
    """Tracks and displays analysis progress."""
    
    def __init__(self):
        """Initialize progress tracker."""
        self.stages = [
            "Initializing",
            "Collecting video data",
            "Fetching detailed statistics",
            "Analyzing content strategy",
            "Analyzing engagement metrics",
            "Analyzing competition",
            "Analyzing growth patterns",
            "Generating content blueprint",
            "Creating visualizations",
            "Exporting results"
        ]
        self.current_stage = 0
    
    def next_stage(self, message: str = None):
        """Move to next stage."""
        if self.current_stage < len(self.stages):
            stage = self.stages[self.current_stage]
            status = f"✓ {stage}"
            if message:
                status += f" - {message}"
            click.echo(f"  {status}")
            self.current_stage += 1
    
    def print_header(self):
        """Print progress header."""
        click.echo("\n" + "="*60)
        click.echo("  YouTube Niche Analyzer - Analysis Pipeline")
        click.echo("="*60 + "\n")


@click.command()
@click.argument('niche', type=str)
@click.option('--videos', '-v', default=50, help='Number of videos to analyze (10-500)', type=int)
@click.option('--api-key', '-k', default=None, help='YouTube API key (or set YOUTUBE_API_KEY env var)')
@click.option('--output', '-o', default='output', help='Output directory for reports')
@click.option('--force-refresh', '-f', is_flag=True, help='Force refresh even if cached')
@click.option('--skip-visualizations', '-s', is_flag=True, help='Skip generating visualizations')
def analyze_niche(niche: str, videos: int, api_key: Optional[str], output: str, 
                 force_refresh: bool, skip_visualizations: bool):
    """
    Analyze a YouTube niche and generate content strategy blueprint.
    
    NICHE: The YouTube niche to analyze (e.g., "AI tutorials", "fitness", "cooking")
    
    Example:
        python main.py "AI tutorials" --videos 50
        python main.py "fitness motivation" -v 75 -o ./reports
    """
    
    tracker = AnalysisProgressTracker()
    tracker.print_header()
    
    try:
        # Validate input
        if not niche or len(niche.strip()) == 0:
            click.echo("❌ Error: Niche cannot be empty")
            sys.exit(1)
        
        if videos < 10 or videos > 500:
            click.echo("❌ Error: Number of videos must be between 10 and 500")
            sys.exit(1)
        
        niche = niche.strip()
        
        click.echo(f"📊 Niche: {niche}")
        click.echo(f"📹 Videos to analyze: {videos}")
        click.echo(f"💾 Output directory: {output}\n")
        
        # Stage 1: Initialize
        tracker.next_stage()
        
        # Stage 2: Collect data
        tracker.next_stage()
        click.echo(f"  Searching for videos and fetching metadata...")
        
        collector = NicheDataCollector(api_key=api_key)
        video_data = collector.collect_niche_data(niche, num_videos=videos, force_refresh=force_refresh)
        
        if not video_data:
            click.echo("❌ Error: Could not collect any video data. Check your niche name and API key.")
            sys.exit(1)
        
        click.echo(f"  Found and enriched {len(video_data)} videos")
        
        # Stage 3: Analysis
        tracker.next_stage("Running comprehensive analysis")
        
        analyzer = ComprehensiveAnalyzer()
        analysis_results = analyzer.analyze_niche(video_data)
        
        # Cache analysis results
        db = get_db()
        db.cache_niche_analysis(niche, analysis_results, len(video_data))
        
        tracker.next_stage()
        tracker.next_stage()
        tracker.next_stage()
        tracker.next_stage()
        
        # Stage 8: Generate blueprint
        tracker.next_stage("Generating content strategy blueprint")
        
        orchestrator = BlueprintOrchestrator()
        blueprint = orchestrator.generate_complete_blueprint(analysis_results, niche)
        
        # Stage 9: Visualizations
        tracker.next_stage()
        output_manager = OutputManager(output_dir=output)
        
        visualization_files = []
        if not skip_visualizations:
            visualization_files = output_manager.generate_visualizations(analysis_results, video_data, niche)
            click.echo(f"  Created {len(visualization_files)} visualizations")
        else:
            click.echo("  Skipped visualization generation")
        
        # Stage 10: Export
        tracker.next_stage("Exporting reports in multiple formats")
        
        # Export all formats
        json_file = output_manager.export_json(
            {
                "analysis": analysis_results,
                "blueprint": blueprint,
                "metadata": {
                    "niche": niche,
                    "total_videos": len(video_data),
                    "generated_at": datetime.utcnow().isoformat()
                }
            },
            filename=f"complete_analysis_{niche.replace(' ', '_')}"
        )
        
        csv_file = output_manager.export_csv(video_data, filename=f"videos_{niche.replace(' ', '_')}")
        
        markdown_file = output_manager.export_markdown_report(
            analysis_results, blueprint, video_data, niche
        )
        
        click.echo(f"  Exported JSON, CSV, and Markdown reports")
        
        # Summary
        click.echo("\n" + "="*60)
        click.echo("  ✅ Analysis Complete!")
        click.echo("="*60 + "\n")
        
        click.echo("📄 Generated Files:")
        click.echo(f"  📊 Analysis Data:    {json_file}")
        click.echo(f"  📋 Video CSV:        {csv_file}")
        click.echo(f"  📝 Markdown Report:  {markdown_file}")
        
        if visualization_files:
            click.echo(f"  📈 Visualizations:   {len(visualization_files)} charts created")
        
        click.echo(f"\n💡 Key Findings:")
        
        # Extract key metrics
        metadata = analysis_results.get("metadata", {})
        engagement = analysis_results.get("engagement", {}).get("engagement_analysis", {})
        content_strat = analysis_results.get("content_strategy", {})
        competition = analysis_results.get("competition", {}).get("competitive_landscape", {})
        
        click.echo(f"  • Unique channels analyzed: {metadata.get('unique_channels', 'N/A')}")
        click.echo(f"  • Average views per video: {engagement.get('average_views_per_video', 'N/A'):,.0f}")
        click.echo(f"  • Market saturation: {competition.get('market_saturation', 'Unknown')}")
        
        video_len = content_strat.get("video_lengths", {}).get("distribution", {})
        if video_len:
            dominant_format = max(
                ("Short", video_len.get("short_form_10min_or_less", {}).get("percentage", 0)),
                ("Medium", video_len.get("medium_form_10_20min", {}).get("percentage", 0)),
                ("Long", video_len.get("long_form_20min_plus", {}).get("percentage", 0)),
                key=lambda x: x[1]
            )
            click.echo(f"  • Dominant format: {dominant_format[0]}-form videos ({dominant_format[1]}%)")
        
        # Strategy recommendations
        strategy = blueprint.get("video_strategy", {})
        click.echo(f"\n🎬 Quick Strategy:")
        click.echo(f"  • Length: {strategy.get('optimal_video_length', 'N/A')}")
        click.echo(f"  • Frequency: {strategy.get('recommended_upload_frequency', 'N/A')}")
        click.echo(f"  • Upload Day: {strategy.get('best_upload_day', 'N/A')} @ {strategy.get('best_upload_time', 'N/A')}")
        
        click.echo("\n" + "="*60)
        click.echo("  Open the Markdown report to see detailed recommendations!")
        click.echo("="*60 + "\n")
        
        logger.info(f"Analysis complete for niche: {niche}")
    
    except KeyboardInterrupt:
        click.echo("\n⚠️  Analysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error during analysis: {e}")
        click.echo(f"\n❌ Error: {str(e)}")
        click.echo("\nFor more details, check youtube_analyzer.log")
        sys.exit(1)


@click.command()
@click.argument('niche', type=str, required=False)
def list_cached(niche: Optional[str]):
    """List cached analysis results."""
    db = get_db()
    
    if niche:
        videos = db.get_videos_by_niche(niche)
        click.echo(f"\n{niche}: {len(videos)} cached videos")
    else:
        click.echo("\n📚 Cached Analysis Results:")
        # This would need a method to list all niches, placeholder for now
        click.echo("  Use 'youtube_analyzer analyze <niche>' to start an analysis")


@click.command()
def gui():
    """Launch the graphical user interface."""
    click.echo("🎬 Launching YouTube Niche Analyzer GUI...")
    try:
        from gui import launch_gui
        launch_gui()
    except ImportError as e:
        click.echo(f"\n❌ Error: Could not import GUI module.")
        click.echo(f"   Make sure customtkinter is installed: pip install customtkinter")
        click.echo(f"   Error details: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error launching GUI: {e}")
        sys.exit(1)


@click.group()
def cli():
    """YouTube Niche Analyzer - Analyze YouTube niches and generate content strategies.
    
    \b
    Available Commands:
      analyze  - Run analysis from command line
      gui      - Launch the graphical user interface
      cache    - View cached analysis results
    
    \b
    Examples:
      python main.py analyze "AI tutorials" --videos 50
      python main.py gui
    """
    pass


# Add commands
cli.add_command(analyze_niche, name='analyze')
cli.add_command(list_cached, name='cache')
cli.add_command(gui, name='gui')


if __name__ == '__main__':
    # If no arguments provided, show help or launch GUI by default
    if len(sys.argv) == 1:
        # Default to GUI mode when run without arguments
        try:
            from gui import launch_gui
            print("Launching YouTube Niche Analyzer GUI...")
            print("(Use 'python main.py --help' for CLI options)")
            launch_gui()
        except ImportError:
            # If GUI dependencies not available, show CLI help
            cli(['--help'])
    else:
        cli()
