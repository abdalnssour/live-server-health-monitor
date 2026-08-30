import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/metrics"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket!")
            print("📊 Receiving real CPU data with status...\n")
            
            for i in range(10):
                response = await websocket.recv()
                data = json.loads(response)
                
                # Use 'value' field (not 'cpu_percent')
                cpu = data.get('value', 0)
                status = data.get('status', 'unknown')
                threshold = data.get('threshold', 80)
                record_id = data.get('id', 'N/A')
                
                emoji = "⚠️" if status == "warning" else "✅"
                print(f"[{i+1}] {emoji} CPU: {cpu:5.1f}% | Status: {status:7} | ID: {record_id} | Threshold: {threshold}%")
            
            print("\n✅ WebSocket test passed!")
            print("📈 Real CPU data is streaming with alert status.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure the server is running:")
        print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    asyncio.run(test_websocket())
