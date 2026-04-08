from pydantic import BaseModel
from datetime import date
from typing import List
from enum import Enum

class Type(Enum):
    income = "income"
    expense = "expense"

class User(BaseModel):
    id: int
    name: str
    login: str
    password: str

class Account(BaseModel):
    id: int
    name: str
    currency: str
    created_at: date


class Category(BaseModel):
    id: int
    name: str

class TransactionCategory(BaseModel):
    category: Category
    amount: float

class Transaction(BaseModel):
    id: int
    transaction_date: date
    total_amount: float
    type: Type
    description: str | None = None

    account: Account
    categories: List[TransactionCategory]

class Budget(BaseModel):
    category_id: int
    start_date: date
    end_date: date
    limit_amount: float

