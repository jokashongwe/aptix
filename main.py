from fastapi import FastAPI, Request
import requests, os
from dotenv import load_dotenv
import logging

from datetime import datetime



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
        send_text(user_id, "🚌 Entrez la **ville de départ** :")
    elif choice_id == "avion":
        user_states[user_id] = {"type": "avion", "step": "depart"}
        send_text(user_id, "✈️ Entrez la **ville de départ** :")
    elif choice_id == "concert":
        user_states[user_id] = {"type": "concert", "step": "nom"}
        send_text(user_id, "🎵 Quel **événement** souhaitez-vous réserver ?")
    else:
        send_menu_buttons(user_id)

# -------------------------------------------------------------
# 5️⃣ Conversations par type de billet
# -------------------------------------------------------------
def handle_bus_conversation(user_id, text, state, step):
    if step == "depart":
        state["depart"] = text.title()
        state["step"] = "destination"
        send_text(user_id, "🚏 Entrez la **ville de destination** :")
    elif step == "destination":
        state["destination"] = text.title()
        state["step"] = "date"
        send_text(user_id, "📅 Quelle **date** souhaitez-vous voyager ? (JJ/MM/AAAA)")
    elif step == "date":
        state["date"] = text
        state["step"] = "confirm"
        send_text(user_id, f"🚌 {state['depart']} → {state['destination']} le {state['date']}.\nSouhaitez-vous confirmer et payer ? (oui / non)")
    elif step == "confirm":
        if "oui" in text:
            send_text(user_id, "💳 Voici votre lien de paiement : https://paiement.exemple.com")
        else:
            send_text(user_id, "❌ Réservation annulée. Tapez *menu* pour recommencer.")
            user_states[user_id] = {}

def handle_avion_conversation(user_id, text, state, step):
    if step == "depart":
        state["depart"] = text.title()
        state["step"] = "destination"
        send_text(user_id, "🛫 Entrez la **ville de destination** :")
    elif step == "destination":
        state["destination"] = text.title()
        state["step"] = "date"
        send_text(user_id, "📅 Quelle **date de vol** souhaitez-vous ?")
    elif step == "date":
        state["date"] = text
        state["step"] = "confirm"
        send_text(user_id, f"✈️ Vol {state['depart']} → {state['destination']} le {state['date']}.\nSouhaitez-vous confirmer et payer ? (oui / non)")
    elif step == "confirm":
        if "oui" in text:
            send_text(user_id, "💳 Voici votre lien de paiement : https://paiement.exemple.com")
        else:
            send_text(user_id, "❌ Réservation annulée. Tapez *menu* pour recommencer.")
            user_states[user_id] = {}

def handle_concert_conversation(user_id, text, state, step):
    if step == "nom":
        state["event"] = text.title()
        state["step"] = "lieu"
        send_text(user_id, "📍 Où aura lieu cet événement ?")
    elif step == "lieu":
        state["lieu"] = text.title()
        state["step"] = "date"
        send_text(user_id, "📅 Quelle **date** pour cet événement ?")
    elif step == "date":
        state["date"] = text
        state["step"] = "confirm"
        send_text(user_id, f"🎫 {state['event']} à {state['lieu']} le {state['date']}.\nSouhaitez-vous confirmer et payer ? (oui / non)")
    elif step == "confirm":
        if "oui" in text:
            send_text(user_id, "💳 Voici votre lien de paiement : https://paiement.exemple.com")
        else:
            send_text(user_id, "❌ Réservation annulée. Tapez *menu* pour recommencer.")
            user_states[user_id] = {}

# -------------------------------------------------------------
# 6️⃣ Envoi de messages vers WhatsApp Cloud API
# -------------------------------------------------------------
def send_text(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=payload)

def send_menu_buttons(to):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "👋 Bonjour ! Que souhaitez-vous réserver ?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "bus", "title": "🚌 Ticket Bus"}},
                    {"type": "reply", "reply": {"id": "avion", "title": "✈️ Billet Avion"}},
                    {"type": "reply", "reply": {"id": "concert", "title": "🎵 Concert/Événement"}},
                ]
            }
        }
    }
    requests.post(url, headers=headers, json=payload)

# -------------------------------------------------------------
# Démarrage du serveur
# -------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)