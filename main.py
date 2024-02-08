from DB_find import *
from datetime import *
from fastapi import FastAPI, Request, Form,HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from pydantic import BaseModel, Field
from typing import Annotated
# import threading, time

thread_Count = 0

app = FastAPI()
templates = Jinja2Templates(directory="templates")

client = MongoClient('mongodb://zxc0214:asd64026@3.35.10.100', 27017)
db = client.PB_Auto
collection  = db.users

class WebSocketManager:
    def __init__(self):
        self.connections = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.connections:
            await connection.send_text(message)

manager = WebSocketManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

#############################################################################################################################################

# 클라이언트에서 호출할 엔드포인트 추가
@app.post("/toggle_status/{ID}")
async def toggle_status(ID: str):
    # MongoDB에서 해당 계좌번호의 사용자 정보 조회
    user = collection.find_one({"ID": ID})

    if user:
        # 사용자의 OnOff 필드 값을 토글
        new_status = not user["Userble"]

        # MongoDB에서 사용자 정보 업데이트
        collection.update_one(
            {"ID": ID},
            {"$set": {"Userble": new_status}}
        )

        return {"status": "success", "new_status": new_status}

    return {"status": "error", "message": "User not found"}
#완료
@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})
#완료
@app.post("/main/", response_class=HTMLResponse)
async def main_login(request: Request, password: str = Form(...)):
    if password == "5555":
        return templates.TemplateResponse("main_logged_in.html", {"request": request})
    else:
        raise HTTPException(status_code=401, detail="Incorrect password")

#완료
@app.get("/all_members/", response_class=HTMLResponse)
async def all_members(request: Request):
    # Get all members from MongoDB
    all_members = list(collection.find({}))

    return templates.TemplateResponse("all_members.html", {"request": request, "members": all_members})
#완료
@app.post("/delete_member/{ID}")
async def delete_member(ID: str):
    # MongoDB에서 해당 계좌번호의 사용자 정보 조회
    user = collection.find_one({"ID": ID})

    if user:
        # 사용자 정보 삭제
        collection.delete_one({"ID": ID})

        # WebSocket을 통해 클라이언트에게 삭제 이벤트를 알림
        await manager.broadcast({"event": "member_deleted", "ID": ID})

        return {"status": "success", "message": "Member deleted"}

    return {"status": "error", "message": "User not found"}

##완료
# 회원 등록 페이지 (폼 표시)
@app.get("/register", response_class=HTMLResponse)
async def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register/", response_class=HTMLResponse)
async def register(
    request: Request,
    ID: str = Form(...),
    PW: str = Form(...),
    APIKEY: str = Form(...),
):
    # Check if AccountNumber already exists
    if collection.find_one({"ID": ID}):
        raise HTTPException(status_code=400, detail="동일한 계좌번호가 이미 존재합니다.")
    
    # MongoDB에 회원 정보 저장
    new_member = {'ID':str(ID),'PW':str(PW),'APIKEY':str(APIKEY),'Userble':True,}
    
    collection.insert_one(new_member)

    return templates.TemplateResponse(
        "register_result.html",
        {"request": request, "ID": str(ID), "PW": str(PW),'APIKEY':str(APIKEY)},
    )

#############################################################################################################################################
