from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class Student(BaseModel):
    full_name: str
    student_id: str
    classroom: str
    school_code: str
    is_active: bool = True
    created_at: str
    academic_year: Optional[str]


class School(BaseModel):
    title: str
    code: str
    address: str
    logo_url: str
    created_at: datetime

class ChargeConfig(BaseModel):
    school_code: str
    fee_id: str
    currency: str  # USD/CDF
    charge_type: str  # percentage/fixed
    commission_type: str  # percentage/fixed
    commission_value: float
    value: float
    created_at: Optional[str]
    created_by: Optional[str]
    academic_year: Optional[str]
    
class SchoolFee(BaseModel):
    fee_id: str
    title: str
    school_code: str
    price_usd: float
    price_cdf: float
    academic_year: Optional[str]
    is_follow_rate: Optional[bool]  = False
    created_at: Optional[str]
    

class AccountTransaction(BaseModel):
    trn_id: str
    currency: str # USD/CDF
    amount: float
    academic_year: str
    student_id: str
    trn_date: str
    is_full: Optional[bool]
    charge: Optional[float] = 0.0
    commission: Optional[float] = 0.0
    account: Optional[str]
    charge_account: Optional[str]


class Account(BaseModel):
    account_number: str
    title: str
    current_balance: float
    school_code: str
    currency: str # USD/CDF

class ExhangeRate(BaseModel):
    sale_rate: float
    mid_rate: float
    buy_rate: float
    created_at: str
    uploaded_by: str