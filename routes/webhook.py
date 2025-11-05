from fastapi import APIRouter, Request
from db import bus_options, airplane_options, concert_options
from datetime import datetime
import logging
import os
from services.conversation import handle_message, parse_data
from services.fees_conversation import handle_fees_message

webhook_router = APIRouter()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
CHAT_OPTION = os.getenv("CHAT_OPTION", "TICKET")

@webhook_router.get("/webhook")
async def verify(request: Request):
    logging.info("Vérification du webhook")
    try:
        params = request.query_params
        if params.get("hub.verify_token") == VERIFY_TOKEN:
            return int(params.get("hub.challenge"))
        return {"error": "invalid token"}
    except Exception as e:
        logging.error(f"Erreur lors de la vérification du webhook: {e}")
        return {"error": "internal error"}

@webhook_router.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    try:
        raw_data = data["entry"][0]["changes"][0]["value"]
        if not raw_data.get("messages"):
            return
        field_data  = raw_data["messages"][0]
        
        phone, text = parse_data(field_data)
        if CHAT_OPTION == "TICKET":
            handle_message(phone, text)
        else: 
            print(f"Field Data: {field_data}")
            await handle_fees_message(phone, text)
    except Exception as e:
        print("Erreur webhook: ", e)
    return {"status": "received"}