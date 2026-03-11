# YouTube Niche Analyzer

A comprehensive Python application that analyzes YouTube niches and generates strategic content blueprints. This tool collects video data from any YouTube niche, performs deep analysis across multiple dimensions, and produces actionable recommendations for content creators.

## Features

✨ **Complete Niche Analysis**
- Video metadata collection (views, likes, comments, duration, etc.)
- Content strategy pattern detection
- Engagement metrics analysis
- Competitive landscape assessment
- Growth pattern identification
- Trending topic extraction

📊 **Data-Driven Insights**
- Optimal video length recommendations
- Upload timing analysis
- Title formula effectiveness
- Thumbnail strategy patterns
- Engagement benchmarks
- Market saturation analysis

🎬 **Content Blueprint Generation**
- Recommended video strategy with specific metrics
- Top 5 content ideas with detailed scoring
- "What works" and "What doesn't work" lists
- Competitive positioning strategies
- 12-month growth roadmap
- Differentiation opportunities

📈 **Multiple Output Formats**
- JSON export (programmatic access)
- CSV export (spreadsheet analysis)
- Markdown reports (human-readable)
- Interactive visualizations (Plotly)
- PNG charts (static images)

💾 **Smart Caching**
- SQLite database for video data persistence
- Analysis result caching
- Avoid re-fetching duplicate data
- Query historical data

## System Requirements

- **Python:** 3.11 or higher
- **Operating System:** Windows, macOS, or Linux
- **RAM:** 4GB minimum (8GB+ recommended)
- **Disk Space:** 1GB for database and outputs

## Installation

### 1. Clone or Download the Repository

```bash
cd youtube_analyzer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Google YouTube API client
- yt-dlp (for fallback scraping)
- pandas & numpy (data analysis)
- matplotlib & plotly (visualizations)
- NLTK (sentiment analysis)
- Click (CLI framework)
- And more...

### 3. Set Up YouTube API Key (Optional but Recommended)

For best results, get a YouTube API key:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create an "API key" credential
5. Create a `.env` file in the project root:

```bash
echo "YOUTUBE_API_KEY=your_api_key_here" > .env
```

**Note:** Without an API key, the tool will use fallback scraping (slower but still works).

### 4. Test Installation

```bash
python main.py --help
```

You should see the help menu.

## Tutorial: Your First Analysis

This walks you through a complete analysis from scratch.

### 1. Launch the App

```bash
cd youtube_analyzer
source venv/bin/activate   # activate virtual environment
python main.py             # opens the GUI
```

On your first launch you'll see a **welcome walkthrough** — it explains each tab and lets you enter a license key (if you have one). You can skip it and come back later.

### 2. Enter a Niche and Run

1. In the **Analyze** tab, type a niche in the text field, e.g. `cyber security`
2. Use the slider to pick how many videos to analyse (start with 50 for a quick test)
3. Click **Start Analysis**

The tool will:
- Search YouTube for videos matching your niche (using multiple search strategies)
- Collect view counts, like counts, durations, titles, and descriptions
- Run engagement, competition, and correlation analysis
- Generate a content strategy blueprint
- Export reports to the `output/` folder

### 3. View Your Dashboard

Once the analysis completes, switch to the **Dashboard** tab to see:
- **Metric cards** — median views, avg views, engagement rate, video count, channel count
- **View distribution pie chart** — how many videos fall into each view bracket
- **Video length vs views** — which video length performs best
- **Title pattern impact** — which title patterns (numbers, questions, how-to, etc.) boost or hurt views
- **Upload day analysis** — which days get the most views

### 4. Check Your Reports

Click the **Report** button in the Analyze tab (or open `output/` directly) to see:
- `report_*.md` — full markdown report with strategy, roadmap, and correlations
- `complete_analysis_*.json` — raw analysis data
- `videos_*.csv` — spreadsheet of all collected videos

### 5. Track Trends Over Time

Each analysis automatically saves a snapshot. Run the same niche again in a few days/weeks, then go to the **Trends** tab, enter the niche, and click **Load Trends** to see how metrics change over time with trend line charts.

### 6. Set Up Auto-Scrape (Pro)

In the **Settings** tab, add a niche to the auto-scrape scheduler with a custom interval (e.g. every 24 hours). Toggle the scheduler on, and it will automatically re-scrape and save snapshots in the background.

### License Keys

The app works without a license key (limited to 15 videos, markdown-only export). Enter a Free or Pro key in Settings or during the onboarding walkthrough to unlock more features. See the Help tab in the app for a full tier comparison.

---

## Quick Start (CLI)

### Basic Usage

Analyze a niche with default settings (50 videos):

```bash
python main.py "AI tutorials"
```

### With Custom Options

```bash
python main.py "fitness motivation" --videos 100 --output ./reports
```

### Using API Key from Environment

```bash
python main.py "cooking tutorials" --videos 75
```

### Force Refresh (Bypass Cache)

```bash
python main.py "crypto" --videos 50 --force-refresh
```

### Skip Visualizations (Faster)

```bash
python main.py "productivity" --videos 50 --skip-visualizations
```

## Command-Line Options

```
Usage: main.py [OPTIONS] NICHE

Options:
  -v, --videos INTEGER    Number of videos to analyze (10-500) [default: 50]
  -k, --api-key TEXT      YouTube API key (overrides env var)
  -o, --output PATH       Output directory for reports [default: output]
  -f, --force-refresh     Force refresh even if cached
  -s, --skip-visualizations  Skip generating visualizations
  --help                  Show this message and exit

Examples:
  python main.py "Python programming"
  python main.py "makeup tutorials" --videos 100
  python main.py "gaming" -v 75 -o ./my_reports -f
```

## Output Files

After running analysis, you'll find these files in the `output/` directory:

### 1. **complete_analysis_[niche].json**
Full analysis results in JSON format:
- All metrics and statistics
- Content strategy analysis
- Engagement benchmarks
- Competition data
- Growth patterns
- Blueprint recommendations

### 2. **videos_[niche].csv**
Spreadsheet-ready video data:
- Title, Channel, Upload Date
- View/Like/Comment counts
- Duration, Engagement ratios
- YouTube URLs

### 3. **report_[niche]_[timestamp].md**
Human-readable strategic report including:
- Executive summary
- Video strategy recommendations
- Top 5 content ideas with hooks
- What works/doesn't work analysis
- Competitive positioning
- 3-phase growth roadmap

### 4. Visualizations (HTML & PNG)
- `view_distribution_[timestamp].html` - View count distribution
- `engagement_distribution_[timestamp].html` - Like/comment ratios
- `upload_patterns_[timestamp].html` - Upload timing analysis
- `strategy_overview_[timestamp].png` - All metrics summary

## Analysis Sections Explained

### Content Strategy Analysis

**Video Length Distribution**
- Shows what format works best (short/medium/long form)
- Helps determine your target video length

**Upload Patterns**
- Best days and times to upload
- Upload frequency in the niche
- Helps optimize for algorithm

**Title Analysis**
- Common title patterns (questions, numbers, brackets)
- Most frequently used words
- Title length benchmarks

**Description Analysis**
- Call-to-action prevalence
- Link and timestamp usage
- Description length patterns

### Engagement Analysis

**Engagement Benchmarks**
- Average like ratio (likes per 1000 views)
- Average comment ratio (comments per 1000 views)
- Total engagement rate
- Compared to your niche standard

**View Distribution**
- How many videos reach different view thresholds
- Helps set realistic expectations

**Top Performing Videos**
- Videos with highest engagement
- Patterns in their titles/strategies

### Competitive Analysis

**Market Saturation**
- How many creators compete in niche
- Market concentration (top 10 dominance)
- Saturation level (Low/Medium/High)

**Content Gaps**
- Underexplored topics
- Low-frequency keywords
- Untapped angles

**Top Channels**
- Dominant creators in niche
- Their video count
- Market share

### Growth Pattern Analysis

**Growth Curves**
- How fast videos typically gain views
- By age (0-7 days, 8-30 days, etc.)
- Viral potential indicators

**Trending Topics**
- Most mentioned topics in recent videos
- Emerging vs. evergreen content balance

## Blueprint Generator Outputs

### Video Strategy
- Optimal video length with reasoning
- Recommended upload frequency
- Best days/times to post
- Title style recommendations
- Thumbnail guidance

### Top 5 Content Ideas

Each idea includes:
- **Title** - Descriptive name
- **Type** - Tutorial, Problem-solving, Comparison, etc.
- **Rationale** - Why this video will perform
- **Length** - Recommended duration
- **Title Options** - 3 specific title templates
- **Hook Strategy** - How to open the video
- **Estimated Views** - Expected performance range

### What Works (Proven Strategies)
- Top engagement drivers in this niche
- Thumbnail styles by performance
- Title formulas that work
- Content structures that convert
- Best practices from top creators

### What Doesn't Work (Anti-Patterns)
- Common mistakes to avoid
- Engagement killers
- Thumbnail red flags
- Creator mistakes
- Content structure problems

### Competitive Positioning
- Market saturation analysis
- Differentiation strategies
- Underexplored subtopics
- Partnership opportunities
- Unique positioning angles

### Growth Roadmap

**Phase 1: Foundation (Months 1-3)**
- 30-50 foundational videos
- Build audience base
- Optimize for algorithm
- Goal: 1,000 subscribers

**Phase 2: Scaling (Months 3-6)**
- Scale production quality
- Double down on what works
- Start collaborations
- Goal: 10,000 subscribers

**Phase 3: Monetization (Months 6-12)**
- Enable ad revenue
- Sponsorships & affiliates
- Digital products
- Goal: $500+/month revenue

## Configuration

Edit `config.py` to customize:

```python
# Video analysis settings
DEFAULT_VIDEO_COUNT = 50
MAX_VIDEO_COUNT = 500

# Caching
CACHE_DURATION_HOURS = 24
ENABLE_CACHING = True

# Features
EXTRACT_TRANSCRIPTS = True
ANALYZE_THUMBNAILS = True
CREATE_VISUALIZATIONS = True

# API
RATE_LIMIT_DELAY = 0.1  # seconds between requests
REQUEST_TIMEOUT = 10    # seconds
```

## Database

Data is stored in SQLite at `data/youtube_analyzer.db`:

- **videos** - Video metadata and stats
- **channels** - Channel information
- **niche_analysis** - Cached analysis results
- **content_analysis** - Content-specific analysis

Query the database:

```python
from database import get_db

db = get_db()
videos = db.get_videos_by_niche("AI tutorials")
```

## Logging

Analysis logs are saved to `youtube_analyzer.log`:

```
2024-01-15 10:30:45 - youtube_analyzer - INFO - Starting data collection for niche: AI tutorials
2024-01-15 10:30:46 - youtube_analyzer - INFO - Found 52 videos, fetching detailed stats...
```

View logs in real-time:

```bash
tail -f youtube_analyzer.log
```

## Troubleshooting

### "No API key provided"
**Solution:** Set `YOUTUBE_API_KEY` in `.env` or pass with `--api-key`. The tool works without it but slower.

### "No videos found"
**Solution:** 
- Check niche name spelling
- Try a broader term (e.g., "gaming" instead of "specific game")
- Check YouTube API quota

### Rate Limiting Issues
**Solution:** Increase `RATE_LIMIT_DELAY` in `config.py` from 0.1 to 0.5 seconds.

### Out of Memory on Large Analyses
**Solution:** Reduce `--videos` count or analyze on machine with more RAM.

### Database Lock Errors
**Solution:** Close other processes using the database and retry.

## Advanced Usage

### Using as a Module

```python
from youtube_analyzer import NicheDataCollector
from analysis import ComprehensiveAnalyzer
from blueprint_generator import BlueprintOrchestrator

# Collect data
collector = NicheDataCollector(api_key="your_key")
videos = collector.collect_niche_data("AI tutorials", num_videos=50)

# Analyze
analyzer = ComprehensiveAnalyzer()
analysis = analyzer.analyze_niche(videos)

# Generate blueprint
orchestrator = BlueprintOrchestrator()
blueprint = orchestrator.generate_complete_blueprint(analysis, "AI tutorials")

# Export
from output import OutputManager
output_mgr = OutputManager()
output_mgr.export_markdown_report(analysis, blueprint, videos, "AI tutorials")
```

### Batch Analysis

```bash
#!/bin/bash
for niche in "Python programming" "JavaScript" "Web design" "Data science"; do
    python main.py "$niche" --videos 50 --output "./reports/$niche"
    echo "Completed: $niche"
done
```

### Custom Analysis

Extend the analysis by modifying `analysis.py`:

```python
class CustomAnalyzer(ContentStrategyAnalyzer):
    @staticmethod
    def analyze_custom_metric(videos):
        # Your custom analysis logic
        pass
```

## Performance

- **50 videos:** ~3-5 minutes (with API key)
- **100 videos:** ~6-10 minutes
- **250 videos:** ~15-25 minutes
- **500 videos:** ~30-45 minutes

Factors affecting speed:
- YouTube API quota availability
- Network speed
- Your computer's CPU/RAM
- Transcript extraction (slowest step)

## API Quotas

YouTube API has a daily quota of 10,000 units:
- Search: 100 units per call
- Get video stats: 1 unit per call
- Get channel info: 1 unit per call

Example: Analyzing 50 videos uses ~150 quota units (easily within daily limit).

## Data Privacy & Ethics

- **Data Storage:** All data stored locally in SQLite
- **API Use:** Respects YouTube's Terms of Service
- **Fairness:** Doesn't bypass rate limiting or auth
- **Attribution:** Always credit original creators

## Contributing

To improve the analyzer:

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Test thoroughly
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:

1. Check `youtube_analyzer.log` for error details
2. Review this README's Troubleshooting section
3. Open an issue on GitHub with:
   - What you tried
   - Error messages
   - Your environment (OS, Python version)

## Roadmap

Planned features:

- [ ] Web dashboard interface
- [ ] Real-time analysis updates
- [ ] Competitor comparison mode
- [ ] Comment sentiment analysis
- [ ] Thumbnail color analysis
- [ ] Video transcript search
- [ ] Integration with scheduling tools
- [ ] Bulk niche comparison

## Credits

Built with:
- [Google YouTube API](https://developers.google.com/youtube)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [pandas](https://pandas.pydata.org/)
- [plotly](https://plotly.com/)
- [NLTK](https://www.nltk.org/)
- [Click](https://click.palletsprojects.com/)

---

**Made with ❤️ for YouTube creators**

Start analyzing your niche today:
```bash
python main.py "your niche here"
```
