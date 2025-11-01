from fastapi import FastAPI, Request
import requests, os
from dotenv import load_dotenv
import logging
from datetime import datetime
from chat.utils.messaging import send_text, send_menu_buttons, send_custom_menu_buttons
from chat.handlers.conv_handler import handle_bus_conversation, handle_avion_conversation, handle_concert_conversation

load_dotenv()

app = FastAPI()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

filename = f"whatsapp_{datetime.now().strftime("%d%m%Y")}.log"
logging.basicConfig(filename=filename, filemode='a',
                    format="%(asctime)s, %(msecs)d %(name)s %(levelname)s: %(message)s",
                    datefmt="%H:%M:%S",
                    level=logging.DEBUG)

# Mémoire temporaire pour stocker l'état utilisateur
user_states = {}

# -------------------------------------------------------------
# 1️⃣ Vérification du webhook (nécessaire pour Meta)
# -------------------------------------------------------------
@app.get("/webhook")
async def verify(request: Request):
    logging.info("Vérification du webhook")
    params = request.query_params
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge"))
    return {"error": "invalid token"}

# -------------------------------------------------------------
# 2️⃣ Réception des messages entrants
# -------------------------------------------------------------
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    # Vérifie que le message vient bien d'un utilisateur WhatsApp
    if "messages" in data["entry"][0]["changes"][0]["value"]:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        user_id = msg["from"]
        logging.info(f"message de {user_id}: {msg}")
        # Cas 1 : clic sur bouton interactif
        if msg.get("interactive"):
            choice_id = msg["interactive"]["button_reply"]["id"]
            handle_choice(user_id, choice_id)
            return {"status": "ok"}

        # Cas 2 : texte normal
        text = msg.get("text", {}).get("body", "").lower()
        handle_text_message(user_id, text)

    return {"status": "received"}

# -------------------------------------------------------------
# 3️⃣ Gérer message texte classique
# -------------------------------------------------------------
def handle_text_message(user_id: str, text: str):
    if text in ["menu", "bonjour", "salut"]:
        send_menu_buttons(user_id)
    else:
        state = user_states.get(user_id, {})
        if not state:
            send_menu_buttons(user_id)
            return

        step = state.get("step")

        if state["type"] == "bus":
            handle_bus_conversation(user_id, text, state, step)
        elif state["type"] == "avion":
            handle_avion_conversation(user_id, text, state, step)
        elif state["type"] == "concert":
            handle_concert_conversation(user_id, text, state, step)

# -------------------------------------------------------------
# 4️⃣ Gérer les boutons du menu principal
# -------------------------------------------------------------
def handle_choice(user_id: str, choice_id: str):
    if choice_id == "bus":
        user_states[user_id] = {"type": "bus", "step": "depart"}
        #send_text(user_id, "🚌 Entrez la **ville de départ** :")
        send_custom_menu_buttons(
            to=user_id,
            buttons=[
                {"id": "Kinshasa", "title": "Kinshasa"},
                {"id": "Boma", "title": "Boma"},
                {"id": "Matadi", "title": "Matadi"}
            ],
            body_text="🚌 Sélectionnez la **ville de départ** :"
        )
    elif choice_id == "avion":
        user_states[user_id] = {"type": "avion", "step": "depart"}
        send_text(user_id, "✈️ Entrez la **ville de départ** :")
    elif choice_id == "concert":
        user_states[user_id] = {"type": "concert", "step": "nom"}
        send_text(user_id, "🎵 Quel **événement** souhaitez-vous réserver ?")
    else:
        send_menu_buttons(user_id)



# -------------------------------------------------------------
# Démarrage du serveur
# -------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)