from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from notebook_database import NotebookDatabase
from wikipedia_api import WikipediaClient


class NotebookRPCService:
    def __init__(self, xml_path: str = "database.xml") -> None:
        self.db = NotebookDatabase(xml_path)
        self.wiki = WikipediaClient()
        self.xml_path = str(Path(xml_path).resolve())

    def ping(self) -> Dict[str, object]:
        return {
            "success": True,
            "message": "Server is running.",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    def add_note(self, topic: str, text: str, timestamp: Optional[str] = None) -> Dict[str, object]:
        try:
            return self.db.add_manual_note(topic, text, timestamp)
        except Exception as exc:
            return {"success": False, "message": f"Server error while saving note: {exc}"}

    def get_notes_by_topic(self, topic: str) -> Dict[str, object]:
        try:
            return self.db.get_topic_notes(topic)
        except Exception as exc:
            return {"success": False, "message": f"Server error while reading topic: {exc}"}

    def list_topics(self) -> Dict[str, object]:
        try:
            return self.db.list_topics()
        except Exception as exc:
            return {"success": False, "message": f"Server error while listing topics: {exc}", "topics": []}

    def search_wikipedia(self, search_term: str) -> Dict[str, object]:
        try:
            return self.wiki.search_first_result(search_term)
        except Exception as exc:
            return {"success": False, "message": f"Server error while querying Wikipedia: {exc}"}

    def append_wikipedia_to_topic(self, topic: str, search_term: str) -> Dict[str, object]:
        try:
            wiki_result = self.wiki.search_first_result(search_term)
            if not wiki_result.get("success"):
                return wiki_result

            return self.db.append_wikipedia_note(
                topic_name=topic,
                search_term=str(wiki_result.get("search_term", search_term)),
                title=str(wiki_result.get("title", "")),
                description=str(wiki_result.get("description", "")),
                url=str(wiki_result.get("url", "")),
            )
        except Exception as exc:
            return {"success": False, "message": f"Server error while appending Wikipedia data: {exc}"}

    def get_server_info(self) -> Dict[str, object]:
        return {
            "success": True,
            "message": "Notebook RPC server information.",
            "xml_path": self.xml_path,
            "features": [
                "XML-RPC communication",
                "Threaded multi-client server",
                "XML database",
                "Wikipedia API integration",
                "Failure-safe structured responses",
            ],
        }
