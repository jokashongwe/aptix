import requests
import os

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

def send_message(phone: str, text: str):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(API_URL, headers=headers, json=data)

def send_image_message(phone: str, image_url: str, caption: str = None):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption
        }
    }
    requests.post(API_URL, headers=headers, json=data)

def send_image_buttons(phone: str, image_url: str, body: str, buttons: list):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "image",
                "image": {"link": image_url}
            },
            "body": {"text": body},
            "action": {"buttons": buttons}
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)

def send_buttons(phone: str, body: str, buttons: list):
    #print("Envoi des boutons")
    """
    buttons = [
        {"type": "reply", "reply": {"id": "bus", "title": "🚌 Ticket Bus"}},
        {"type": "reply", "reply": {"id": "avion", "title": "✈️ Billet Avion"}},
        {"type": "reply", "reply": {"id": "concert", "title": "🎤 Concert"}},
    ]
    """
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {"buttons": buttons}
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    #print("Response buttons: ", response.json())

def send_list_message(phone: str, header: str, body: str, footer: str, sections: list, button_text: str="Voir les options"):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header},
            "body": {"text": body},
            "footer": {"text": footer},
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    print("Response list message: ", response.json())

def send_concert_catalog(phone, catalog: str):
    print("Envoi du catalogue des concerts: ", catalog)
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "product_list",
            "header": {"type": "text", "text": "🎶 Événements disponibles"},
            "body": {"text": "Voici les concerts et événements à venir :"},
            "footer": {"text": "Powered by E-Ticket Bot"},
            "action": {
                "catalog_id": catalog,
                "sections": [
                    {
                        "title": "Concerts à venir",
                        "product_items": [
                            {"product_retailer_id": "ljg8oaeiv3"},
                            {"product_retailer_id": "q7adhw040q"},
                            {"product_retailer_id": "jh5t72jjk3"},
                            {"product_retailer_id": "a4axx5iulr"}
                        ]
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response.json())