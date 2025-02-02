from fastapi import Body, FastAPI, File, UploadFile, HTTPException
import csv
from io import StringIO
from pydantic import BaseModel
from typing import Annotated
import json
import os
from dotenv import load_dotenv
import psycopg2 as pg
from typing import List, Optional
from datetime import date

# Create a FastAPI instance
app = FastAPI()

load_dotenv("/app/.env") 

class Category(BaseModel):
    id: int
    name: str
    main_category_id: int
    hidden: bool

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Category name",
                    "main_category_id": 2,
                    "hidden": False,
                }
            ]
        }
    }

class Transaction(BaseModel):
    id: int
    date: date
    amount: float
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    memo: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "date": "2021-01-01",
                    "amount": 100.00,
                    "category_id": 1,
                    "account_id": 1,
                    "memo": "Transaction description",
                }
            ]
        }
    }

    @classmethod
    def from_db(cls, db_obj):
        return cls(date=db_obj.date.isoformat())

class TransactionIn(BaseModel):
    amount: float 
    category_id: Optional[int] = None
    date: date
    memo: str
    account_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "amount": 100.00,
                    "category_id": 1,
                    "date": "2021-01-01",
                    "memo": "Transaction description",
                    "account_id": 1
                }
            ]
        }
    }

class TransactionOut(BaseModel):
    id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 100,
                }
            ]
        }
    }

# Simple GET endpoint to get all categories
@app.get("/categories", response_model=List[Category])
async def get_all_categories():
    try:
        # Connect to an existing database
        conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
        # Open a cursor to perform database operations
        cur = conn.cursor()
        cur.execute("SELECT * FROM categories WHERE main_category_id IS NOT NULL")
        rows = cur.fetchall()
        # Convert the result into a list of dictionaries
        columns = [desc[0] for desc in cur.description]
        result = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return result

@app.get("/transactions", response_model=List[Transaction])
async def get_all_transactions():
    try:
        # Connect to an existing database
        conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
        # Open a cursor to perform database operations
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions ORDER BY id DESC")
        rows = cur.fetchall()
        # Convert the result into a list of dictionaries
        columns = [desc[0] for desc in cur.description]
        result = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return result


@app.post("/transactions/add", response_model=TransactionOut)
async def add_transaction(transaction: TransactionIn):
    # Connect to an existing database
    conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
    try:
        # Open a cursor to perform database operations
        cur = conn.cursor()
        # Execute a command: add a transaction
        cur.execute("INSERT INTO transactions (amount, category_id, date, memo, account_id) VALUES (%s, %s, %s, %s, %s) RETURNING id", (transaction.amount, transaction.category_id, transaction.date, transaction.memo, transaction.account_id))
        # Get the id of the newly added transaction
        transaction_id = cur.fetchone()[0]
        # Commit the transaction
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"id": transaction_id}

@app.put("/transactions/update/{transaction_id}", response_model=TransactionOut)
async def update_transaction(transaction_id: int, transaction: TransactionIn):
    # Connect to an existing database
    conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
    # Open a cursor to perform database operations
    cur = conn.cursor()
    # Check if the transaction exists
    cur.execute("SELECT id FROM transactions WHERE id = %s", (transaction_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    # Execute a command: update the transaction
    cur.execute("UPDATE transactions SET amount = %s, category_id = %s, date = %s, memo = %s, account_id = %s WHERE id = %s", (transaction.amount, transaction.category_id, transaction.date, transaction.memo, transaction.account_id, transaction_id))
    # Commit the transaction
    conn.commit()
    cur.close()
    conn.close()
    return {"id": transaction_id}

@app.post("/transactions/remove/{transaction_id}", response_model=TransactionOut)
async def remove_transaction(transaction_id: int):
    # Connect to an existing database
    conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
    # Open a cursor to perform database operations
    cur = conn.cursor()
    # Check if the transaction exists
    cur.execute("SELECT id FROM transactions WHERE id = %s", (transaction_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    # Execute a command: delete the transaction
    cur.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
    # Commit the transaction
    conn.commit()
    cur.close()
    conn.close()
    return {"id": transaction_id}

@app.put("/transactions/import", response_model=List[TransactionOut])
async def upload_csv_transactions(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type")

    data = []
    # read file as bytes and decode bytes into text stream
    file_bytes = file.file.read()
    buffer = StringIO(file_bytes.decode('utf-8'))

    # process CSV
    csvReader = csv.DictReader(buffer)
    conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
    try:
        for row in csvReader:
            # Validate CSV row data
            if 'Date' not in row or 'Payee' not in row or 'Amount' not in row:
                raise HTTPException(status_code=400, detail="Invalid CSV format")
            if not row['Date'] or not row['Payee'] or not row['Amount']:
                raise HTTPException(status_code=400, detail="Missing data in CSV row")

            # Open a cursor to perform database operations
            cur = conn.cursor()
            # Execute a command: add a transaction
            cur.execute(
                "INSERT INTO transactions (date, memo, amount) VALUES (to_date(%s,'DD/MM/YYYY'), %s, %s) RETURNING id",
                (row['Date'], row['Payee'], row['Amount'])
            )
            # Get the id of the newly added transaction
            transaction_id = cur.fetchone()[0]
            data.append({"id": transaction_id})
            # Commit the transaction
            conn.commit()
            cur.close()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    # close buffer and file
    buffer.close()
    file.file.close()

    return data




