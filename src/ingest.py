import feedparser
import json
import os
import glob
from datetime import datetime

def ingest_rss(feed_url, max_articles=3):
    """STREAM 1: Fetches and parses an RSS feed."""
    print(f"[*] Fetching RSS feed: {feed_url}")
    feed = feedparser.parse(feed_url)
    
    if feed.bozo:
        print("  [-] Error parsing feed. It might be malformed.")
        return []

    articles = []
    for entry in feed.entries[:max_articles]:
        articles.append({
            "source": "RSS",
            "title": entry.title,
            "link": entry.link,
            "published": entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
            "summary": entry.summary if hasattr(entry, 'summary') else ""
        })
    return articles

def ingest_local_files(directory_path):
    """STREAM 2: Reads plain text files (e.g., phishing emails, logs) from a drop folder."""
    print(f"[*] Checking local drop folder: {directory_path}")
    
    # Create the folder if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        print("  [i] Folder created. Drop .txt files here to analyze them.")
        return []

    articles = []
    # Find all .txt files in the directory
    search_pattern = os.path.join(directory_path, "*.txt")
    for filepath in glob.glob(search_pattern):
        filename = os.path.basename(filepath)
        print(f"  [+] Reading local file: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            articles.append({
                "source": "Local File",
                "title": f"Local File Analysis: {filename}",
                "link": f"file://{filepath}",
                "published": datetime.now().isoformat(),
                # We feed the entire text file to the AI as the "summary"
                "summary": content 
            })
        except Exception as e:
            print(f"  [-] Error reading {filename}: {e}")
            
    return articles

def save_raw_data(all_data, filename="latest_intel.json"):
    """Saves aggregated data from all streams."""
    save_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4)
        
    print(f"\n[+] Successfully saved {len(all_data)} total items to {filepath}")

if __name__ == "__main__":
    print("Starting Phase 2: Multi-Stream Data Ingestion...\n")
    
    aggregated_data = []
    
    # --- STREAM 1: Execute RSS Ingestion ---
    rss_target = "https://www.bleepingcomputer.com/feed/"
    rss_data = ingest_rss(rss_target)
    aggregated_data.extend(rss_data)
    
    # --- STREAM 2: Execute Local File Ingestion ---
    # Creates a 'data/input_drop' folder for you to throw files into
    drop_folder = os.path.join(os.path.dirname(__file__), "..", "data", "input_drop")
    local_data = ingest_local_files(drop_folder)
    aggregated_data.extend(local_data)
    
    # --- AGGREGATE AND SAVE ---
    if aggregated_data:
        save_raw_data(aggregated_data)
        print("[*] Phase 2 Complete. Multi-stream data is ready for the LLM.")
    else:
        print("[-] No data ingested from any stream.")