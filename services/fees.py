from db import students, fees, transactions, accounts, charges, failed_transactions
import re
from datetime import datetime

def get_fees(school_code: str, school_year: str):
    code_s= str(school_code)
    if len(code_s) == 3:
        code_s = f"0{school_code}"
    query = {"school_code": code_s, "academic_year": school_year}
    projection = {"_id": 0, "title": 1, "price_usd": 1, "price_cdf": 1, "fee_id": 1}
    return list(fees.find(query, projection))

def get_fee_charges(fee_id: str, school_year: str):
    return charges.find_one({"fee_id": fee_id, "academic_year": school_year}, {"_id": 0, "commission_type": 1, "title": 1, "commission_value": 1, "value": 1, "charge_type": 1})

def get_fee_title(fee_id: str):
    return fees.find_one({"fee_id": fee_id}, {"_id": 0,"title": 1})

def get_student_name(student_id: str):
    return students.find_one({"student_id": student_id}, {"_id": 0,"full_name": 1})

def search_by_studentid(id: str, school_year: str):
    query = {"student_id": id, "academic_year": school_year}
    projection = {"_id": 0, "student_id": 1, "full_name": 1, "classroom": 1} 
    return list(students.find(query, projection))

def search_by_fullname(fullname: str, school_year: str):
    #TODO : Ajouter un index textuel sur fullname dans mongoDB
    words = fullname.strip().split()
    # crée une regex qui impose la présence de tous les mots, dans n’importe quel ordre
    regex = "".join(f"(?=.*\\b{re.escape(w)}\\b)" for w in words)
    pattern = re.compile(regex, re.IGNORECASE)
    projection = {"_id": 0, "student_id": 1, "full_name": 1, "classroom": 1} 
    return list(students.find({"fullname": {"$regex": pattern}, "academic_year": school_year}, projection))

def compute_charge(amount: float, charge_config: dict):
    if charge_config["charge_type"] == "percentage":
        charge = (charge_config["value"] / 100) * amount
    else:
        charge = charge_config["value"]
    return charge

def compute_commission(amount: float, commission_config: dict):
    if commission_config["commission_type"] == "percentage":
        commission = (commission_config["commission_value"] / 100) * amount
    else:
        commission = commission_config["commission_value"]
    return commission

def get_school_account(school_code: str, currency: str):
    query = {"school_code": school_code, "currency": currency}
    projection= {"_id": 0, "account_number": 1}
    return accounts.find_one(query, projection)

def create_failed_transaction(trn_data: dict, api_error: dict):
    failed_transactions.insert_one({**trn_data, "status": "failed", "api_response": str(api_error)})

def create_credit_transaction(trn_data: dict, api_response: dict):
    fee_id = trn_data.get("fee_id")
    if not fee_id:
        raise Exception("Bad Transaction Data provider set")
    fee = get_fee_charges(fee_id=fee_id, school_year=trn_data["academic_year"])
    if not fee:
        raise Exception("Bad Transaction Data provider set")
    charge = compute_charge(trn_data["amount"], fee)
    commission = compute_commission(trn_data["amount"], fee)
    trn_data["charge"] = charge
    trn_data["commission"] = commission
    transactions.insert_one({trn_data | {"status": "successful", "trn_date": datetime.now().isoformat(), "api_response": str(api_response)}})
    # update account balance
    accounts.update_one({"account_number": trn_data["account"]}, {"$inc": {"current_balance": trn_data["amount"]}})

def create_debit_transaction(trn_data: dict, api_response: dict):
    transactions.insert_one({trn_data | {"status": "successful", "trn_date": datetime.now().isoformat(), "api_response": str(api_response)}})
    # update account balance
    accounts.update_one({"account_number": trn_data["account"]}, {"$inc": {"current_balance": -trn_data["amount"]}})

def get_student_transactions(student_id: str, school_year: str):
    query = {"student_id": student_id, "academic_year": school_year}
    projection = {"_id": 0, "trn_id": 1, "currency": 1, "amount": 1, "is_full": 1, "trn_date": 1, "charge": 1, "commission": 1}
    return list(transactions.find(query, projection))

def get_account_details(account_number: str):
    projection = {"_id": 0, "account_number": 1, "title": 1, "current_balance": 1, "currency": 1}
    return accounts.find_one({"account_number": account_number}, projection)

def get_account_history(account_number: str):
    projection = {"_id": 0, "trn_id": 1, "currency": 1, "amount": 1, "is_full": 1, "trn_date": 1, "charge": 1, "commission": 1}
    return list(transactions.find({"account": account_number}, projection))