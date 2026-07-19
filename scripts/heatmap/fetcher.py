import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from utils.logger import setup_logger
import json
from pathlib import Path
from datetime import datetime

logger = setup_logger("heatmap_fetcher")

class ContributionFetcher:
    def __init__(self, username: str, cache_dir: Path = Path("data")):
        self.username = username
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "contributions.json"
        
    def _fetch_html(self) -> str:
        url = f"https://github.com/users/{self.username}/contributions"
        logger.info(f"Fetching contributions from {url}")
        # Need user agent, sometimes GitHub blocks python requests
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
        
    def _parse_html(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        contributions = []
        
        days = soup.find_all("td", {"class": "ContributionCalendar-day"})
        for day in days:
            date_str = day.get("data-date")
            level_str = day.get("data-level")
            
            if date_str and level_str:
                contributions.append({
                    "date": date_str,
                    "level": int(level_str)
                })
                
        if not contributions:
            logger.warning("No contributions found. GitHub DOM may have changed.")
            
        return contributions

    def get_contributions(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        if use_cache and self.cache_file.exists():
            mtime = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            if mtime.date() == datetime.now().date():
                logger.debug("Using cached contributions data")
                with open(self.cache_file, "r") as f:
                    return json.load(f)
                    
        html = self._fetch_html()
        data = self._parse_html(html)
        
        with open(self.cache_file, "w") as f:
            json.dump(data, f)
            
        return data
