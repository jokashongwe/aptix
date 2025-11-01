from chat.utils.messaging import send_text

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
            #user_states[user_id] = {}

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
            #user_states[user_id] = {}

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
            #user_states[user_id] = {}
