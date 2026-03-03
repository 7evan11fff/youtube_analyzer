# Getting Started with YouTube Niche Analyzer

Welcome! This guide will get you up and running in 5 minutes.

## Prerequisites

- Windows, macOS, or Linux
- Python 3.11 or higher
- Internet connection
- ~500MB disk space

## Step 1: Install Python (if needed)

Check if you have Python 3.11+:

```bash
python --version
```

If not, download from [python.org](https://www.python.org/downloads/)

## Step 2: Set Up the Project

```bash
# Navigate to the project directory
cd youtube_analyzer

# Install dependencies
pip install -r requirements.txt
```

This takes ~2-3 minutes depending on your internet speed.

## Step 3: Get a YouTube API Key (Optional but Recommended)

For faster and more reliable results, get a free API key:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project" (if new to Google Cloud)
3. Search for "YouTube Data API v3" and click "Enable"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy your API key

### Add it to the project:

Create a file named `.env` in the project folder:

```
YOUTUBE_API_KEY=your_api_key_here
```

Or pass it when running:

```bash
python main.py "your niche" --api-key "your_api_key_here"
```

**Without an API key?** No problem! The tool still works using fallback scraping (just slower).

## Step 4: Run Your First Analysis

Try analyzing a popular niche:

```bash
python main.py "AI tutorials"
```

That's it! The tool will:
- ✓ Search for 50 AI tutorial videos
- ✓ Fetch detailed statistics
- ✓ Analyze patterns and trends
- ✓ Generate content recommendations
- ✓ Create reports and visualizations

This takes 3-10 minutes depending on your internet speed.

## Step 5: Check Your Results

When done, you'll see:

```
📄 Generated Files:
  📊 Analysis Data:    output/complete_analysis_ai_tutorials.json
  📋 Video CSV:        output/videos_ai_tutorials.csv
  📝 Markdown Report:  output/report_ai_tutorials_20240115_103045.md
  📈 Visualizations:   5 charts created

💡 Key Findings:
  • Unique channels analyzed: 47
  • Average views per video: 15,420
  • Market saturation: Medium
  • Dominant format: Medium-form videos (55%)
```

Open the Markdown report in any text editor to see detailed recommendations!

## Common First Analyses

### 1. Broad Niche (General Topic)

```bash
python main.py "gaming"
```

Good for understanding market trends, large audience.

### 2. Specific Niche (Narrow Focus)

```bash
python main.py "Python web scraping tutorial"
```

Better targeting, less competition, better for new creators.

### 3. Problem-Based Niche

```bash
python main.py "how to lose weight naturally"
```

High intent audience, good monetization potential.

## Analyzing Your Own Niche

Think about your YouTube niche idea and run:

```bash
python main.py "your niche here" --videos 50
```

Try different variations:

```bash
# Specific angle
python main.py "fitness for beginners"

# Problem-solving
python main.py "how to make money online"

# Product-focused
python main.py "Blender 3D animation tutorials"
```

## Understanding Your Report

### The Markdown Report Contains:

1. **Executive Summary** - Overview of what's analyzed
2. **Video Strategy** - Optimal length, upload times, title style
3. **Top 5 Content Ideas** - Ready-to-produce video concepts
4. **What Works** - Proven engagement strategies
5. **What Doesn't Work** - Mistakes to avoid
6. **Competition Analysis** - Market saturation, top creators
7. **12-Month Roadmap** - How to build and scale

### Key Metrics You'll See:

- **Average Views per Video** - Expected performance
- **Engagement Rate** - Likes + comments per 1000 views
- **Upload Frequency** - How often successful creators post
- **Video Length** - What duration performs best
- **Market Saturation** - How competitive the niche is

## Next Steps

### Create Content

1. Pick one of the **Top 5 Ideas** from your report
2. Follow the **Video Strategy** recommendations
3. Use a **Title Formula** that works in your niche
4. Apply the **Hook Strategy** in your opening

### Monitor Your Progress

- Use the **CSV export** to track top videos
- Study their titles, lengths, and upload times
- Replicate patterns that work

### Build Your Channel

Follow the **3-phase growth roadmap**:

- **Phase 1** (Months 1-3): Build foundation
- **Phase 2** (Months 3-6): Scale what works
- **Phase 3** (Months 6-12): Monetize

## Troubleshooting

### "Could not collect any video data"

**Causes:** Wrong niche name, API quota exceeded, network issue

**Solution:** 
```bash
# Try a simpler niche
python main.py "gaming tutorials"

# Add --force-refresh to bypass cache
python main.py "your niche" --force-refresh
```

### "No API key provided"

This is just a warning. The tool still works but slower. To fix:

1. Create `.env` file with `YOUTUBE_API_KEY=your_key`
2. Or pass `--api-key your_key` when running

### Slow Analysis

**Solution:** Skip visualizations:

```bash
python main.py "your niche" --skip-visualizations
```

## Advanced Options

### Analyze More Videos (For Deeper Insights)

```bash
python main.py "your niche" --videos 100
```

Takes longer but more comprehensive.

### Skip Visualizations (Faster)

```bash
python main.py "your niche" --skip-visualizations
```

Only creates JSON, CSV, and Markdown.

### Use Custom Output Directory

```bash
python main.py "your niche" --output ./my_reports
```

## Need Help?

1. **Check the logs** - See `youtube_analyzer.log` for details
2. **Read the README** - Comprehensive documentation
3. **Try a different niche** - Some niches have more data

## Pro Tips

✅ **Do This:**
- Analyze multiple niches to compare markets
- Look at what works in similar niches
- Focus on underexplored subtopics
- Create 5-10 videos before expecting views

❌ **Don't Do This:**
- Expect overnight success (takes 50+ videos)
- Copy others exactly (add your unique angle)
- Ignore the data (that's the whole point!)
- Give up too early (consistency wins)

## Next: Dive Deeper

Once you've run your first analysis:

1. **Read the Full Report** - Open the Markdown file
2. **Study Your Data** - Open the CSV in Excel/Sheets
3. **Explore Visualizations** - Open the HTML charts
4. **Make a Spreadsheet** - Track your own video ideas
5. **Create Your First Video** - Use the top idea with the hook

## Questions?

Check these files for more info:

- `README.md` - Complete documentation
- `config.py` - Configuration options
- `youtube_analyzer.log` - Detailed logs

---

**You're ready to analyze! Run your first niche:**

```bash
python main.py "your niche here"
```

Good luck! 🚀
