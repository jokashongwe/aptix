import requests
import os

PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID","")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN","")

# -------------------------------------------------------------
# 6️⃣ Envoi de messages vers WhatsApp Cloud API
# -------------------------------------------------------------
def send_text(to, text, phone_number_d_id=PHONE_NUMBER_ID, whatsapp_token=WHATSAPP_TOKEN):
    url = f"https://graph.facebook.com/v19.0/{phone_number_d_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=payload)

def send_custom_menu_buttons(to, buttons, body_text="Veuillez faire un choix :", phone_number_d_id=PHONE_NUMBER_ID, whatsapp_token=WHATSAPP_TOKEN):
    url = f"https://graph.facebook.com/v19.0/{phone_number_d_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json"
    }

    custom_buttons = []

    for button in buttons:
        custom_buttons.append({"type": "reply", "reply": {"id": button['id'], "title": button['title']}})

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": custom_buttons
            }
        }
    }
    requests.post(url, headers=headers, json=payload) 

def send_menu_buttons(to, phone_number_d_id=PHONE_NUMBER_ID, whatsapp_token=WHATSAPP_TOKEN):
    url = f"https://graph.facebook.com/v19.0/{phone_number_d_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
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
