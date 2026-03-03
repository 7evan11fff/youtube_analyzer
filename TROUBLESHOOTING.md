# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### "pip is not recognized"

**Problem:** Python or pip not in PATH

**Solution:**
```bash
# Option 1: Use python -m pip
python -m pip install -r requirements.txt

# Option 2: Reinstall Python with "Add Python to PATH" checked
# Then restart your terminal
```

#### "ModuleNotFoundError: No module named 'youtube_api'"

**Problem:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
# Wait for installation to complete fully
python main.py --help  # Test if it works now
```

#### "Permission denied" when installing

**Problem:** Need admin rights

**Solution:**
```bash
# Windows
python -m pip install --user -r requirements.txt

# macOS/Linux
pip3 install --user -r requirements.txt
```

---

### Runtime Issues

#### "No YouTube API key provided"

**This is just a warning.** The tool still works but slower.

**Fix it (optional):**

1. Create `.env` file in project root:
   ```
   YOUTUBE_API_KEY=your_key_here
   ```

2. Or pass via command line:
   ```bash
   python main.py "your niche" --api-key "your_key_here"
   ```

3. Get a free key:
   - Go to https://console.cloud.google.com/
   - Create project
   - Enable YouTube Data API v3
   - Create API key

---

#### "No videos found for niche"

**Problem:** Niche name not found or too specific

**Solutions:**

```bash
# Use simpler, more popular terms
python main.py "gaming"           # Instead of "minecraft speedrun"
python main.py "fitness"          # Instead of "specific gym routine"

# Try related search terms
python main.py "machine learning tutorial"
python main.py "web development for beginners"

# Try broader category
python main.py "cooking"  # Instead of "keto cooking"
```

**Tips:**
- Use nouns people actually search for
- Avoid overly specific brand names
- Check if it's a real YouTube category

---

#### "Rate limit exceeded" or API errors

**Problem:** YouTube API quota depleted

**Solutions:**

1. Wait a few hours (quota resets daily)
2. Reduce video count:
   ```bash
   python main.py "niche" --videos 30
   ```
3. Use fallback mode (no API key):
   - Remove `YOUTUBE_API_KEY` from `.env`
   - Tool automatically switches to slower fallback method
4. Skip transcript extraction:
   - Edit `config.py` and set `EXTRACT_TRANSCRIPTS=False`

**Note:** Without API key, you get ~10 videos before rate limiting. With key, you can analyze 50-100 videos.

---

#### "Database locked" error

**Problem:** Database is being used by another process

**Solutions:**

```bash
# Option 1: Close other Python instances
# Check Task Manager (Windows) or Activity Monitor (macOS)
# Kill any python.exe or python3 processes

# Option 2: Delete and recreate database
# Delete: data/youtube_analyzer.db
# Rerun the analysis

# Option 3: Wait a moment and retry
# The lock usually clears quickly
```

---

#### "Connection timeout" or "Network error"

**Problem:** Slow internet or YouTube blocking

**Solutions:**

```bash
# Increase timeout in config.py
REQUEST_TIMEOUT = 20  # was 10

# Reduce rate limit delay
RATE_LIMIT_DELAY = 0.5  # was 0.1

# Use different network (WiFi vs LTE)
# Check internet speed: speedtest.net
```

---

### Output Issues

#### No visualizations created

**Problem:** matplotlib/plotly not installed or error occurred

**Solution:**

```bash
# Reinstall visualization libraries
pip install --upgrade matplotlib plotly

# Skip visualizations if they're causing issues
python main.py "niche" --skip-visualizations
```

Check `youtube_analyzer.log` for specific errors.

---

#### CSV file is empty or corrupted

**Problem:** Video data wasn't properly fetched

**Solution:**

```bash
# Force refresh the data
python main.py "niche" --force-refresh

# Check if videos were collected
python -c "from database import get_db; db = get_db(); print(db.get_videos_by_niche('niche'))"
```

---

#### Markdown report not opening

**Problem:** Special characters in niche name

**Solution:**

1. Use simpler niche names without special chars
2. Open report file directly:
   - Windows: Right-click → "Open with" → Notepad
   - macOS: Double-click (should open in TextEdit)
   - Linux: `cat output/report_*.md`

---

### Performance Issues

#### Analysis is very slow

**Problem:** Analyzing too many videos, extracting transcripts

**Solutions:**

```bash
# Analyze fewer videos
python main.py "niche" --videos 25

# Skip visualizations
python main.py "niche" --skip-visualizations

# Disable transcript extraction in config.py
EXTRACT_TRANSCRIPTS = False

# Use with API key (faster than fallback)
# Set YOUTUBE_API_KEY in .env
```

**Expected times:**
- 30 videos: 2-5 minutes (with API key)
- 50 videos: 3-10 minutes
- 100 videos: 6-20 minutes

Without API key, add 50% more time.

---

#### Out of memory error

**Problem:** Analyzing too many videos on limited RAM

**Solutions:**

```bash
# Analyze fewer videos
python main.py "niche" --videos 30

# Close other applications to free RAM
# Restart your computer
# Use a more powerful machine
```

---

### Data Quality Issues

#### Low quality/spam videos in results

**Problem:** Search returned non-relevant results

**Solution:**

Use more specific niche terms:

```bash
# Bad: Too generic
python main.py "tutorial"

# Good: Specific niche
python main.py "Python web scraping tutorial"
```

---

#### Transcripts not extracted

**Problem:** Some videos have no captions

**Solution:** This is normal. Not all videos have transcripts available.

To disable transcript extraction:
```python
# In config.py
EXTRACT_TRANSCRIPTS = False
```

---

### Logging & Debugging

#### Check detailed error logs

```bash
# View last 50 lines of log
tail -50 youtube_analyzer.log

# Search for errors
grep ERROR youtube_analyzer.log

# View all warnings
grep WARNING youtube_analyzer.log
```

#### Enable debug logging

Edit the log level in `youtube_analyzer.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    ...
)
```

---

#### Test your setup

```bash
# Test Python installation
python --version

# Test pip
pip --version

# Test imports
python -c "import youtube_analyzer; print('OK')"

# Check YouTube API
python -c "import requests; print('OK')"

# List cached niches
python -c "from database import get_db; db = get_db()"
```

---

### Getting Help

#### Still stuck? Try this order:

1. **Check the logs**
   ```bash
   tail youtube_analyzer.log
   ```

2. **Read the README**
   - README.md has comprehensive docs
   - GETTING_STARTED.md has beginner guide

3. **Try a different niche**
   ```bash
   python main.py "gaming" --videos 30
   ```

4. **Reinstall cleanly**
   ```bash
   pip uninstall -r requirements.txt
   pip install -r requirements.txt
   ```

5. **Check your environment**
   ```bash
   python --version  # Should be 3.11+
   pip --version
   ```

6. **Test with example**
   ```bash
   python example_usage.py
   ```

---

### Known Limitations

#### These are normal, not bugs:

- ✓ Some videos have no transcripts (YouTube doesn't provide them)
- ✓ Thumbnail analysis is basic (no complex ML)
- ✓ Comment analysis is limited (requires more API quota)
- ✓ Long analyses take time (lots of data processing)
- ✓ Trending topics are based on video titles only
- ✓ Growth curves are estimates, not exact

---

### Windows-Specific Issues

#### "Python" command not found but "python3" works

Use `python3` instead:
```bash
python3 main.py "niche"
```

---

#### Special characters in output path

**Problem:** Error with Unicode characters

**Solution:**
```bash
# Use simple ASCII path names
python main.py "niche" --output "./reports"
# Not: --output "./報告書"
```

---

### macOS-Specific Issues

#### "Microsoft Visual C++ Runtime Error"

This shouldn't happen on macOS, but if it does:

```bash
pip install --upgrade numpy
```

---

### Linux-Specific Issues

#### Missing system dependencies

```bash
# Ubuntu/Debian
sudo apt-get install python3-pip python3-dev

# Fedora
sudo dnf install python3-pip python3-devel
```

---

## Prevention Tips

✅ **Do This:**
- Keep Python updated
- Keep packages updated: `pip install --upgrade -r requirements.txt`
- Use .env for sensitive keys
- Check logs when something fails
- Test with small videos count first (--videos 25)

❌ **Avoid This:**
- Don't use special characters in niche names
- Don't analyze > 500 videos (limit enforced anyway)
- Don't run multiple instances simultaneously
- Don't edit database files directly

---

## Still Need Help?

**Before reporting a bug, try:**

1. Close all Python windows
2. Delete `data/youtube_analyzer.db` (it will be recreated)
3. Run again: `python main.py "simple niche" --videos 25`

**If that doesn't work:**

Collect this info:
- Python version: `python --version`
- Error message (from .log file)
- Command you ran
- Operating system

---

**Remember:** Most issues are solved by:
1. Reinstalling packages: `pip install -r requirements.txt`
2. Clearing cache: Delete `data/` folder
3. Using simpler niche names
4. Analyzing fewer videos first

Good luck! 🎯
