from dotenv import load_dotenv
import os

load_dotenv()

# Configuration class
class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./health_monitor.db")
    CPU_THRESHOLD = float(os.getenv("CPU_THRESHOLD", 80.0))  # Alert at 80%
    WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", 8000))
    
config = Config()
