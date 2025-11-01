from db import users
from services.whatsapp import send_message, send_buttons

def handle_message(phone: str, text: str):
    user = users.find_one({"phone": phone})
    
    if not user:
        # Nouveau client
        users.insert_one({"phone": phone, "step": "menu"})
        send_buttons(phone, "Bienvenue sur *E-Ticket Bot* 🎟️\nQue souhaitez-vous acheter ?", [
            {"type": "reply", "reply": {"id": "bus", "title": "🚌 Ticket Bus"}},
            {"type": "reply", "reply": {"id": "avion", "title": "✈️ Billet Avion"}},
            {"type": "reply", "reply": {"id": "concert", "title": "🎤 Concert"}},
        ])
        return

    step = user["step"]

    # Gestion du menu principal
    if step == "menu":
        if text.lower() in ["bus", "🚌 ticket bus"]:
            users.update_one({"phone": phone}, {"$set": {"step": "bus_depart"}})
            send_message(phone, "🚌 Très bien ! Quel est votre lieu de départ ?")
        elif text.lower() in ["avion", "✈️ billet avion"]:
            users.update_one({"phone": phone}, {"$set": {"step": "avion_depart"}})
            send_message(phone, "✈️ Super ! Depuis quel aéroport partez-vous ?")
        elif text.lower() in ["concert", "🎤 concert"]:
            users.update_one({"phone": phone}, {"$set": {"step": "concert_nom"}})
            send_message(phone, "🎶 Quel concert ou événement souhaitez-vous réserver ?")
        else:
            send_message(phone, "Veuillez choisir une option valide.")

    elif step == "bus_depart":
        users.update_one({"phone": phone}, {"$set": {"step": "bus_arrivee", "data.depart": text}})
        send_message(phone, "Et votre destination ?")

    elif step == "bus_arrivee":
        users.update_one({"phone": phone}, {"$set": {"step": "bus_date", "data.arrivee": text}})
        send_message(phone, "Pour quelle date souhaitez-vous voyager ? (ex: 2025-11-05)")

    elif step == "bus_date":
        users.update_one({"phone": phone}, {"$set": {"step": "menu"}})
        send_message(phone, f"✅ Votre demande de billet de bus de {user['data']['depart']} à {user['data']['arrivee']} pour le {text} a été enregistrée.")
        send_message(phone, "Souhaitez-vous faire une autre réservation ?")
        send_buttons(phone, "Choisissez une catégorie :", [
            {"type": "reply", "reply": {"id": "bus", "title": "🚌 Ticket Bus"}},
            {"type": "reply", "reply": {"id": "avion", "title": "✈️ Billet Avion"}},
            {"type": "reply", "reply": {"id": "concert", "title": "🎤 Concert"}},
        ])
