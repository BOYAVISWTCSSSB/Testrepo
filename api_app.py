"""Mock banking APIs for the SSB Bank POC. All data is fictional."""
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="SSB Banking Demo API")

ACCOUNTS = {
    "SSB-1001": {
        "customer_name": "Demo Customer One",
        "account_type": "savings",
        "currency": "INR",
        "status": "active",
        "balance": Decimal("125000.00"),
    },
    "SSB-1002": {
        "customer_name": "Demo Customer One",
        "account_type": "current",
        "currency": "INR",
        "status": "active",
        "balance": Decimal("42000.00"),
    },
    "SSB-2001": {
        "customer_name": "Demo Customer Two",
        "account_type": "savings",
        "currency": "INR",
        "status": "active",
        "balance": Decimal("18500.00"),
    },
}

TRANSACTIONS = {
    "SSB-1001": [
        {"transaction_id": "TXN-10001", "date": "2026-10-22", "description": "UPI payment to Demo Cafe", "type": "debit", "amount": Decimal("450.00"), "status": "completed"},
        {"transaction_id": "TXN-10002", "date": "2026-10-20", "description": "Salary credit", "type": "credit", "amount": Decimal("65000.00"), "status": "completed"},
        {"transaction_id": "TXN-10003", "date": "2026-10-18", "description": "Electricity bill payment", "type": "debit", "amount": Decimal("2200.00"), "status": "completed"},
    ],
    "SSB-1002": [
        {"transaction_id": "TXN-10004", "date": "2026-10-21", "description": "Funds added", "type": "credit", "amount": Decimal("5000.00"), "status": "completed"},
        {"transaction_id": "TXN-10005", "date": "2026-10-19", "description": "Office supplies", "type": "debit", "amount": Decimal("1250.00"), "status": "completed"},
    ],
    "SSB-2001": [
        {"transaction_id": "TXN-10006", "date": "2026-10-22", "description": "ATM cash withdrawal", "type": "debit", "amount": Decimal("2000.00"), "status": "completed"},
    ],
}


def require_account(account_id: str):
    account = ACCOUNTS.get(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Demo account not found")
    return account


@app.get("/accounts/{account_id}", operation_id="get_account")
def get_account(account_id: str):
    """Get a demo customer's account type, currency, and status by SSB account ID."""
    account = require_account(account_id)
    return {
        "account_id": account_id,
        "customer_name": account["customer_name"],
        "account_type": account["account_type"],
        "currency": account["currency"],
        "status": account["status"],
    }


@app.get("/accounts/{account_id}/balance", operation_id="get_account_balance")
def get_account_balance(account_id: str):
    """Get the current mock balance and currency for an SSB demo account."""
    account = require_account(account_id)
    return {
        "account_id": account_id,
        "balance": account["balance"],
        "currency": account["currency"],
    }


@app.get("/accounts/{account_id}/transactions", operation_id="list_account_transactions")
def list_account_transactions(
    account_id: str,
    limit: int = Query(default=10, ge=1, le=50),
):
    """List recent mock transactions for an SSB demo account, up to the requested limit."""
    require_account(account_id)
    transactions = TRANSACTIONS[account_id][:limit]
    return {
        "account_id": account_id,
        "count": len(transactions),
        "transactions": transactions,
    }


@app.get("/transfers/simulate", operation_id="simulate_transfer")
def simulate_transfer(
    source_account_id: str,
    destination_account_id: str,
    amount: Decimal = Query(gt=0),
):

    """Check whether a mock transfer could be made; this never moves or changes money."""
    source = require_account(source_account_id)
    destination = require_account(destination_account_id)
    if source_account_id == destination_account_id:
        raise HTTPException(status_code=400, detail="Source and destination accounts must differ")

    eligible = True
    reason = "Transfer simulation passed; no money was moved."
    if source["status"] != "active" or destination["status"] != "active":
        eligible = False
        reason = "Both accounts must be active. No money was moved."
    elif source["currency"] != destination["currency"]:
        eligible = False
        reason = "Source and destination currencies must match. No money was moved."
    elif amount > source["balance"]:
        eligible = False
        reason = "Insufficient demo balance. No money was moved."

    return {
        "eligible": eligible,
        "source_account_id": source_account_id,
        "destination_account_id": destination_account_id,
        "amount": amount,
        "currency": source["currency"],
        "message": reason,
    }
