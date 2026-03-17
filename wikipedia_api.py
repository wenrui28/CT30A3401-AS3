from urllib.request import urlopen, Request

from typing import Dict
from urllib.parse import urlencode
from urllib.request import urlopen
import json


class WikipediaClient:
    """Very small wrapper around MediaWiki OpenSearch API."""

    API_URL = "https://en.wikipedia.org/w/api.php"

    def search_first_result(self, search_term: str) -> Dict[str, object]:
        search_term = search_term.strip()
        if not search_term:
            return {"success": False, "message": "Search term cannot be empty."}

        params = {
            "action": "opensearch",
            "search": search_term,
            "limit": 1,
            "namespace": 0,
            "format": "json",
        }
        url = f"{self.API_URL}?{urlencode(params)}"

        try:
            headers = {
                "User-Agent": "RPCNotebookAssignment/1.0 (student project; contact: your_email@example.com)"
}
            request = Request(url, headers=headers)

            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            return {
                "success": False,
                "message": f"Wikipedia query failed: {exc}",
                "search_term": search_term,
            }

        titles = data[1] if len(data) > 1 else []
        descriptions = data[2] if len(data) > 2 else []
        urls = data[3] if len(data) > 3 else []

        if not titles:
            return {
                "success": False,
                "message": f"No Wikipedia article found for '{search_term}'.",
                "search_term": search_term,
            }

        title = titles[0]
        description = descriptions[0] if descriptions else ""
        article_url = urls[0] if urls else ""

        return {
            "success": True,
            "message": "Wikipedia article found successfully.",
            "search_term": search_term,
            "title": title,
            "description": description,
            "url": article_url,
        }
