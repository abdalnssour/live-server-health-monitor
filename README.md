
# 🖥️ Live Server Health Monitor

A real-time CPU monitoring dashboard with WebSocket streaming, PostgreSQL database, and alert system.

## 📋 Overview

This project monitors your computer's CPU usage in real-time, saves readings to a PostgreSQL database, flags high CPU usage, and displays everything on a live React dashboard with WebSocket streaming.

### 🎯 Features

- **Real-time CPU Monitoring** - Live CPU updates every 2 seconds
- **WebSocket Streaming** - No page refresh needed
- **Alert System** - Automatic warning when CPU exceeds threshold (default 80%)
- **PostgreSQL Storage** - All readings saved with status tracking
- **Beautiful Dashboard** - Modern dark theme with animations
- **Warning Log** - Dedicated list of high CPU events
- **Dynamic Threshold** - Change alert threshold via API
- **History Endpoint** - Fetch recent readings via HTTP

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Python web framework
- **SQLAlchemy Core** - Database ORM
- **PostgreSQL** - Database
- **Alembic** - Database migrations
- **Psutil** - System monitoring
- **WebSockets** - Real-time communication

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **WebSocket API** - Real-time data streaming
- **CSS3** - Modern animations and styling

## 📁 Project Structure
live-server-health-monitor/
├── backend/
│ ├── main.py # FastAPI app with WebSocket
│ ├── db.py # SQLAlchemy Core config
│ ├── requirements.txt # Python dependencies
│ ├── alembic/ # Database migrations
│ └── venv/ # Virtual environment
└── frontend/
├── src/
│ ├── App.jsx # React dashboard
│ ├── App.css # Styling
│ ├── main.jsx # Entry point
│ └── index.css # Global styles
├── package.json # Dependencies
└── vite.config.js # Vite config