from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from starlette.responses import RedirectResponse
from urllib.parse import urlencode
from enum import Enum
from pymongo import MongoClient
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging
import sys
import uvicorn
from datetime import datetime


def setup_logger(name="twitterui") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    for handler in [
        logging.FileHandler("twitterui.log"),
        logging.StreamHandler(sys.stdout),
    ]:
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

logger = setup_logger()

logger.info("Server started")


class AgentType(str, Enum):
    investor = "investor"
    actor = "actor"
    actress = "actress"
    director = "director"
    script_writter = "script_writter"
    producer = "producer"
    technical_supporter_specialist = "technical_supporter_specialist"
    marketing_and_promotion_specialist = "marketing_and_promotion_specialist"


@dataclass
class MongoConfig:
    host: str = os.getenv("HOST")  # host should be set in .env file
    port: int = 8002
    username: str = "root"
    password: str = os.getenv("PASSWORD")  # password should be set in .env file
    auth_db: str = "admin"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Only for dev. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = MongoConfig()
client = AsyncIOMotorClient(
    host=config.host,
    port=config.port,
    username=config.username,
    password=config.password,
    authSource=config.auth_db,
)
db = client["fuss_agent"]
collection = db["tweets"]


async def add_records(twit_id: str, agent_type: str):
    try:
        # Insert a sample document (creates DB and collection if not exist)
        doc = {
            "tweetId": twit_id,
            "agentType": agent_type,
            "createdAt": datetime.now(),
            "status": "pending",
        }
        result = await collection.insert_one(doc)
        logger.info(f"Inserted with _id:{result.inserted_id}")
    except Exception as e:
        logger.error(f"Error inserting document: {e}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, status: str = None, message: str = None):
    return templates.TemplateResponse(
        "index.html", {"request": request, "status": status, "message": message}
    )


@app.post("/submit")
async def submit(
    request: Request,
    twitter_id: List[str] = Form(...),
    agent_name: List[str] = Form(...),
):
    try:
        if not twitter_id or not agent_name or len(twitter_id) != len(agent_name):
            msg = "Twitter ID and Agent Name are required and must match in count."
            return RedirectResponse(
                url=f"/?{urlencode({'status': 'error', 'message': msg})}",
                status_code=303,
            )

        # Validate each agent_name using the Enum
        for aname in agent_name:
            if aname not in AgentType._value2member_map_:
                msg = f"Invalid agent type: {aname}"
                return RedirectResponse(
                    url=f"/?{urlencode({'status': 'error', 'message': msg})}",
                    status_code=303,
                )

        data = [
            {"twitter_id": tid, "agent_name": aname}
            for tid, aname in zip(twitter_id, agent_name)
        ]
        for item in data:
            logger.info(f"Processing item: {item}")
            await add_records(item["twitter_id"], item["agent_name"])
            logger.info(
                f"Inserted Twitter ID: {item['twitter_id']}, Agent Name: {item['agent_name']}"
            )
        return RedirectResponse(
            url=f"/?{urlencode({'status': 'success', 'message': 'Data submitted successfully!'})}",
            status_code=303,
        )
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return RedirectResponse(
            url=f"/?{urlencode({'status': 'error', 'message': 'Internal server error.'})}",
            status_code=303,
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5006, log_level="info")
