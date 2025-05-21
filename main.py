from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from starlette.responses import RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Only for dev. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/submit", response_class=JSONResponse)
async def submit(
    request: Request,
    twitter_id: List[str] = Form(...),
    agent_name: List[str] = Form(...),
):
    data = [
        {"twitter_id": tid, "agent_name": aname}
        for tid, aname in zip(twitter_id, agent_name)
    ]
    for item in data:
        print(f"Twitter ID: {item['twitter_id']}, Agent Name: {item['agent_name']}")
    return {"status": "success", "received_count": len(data), "data": data}
