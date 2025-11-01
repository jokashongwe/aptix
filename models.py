from pydantic import BaseModel
from typing import Optional, Dict

class UserState(BaseModel):
    phone: str
    step: str
    data: Optional[Dict] = {}