from fastapi import FastAPI, Request
from services.conversation import handle_message
import os
import logging
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.get("/webhook")
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

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    try:
        phone = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        text = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        handle_message(phone, text)
    except Exception as e:
        print("Erreur webhook:", e)
    return {"status": "received"}
