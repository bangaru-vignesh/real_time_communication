# RealChat

RealChat is a scalable, real-time messaging application MVP built with FastAPI. It supports real-time private messaging via WebSockets, persistent chat history, and is designed to scale across multiple server nodes using Redis Pub/Sub.

## Features

- **Real-Time Messaging**: Instant messaging utilizing WebSockets.
- **Private Chats**: Direct 1-on-1 messaging between users.
- **Message Persistence**: Chat messages are stored in an SQLite database using SQLAlchemy and can be easily retrieved.
- **Chat History API**: Fetch the past messages between two users seamlessly.
- **Multi-Device Support**: A single user can be connected simultaneously from multiple devices/tabs, and real-time events are effectively broadcasted to all active connections.
- **Distributed Architecture ready**: Integrated with Redis Pub/Sub to route messages across multiple horizontally scaled backend servers.
- **Message Status Tracking**: Backend support for tracking if a message is `sent`, `delivered`, or `seen`.
- **Typing Indicators**: WebSocket routing support for "typing" events.

## Tech Stack

- **Python 3.x**
- **FastAPI**: Backend framework
- **Uvicorn**: ASGI Server
- **WebSockets**: Real-time communication protocol
- **SQLAlchemy & SQLite**: ORM and Database
- **Redis (aioredis)**: Cross-server message broker & Pub/Sub
- **Jinja2**: Templating engine for the UI

## Project Structure

```text
realchat/
├── app/
│   ├── core/
│   │   ├── config.py           # Application configurations (if any)
│   │   └── database.py         # SQLAlchemy engine and session setup
│   ├── models/
│   │   └── message.py          # SQLAlchemy DB models for messages
│   ├── routers/
│   │   └── chat.py             # FastAPI routes (WebSockets & REST endpoints)
│   ├── schemas/
│   │   └── message_schema.py   # Pydantic models for validation & serialization
│   ├── static/                 # Static assets (CSS, JS)
│   ├── templates/
│   │   └── chat.html           # Jinja2 HTML template for the chat client
│   ├── utils/
│   │   └── connection_manager.py # WebSocket & Redis connection manager
│   ├── __init__.py
│   └── main.py                 # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── realchat.db                 # Auto-generated SQLite Database
└── README.md                   # Project documentation
```

## Prerequisites

- **Python 3.8+**
- **Redis Server**: Make sure you have a Redis server running locally on `localhost:6379`. (You can run one using Docker: `docker run -p 6379:6379 -d redis`)

## Installation & Setup

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd realchat
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Make sure your Redis server is up and running.
2. Start the FastAPI server using Uvicorn:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Open your browser and navigate to the application:
   ```
   http://localhost:8000/
   ```

## Usage

1. Open the UI via `http://localhost:8000/`.
2. To test the chat, you can open two different browsers (or one normal and one incognito window).
3. In the first window, type your user ID (e.g., `user1`) and the receiver ID (e.g., `user2`), and click **Connect**.
4. In the second window, act as the receiver: type your ID (`user2`) and the receiver ID (`user1`), and click **Connect**.
5. Start sending messages. The messages will instantly appear on both screens and will be saved in the local database.
6. Re-connecting to the same user pair will load and display the full chat history.
