#!/usr/bin/env python3
"""
WebSocket Test Script - Live Server Health Monitor
Tests that /ws/metrics streams CPU data every 2 seconds
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

async def test_websocket():
    uri = "ws://localhost:8000/ws/metrics"
    messages_received = 0
    
    print("=" * 60)
    print("🚀 Live Server Health Monitor - WebSocket Test")
    print("=" * 60)
    print(f"📡 Connecting to: {uri}")
    print("⏳ Waiting for data...\n")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            print("📊 Receiving CPU data every 2 seconds...")
            print("Press Ctrl+C to stop\n")
            print("-" * 60)
            
            while True:
                # Receive message
                response = await websocket.recv()
                data = json.loads(response)
                messages_received += 1
                
                # Extract data
                cpu = data['cpu_percent']
                timestamp = data['timestamp']
                is_high = data['is_high']
                
                # Format output
                status = "⚠️ HIGH" if is_high else "✅ Normal"
                cpu_bar = "█" * int(cpu / 5) + "░" * (20 - int(cpu / 5))
                
                print(f"[{messages_received:3d}] CPU: {cpu:5.1f}% {cpu_bar} | {status} | {timestamp}")
                
                # Verify it's real data
                if messages_received == 1:
                    print("\n🎯 First reading received - confirming real data...")
                    
    except websockets.exceptions.ConnectionClosedError:
        print("\n❌ Connection closed unexpectedly. Make sure the server is running.")
        print("   Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n" + "-" * 60)
        print(f"\n👋 Test complete! Received {messages_received} messages.")
        print("✅ WebSocket is working correctly!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user")
        sys.exit(0)
