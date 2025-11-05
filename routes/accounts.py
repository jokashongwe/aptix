from fastapi import Depends, HTTPException, APIRouter
from db import accounts
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


@account_router.get("/accounts/{account_id}", tags=["Account Management"])
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

