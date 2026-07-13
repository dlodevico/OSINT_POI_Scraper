import asyncio
import aiohttp
from bs4 import BeautifulSoup

# A dictionary of platforms and their URL structures
# {} is a placeholder for the username/alias
PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "Twitter/X": "https://twitter.com/{}",
    "Archive.org": "https://archive.org/details/@{}",
}

async def check_platform(session, name, username, url_template):
    """Checks if a username exists on a specific platform."""
    url = url_template.format(username)
    try:
        async with session.get(url, timeout=10) as response:
            # Logic: If 200, the page exists. If 404, it doesn't.
            if response.status == 200:
                print(f"[+] FOUND: {name} - {url}")
                return (name, url, "Active")
            elif response.status == 404:
                return (name, url, "Not Found")
            else:
                return (name, url, f"Error: {response.status}")
    except Exception as e:
        return (name, url, f"Failed: {str(e)}")

async def run_scraper(target_username):
    """Orchestrates the asynchronous requests."""
    print(f"--- Searching for Alias: {target_username} ---\n")
    
    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        tasks = []
        for name, url_template in PLATFORMS.items():
            tasks.append(check_platform(session, name, target_username, url_template))
        
        results = await asyncio.gather(*tasks)
        return results

if __name__ == "__main__":
    # In a real scenario, this would come from a case file or lead
    alias_to_track = "suspicious_user_01" 
    
    # Run the async loop
    asyncio.run(run_scraper(alias_to_track))