from fastapi import FastAPI
# from services.conversation import handle_message, parse_data
import os
import logging
from dotenv import load_dotenv
from routes import ticket_router, webhook_router, fees_router, auth_router, account_router
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

origins = [
    "https://aptix.afrimetrik.com",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(auth_router, prefix="/auth")
app.include_router(fees_router)
app.include_router(ticket_router)
app.include_router(account_router)

@app.get("/")
async def root():
    return {"message": "API en ligne"}