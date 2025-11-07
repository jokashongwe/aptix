from fastapi import APIRouter, HTTPException, Depends, status, Request
from schema.auth import Token
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from services.auth import authenticate_user, create_access_token,get_current_active_user, get_password_hash
from datetime import timedelta
from schema.auth import AppUser, AppUserRequest
from db import appusers

import os
from datetime import datetime

auth_router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

@auth_router.post("/token", tags=["Authentication"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    print("FormData:", form_data)
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@auth_router.post("/register", tags=["Authentication"])
async def register(req: Request):
    form_data = await req.json()
    appusers.insert_one({
        "username": form_data["username"],
        "fullname": form_data["fullname"],
        "email": form_data.get("email", ""),
        "hashed_password": get_password_hash(form_data['plain_password']),
        "disabled": True,
        "created_at": datetime.now().isoformat()
    })
    return {"Acccount": "Created!"}

@auth_router.get("/users/me/", response_model=AppUser, tags=["Authentication"])
async def read_users_me(
    current_user: Annotated[AppUser, Depends(get_current_active_user)],
):
    return current_user