from fastapi import FastAPI
# from services.conversation import handle_message, parse_data
import os
import logging
from dotenv import load_dotenv
from routes import ticket_router, webhook_router, fees_router

load_dotenv()

app = FastAPI()

app.include_router(webhook_router)
app.include_router(fees_router)
app.include_router(ticket_router)

@app.get("/")
async def root():
    return {"message": "API en ligne"}