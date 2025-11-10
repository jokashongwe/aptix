from db import users
from services.whatsapp import send_message, send_buttons, send_list_message, send_image_message
from datetime import date
from services.fees import *
from services.maxicash import send_payment_async
import os
from fastapi import HTTPException
import random

acad_year = os.getenv("SCHOOL_YEAR", "2025-2026")

def handle_start(phone:str):
    send_image_message(phone=phone
                       , caption="Bonjour! Bienvenue dans SkulIA. L'écosystème qui simplifie le paiement des frais de vos enfants\nQuel est le code de l'école ?"
                       , image_url="https://www.shutterstock.com/image-vector/chat-bot-icon-virtual-smart-600nw-2478937553.jpg")
    users.update_one({"phone": phone}, {"$set": {"step": "search"}})

async def handle_fees_message(phone: str, text:str):
    user = users.find_one({"phone": phone})
    if not user:
        users.insert_one({"phone": phone, "step": "start",  "created_at": date.today().isoformat()})
        return handle_start(phone=phone)
        
    current_step = user["step"]
    #options_slug = ["search", "select_student", "list_fees", "put_amount", "select_currency", "confirm", "payment_method" ,"wait_for_payment"]
    text = text.lower().strip()
    if text in ["annuler", "quitter", "arret", "stop", "quit"]:
        send_message(phone=phone, text="Merci d'avoir utiliser notre service et à bientôt")
        users.update_one({"phone": phone}, {"$set": {"step": "start"}})
        return

    if current_step == "start":
        return handle_start(phone=phone)
    elif current_step == "search":
        users.update_one({"phone": phone}, {"$set": {"step": "select_student", "data.school_code": text}})
        send_buttons(phone=phone, body="Souhaitez-vous rechercher par matricule ou par nom ?", buttons=[
            {"type": "reply", "reply": {"id": "select_student_mat", "title": "Matricule"}},
            {"type": "reply", "reply": {"id": "select_student_name", "title": "Nom de l'élève"}}
        ])
    elif current_step == "select_student":
        #users.update_one({"phone": phone}, {"$set": {"step": "select_student", "data.school_code": text}})
        text_field = "nom"
        pp = "select_student_name"
        if text == "select_student_mat":
            pp = "select_student_mat"
            text_field = "matricule"
        send_message(phone=phone, text=f"Quel est le {text_field} de l'élève ?")
        users.update_one({"phone": phone}, {"$set": {"step": pp, "data.fieldtype": text_field}})
    elif current_step.startswith("select_student_"):
        students = []
        field_type = "matricule"
        if current_step == "select_student_mat":
            students = search_by_studentid(id=text.upper(), school_year=acad_year)
        else:
            students = search_by_fullname(fullname=text.upper(), school_year=acad_year)
            field_type = "nom"
        if not students or len(students) == 0:
            users.update_one({"phone": phone}, {"$set": {"step": "search"}})
            send_buttons(phone=phone, body=f"Nous n'avons trouvé aucune correspondance pour ce {field_type}.\nSouhaitez-vous reprendre la recherche par matricule ou par nom ?", buttons=[
                {"type": "reply", "reply": {"id": "select_student_mat", "title": "Matricule"}},
                {"type": "reply", "reply": {"id": "select_student_name", "title": "Nom de l'élève"}},
                {"type": "reply", "reply": {"id": "quitter", "title": "Annuler"}}
            ])
            return
        sections = [{
            "title": "Résultats",
            "rows": [{
                "id": f"{student["student_id"]}",
                "title":  f"{student["student_id"].upper()}", 
                "description": f"{student["full_name"]} {student["classroom"]}"
            } for student in students ]
        }]
        send_list_message(phone=phone,
                           header="Resultat trouvés pour votre recherche",
                           body="Consultez la liste des résulats trouvés",
                           footer="Powerd By SkulIA",
                           sections=sections)
        users.update_one({"phone": phone}, {"$set": {"step": "list_fees", "data.identity": text}})
    elif current_step.startswith("list_fees"):
        fees = get_fees(school_code=user["data"]["school_code"], school_year=acad_year)
        print("Fees: ", fees)
        sections = [{
            "title": "List des Frais",
            "rows": [{"id": f"{fee["fee_id"]}", "title": f"{fee["title"][:23]}" ,"description": f"{fee["title"]} {fee["price_cdf"]} Fc ({fee["price_usd"]}$)" } for fee in fees ]
        }]
        send_list_message(phone=phone,
                           header="Liste des Frais",
                           body="Sélectionner le frais que vous souhaitez payer",
                           footer="Powered By",
                           sections=sections)
        users.update_one({"phone": phone}, {"$set": {"step": "put_amount", "data.student_id": text}})
    elif current_step.startswith("put_amount"):
        users.update_one({"phone": phone}, {"$set": {"step": "select_currency", "data.fee_id": text}})
        send_message(phone=phone, text="Combien souhaitez vous payer ? (Donnez juste le montant vous sélectionnerez la devise par la suite)")
    elif current_step.startswith("select_currency"):
        users.update_one({"phone": phone}, {"$set": {"step": "confirm", "data.amount": text}})
        send_buttons(phone=phone, body=f"Sélectionner la devise", buttons=[
                {"type": "reply", "reply": {"id": "cdf", "title": "Francs Congolais"}},
                {"type": "reply", "reply": {"id": "usd", "title": "Dollars américains"}},
            ])
    elif current_step.startswith("confirm"):
        users.update_one({"phone": phone}, {"$set": {"step": "payment_phone", "data.currency": text}})
        fee = get_fee_title(fee_id=user['data']['fee_id'])
        student = get_student_name(student_id=user['data']['student_id'].upper())
        send_buttons(phone=phone, body=f"Confirmez-vous le paiement de {fee['title']} d'un montant de {user['data']['amount']} {text} pour l'élève {student['full_name']} ?", buttons=[
                {"type": "reply", "reply": {"id": "yes", "title": "Oui"}},
                {"type": "reply", "reply": {"id": "no", "title": "Non"}},
            ])
    elif current_step.startswith("payment_phone"):
        if text == "no":
            users.update_one({"phone": phone}, {"$set": {"step": "start", "data": None}})
            send_message(phone=phone, text="Merci d'avoir utiliser notre service. A bientôt!")
            return
        users.update_one({"phone": phone}, {"$set": {"step": "payment_method", "data.hasConfirmed": "yes"}})
        send_message(phone=phone, text="Quel est le numéro pour le paiement ?")
    elif current_step.startswith("payment_method"):
        users.update_one({"phone": phone}, {"$set": {"step": "wait_for_payment", "data.phone": text}})
        parsedPhone = text
        payType = None
        phone_code = parsedPhone[:2]
        print("Phone Code: ", phone_code)
        if phone_code in ['81', '82', '83']:
            payType = 2
        elif phone_code in ['84', '85', '89']:
            payType = 3
        elif phone_code in ['99', '98', '97']:
            payType = 1
        elif phone_code in ['90', '91', '92']:
            payType = 52
        
        if not payType:
            send_message(phone=phone, text="Nous rencontrons actuellement un soucis avec notre système.\nVeuillez réessayer plus tard")
            raise HTTPException(status_code=502, detail=result.get("error") or "Payment provider error")
        # contact MaxiCash API
        endpoint = os.getenv('MAXICASH_API_URL', '"https://webapi-test.maxicashapp.com')
        endpoint = f"{endpoint}/Integration/PayNowSync"
        put_amount = int(user['data']['amount'])
        amount = put_amount * 100
        trx_detail = {"Amount": amount,"Reference": f"{generate_trx_ref()}","Telephone": text}
        currency = f"{user["data"]['currency']}".upper()
        account = get_school_account(school_code=user['data']['school_code'],
                                     currency=currency)
        result = await send_payment_async(endpoint_url=endpoint,
                                          pay_type=payType,
                                          request_data=trx_detail,
                                          currency_code=currency,
                                          timeout=20)
        response = result.get("response")
        if not result.get("ok"):
            users.update_one({"phone": phone}, {"$set": {"step": "start"}})
            create_failed_transaction(trn_data=user['data'], api_error=result)
            send_message(phone=phone, text="Nous rencontrons actuellement un soucis avec notre système.\nVeuillez réessayer plus tard")
            raise HTTPException(status_code=502, detail=result.get("error") or "Payment provider error")
        
        if response and response.get("ResponseStatus"):
            status = f"{response.get("ResponseStatus", "failed")}"
            if "failed" in status.lower():
                users.update_one({"phone": phone}, {"$set": {"step": "start"}})
                create_failed_transaction(trn_data=user['data'], api_error=result)
                send_message(phone=phone, text="Nous rencontrons actuellement un soucis avec notre système.\nVeuillez réessayer plus tard")
                raise HTTPException(status_code=502, detail=result.get("error") or "Payment provider error")
        trn_data = {user['data'] | {"account": account}}
        create_credit_transaction(trn_data=trn_data, api_response=result)
        send_image_message(phone=phone
                           , image_url="https://cdn-icons-png.freepik.com/256/18327/18327199.png",
                           caption="🟩Votre demande est en cours de traitement.Veuillez confirmer la transactions SVP.\nUne fois fait vous recevrez votre borderau de paiment")
        users.update_one({"phone": phone}, {"$set": {"step": "start"}})
        # END CALL MAXICASH
        
def generate_trx_ref():
    random.seed(1656534)
    randInt =random.randint(135442, 989999)
    return f"TR{randInt}"


#0510