# requirements.txt
# telethon==1.34.0
# asyncio==3.4.3
# aiohttp==3.9.3
# beautifulsoup4==4.12.3

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path

from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

# === CONFIGURATION ===
API_ID = 22697853  # Get from my.telegram.org
API_HASH = "4801319a0aeb52817bc01d3cc60bb245"
SESSION_NAME = "iraq_leak_scraper"

# Known Iraqi data leak channels (update from monitoring)
TARGET_CHANNELS = [
    "https://t.me/iraqleaks",
    "https://t.me/iqdatabase",
    "https://t.me/iraq_cyber_zone",
    "https://t.me/telegram_iraq_leaks",
    "https://t.me/bot_hoax_warning",  # Known fake bot mentioned in arrests [citation:4]
]

OUTPUT_DIR = Path("./collected_data")
LOG_DIR = Path("./logs")

# === LOGGING SETUP ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === MEDIA DOWNLOAD PATTERNS ===
LEAK_KEYWORDS = re.compile(r'(\b(?:بيانات|داتا|قاعدة\s*بيانات|تسريب|هاك|اختراق|leak|data|database|breach|dump|sql|csv|xlsx|json)\b)', re.IGNORECASE)
TELEPHONE_PATTERN = re.compile(r'(07[3-9]\d{8})')
NATIONAL_ID_PATTERN = re.compile(r'\b\d{11}\b')  # Iraqi national ID is 11 digits


class IraqLeakCollector:
    def __init__(self):
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        self.discovered_links = []
        self.downloaded_files = []
        
    async def connect_and_scan(self):
        """Main entry point - connect and scan all target channels"""
        await self.client.start()
        logger.info(f"Connected as: {await self.client.get_me()}")
        
        for channel_url in TARGET_CHANNELS:
            await self.scan_channel(channel_url)
            
        # Also search globally for keywords
        await self.global_search()
        
        return self.discovered_links
    
    async def scan_channel(self, channel_url, limit=500):
        """Extract all messages with media or links from a channel"""
        try:
            entity = await self.client.get_entity(channel_url)
            logger.info(f"Scanning: {channel_url}")
            
            async for message in self.client.iter_messages(entity, limit=limit):
                await self.process_message(message, channel_url)
                
        except FloodWaitError as e:
            logger.warning(f"Flood wait: {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"Failed on {channel_url}: {str(e)}")
    
    async def process_message(self, message, source):
        """Extract links, download media matching leak patterns"""
        message_data = {
            "id": message.id,
            "date": str(message.date),
            "source": source,
            "text": message.text or "",
            "links": [],
            "has_media": False,
            "media_type": None
        }
        
        # Extract URLs from message text
        if message.text:
            urls = re.findall(r'https?://[^\s]+|t\.me/[^\s]+|drive\.google\.com/[^\s]+|mega\.nz/[^\s]+|mediafire\.com/[^\s]+', message.text)
            message_data["links"].extend(urls)
            
            # Flag if contains leak keywords
            if LEAK_KEYWORDS.search(message.text):
                message_data["flagged_leak"] = True
                self.discovered_links.append(message_data)
                logger.info(f"Found potential leak at {source}: {message.id}")
        
        # Download media files if they might be database dumps
        if message.media:
            message_data["has_media"] = True
            if isinstance(message.media, MessageMediaDocument):
                message_data["media_type"] = "document"
                file_name = getattr(message.file, 'name', f"msg_{message.id}")
                if any(ext in str(file_name).lower() for ext in ['.csv', '.xlsx', '.json', '.sql', '.zip', '.rar', '.7z', '.txt', '.db']):
                    await self.download_media(message, file_name)
            elif isinstance(message.media, MessageMediaPhoto):
                message_data["media_type"] = "photo"
                # Photos might contain screenshots of database records
                await self.download_media(message, f"screenshot_{message.id}.jpg")
        
        # Save metadata
        self.save_metadata(message_data)
    
    async def download_media(self, message, filename):
        """Download file with retry logic"""
        output_path = OUTPUT_DIR / "downloads" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        for attempt in range(3):
            try:
                path = await message.download_media(file=str(output_path))
                if path:
                    self.downloaded_files.append(str(path))
                    logger.info(f"Downloaded: {path}")
                break
            except Exception as e:
                logger.error(f"Download attempt {attempt+1} failed: {e}")
                await asyncio.sleep(2 ** attempt)
    
    async def global_search(self):
        """Search all accessible chats for keywords"""
        keywords = ["تسريب بيانات العراق", "قاعدة بيانات عراقية", "Iraq database leak", "IQ data dump", "بطاقة وطنية", "Korek leak"]
        
        for keyword in keywords:
            logger.info(f"Searching for: {keyword}")
            try:
                async for message in self.client.iter_messages(None, search=keyword, limit=100):
                    if message.chat and hasattr(message.chat, 'username'):
                        await self.process_message(message, f"search_{keyword}@{message.chat.username}")
            except Exception as e:
                logger.error(f"Search failed for {keyword}: {e}")
    
    def save_metadata(self, data):
        """Persist discovered links to JSON"""
        metadata_file = OUTPUT_DIR / "discovered_links.json"
        existing = []
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        
        existing.append(data)
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)


async def main():
    collector = IraqLeakCollector()
    results = await collector.connect_and_scan()
    print(f"\n=== COLLECTION COMPLETE ===")
    print(f"Flagged messages: {len(results)}")
    print(f"Downloaded files: {len(collector.downloaded_files)}")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")

if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    asyncio.run(main())
