from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
import psutil
import asyncio
import json
from datetime import datetime
from sqlalchemy import text
from db import engine, readings

# --- FastAPI App ---
app = FastAPI(title="Live Server Health Monitor")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
CPU_THRESHOLD = 80.0

# --- CPU Reading Function ---
def get_reading():
    """Get current CPU usage"""
    return psutil.cpu_percent(interval=1)

def check_alert(value, threshold=CPU_THRESHOLD):
    """Check if CPU value exceeds threshold"""
    return "warning" if value > threshold else "ok"

# --- Endpoints ---
@app.get("/")
async def root():
    return {
        "message": "Live Server Health Monitor API",
        "status": "running",
        "threshold": CPU_THRESHOLD
    }

@app.get("/cpu/current")
async def get_current_cpu():
    cpu_value = get_reading()
    status = check_alert(cpu_value)
    return {
        "value": cpu_value,
        "status": status,
        "threshold": CPU_THRESHOLD,
        "created_at": datetime.now().isoformat()
    }

@app.get("/readings")
async def get_readings(limit: int = Query(100, ge=1, le=1000)):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, value, status, created_at FROM readings ORDER BY id DESC LIMIT :limit"),
            {"limit": limit}
        )
        rows = result.fetchall()
        return [
            {
                "id": row[0],
                "value": row[1],
                "status": row[2],
                "created_at": row[3].isoformat() if row[3] else None
            }
            for row in rows
        ]

@app.get("/readings/stats")
async def get_stats():
    with engine.connect() as conn:
        count_result = conn.execute(text("SELECT COUNT(*) FROM readings"))
        total = count_result.scalar()
        
        stats_result = conn.execute(text("""
            SELECT 
                AVG(value) as avg_cpu,
                MAX(value) as max_cpu,
                MIN(value) as min_cpu,
                COUNT(CASE WHEN status = 'warning' THEN 1 END) as warning_count
            FROM readings
        """))
        stats = stats_result.fetchone()
        
        return {
            "total_readings": total,
            "avg_cpu": float(stats[0]) if stats[0] else 0,
            "max_cpu": float(stats[1]) if stats[1] else 0,
            "min_cpu": float(stats[2]) if stats[2] else 0,
            "warning_count": int(stats[3]) if stats[3] else 0,
            "threshold": CPU_THRESHOLD
        }

@app.post("/config/threshold")
async def set_threshold(threshold: float = Query(..., ge=10, le=100)):
    global CPU_THRESHOLD
    CPU_THRESHOLD = threshold
    return {
        "message": "Threshold updated",
        "new_threshold": CPU_THRESHOLD
    }

@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    await websocket.accept()
    print(f"✅ WebSocket connection established - {datetime.now()}")
    
    try:
        while True:
            cpu_value = get_reading()
            status = check_alert(cpu_value, CPU_THRESHOLD)
            timestamp = datetime.now()
            
            with engine.connect() as conn:
                stmt = readings.insert().values(
                    value=cpu_value,
                    status=status,
                    created_at=timestamp
                )
                result = conn.execute(stmt)
                conn.commit()
                inserted_id = result.inserted_primary_key[0]
            
            data = {
                "id": inserted_id,
                "value": cpu_value,
                "status": status,
                "threshold": CPU_THRESHOLD,
                "created_at": timestamp.isoformat()
            }
            await websocket.send_json(data)
            
            emoji = "⚠️" if status == "warning" else "✅"
            print(f"{emoji} CPU: {cpu_value:.1f}% | Status: {status} | ID: {inserted_id}")
            
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        print(f"❌ WebSocket connection closed - {datetime.now()}")
    except Exception as e:
        print(f"❌ Error: {e}")