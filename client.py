from __future__ import annotations

import argparse
import sys
import xmlrpc.client


def print_separator() -> None:
    print("-" * 72)


def print_notes(result: dict) -> None:
    if not result.get("success"):
        print(f"[ERROR] {result.get('message', 'Unknown error')}")
        return

    print(f"Topic: {result.get('topic', '')}")
    print(f"{result.get('message', '')}")
    print_separator()

    for index, note in enumerate(result.get("notes", []), start=1):
        print(f"Note #{index}")
        print(f"Source     : {note.get('source', '')}")
        print(f"Timestamp  : {note.get('timestamp', '')}")
        if note.get("search_term"):
            print(f"Search term: {note.get('search_term', '')}")
        if note.get("title"):
            print(f"Title      : {note.get('title', '')}")
        if note.get("description"):
            print(f"Description: {note.get('description', '')}")
        if note.get("url"):
            print(f"URL        : {note.get('url', '')}")
        print(f"Text       : {note.get('text', '')}")
        print_separator()


def interactive_menu(proxy: xmlrpc.client.ServerProxy) -> None:
    while True:
        print("\n===== RPC Notebook Client =====")
        print("1. Add note")
        print("2. Get notes by topic")
        print("3. List topics")
        print("4. Search Wikipedia")
        print("5. Search Wikipedia and append to topic")
        print("6. Ping server")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                topic = input("Topic: ").strip()
                text = input("Text: ").strip()
                timestamp = input("Timestamp (press Enter for current time): ").strip() or None
                result = proxy.add_note(topic, text, timestamp)
                print(result.get("message", result))

            elif choice == "2":
                topic = input("Topic to search: ").strip()
                result = proxy.get_notes_by_topic(topic)
                print_notes(result)

            elif choice == "3":
                result = proxy.list_topics()
                if result.get("success"):
                    print(result.get("message", ""))
                    for topic in result.get("topics", []):
                        print(f"- {topic}")
                else:
                    print(result.get("message", "Unknown error"))

            elif choice == "4":
                search_term = input("Wikipedia search term: ").strip()
                result = proxy.search_wikipedia(search_term)
                if result.get("success"):
                    print(f"Title      : {result.get('title', '')}")
                    print(f"Description: {result.get('description', '')}")
                    print(f"URL        : {result.get('url', '')}")
                else:
                    print(result.get("message", "Unknown error"))

            elif choice == "5":
                topic = input("Topic to append to: ").strip()
                search_term = input("Wikipedia search term: ").strip()
                result = proxy.append_wikipedia_to_topic(topic, search_term)
                print(result.get("message", result))

            elif choice == "6":
                result = proxy.ping()
                print(result.get("message", result))
                print(f"Server time: {result.get('timestamp', '')}")

            elif choice == "0":
                print("Goodbye.")
                break

            else:
                print("Invalid option. Please try again.")

        except xmlrpc.client.Fault as fault:
            print(f"[XML-RPC FAULT] {fault}")
        except ConnectionRefusedError:
            print("[ERROR] Could not connect to the server. Is server.py running?")
        except OSError as exc:
            print(f"[NETWORK ERROR] {exc}")
        except KeyboardInterrupt:
            print("\nClient interrupted by user.")
            break
        except Exception as exc:
            print(f"[UNEXPECTED ERROR] {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="XML-RPC notebook client")
    parser.add_argument("--host", default="127.0.0.1", help="Server host address")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    url = f"http://{args.host}:{args.port}/RPC2"
    print(f"Connecting to {url}")

    try:
        proxy = xmlrpc.client.ServerProxy(url, allow_none=True)
        print(proxy.ping().get("message", "Connected."))
    except Exception as exc:
        print(f"Failed to connect to server: {exc}")
        sys.exit(1)

    interactive_menu(proxy)


if __name__ == "__main__":
    main()
