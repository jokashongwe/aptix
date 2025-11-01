from db import users
from services.whatsapp import send_message, send_buttons
from datetime import date
from services.offer import get_destinations, get_departure_locations, get_prices_with_company

def parse_data(data: dict):
    if data is None:
        return {}
    
    if data.get("type") == "interactive":
        phone = data["from"]
        text = data["interactive"]["button_reply"]["id"]
        return phone, text
        # text message
    phone = data["from"]
    text = data["text"]["body"]
    return phone, text
    # text message


def handle_message(phone: str, text: str):
    print(f"Handling message from {phone}: {text}")
    user = users.find_one({"phone": phone})
    
    if not user:
        # Nouveau client
        users.insert_one({"phone": phone, "step": "menu",  "created_at": date.today().isoformat()})
        send_buttons(phone, "Bienvenue sur *E-Ticket Bot* 🎟️\nQue souhaitez-vous acheter ?", [
            {"type": "reply", "reply": {"id": "bus", "title": "🚌 Ticket Bus"}},
            {"type": "reply", "reply": {"id": "avion", "title": "✈️ Billet Avion"}},
            {"type": "reply", "reply": {"id": "concert", "title": "🎤 Concert"}},
        ])
        return

    step = user["step"]
    print(f"Handling message step: {step}")
    # Gestion du menu principal
    text = text.strip()

    if step == "menu" and text.lower() not in ["bus", "avion", "concert"]:
        send_buttons(phone, "Bienvenue sur *E-Ticket Bot* 🎟️\nQue souhaitez-vous acheter ?", [
            {"type": "reply", "reply": {"id": "bus", "title": "🚌 Ticket Bus"}},
            {"type": "reply", "reply": {"id": "avion", "title": "✈️ Billet Avion"}},
            {"type": "reply", "reply": {"id": "concert", "title": "🎤 Concert"}},
        ])
        return

    if step == "menu":
        if text.lower() in ["bus", "🚌 ticket bus"]:
            users.update_one({"phone": phone}, {"$set": {"step": "bus_depart"}})
            departure_list = get_departure_locations(type="bus")
            departure_buttons = [{"type": "reply", "reply": {"id": loc, "title": loc}} for loc in departure_list]
            send_buttons(phone, "🚌 Très bien ! Quel est votre lieu de départ ?", departure_buttons)
            #send_message(phone, "🚌 Très bien ! Quel est votre lieu de départ ?")
        elif text.lower() in ["avion", "✈️ billet avion"]:
            users.update_one({"phone": phone}, {"$set": {"step": "avion_depart"}})
            departure_list = get_departure_locations(type="avion")
            departure_buttons = [{"type": "reply", "reply": {"id": loc, "title": loc}} for loc in departure_list]
            send_buttons(phone, "🚌 Très bien ! Quel est votre lieu de départ ?", departure_buttons)
        elif text.lower() in ["concert", "🎤 concert"]:
            users.update_one({"phone": phone}, {"$set": {"step": "concert_nom"}})
            send_message(phone, "🎶 Quel concert ou événement souhaitez-vous réserver ?")
        else:
            send_message(phone, "Veuillez choisir une option valide.")

    elif step.startswith("bus_"):
        handle_bus_conversation(phone, text, user, step)
    elif step.startswith("avion_"):
        handle_airplane_conversation(phone, text, user, step)
    elif step.startswith("concert_"):
        handle_concert_conversation(phone, text, user, step)

def handle_bus_conversation(phone: str, text: str, user: dict, step: str):
    step = user["step"]
    if step == "bus_depart":
        users.update_one({"phone": phone}, {"$set": {"step": "bus_arrivee", "data.depart": text}})
        destination_list = get_destinations(type="bus")
        destination_buttons = [{"type": "reply", "reply": {"id": loc, "title": loc}} for loc in destination_list]
        send_buttons(phone, "🚌 Très bien ! Quel est votre lieu de départ ?", destination_buttons)

    elif step == "bus_arrivee":
        users.update_one({"phone": phone}, {"$set": {"step": "bus_nbplace", "data.arrivee": text}})
        send_message(phone, "Combien de places souhaitez-vous réserver ?")
        #Pour quelle date souhaitez-vous voyager ? (ex: 2025-11-05)
    elif step == "bus_nbplace":
        users.update_one({"phone": phone}, {"$set": {"step": "bus_date", "data.nbplace": text}})
        send_message(phone, "Pour quelle date souhaitez-vous voyager ? (ex: 2025-11-05)")    

    elif step == "bus_date":
        users.update_one({"phone": phone}, {"$set": {"step": "bus_end", "data.datedepart": text}})
        send_buttons(phone, f"Confirmez vous votre réservation de {user['data']['nbplace']} places au départ de {user['data']['depart']} pour {user['data']['arrivee']} ?", [
            {"type": "reply", "reply": {"id": "oui", "title": "Oui"}},
            {"type": "reply", "reply": {"id": "non", "title": "Non"}}
        ])    
    
    elif step == "bus_end":
        users.update_one({"phone": phone}, {"$set": {"step": "menu"}})
        if(text.lower() not in ["oui", "yes"]):
            send_message(phone, "Réservation annulée. Souhaitez-vous faire une autre réservation ?")
            send_buttons(phone, "Choisissez une catégorie :", [
                {"type": "reply", "reply": {"id": "bus", "title": "🚌 Ticket Bus"}},
                {"type": "reply", "reply": {"id": "avion", "title": "✈️ Billet Avion"}},
                {"type": "reply", "reply": {"id": "concert", "title": "🎤 Concert"}},
            ])
            return
        send_message(phone, f"✅ Votre demande de billet de bus de {user['data']['depart']} à {user['data']['arrivee']} pour le {user['data']['depart']} a été enregistrée.")
        # save to db tickets collection
        send_message(phone, "Souhaitez-vous faire une autre réservation ?")
        send_buttons(phone, "Choisissez une catégorie :", [
            {"type": "reply", "reply": {"id": "bus", "title": "🚌 Ticket Bus"}},
            {"type": "reply", "reply": {"id": "avion", "title": "✈️ Billet Avion"}},
            {"type": "reply", "reply": {"id": "concert", "title": "🎤 Concert"}},
        ])

def handle_airplane_conversation(phone: str, text: str, user: dict, step: str):
    step = user["step"]
    if step == "avion_depart":
        users.update_one({"phone": phone}, {"$set": {"step": "avion_arrivee", "data.depart": text}})
        destination_list = get_destinations(type="avion")
        destination_buttons = [{"type": "reply", "reply": {"id": loc, "title": loc}} for loc in destination_list]
        send_buttons(phone, "🚌 Très bien ! Quel est votre lieu de départ ?", destination_buttons)

    elif step == "avion_arrivee":
        users.update_one({"phone": phone}, {"$set": {"step": "avion_nbplace", "data.arrivee": text}})
        send_message(phone, "Combien de places souhaitez-vous réserver ?")
        # Pour quelle date souhaitez-vous voyager ? (ex: 2025-11-05)
    elif step == "avion_nbplace":
        users.update_one({"phone": phone}, {"$set": {"step": "avion_class", "data.nbplace": text}})
        send_buttons(phone, "Quelle classe préférez-vous ?", [
            {"type": "reply", "reply": {"id": "economique", "title": "Economique"}},
            {"type": "reply", "reply": {"id": "affaires", "title": "Affaire"}}
        ])

    elif step == "avion_class":
        users.update_one({"phone": phone}, {"$set": {"step": "avion_end", "data.classe": text}})
        send_buttons(phone, f"Confirmez vous votre réservation de {user['data']['nbplace']} places au départ de {user['data']['depart']} pour {user['data']['arrivee']} en classe {user['data']['classe']} ?", [
            {"type": "reply", "reply": {"id": "oui", "title": "Oui"}},
            {"type": "reply", "reply": {"id": "non", "title": "Non"}}
        ]) 

    elif step == "avion_end":
        users.update_one({"phone": phone}, {"$set": {"step": "menu"}})
        if(text.lower() not in ["oui", "yes"]):
            send_message(phone, "Réservation annulée. Souhaitez-vous faire une autre réservation ?")
            send_buttons(phone, "Choisissez une catégorie :", [
                {"type": "reply", "reply": {"id": "bus", "title": "🚌 Ticket Bus"}},
                {"type": "reply", "reply": {"id": "avion", "title": "✈️ Billet Avion"}},
                {"type": "reply", "reply": {"id": "concert", "title": "🎤 Concert"}},
            ])
            return
        send_message(phone, f"✅ Votre demande de billet d'avion de {user['data']['depart']} à {user['data']['arrivee']} pour le {text} a été enregistrée.")
        # save to db tickets collection
        send_message(phone, "Souhaitez-vous faire une autre réservation ?")
        send_buttons(phone, "Choisissez une catégorie :", [
            {"type": "reply", "reply": {"id": "bus", "title": "🚌 Ticket Bus"}},
            {"type": "reply", "reply": {"id": "avion", "title": "✈️ Billet Avion"}},
            {"type": "reply", "reply": {"id": "concert", "title": "🎤 Concert"}},
        ])

def handle_concert_conversation(phone: str, text: str, user: dict, step: str):
    send_message(phone=phone, text="Cette option n'est pas encore dispoible")  # À implémenter de manière similaire à handle_bus_conversation