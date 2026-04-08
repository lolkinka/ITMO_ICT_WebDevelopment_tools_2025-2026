from datetime import date
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from dateutil.relativedelta import relativedelta


# Тип транзакции
class Type(Enum):
    income = "income"
    expense = "expense"
    unknown = "unknown"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(SQLModel):
    name: str
    login: str = Field(unique=True, index=True)


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UserUpdatePassword(SQLModel):
    old_password: str
    new_password: str


class User(UserBase, table=True):
    __tablename__ = "user"
    hashed_password: str
    id: Optional[int] = Field(default=None, primary_key=True)
    accounts: List["Account"] = Relationship(back_populates="user")


# Модель счета
class AccountDefault(SQLModel):
    name: str
    currency: str
    created_at: date = date.today()
    user_id: int = Field(foreign_key="user.id")


class Account(AccountDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="accounts")
    transactions: List["Transaction"] = Relationship(back_populates="account")


# Модель категории
class CategoryDefault(SQLModel):
    name: str


class Category(CategoryDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    budgets: List["Budget"] = Relationship(back_populates="category")


# Модель для связи между транзакциями и категориями
class TransactionCategoryDefault(SQLModel):
    transaction_id: int = Field(foreign_key="transaction.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float


class TransactionCategory(TransactionCategoryDefault, table=True):
    id: int = Field(default=None, primary_key=True)

    # Связи с транзакцией и категорией
    transaction: "Transaction" = Relationship(back_populates="categories")
    category: "Category" = Relationship()


# Модель транзакции
class TransactionDefault(SQLModel):
    transaction_date: date = date.today()
    type: Type = Type.unknown
    description: Optional[str] = None
    total_amount: float = 0
    account_id: int = Field(foreign_key="account.id")


class Transaction(TransactionDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    account: "Account" = Relationship(back_populates="transactions")

    # Связь с категориями транзакции
    categories: List[TransactionCategory] = Relationship(back_populates="transaction")


class TransactionCreate(BaseModel):
    type: Type = Type.unknown
    description: Optional[str] = None
    account_id: int


# Модель бюджета
class BudgetDefault(SQLModel):
    category_id: int = Field(foreign_key="category.id")
    start_date: date = date.today()
    end_date: date = start_date + relativedelta(months=1)
    limit_amount: float


class Budget(BudgetDefault, table=True):
    id: int = Field(default=None, primary_key=True)

    # Связь с категорией
    category: "Category" = Relationship(back_populates="budgets")


class BudgetOut(BaseModel):
    id: int
    limit_amount: float
    start_date: date
    end_date: date

    class Config:
        orm_mode = True


class CategoryOut(BaseModel):
    id: int
    name: str
    budgets: List[BudgetOut]

    class Config:
        orm_mode = True
