# CT30A3401 Assignment 3 - RPC Notebook System

This repository contains my solution for **CT30A3401 Assignment 3**.

The project implements a simple **distributed notebook system** using **Python XML-RPC**.  
It includes a **client**, a **server**, a local **XML database**, and **Wikipedia API integration** for the higher grade requirements.

---

## Features

- **Client-server communication through XML-RPC**
- **Add notes** with:
  - topic
  - text
  - timestamp
- **Get notes by topic**
- **List all topics**
- If a topic already exists, the new note is **appended**
- If a topic does not exist, a **new XML entry** is created
- Local mock database stored in **XML**
- Server can handle **multiple client requests** using threading
- **Wikipedia search**
- **Append Wikipedia results to an existing topic**
- Basic **failure handling** for invalid input and missing topics

---

## Project Structure

- `client.py` - client application for user interaction
- `server.py` - XML-RPC server
- `rpc_service.py` - remote methods used by the server
- `notebook_database.py` - XML database handling
- `wikipedia_api.py` - Wikipedia API communication
- `database.xml` - local XML mock database

---

## Requirements

- Python 3.10+  
- Standard Python libraries used in most parts of the project
- Internet connection required for Wikipedia search

---

## How to Run

### 1. Start the server

Open a terminal in the project folder and run:

```bash
python server.py
````

The server will start on:

```text
http://127.0.0.1:8000/RPC2
```

### 2. Start the client

Open another terminal in the same project folder and run:

```bash
python client.py
```

---

## Client Menu Functions

1. Add note
2. Get notes by topic
3. List topics
4. Search Wikipedia
5. Search Wikipedia and append to topic
6. Ping server
7. Exit

---

## Example Demo Flow

A simple demo for the assignment video:

1. Start `server.py`
2. Start `client.py`
3. Add a note to topic `Distributed Systems`
4. Add another note to the same topic
5. Query notes by topic
6. Open `database.xml` and show stored data
7. Search Wikipedia for `Remote procedure call`
8. Append Wikipedia data to `Distributed Systems`
9. Query the topic again
10. Demonstrate failure handling with a missing topic

---

## Assignment Requirements Covered

This project covers the following assignment requirements:

* **RPC-based communication** between client and server
* Local **XML mock database**
* Add and retrieve notes by topic
* **Append** to existing topics
* Create **new XML entries** for new topics
* Handle **multiple client requests**
* Query **Wikipedia API**
* Append Wikipedia result to an existing topic
* Show **failure handling** without crashing

---

## Notes

* The client does not modify the XML file directly.
* All database operations are handled by the server.
* The XML file is used as a simple local database mock.
* Wikipedia integration is included for the full mark range of the assignment.

---

## Submission

This submission includes:

- GitHub repository: https://github.com/wenrui28/CT30A3401-AS3
- Video demonstration: https://youtu.be/80IsNmbriZM
---

## Author

Wenrui Xing
