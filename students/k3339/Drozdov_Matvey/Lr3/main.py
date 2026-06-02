import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models import *
from connection import init_db, get_session
from sqlmodel import select
from auth import hash_password, verify_password, create_access_token, get_current_user
import os
from celery import Celery
from pydantic import BaseModel

app = FastAPI(title="Finance Manager API")


@app.on_event("startup")
def on_startup():
    init_db()


# --- 1. АУТЕНТИФИКАЦИЯ И ПОЛЬЗОВАТЕЛИ ---

@app.post("/register", tags=["Auth"])
def register(user_in: UserCreate, session=Depends(get_session)):
    if session.exec(select(User).where(User.login == user_in.login)).first():
        raise HTTPException(status_code=400, detail="Login already taken")

    db_user = User(
        name=user_in.name,
        login=user_in.login,
        hashed_password=hash_password(user_in.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"status": 200, "data": db_user}


@app.post("/login", tags=["Auth"], response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)):
    user = session.exec(select(User).where(User.login == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect login or password")

    access_token = create_access_token(data={"sub": user.login})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", tags=["Users"], response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.patch("/users/me/password", tags=["Users"])
def change_password(pass_data: UserUpdatePassword, current_user: User = Depends(get_current_user),
                    session=Depends(get_session)):
    if not verify_password(pass_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password incorrect")
    current_user.hashed_password = hash_password(pass_data.new_password)
    session.add(current_user)
    session.commit()
    return {"status": "success"}


@app.get("/users", tags=["Users"], response_model=List[UserRead])
def users_list(session=Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(User)).all()


# --- 2. СЧЕТА (ACCOUNTS) ---

@app.get("/accounts", tags=["Accounts"], response_model=List[Account])
def accounts_list(session=Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Account).where(Account.user_id == current_user.id)).all()


@app.get("/accounts/{account_id}", tags=["Accounts"], response_model=Account)
def account_get(account_id: int, session=Depends(get_session), current_user: User = Depends(get_current_user)):
    account = session.exec(select(Account).where(Account.id == account_id, Account.user_id == current_user.id)).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.post("/accounts", tags=["Accounts"])
def account_create(account: AccountDefault, session=Depends(get_session),
                   current_user: User = Depends(get_current_user)):
    db_account = Account.model_validate(account)
    db_account.user_id = current_user.id
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return {"status": 200, "data": db_account}


@app.patch("/accounts/{account_id}", tags=["Accounts"])
def account_update(account_id: int, account: AccountDefault, session=Depends(get_session),
                   current_user: User = Depends(get_current_user)):
    db_account = session.exec(
        select(Account).where(Account.id == account_id, Account.user_id == current_user.id)).first()
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
def account_delete(account_id: int, session=Depends(get_session), current_user: User = Depends(get_current_user)):
    account = session.exec(select(Account).where(Account.id == account_id, Account.user_id == current_user.id)).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(account)
    session.commit()
    return {"ok": True}


# --- 3. КАТЕГОРИИ (CATEGORIES) ---

@app.get("/categories", tags=["Category"], response_model=List[CategoryOut])
def categories_list(session=Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Category)).all()


@app.get("/categories/{category_id}", tags=["Category"], response_model=CategoryOut)
def category_get(category_id: int, session=Depends(get_session), current_user: User = Depends(get_current_user)):
    cat = session.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@app.post("/category", tags=["Category"])
def category_create(cat: CategoryDefault, session=Depends(get_session), current_user: User = Depends(get_current_user)):
    db_cat = Category.model_validate(cat)
    session.add(db_cat)
    session.commit()
    session.refresh(db_cat)
    return {"status": 200, "data": db_cat}


@app.patch("/category/{category_id}", tags=["Category"])
def category_update(category_id: int, cat: CategoryDefault, session=Depends(get_session),
                    current_user: User = Depends(get_current_user)):
    db_cat = session.get(Category, category_id)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat_data = cat.model_dump(exclude_unset=True)
    for key, value in cat_data.items():
        setattr(db_cat, key, value)
    session.add(db_cat)
    session.commit()
    session.refresh(db_cat)
    return db_cat


@app.delete("/category/{category_id}", tags=["Category"])
def category_delete(category_id: int, session=Depends(get_session), current_user: User = Depends(get_current_user)):
    cat = session.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(cat)
    session.commit()
    return {"ok": True}


# --- 4. БЮДЖЕТЫ (BUDGETS) ---

@app.get("/budget", tags=["Budget"], response_model=List[Budget])
def budget_list(session=Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Budget)).all()


@app.post("/budget", tags=["Budget"])
def budget_create(budget: BudgetDefault, session=Depends(get_session), current_user: User = Depends(get_current_user)):
    db_budget = Budget.model_validate(budget)
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return {"status": 200, "data": db_budget}


@app.get("/budget/{budget_id}", tags=["Budget"], response_model=Budget)
def budget_get(budget_id: int, session=Depends(get_session), current_user: User = Depends(get_current_user)):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@app.patch("/budget/{budget_id}", tags=["Budget"])
def budget_update(budget_id: int, budget: BudgetDefault, session=Depends(get_session),
                  current_user: User = Depends(get_current_user)):
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
def budget_delete(budget_id: int, session=Depends(get_session), current_user: User = Depends(get_current_user)):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    session.delete(budget)
    session.commit()
    return {"ok": True}


# --- 5. ТРАНЗАКЦИИ (TRANSACTIONS) ---

@app.get("/transactions", tags=["Transaction"], response_model=List[Transaction])
def transaction_list(session=Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(Transaction).join(Account).where(Account.user_id == current_user.id)
    return session.exec(statement).all()


@app.get("/transactions/{transaction_id}", tags=["Transaction"], response_model=Transaction)
def transaction_get(transaction_id: int, session=Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(Transaction).join(Account).where(Transaction.id == transaction_id,
                                                        Account.user_id == current_user.id)
    transaction = session.exec(statement).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.post("/create_transaction", tags=["Transaction"])
def create_transaction(transaction_data: TransactionCreate, session=Depends(get_session),
                       current_user: User = Depends(get_current_user)):
    account = session.exec(
        select(Account).where(Account.id == transaction_data.account_id, Account.user_id == current_user.id)).first()
    if not account:
        raise HTTPException(status_code=400, detail="Invalid account or access denied")

    transaction = Transaction.model_validate(transaction_data)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return {"status": 200, "data": transaction}


@app.patch("/transaction/{transaction_id}", tags=["Transaction"])
def transaction_update(transaction_id: int, transaction: TransactionDefault, session=Depends(get_session),
                       current_user: User = Depends(get_current_user)):
    statement = select(Transaction).join(Account).where(Transaction.id == transaction_id,
                                                        Account.user_id == current_user.id)
    db_transaction = session.exec(statement).first()
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
def transaction_delete(transaction_id: int, session=Depends(get_session),
                       current_user: User = Depends(get_current_user)):
    statement = select(Transaction).join(Account).where(Transaction.id == transaction_id,
                                                        Account.user_id == current_user.id)
    transaction = session.exec(statement).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
    return {"ok": True}


# --- 6. ТРАНЗАКЦИИ ПО КАТЕГОРИЯМ (TRANSACTION_CAT) ---

@app.post("/create_transactions_categories", tags=["Transaction_Cat"])
def create_trans_cat(trans_cat_data: TransactionCategoryDefault, session=Depends(get_session),
                     current_user: User = Depends(get_current_user)):
    trans_cat = TransactionCategory.model_validate(trans_cat_data)
    session.add(trans_cat)
    session.commit()
    session.refresh(trans_cat)
    return {"status": 200, "data": trans_cat}


@app.get("/transactions_categories", tags=["Transaction_Cat"], response_model=List[TransactionCategory])
def trans_cat_list(session=Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(TransactionCategory)).all()


@app.get("/transactions_categories/{transaction_cat_id}", tags=["Transaction_Cat"], response_model=TransactionCategory)
def trans_cat_get(transaction_cat_id: int, session=Depends(get_session),
                  current_user: User = Depends(get_current_user)):
    res = session.get(TransactionCategory, transaction_cat_id)
    if not res:
        raise HTTPException(status_code=404, detail="Relation not found")
    return res


@app.patch("/transactions_categories/{transaction_cat_id}", tags=["Transaction_Cat"])
def transaction_cat_update(transaction_cat_id: int, transaction_cat: TransactionCategoryDefault,
                           session=Depends(get_session), current_user: User = Depends(get_current_user)):
    db_transaction_cat = session.get(TransactionCategory, transaction_cat_id)
    if not db_transaction_cat:
        raise HTTPException(status_code=404, detail="Relation not found")
    data = transaction_cat.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_transaction_cat, key, value)
    session.add(db_transaction_cat)
    session.commit()
    session.refresh(db_transaction_cat)
    return db_transaction_cat


@app.delete("/transaction_category/{transaction_cat_id}", tags=["Transaction_Cat"])
def transaction_cat_delete(transaction_cat_id: int, session=Depends(get_session),
                           current_user: User = Depends(get_current_user)):
    transaction_cat = session.get(TransactionCategory, transaction_cat_id)
    if not transaction_cat:
        raise HTTPException(status_code=404, detail="Relation not found")
    session.delete(transaction_cat)
    session.commit()
    return {"ok": True}


REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
celery_app = Celery("parser_tasks", broker=REDIS_URL, backend=REDIS_URL)

class ParseRequest(BaseModel):
    article_ids: list[int]

@app.post("/parse", tags=["Parser"], status_code=status.HTTP_202_ACCEPTED)
def parse_endpoint(request: ParseRequest):
    try:
        # Отправляем задачу в Redis по названию.
        # Метод выполнится МГНОВЕННО, не блокируя FastAPI.
        task = celery_app.send_task(
            "tasks.run_parsing_task",
            args=[request.article_ids]
        )

        # Возвращаем клиенту ID задачи, чтобы он мог при желании проверять статус
        return {
            "message": "Parsing task background execution started",
            "task_id": task.id,
            "status": "Dispatched"
        }

    except Exception as e:
        return {"error": f"Failed to dispatch task: {str(e)}"}