"""
Web Search Skill - DuckDuckGo HTML scraping (no API key needed)
Compatible with: Phoenix, Claude Code, Codex, Hermes, OpenCode
"""
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
from typing import List, Dict, Optional
import time


class WebSearchSkill:
    """Web search via DuckDuckGo - no API key required."""
    
    BASE_URL = "https://html.duckduckgo.com/html/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.max_results = self.config.get("max_results", 5)
        self.timeout = self.config.get("timeout", 10)
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """Search web and return structured results."""
        max_results = max_results or self.max_results
        params = {"q": query}
        
        try:
            resp = requests.post(
                self.BASE_URL,
                data=params,
                headers=self.HEADERS,
                timeout=self.timeout
            )
            resp.raise_for_status()
        except Exception as e:
            return [{"error": f"Search failed: {e}"}]
        
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        
        for result in soup.select(".result__snippet"):
            if len(results) >= max_results:
                break
            
            # Get title and link
            title_elem = result.find_previous("a", class_="result__url")
            link_elem = result.find_previous("a", class_="result__snippet")
            
            # Better extraction
            container = result.find_parent("div", class_="result")
            if container:
                title_a = container.select_one("a.result__snippet")
                url_a = container.select_one("a.result__url")
                
                title = title_a.get_text(strip=True) if title_a else ""
                url = url_a.get("href", "") if url_a else ""
                snippet = result.get_text(strip=True)
                
                if title and url:
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet[:300]
                    })
        
        return results
    
    def search_and_format(self, query: str, max_results: Optional[int] = None) -> str:
        """Search and return formatted string for agents."""
        results = self.search(query, max_results)
        
        if not results or "error" in results[0]:
            return f"Search failed: {results[0].get('error', 'No results')}"
        
        lines = [f"Web search results for: {query}\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. **{r['title']}**")
            lines.append(f"   URL: {r['url']}")
            lines.append(f"   {r['snippet']}\n")
        
        return "\n".join(lines)


# Agent-agnostic entry point
def run(query: str, max_results: int = 5, **kwargs) -> str:
    """Main entry point for any agent."""
    skill = WebSearchSkill(kwargs)
    return skill.search_and_format(query, max_results)


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) or "test query"
    print(run(query))