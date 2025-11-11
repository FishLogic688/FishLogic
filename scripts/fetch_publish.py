scripts/
site/
.github/workflows/
# scripts/fetch_publish.py
import feedparser, json, hashlib, os, time
from gtts import gTTS
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests
import shutil

# --- CONFIG ---
SITE_DIR = Path("site")
DATA_DIR = SITE_DIR / "data"
FEEDS = [
    "https://www.thehindu.com/sci-tech/technology/fisheries/feeder/default.rss",
    "https://www.fao.org/fishery/en/feed/en/news",  # example, may fail if not valid RSS
]
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_IMAGE = SITE_DIR / "default.jpg"

def slugify(s):
    return hashlib.md5(s.encode()).hexdigest()[:10]

def summarize(text, limit=2):
    parts = text.split(". ")
    return ". ".join(parts[:limit]) + "."

def make_thumbnail(title, out_path):
    img = Image.new("RGB", (800, 450), color=(0, 90, 160))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((20, 200), title[:80], fill=(255, 255, 255), font=font)
    img.save(out_path)

def main():
    posts = []
    for feed_url in FEEDS:
        d = feedparser.parse(feed_url)
        for e in d.entries[:3]:  # few per feed
            title = e.get("title", "Untitled")
            summary = e.get("summary", "")
            short_summary = summarize(summary)
            url = e.get("link", "#")
            slug = slugify(url)
            post_dir = DATA_DIR / slug
            post_dir.mkdir(parents=True, exist_ok=True)

            # Create audio
            try:
                tts = gTTS(short_summary, lang="en")
                tts.save(str(post_dir / "summary.mp3"))
            except Exception as ex:
                print("TTS failed:", ex)

            # Thumbnail
            make_thumbnail(title, post_dir / "thumb.jpg")

            # Metadata JSON
            meta = {
                "title": title,
                "summary": short_summary,
                "url": url,
                "thumb": f"data/{slug}/thumb.jpg",
                "audio": f"data/{slug}/summary.mp3"
            }
            with open(post_dir / "meta.json", "w") as f:
                json.dump(meta, f, indent=2)
            posts.append(meta)
            time.sleep(1)
    with open(DATA_DIR / "index.json", "w") as f:
        json.dump(posts, f, indent=2)
    print("✅ Done. Generated", len(posts), "posts.")

if __name__ == "__main__":
    main()
