from fastapi import Depends, HTTPException, APIRouter
from db import accounts, transactions
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



