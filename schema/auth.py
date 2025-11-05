from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class AppUser(BaseModel):
    username: str
    email: str | None = None
    fullname: str | None = None
    disabled: bool | None = None
    created_at: str | None = None

class AppUserRequest(BaseModel):
    username: str
    fullname: str
    plain_password: str
    email: str | None = None


class AppUserInDB(AppUser):
    hashed_password: str