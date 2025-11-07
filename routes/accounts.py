from fastapi import Depends, HTTPException, APIRouter
from db import accounts, transactions, schools, failed_transactions
from schema.auth import AppUser
from typing import Annotated, List
from services.auth import get_current_active_user

account_router = APIRouter()

@account_router.get("/accounts", tags=["Account Management"])
async def get_accounts(
    current_user: Annotated[AppUser, Depends(get_current_active_user)],
):
    projection = {
        "_id": 0,
        "account_number": 1,
        "title": 1,
        "current_balance":1,
        "school_code": 1,
        "currency": 1
    }
    account_list = list(accounts.find({}, projection))
    return  {
        "accounts": account_list
    }

@account_router.get("/accounts/summary", tags=["Account Management"])
async def get_dashboard():
    # --- Total Balance ---
    balance_result = await accounts.aggregate([
        {"$group": {"_id": None, "total_balance": {"$sum": "$current_balance"}}}
    ]).to_list(1)
    total_balance = balance_result[0]["total_balance"] if balance_result else 0

    # --- Active Customers ---
    active_schools = await schools.count_documents({"status": "active"})

    # --- Total Failed Transactions ---
    failed_transactions = await failed_transactions.count_documents({})

    # --- Total Credits ---
    total_credits_result = await transactions.aggregate([
        {"$match": {"type": "credit"}},
        {"$group": {"_id": None, "total_credits": {"$sum": "$amount"}}}
    ]).to_list(1)
    total_credits = total_credits_result[0]["total_credits"] if total_credits_result else 0

    # --- Total Debits ---
    total_debits_result = await transactions.aggregate([
        {"$match": {"type": "debit"}},
        {"$group": {"_id": None, "total_debits": {"$sum": "$amount"}}}
    ]).to_list(1)
    total_debits = total_debits_result[0]["total_debits"] if total_debits_result else 0

    return {
        "total_balance": total_balance,
        "active_customers": active_schools,
        "total_failed_transactions": failed_transactions,
        "total_credits": total_credits,
        "total_debits": total_debits
    }

@account_router.get("/accounts/{account_number}", tags=["Account Management"])
async def account_detail(
    account_number: str,
    current_user: Annotated[AppUser, Depends(get_current_active_user)],
):
    projection = {
        "_id": 0,
        "account_number": 1,
        "title": 1,
        "current_balance":1,
        "school_code": 1,
        "currency": 1
    }
    account = accounts.find_one({"account_number": account_number}, projection)
    return  {
        "account": account
    }

@account_router.get("/accounts/{account_number}/transactions", tags=["Account Management"])
async def get_accounts(
    account_number: str,
    current_user: Annotated[AppUser, Depends(get_current_active_user)],
):
    projection = {
        "_id": 0,
        "currency": 1,
        "amount": 1,
        "academic_year":1,
        "charge": 1,
        "commission": 1,
        "status": 1,
        "phone": 1,
        "created_dt": 1
    }
    transaction_list = list(transactions.find({"account_number": account_number}, projection))
    return  {
        "transactions": transaction_list
    }

@account_router.get("/transactions/{tran_id}", tags=["Account Management"])
async def account_detail(
    tran_id: str,
    current_user: Annotated[AppUser, Depends(get_current_active_user)],
):
    projection = {
        "_id": 0,
        "currency": 1,
        "amount": 1,
        "academic_year":1,
        "charge": 1,
        "commission": 1,
        "status": 1,
        "phone": 1,
        "created_dt": 1
    }
    transaction = transactions.find_one({"tran_id": tran_id}, projection)
    return  {
        "transaction": transaction
    }



