from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import selectinload

from models import *
from typing_extensions import TypedDict
from connection import init_db, get_session
from sqlalchemy import select

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


# API для пользователя

@app.get("/users", tags=["Users"])
def users_list(session=Depends(get_session)) -> List[User]:
    return session.exec(select(User)).scalars().all()


@app.get("/users/{user_id}", tags=["Users"])
def user_get(user_id: int, session=Depends(get_session)) -> User:
    return session.exec(select(User).where(User.id == user_id)).scalars().first()


@app.post("/users", tags=["Users"])
def user_create(user: UserDefault, session=Depends(get_session)) -> TypedDict('Response',
                                                                              {"status": int, "data": User}):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return {"status": 200, "data": db_user}


@app.patch("/users/{user_id}", tags=["Users"])
def user_update(user_id: int, user: UserDefault, session=Depends(get_session)) -> UserDefault:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}", tags=["Users"])
def user_delete(user_id: int, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


# API для фин.профилей

@app.get("/accounts", tags=["Accounts"])
def accounts_list(session=Depends(get_session)) -> List[Account]:
    return session.exec(select(Account)).scalars().all()


@app.get("/accounts/{account_id}", tags=["Accounts"])
def account_get(account_id: int, session=Depends(get_session)) -> Account:
    return session.exec(select(Account).where(Account.id == account_id)).scalars().first()


@app.post("/accounts", tags=["Accounts"])
def account_create(account: AccountDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                    "data": Account}):
    db_account = Account.model_validate(account)
    session.add(db_account)
    session.commit()
    session.refresh(db_account)

    return {"status": 200, "data": db_account}


@app.patch("/accounts/{account_id}", tags=["Accounts"])
def account_update(account_id: int, account: AccountDefault, session=Depends(get_session)) -> AccountDefault:
    db_account = session.get(Account, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    account_data = account.model_dump(exclude_unset=True)
    for key, value in account_data.items():
        setattr(db_account, key, value)
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


@app.delete("/accounts/{account_id}", tags=["Accounts"])
def account_delete(account_id: int, session=Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(account)
    session.commit()
    return {"ok": True}


# API для категорий
@app.get("/categories", tags=["Category"])
def categories_list(session=Depends(get_session)) -> List[CategoryOut]:
    categories = session.exec(select(Category)).scalars().all()
    return categories


@app.get("/categories/{category_id}", tags=["Category"])
def category_get(category_id: int, session=Depends(get_session)) -> CategoryOut:
    return session.exec(select(Category).where(Category.id == category_id)).scalars().first()


@app.post("/category", tags=["Category"])
def category_create(cat: CategoryDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                  "data": Category}):
    cat = Category.model_validate(cat)
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return {"status": 200, "data": cat}


@app.patch("/category/{category_id}", tags=["Category"])
def account_update(category_id: int, account: CategoryDefault, session=Depends(get_session)) -> CategoryDefault:
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    category_data = account.model_dump(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@app.delete("/category/{category_id}", tags=["Category"])
def category_delete(category_id: int, session=Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"ok": True}


# API для budgets

@app.get("/budget", tags=["Budget"])
def budget_list(session=Depends(get_session)) -> List[Budget]:
    return session.exec(select(Budget)).scalars().all()


@app.post("/budget", tags=["Budget"])
def budget_create(budget: BudgetDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                 "data": Budget}):
    db_budget = Budget.model_validate(budget)
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return {"status": 200, "data": db_budget}


@app.get("/budget/{budget_id}", tags=["Budget"])
def budget_get(budget_id: int, session=Depends(get_session)) -> Budget:
    return session.exec(select(Budget).where(Budget.id == budget_id)).scalars().first()


@app.patch("/budget/{budget_id}", tags=["Budget"])
def budget_update(budget_id: int, budget: BudgetDefault, session=Depends(get_session)) -> BudgetDefault:
    db_budget = session.get(Budget, budget_id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    budget_data = budget.model_dump(exclude_unset=True)
    for key, value in budget_data.items():
        setattr(db_budget, key, value)
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return db_budget


@app.delete("/budget/{budget_id}", tags=["Budget"])
def budget_delete(budget_id: int, session=Depends(get_session)):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    session.delete(budget)
    session.commit()
    return {"ok": True}


# API для transaction
@app.get("/transactions", tags=["Transaction"])
def transaction_get(session=Depends(get_session)) -> List[Transaction]:
    return session.exec(select(Transaction)).scalars().all()


@app.get("/transactions/{transaction_id}", tags=["Transaction"])
def transaction_get(transaction_id: int, session=Depends(get_session)) -> Transaction:
    return session.exec(select(Transaction).where(Transaction.id == transaction_id)).scalars().first()


@app.post("/create_transaction", tags=["Transaction"])
def create_transaction(transaction_data: TransactionCreate, session=Depends(get_session)) -> TypedDict('Response',
                                                                                                       {"status": int,
                                                                                                        "data": Transaction}):
    transaction = Transaction.model_validate(transaction_data)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    return {"status": 200, "data": transaction}


@app.patch("/transaction/{transaction_id}", tags=["Transaction"])
def transaction_update(transaction_id: int, transaction: TransactionDefault,
                       session=Depends(get_session)) -> TransactionDefault:
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    transaction_data = transaction.model_dump(exclude_unset=True)
    for key, value in transaction_data.items():
        setattr(db_transaction, key, value)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


@app.delete("/transaction/{transaction_id}", tags=["Transaction"])
def transaction_delete(transaction_id: int, session=Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
    return {"ok": True}


# API для transactions_categories
@app.post("/create_transactions_categories", tags=["Transaction_Cat"])
def create_trans_cat(trans_cat_data: TransactionCategoryDefault, session=Depends(get_session)) -> TypedDict('Response',
                                                                                                            {
                                                                                                                "status": int,
                                                                                                                "data": TransactionCategory}):
    trans_cat = TransactionCategory.model_validate(trans_cat_data)
    session.add(trans_cat)
    session.commit()
    session.refresh(trans_cat)

    return {"status": 200, "data": trans_cat}


@app.get("/transactions_categories", tags=["Transaction_Cat"])
def trans_cat_list(session=Depends(get_session)) -> List[TransactionCategory]:
    return session.exec(select(TransactionCategory)).scalars().all()


@app.get("/transactions_categories/{transaction_cat_id}", tags=["Transaction_Cat"])
def trans_cat_list(transaction_cat_id: int, session=Depends(get_session)) -> TransactionCategory:
    return session.exec(
        select(TransactionCategory).where(TransactionCategory.id == transaction_cat_id)).scalars().first()


@app.patch("/transactions_categories/{transaction_cat_id}", tags=["Transaction_Cat"])
def transaction_cat_update(transaction_cat_id: int, transaction_cat: TransactionCategoryDefault,
                           session=Depends(get_session)) -> TransactionCategoryDefault:
    db_transaction_cat = session.get(TransactionCategory, transaction_cat_id)
    if not db_transaction_cat:
        raise HTTPException(status_code=404, detail="Relation not found")
    transaction_cat_data = transaction_cat.model_dump(exclude_unset=True)
    for key, value in transaction_cat_data.items():
        setattr(db_transaction_cat, key, value)
    session.add(db_transaction_cat)
    session.commit()
    session.refresh(db_transaction_cat)
    return db_transaction_cat


@app.delete("/transaction_category/{transaction_cat_id}", tags=["Transaction_Cat"])
def transaction_cat_delete(transaction_cat_id: int, session=Depends(get_session)):
    transaction_cat = session.get(TransactionCategory, transaction_cat_id)
    if not transaction_cat:
        raise HTTPException(status_code=404, detail="Relation not found")
    session.delete(transaction_cat)
    session.commit()
    return {"ok": True}
