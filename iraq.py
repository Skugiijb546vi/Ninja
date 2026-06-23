# modules/forum_scraper.py
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import socks
import socket
from stem import Signal
from stem.control import Controller

class DarkWebScraper:
    """Complete dark web forum scraper with Tor integration"""
    
    def __init__(self, config):
        self.config = config
        self.session = None
        self.tor_controller = None
        self.init_tor()
        
    def init_tor(self):
        """Initialize Tor connection for .onion access"""
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate(password=self.config['tor'].get('password', ''))
                controller.signal(Signal.NEWNYM)
            
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            socket.socket = socks.socksocket
            print("[Tor] Connection established")
        except Exception as e:
            print(f"[Tor] Warning: {e} - continuing without Tor")
    
    async def scrape_forum(self, forum: Dict) -> List[Dict]:
        """Scrape a single forum for leak links"""
        results = []
        onion_url = forum.get('onion_url')
        clearnet_url = forum.get('url')
        
        base_url = onion_url or clearnet_url
        if not base_url:
            return results
        
        async with aiohttp.ClientSession() as session:
            for query in forum['search_queries']:
                search_url = f"{base_url}/search?q={query}"
                
                for page in range(1, forum.get('pages_to_scrape', 10) + 1):
                    try:
                        url = f"{search_url}&page={page}"
                        async with session.get(url, timeout=30) as response:
                            if response.status == 200:
                                html = await response.text()
                                links = self.extract_links_from_html(html, query)
                                results.extend(links)
                    except Exception as e:
                        print(f"Error scraping {url}: {e}")
                    await asyncio.sleep(2)  # Rate limiting
        return results
    
    def extract_links_from_html(self, html: str, query: str) -> List[Dict]:
        """Extract download links from HTML content"""
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        # Patterns for database/download links
        patterns = [
            r'https?://(?:drive\.google\.com|mega\.nz|mediafire\.com|dropbox\.com)/[^\s"\']+',
            r'magnet:\?xt=urn:btih:[a-fA-F0-9]+',
            r'https?://(?:www\.)?(?:sendspace|zippyshare|uploaded)\.net/[^\s"\']+',
            r'https?://(?:anonfiles|bayfiles|letsupload)\.com/[^\s"\']+',
            r'https?://(?:telegram|t)\.me/[^\s"\']+',
            r'https?://(?:github|gitlab)\.com/[^\s"\']+\.(?:csv|sql|db|zip|rar)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                links.append({
                    'url': match,
                    'source': 'darkweb_forum',
                    'query': query,
                    'timestamp': None
                })
        
        return links
