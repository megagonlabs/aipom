import traceback
from pathlib import Path
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agent_registry import AgentRegistry
from controller import Controller
from custom_types import Message, SystemMessage, UIPlan
from plan import PlanConverter
from utils import MsgType, Status, current_time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:4173",  # vite preview
        "http://localhost:5173",  # vite dev
        "http://localhost:8000",  # fastapi
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# dict to store controller for each session
sessions: dict[str, dict] = {}


@app.get("/start-session")
def start_session():
    """Starts a new session and returns a session ID"""
    session_id = str(uuid4())
    sessions[session_id] = Controller()
    print(f"[{current_time()}] Session started: {session_id}")
    print(sessions)
    return {"session_id": session_id}


@app.get("/agent-registry")
def get_agent_registry():
    """Returns agent list"""
    agent_registry = AgentRegistry().get_agents_list()
    return {"agent_registry": agent_registry}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    if session_id not in sessions:
        await websocket.send_json(
            {
                "type": MsgType.STATUS,
                "data": {
                    "action": "session",
                    "status": Status.ERROR,
                    "message": "Invalid session ID",
                },
            }
        )
        await websocket.close()
        return

    controller = sessions[session_id]
    print(f"[{current_time()}] Client connected to session {session_id}")

    try:
        while True:
            message = await websocket.receive_json()
            msgType = message.get("type")
            msgData = message.get("data")
            plan = system_response = chat_history = None

            if msgType == MsgType.CONNECTION:
                print(
                    f"[{current_time()}] Connection state changed: {msgData['state']}"
                )
            else:
                print(f"[{current_time()}] Message received:", message)
                await _send_status(websocket, msgType, Status.STARTING)

                if msgType == MsgType.CHAT:
                    plan, system_response = controller.process_user_message(msgData)
                elif msgType == MsgType.INTERACTION:
                    plan, system_response = controller.process_ui_interaction(msgData)
                elif msgType == MsgType.EXECUTE:
                    plan, system_response = controller.process_execution(msgData)
                elif msgType == MsgType.RESET:
                    plan, system_response, chat_history = controller.reset()

                print("plan:", plan)
                # if plan:
                    # print("plan:", plan.nodes(data=True))
                    # print("plan:", plan.edges(data=True, keys=True))
                    # a = PlanConverter.dag_to_UIPlan(plan)
                    # print("plan-convert", a)
                    # b = PlanConverter.dag_from_UIPlan(a)
                    # print("plan-back", b.nodes(data=True))
                    # print("plan-back", b.edges(data=True, keys=True))
                print("response:", system_response)
                if plan:
                    await _send_plan(websocket, PlanConverter.dag_to_UIPlan(plan))
                if system_response:
                    await _send_chat(websocket, system_response, chat_history)

                await _send_status(websocket, msgType, Status.FINISHED)

    except WebSocketDisconnect:
        print(f"[{current_time()}] Client disconnected from session: {session_id}")
    except Exception as e:
        print(f"[{current_time()}] Error:", e, traceback.format_exc())
    finally:
        await websocket.close()
        print(f"[{current_time()}] WebSocket closed for session: {session_id}")


async def _send_status(websocket: WebSocket, action: str, status: str) -> None:
    await websocket.send_json(
        {"type": MsgType.STATUS, "data": {"action": action, "status": status}}
    )


async def _send_chat(
    websocket: WebSocket,
    system_response: SystemMessage,
    chat_history: list[Message] = [],
) -> None:
    data = {"system_response": system_response}
    if chat_history:
        data["chat_history"] = chat_history
    await websocket.send_json({"type": MsgType.CHAT, "data": data})


async def _send_plan(websocket: WebSocket, plan: UIPlan) -> None:
    await websocket.send_json({"type": MsgType.PLAN, "data": {"plan": plan}})


dist_dir_path = "frontend/dist"
Path(dist_dir_path).mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=dist_dir_path, html=True), name="dist")

if __name__ == "__main__":
    uvicorn.run("server:app", reload=True)
