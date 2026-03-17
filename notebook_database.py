from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom


@dataclass
class Note:
    source: str
    timestamp: str
    text: str
    title: str = ""
    description: str = ""
    url: str = ""
    search_term: str = ""
    note_id: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "source": self.source,
            "timestamp": self.timestamp,
            "text": self.text,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "search_term": self.search_term,
            "note_id": self.note_id,
        }


class NotebookDatabase:
    """Thread-safe XML-backed notebook storage.

    The assignment only requires a local XML mock database.
    This implementation keeps the structure simple and readable:

    <notebook>
      <topic name="RPC">
        <notes>
          <note id="1" source="manual">...</note>
        </notes>
      </topic>
    </notebook>

    It also reads the older, flatter structure where <note> is directly
    under <topic>, so the project stays backwards-compatible.
    """

    def __init__(self, xml_path: str = "database.xml") -> None:
        self.xml_path = Path(xml_path)
        self.lock = Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.xml_path.exists():
            root = ET.Element("notebook")
            root.set("created", datetime.now().isoformat(timespec="seconds"))
            root.set("version", "1.1")
            self._write_tree(ET.ElementTree(root))

    def _read_tree(self) -> ET.ElementTree:
        return ET.parse(self.xml_path)

    def _write_tree(self, tree: ET.ElementTree) -> None:
        rough_xml = ET.tostring(tree.getroot(), encoding="utf-8")
        pretty_xml = minidom.parseString(rough_xml).toprettyxml(indent="  ", encoding="utf-8")
        self.xml_path.write_bytes(pretty_xml)

    def _find_topic(self, root: ET.Element, topic_name: str) -> Optional[ET.Element]:
        for topic in root.findall("topic"):
            if topic.get("name", "").strip().lower() == topic_name.strip().lower():
                return topic
        return None

    def _get_notes_container(self, topic: ET.Element) -> ET.Element:
        notes = topic.find("notes")
        if notes is None:
            notes = ET.SubElement(topic, "notes")
        return notes

    def _get_all_note_elements(self, topic: ET.Element) -> List[ET.Element]:
        notes = list(topic.findall("note"))
        notes_container = topic.find("notes")
        if notes_container is not None:
            notes.extend(notes_container.findall("note"))
        return notes

    def _next_note_id(self, topic: ET.Element) -> str:
        note_ids: List[int] = []
        for note in self._get_all_note_elements(topic):
            raw_id = note.get("id", "").strip()
            if raw_id.isdigit():
                note_ids.append(int(raw_id))
        return str(max(note_ids, default=0) + 1)

    def _create_topic(self, root: ET.Element, topic_name: str, timestamp: str) -> ET.Element:
        topic = ET.SubElement(
            root,
            "topic",
            {
                "name": topic_name,
                "created_at": timestamp,
                "updated_at": timestamp,
            },
        )
        ET.SubElement(topic, "notes")
        return topic

    def _append_note(
        self,
        topic: ET.Element,
        source: str,
        timestamp: str,
        text: str,
        search_term: str = "",
        title: str = "",
        description: str = "",
        url: str = "",
    ) -> Note:
        notes_container = self._get_notes_container(topic)
        note_id = self._next_note_id(topic)

        note_el = ET.SubElement(notes_container, "note", {"id": note_id, "source": source})
        ET.SubElement(note_el, "timestamp").text = timestamp
        ET.SubElement(note_el, "text").text = text

        if search_term:
            ET.SubElement(note_el, "search_term").text = search_term
        if title:
            ET.SubElement(note_el, "title").text = title
        if description:
            ET.SubElement(note_el, "description").text = description
        if url:
            ET.SubElement(note_el, "url").text = url

        topic.set("updated_at", timestamp)

        return Note(
            source=source,
            timestamp=timestamp,
            text=text,
            title=title,
            description=description,
            url=url,
            search_term=search_term,
            note_id=note_id,
        )

    def add_manual_note(self, topic_name: str, text: str, timestamp: Optional[str] = None) -> Dict[str, object]:
        topic_name = topic_name.strip()
        text = text.strip()
        timestamp = (timestamp or datetime.now().isoformat(timespec="seconds")).strip()

        if not topic_name:
            return {"success": False, "message": "Topic cannot be empty."}
        if not text:
            return {"success": False, "message": "Text cannot be empty."}

        with self.lock:
            tree = self._read_tree()
            root = tree.getroot()
            topic = self._find_topic(root, topic_name)
            topic_created = False

            if topic is None:
                topic = self._create_topic(root, topic_name, timestamp)
                topic_created = True

            note = self._append_note(topic=topic, source="manual", timestamp=timestamp, text=text)
            self._write_tree(tree)

        message = "New topic created and note saved." if topic_created else "Topic found; note appended successfully."
        return {
            "success": True,
            "message": message,
            "topic_created": topic_created,
            "topic": topic_name,
            "note": note.to_dict(),
        }

    def append_wikipedia_note(
        self,
        topic_name: str,
        search_term: str,
        title: str,
        description: str,
        url: str,
        timestamp: Optional[str] = None,
    ) -> Dict[str, object]:
        topic_name = topic_name.strip()
        search_term = search_term.strip()
        title = title.strip()
        description = description.strip()
        url = url.strip()
        timestamp = (timestamp or datetime.now().isoformat(timespec="seconds")).strip()

        if not topic_name:
            return {"success": False, "message": "Topic cannot be empty."}
        if not search_term:
            return {"success": False, "message": "Search term cannot be empty."}
        if not url:
            return {"success": False, "message": "Wikipedia URL is required."}

        text = f"Wikipedia result for '{search_term}': {title}. {description}".strip()

        with self.lock:
            tree = self._read_tree()
            root = tree.getroot()
            topic = self._find_topic(root, topic_name)
            topic_created = False

            if topic is None:
                topic = self._create_topic(root, topic_name, timestamp)
                topic_created = True

            note = self._append_note(
                topic=topic,
                source="wikipedia",
                timestamp=timestamp,
                text=text,
                search_term=search_term,
                title=title,
                description=description,
                url=url,
            )
            self._write_tree(tree)

        message = "Wikipedia data appended to existing topic." if not topic_created else "New topic created and Wikipedia data appended."
        return {
            "success": True,
            "message": message,
            "topic_created": topic_created,
            "topic": topic_name,
            "note": note.to_dict(),
        }

    def get_topic_notes(self, topic_name: str) -> Dict[str, object]:
        topic_name = topic_name.strip()
        if not topic_name:
            return {"success": False, "message": "Topic cannot be empty."}

        with self.lock:
            tree = self._read_tree()
            root = tree.getroot()
            topic = self._find_topic(root, topic_name)

            if topic is None:
                return {
                    "success": False,
                    "message": f"Topic '{topic_name}' was not found in the XML database.",
                    "topic": topic_name,
                    "notes": [],
                }

            notes: List[Dict[str, str]] = []
            for note_el in self._get_all_note_elements(topic):
                notes.append(
                    Note(
                        source=note_el.get("source", "manual"),
                        timestamp=note_el.findtext("timestamp", default=""),
                        text=note_el.findtext("text", default=""),
                        title=note_el.findtext("title", default=""),
                        description=note_el.findtext("description", default=""),
                        url=note_el.findtext("url", default=""),
                        search_term=note_el.findtext("search_term", default=""),
                        note_id=note_el.get("id", ""),
                    ).to_dict()
                )

        return {
            "success": True,
            "message": f"Found {len(notes)} note(s) for topic '{topic_name}'.",
            "topic": topic_name,
            "notes": notes,
        }

    def list_topics(self) -> Dict[str, object]:
        with self.lock:
            tree = self._read_tree()
            root = tree.getroot()
            topics = [topic.get("name", "") for topic in root.findall("topic")]

        return {
            "success": True,
            "message": f"Found {len(topics)} topic(s).",
            "topics": topics,
        }
