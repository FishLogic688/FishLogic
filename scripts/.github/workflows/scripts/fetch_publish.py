import feedparser
import requests
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

# ---------------------------
# CONFIGURATION
# ---------------------------
OUTPUT_DIR = "site"
RSS_FEEDS = [
    "https://www.thefishsite.com/rss",             # Global fisheries
    "https://www.fisheries.noaa.gov/rss.xml",      # US NOAA Fisheries
    "https://www.indiawaterportal.org/rss.xml"     # Indian related environmental/fisheries
]

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------
def fetch_news():
    """Fetch news items from all RSS feeds."""
    news_items = []
    for feed in RSS_FEEDS:
        d = feedparser.parse(feed)
        for entry in d.entries[:3]:  # top 3 per site
            news_items.append({
                "title": entry.title,
                "link": entry.link,
                "summary": entry.summary if hasattr(entry, 'summary') else "",
                "published": entry.get("published", "")
            })
    return news_items


def summarize(text):
    """Very simple summarization (you can upgrade later)."""
    return " ".join(text.split()[:40]) + "..."


def create_audio(summary_text, filename):
    """Create audio summary using gTTS."""
    tts = gTTS(summary_text)
    tts.save(filename)


def create_thumbnail(title, filename):
    """Create thumbnail image with title text."""
    img = Image.new("RGB", (800, 450), color=(0, 102, 153))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    d.text((20, 200), title[:70], fill=(255, 255, 255), font=font)
    img.save(filename)


def save_as_html(news_items):
    """Save all summaries as a simple HTML page."""
    html = "<html><head><title>Fisheries Daily News</title></head><body>"
    html += "<h1>🌊 Fisheries News Auto Update</h1>"
    html += f"<p>Updated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p><hr>"

    for i, item in enumerate(news_items):
        summary = summarize(item["summary"])
        audio_path = f"{OUTPUT_DIR}/audio_{i}.mp3"
        thumb_path = f"{OUTPUT_DIR}/thumb_{i}.jpg"

        create_audio(summary, audio_path)
        create_thumbnail(item["title"], thumb_path)

        html += f"""
        <div>
          <h2>{item['title']}</h2>
          <p>{summary}</p>
          <audio controls src="audio_{i}.mp3"></audio><br>
          <img src="thumb_{i}.jpg" width="300"><br>
          <a href="{item['link']}" target="_blank">Read more</a>
        </div><hr>
        """

    html += "</body></html>"

    with open(f"{OUTPUT_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(html)


# ---------------------------
# MAIN SCRIPT
# ---------------------------
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    news = fetch_news()
    save_as_html(news)
    print("✅ Fisheries news updated successfully!")
