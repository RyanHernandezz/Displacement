import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from engine import Economy

# Initialize economy engine
economy = Economy(num_agents=400)
connected_clients = []
SIM_SPEED = 1.0
IS_PAUSED = False
sim_lock = asyncio.Lock()

async def simulation_loop():
    """Background task that runs the simulation and broadcasts state."""
    global SIM_SPEED, IS_PAUSED
    while True:
        # Determine how many ticks to run this frame
        ticks = max(1, int(SIM_SPEED))
        state = None
        
        try:
            async with sim_lock:
                if not IS_PAUSED:
                    latest_report = None
                    for _ in range(ticks):
                        state = economy.tick()
                        if state and state.get('metrics', {}).get('longitudinal_report'):
                            latest_report = state['metrics']['longitudinal_report']
                    
                    if latest_report and state:
                        state['metrics']['longitudinal_report'] = latest_report
            
            # Broadcast state
            if state and connected_clients:
                payload = json.dumps(state)
                await asyncio.gather(
                    *[client.send_text(payload) for client in connected_clients],
                    return_exceptions=True
                )
                # Clean up dead clients (state 3 = DISCONNECTED)
                connected_clients[:] = [c for c in connected_clients if not c.client_state.value == 3]
        except Exception as e:
            logging.error(f"Simulation loop error: {e}", exc_info=True)
            await asyncio.sleep(1.0)
            
        sleep_time = 1/30.0
        if SIM_SPEED < 1.0:
            sleep_time = (1/30.0) / max(0.1, SIM_SPEED)
            
        await asyncio.sleep(sleep_time)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(simulation_loop())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global economy, IS_PAUSED, SIM_SPEED
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle incoming control messages
            if message["type"] == "controls":
                async with sim_lock:
                    SIM_SPEED = float(message.get("sim_speed", SIM_SPEED))
                    
                    for key, val in message.items():
                        if key.startswith('ablation_'):
                            economy.ablations[key] = bool(val)
                
            elif message["type"] == "preset":
                async with sim_lock:
                    economy.trigger_experiment(message["preset"])
                
            elif message["type"] == "reset":
                async with sim_lock:
                    current_ablations = getattr(economy, 'ablations', {})
                    n_agents = int(message.get("num_agents", 400))
                    economy = Economy(num_agents=n_agents, ablations=current_ablations)
                
            elif message["type"] == "pause":
                async with sim_lock:
                    IS_PAUSED = True
                
            elif message["type"] == "play":
                async with sim_lock:
                    IS_PAUSED = False
                
            elif message["type"] == "toggle_pause":
                async with sim_lock:
                    IS_PAUSED = not IS_PAUSED
                
            elif message["type"] == "fetch_report":
                async with sim_lock:
                    report = economy.generate_longitudinal_report()
                await websocket.send_text(json.dumps({'type': 'longitudinal_report', 'data': report}))
                
            elif message["type"] == "run_projection":
                current_ablations = getattr(economy, 'ablations', {})
                n_agents = int(message.get("num_agents", 400))
                def _run_sim():
                    eco = Economy(num_agents=n_agents, ablations=current_ablations)
                    for _ in range(3000):
                        eco.tick()
                    return eco.generate_longitudinal_report()['generational']
                
                report = await asyncio.to_thread(_run_sim)
                await websocket.send_text(json.dumps({'type': 'projection_result', 'data': report}))
                    
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

@app.get("/")
async def get_index():
    from fastapi.responses import FileResponse
    return FileResponse("frontend/index.html")

import uvicorn
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)

