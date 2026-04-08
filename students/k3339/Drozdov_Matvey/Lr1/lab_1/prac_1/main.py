from typing import List
from fastapi import FastAPI
from models import Transaction
from typing_extensions import TypedDict

app = FastAPI()

temp_db = [
    {
        "id": 1,
        "transaction_date": "2026-03-20",
        "total_amount": 1850.00,
        "type": "expense",
        "description": "Покупка в супермаркете",
        "account": {
            "id": 1,
            "name": "Основная карта",
            "currency": "RUB",
            "created_at": "2026-01-01"
        },
        "categories": [
            {
                "category": {
                    "id": 1,
                    "name": "Продукты"
                },
                "amount": 1450.00
            },
            {
                "category": {
                    "id": 2,
                    "name": "Бытовая химия"
                },
                "amount": 400.00
            }
        ]
    },
    {
        "id": 2,
        "transaction_date": "2026-03-21",
        "total_amount": 70000.00,
        "type": "income",
        "description": "Заработная плата",
        "account": {
            "id": 1,
            "name": "Основная карта",
            "currency": "RUB",
            "created_at": "2026-01-01"
        },
        "categories": [
            {
                "category": {
                    "id": 3,
                    "name": "Зарплата"
                },
                "amount": 70000.00
            }
        ]
    }
]


@app.get("/transactions_list")
def transactions_list() -> List[Transaction]:
    return temp_db


@app.get("/transactions_list/{transaction_id}")
def transactions_get(transaction_id: int) -> List[Transaction]:
    return [transaction for transaction in temp_db if transaction.get("id") == transaction_id]


@app.post("/transactions")
def transactions_create(transaction: Transaction) -> TypedDict('Response', {"status": int, "data": Transaction}):
    transaction_to_append = transaction.model_dump()
    temp_db.append(transaction_to_append)
    return {"status": 200, "data": transaction}


@app.delete("/transaction/delete{transaction_id}")
def transaction_delete(transaction_id: int):
    for i, transaction in enumerate(temp_db):
        if transaction.get("id") == transaction_id:
            temp_db.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/transaction{transaction_id}")
def transaction_update(transaction_id: int, transaction: Transaction) -> List[Transaction]:
    for transact in temp_db:
        if transact.get("id") == transaction_id:
            transact_to_append = transaction.model_dump()
            temp_db.remove(transact)
            temp_db.append(transact_to_append)
    return temp_db
