#!/usr/bin/env python3
import requests
import re
import time
from urllib.parse import urlparse

BOT_USERNAME = "eye_osinitBot"

def search_github(query):
    url = f"https://api.github.com/search/code?q={query}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        resp = requests.get(url, headers=headers)
        return resp.json().get("items", [])
    except:
        return []

def search_pastebin(keyword):
    # Pastebin search requires scraping; limited demo
    # Real implementation would use Google dorks
    print(f"[*] Search Pastebin for '{keyword}'...")
    return []

def extract_token_from_text(text):
    tokens = re.findall(r'\d{9,10}:[A-Za-z0-9_-]{35}', text)
    return tokens

def main():
    print(f"[*] Harvesting info for bot @{BOT_USERNAME}")
    # GitHub search
    github_items = search_github(BOT_USERNAME)
    for item in github_items[:5]:
        print(f"GitHub: {item['html_url']}")
        # Fetch raw content if possible
        raw_url = item.get('url', '').replace('https://api.github.com/repos/', 'https://raw.githubusercontent.com/')
        if raw_url:
            try:
                r = requests.get(raw_url)
                tokens = extract_token_from_text(r.text)
                if tokens:
                    print(f"[!] Potential token: {tokens}")
            except:
                pass
    # Public Telegram API endpoints (no auth)
    try:
        # Check if bot has any open information (e.g., via t.me)
        resp = requests.get(f"https://t.me/{BOT_USERNAME}", timeout=5)
        if "tgme_page_photo" in resp.text:
            print("[*] Bot has public profile photo")
        # Try to get sticker set if bot sends stickers
    except:
        pass
    # Brute force common webhook paths on popular ngrok/frp domains (example)
    common_paths = ["/webhook", "/bot", "/", "/telegram", "/api/webhook"]
    # No domain known – requires prior enumeration
    print("[*] No direct token extraction without access. Use above GitHub search manually.")
    
if __name__ == "__main__":
    main()
