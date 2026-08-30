from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, SessionLocal
from app.models import CPUUsage, Base
from app.config import config
import psutil
import asyncio
import json
from datetime import datetime
from typing import List

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Live Server Health Monitor")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Live Server Health Monitor API"}

@app.get("/cpu/history")
async def get_cpu_history(limit: int = 100):
    """Get historical CPU data"""
    db = SessionLocal()
    try:
        records = db.query(CPUUsage).order_by(CPUUsage.timestamp.desc()).limit(limit).all()
        return [record.to_dict() for record in records]
    finally:
        db.close()

@app.post("/cpu/current")
async def save_current_cpu():
    """Save current CPU usage to database"""
    cpu_percent = psutil.cpu_percent(interval=1)
    is_high = cpu_percent > config.CPU_THRESHOLD
    
    db = SessionLocal()
    try:
        record = CPUUsage(cpu_percent=cpu_percent, is_high=is_high)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.to_dict()
    finally:
        db.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")
    
    try:
        while True:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            is_high = cpu_percent > config.CPU_THRESHOLD
            
            # Save to database
            db = SessionLocal()
            try:
                record = CPUUsage(cpu_percent=cpu_percent, is_high=is_high)
                db.add(record)
                db.commit()
                db.refresh(record)
                
                # Send to client
                await websocket.send_json(record.to_dict())
            finally:
                db.close()
                
            # Wait before next reading
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        print("WebSocket connection closed")
