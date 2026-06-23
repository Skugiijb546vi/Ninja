import asyncio
from iraq import DarkWebScraper

async def run_scraper():
    config = {
        'tor': {
            'password': ''
        }
    }
    
    forums_to_scan = [
        {
            'url': 'https://archive.org',
            'onion_url': None,
            'search_queries': ['leak', 'database'],
            'pages_to_scrape': 1
        }
    ]
    
    scraper = DarkWebScraper(config)
    
    print("[*] دەستکردن بە پڕۆسەی گەڕان...")
    for forum in forums_to_scan:
        results = await scraper.scrape_forum(forum)
        print(f"\n[*] گەڕان تەواو بوو. ژمارەی بەستەرەکان: {len(results)}")
        
        for link in results:
            print(f"  - [{link['query']}] -> {link['url']}")

if __name__ == "__main__":
    asyncio.run(run_scraper())
