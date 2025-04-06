from datetime import datetime, timedelta, timezone
from fastapi import Body, FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import csv
from io import StringIO
from pydantic import BaseModel
from typing import Annotated
import json
import os
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import psycopg2 as pg
from typing import List, Optional
from datetime import date, datetime
import base64

# Create a FastAPI instance
app = FastAPI(title="Budget API", version="1.0.0")
pwd_context = CryptContext(
    schemes=["argon2"],
    default="argon2"
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
load_dotenv("/app/.env") 


# ----------------- Authorization -----------
class User(BaseModel):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def encrypt_password(password: str):
    return pwd_context.hash(password)

def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)

def authenticate_user(login: str, password: str):
    conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
    try:
        # Open a cursor to perform database operations
        cur = conn.cursor()
        # Check if account name already exists
        cur.execute("SELECT password FROM users WHERE active = true AND login = %s", (login,))
        result = cur.fetchone()
        if result is None:
            return False
        return check_encrypted_password(password, result[0])     
    finally:
        cur.close()
        conn.close()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    private_key = os.getenv("PRIVATE_KEY")
    private_key = base64.b64decode(private_key).decode('utf-8') if private_key else None
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=os.getenv('ALGORITHM'))
    return encoded_jwt

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

# ----------------- Category -----------------

class Category(BaseModel):
    main_category_name: str
    category_name: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "main_category_name": "Main category name",
                    "category_name": "Category name"
                }
            ]
        }
    }

# Simple GET endpoint to get all categories
@app.get("/categories", response_model=List[Category], tags=["Categories"])
async def get_all_categories(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        # Connect to an existing database
        conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
        # Open a cursor to perform database operations
        cur = conn.cursor()
        cur.execute("SELECT main_category_name, category_name FROM categories_view")
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

# ----------------- Account -----------------

class Account(BaseModel):
    id: Optional[int] = None
    hidden: Optional[bool] = False
    account_name: str
    total: Optional[float] = None

# Simple GET endpoint to get all accounts
@app.get("/accounts", response_model=List[Account], tags=["Accounts"])
async def get_all_accounts(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        # Connect to an existing database
        conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
        # Open a cursor to perform database operations
        cur = conn.cursor()
        cur.execute("SELECT id, name, account_name, total FROM accounts_view JOIN accounts ON accounts_view.account_name = accounts.name")
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

# POST endpoint to add a new account
@app.post("/accounts/add", response_model=Account, tags=["Accounts"])
async def add_account(token: Annotated[str, Depends(oauth2_scheme)], account: Annotated[Account, Body(
    examples=[
        {
            "account_name": "Account name"
        }
    ]
)]):
    # Connect to an existing database
    conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
    try:
        # Open a cursor to perform database operations
        cur = conn.cursor()
        # Check if account name already exists
        cur.execute("SELECT id FROM accounts WHERE name = %s", (account.account_name,))
        if cur.fetchone() is not None:
            raise HTTPException(status_code=400, detail="Account name already exists")
        
        # Insert the new account
        cur.execute(
            "INSERT INTO accounts (name) VALUES (%s) RETURNING id, hidden",
            (account.account_name,)
        )
        # Get the id of the newly added account
        account_id, hidden = cur.fetchone()
        # Commit the transaction
        conn.commit()
        # Return the account object with the new id
        return {"id": account_id, "account_name": account.account_name, "total": 0.0, "hidden": hidden}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
        
# PUT endpoint to update account name and hidden status
@app.put("/accounts/update/{account_id}", response_model=Account, tags=["Accounts"])
async def update_account(token: Annotated[str, Depends(oauth2_scheme)], account_id: int, account: Annotated[Account, Body(
    examples=[
        {
            "account_name": "Account name",
            "hidden": False
        }
    ]
)]):
    # Connect to an existing database
    conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
    try:
        # Open a cursor to perform database operations
        cur = conn.cursor()
        # Check if the account exists
        cur.execute("SELECT id FROM accounts WHERE id = %s", (account_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Check if the new account name already exists
        cur.execute("SELECT id FROM accounts WHERE name = %s AND id != %s", (account.account_name, account_id))
        if cur.fetchone() is not None:
            raise HTTPException(status_code=400, detail="Account name already exists")
        
        # Update the account
        cur.execute(
            "UPDATE accounts SET name = %s, hidden = %s WHERE id = %s",
            (account.account_name, account.hidden, account_id)
        )
        # Commit the transaction
        conn.commit()
        # Return the updated account object
        cur.execute("SELECT id, name, account_name, total, hidden FROM accounts_view JOIN accounts ON accounts_view.account_name = accounts.name WHERE accounts.id = %s", (account_id,))
        row = cur.fetchone()
        if row:
            columns = [desc[0] for desc in cur.description]
            result = dict(zip(columns, row))
            return result
        else:
            raise HTTPException(status_code=404, detail="Account not found")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ----------------- Transaction -----------------

class Transaction(BaseModel):
    id: Optional[int] = None
    date: date
    account_name: str 
    payee_name: str
    category_name: Optional[str] = None
    memo: str
    amount: float

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 100,
                    "date": "2021-01-01",
                    "account_name": "Account name",
                    "payee_name": "Payee name",
                    "category_name": "Category name",
                    "memo": "Transaction description",
                    "amount": 100.00
                }
            ]
        }
    }

    @classmethod
    def from_db(cls, db_obj):
        return cls(date=db_obj.date.isoformat())

@app.get("/transactions", response_model=List[Transaction], tags=["Transactions"])
async def get_all_transactions(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        # Connect to an existing database
        conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
        # Open a cursor to perform database operations
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions_view ORDER BY date DESC")
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


@app.post("/transactions/add", response_model=Transaction, tags=["Transactions"])
async def add_transaction(token: Annotated[str, Depends(oauth2_scheme)], transaction: Transaction):
    # Connect to an existing database
    conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
    try:
        # Open a cursor to perform database operations
        cur = conn.cursor()
        # Execute a command: add a transaction
        # Check if account exists
        cur.execute("SELECT id FROM accounts WHERE name = %s", (transaction.account_name,))
        account_id = cur.fetchone()
        if account_id is None:
            raise HTTPException(status_code=400, detail="Account not found")
        
        # Check if category exists
        if transaction.category_name:
            cur.execute("SELECT id FROM categories WHERE main_category_id IS NOT NULL and name = %s", (transaction.category_name,))
            category_id = cur.fetchone()
            if category_id is None:
                raise HTTPException(status_code=400, detail="Category not found")
        else:
            category_id = None
        
        # Check if payee exists, if not add one
        cur.execute("SELECT id FROM payees WHERE name = %s", (transaction.payee_name,))
        payee_id = cur.fetchone()
        if payee_id is None:
            cur.execute("INSERT INTO payees (name) VALUES (%s) RETURNING id", (transaction.payee_name,))
            payee_id = cur.fetchone()[0]
        else:
            payee_id = payee_id[0]
        
        # Insert the transaction
        cur.execute(
            "INSERT INTO transactions (date, account_id, payee_id, category_id, memo, amount) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (transaction.date, account_id[0], payee_id, category_id[0] if category_id else None, transaction.memo, transaction.amount)
        )

        # Get the id of the newly added transaction
        transaction_id = cur.fetchone()[0]
        # Commit the transaction
        conn.commit()
        transaction.id = transaction_id
        # Return the transaction object with the new id
        return Transaction(**transaction.dict())
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.put("/transactions/update/{transaction_id}", response_model=Transaction, tags=["Transactions"])
async def update_transaction(token: Annotated[str, Depends(oauth2_scheme)], transaction_id: int, transaction: Transaction):
    # Connect to an existing database
    conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
    try:
        # Open a cursor to perform database operations
        cur = conn.cursor()
        # Check if the transaction exists
        cur.execute("SELECT id FROM transactions WHERE id = %s", (transaction_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Check if account exists
        cur.execute("SELECT id FROM accounts WHERE name = %s", (transaction.account_name,))
        account_id = cur.fetchone()
        if account_id is None:
            raise HTTPException(status_code=400, detail="Account not found")
        
        # Check if category exists
        if transaction.category_name:
            cur.execute("SELECT id FROM categories WHERE main_category_id IS NOT NULL and name = %s", (transaction.category_name,))
            category_id = cur.fetchone()
            if category_id is None:
                raise HTTPException(status_code=400, detail="Category not found")
        else:
            category_id = None
        
        # Check if payee exists, if not add one
        cur.execute("SELECT id FROM payees WHERE name = %s", (transaction.payee_name,))
        payee_id = cur.fetchone()
        if payee_id is None:
            cur.execute("INSERT INTO payees (name) VALUES (%s) RETURNING id", (transaction.payee_name,))
            payee_id = cur.fetchone()[0]
        else:
            payee_id = payee_id[0]
        
        # Update the transaction
        cur.execute(
            "UPDATE transactions SET date = %s, account_id = %s, payee_id = %s, category_id = %s, memo = %s, amount = %s WHERE id = %s",
            (transaction.date, account_id[0], payee_id, category_id[0] if category_id else None, transaction.memo, transaction.amount, transaction_id)
        )
        
        # Commit the transaction
        conn.commit()
        transaction.id = transaction_id
        # Return the updated transaction object
        return Transaction(**transaction.dict())
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.post("/transactions/remove/{transaction_id}", response_model=Transaction, tags=["Transactions"])
async def remove_transaction(token: Annotated[str, Depends(oauth2_scheme)],transaction_id: int):
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

@app.put("/transactions/import", response_model=List[Transaction], tags=["Transactions"])
async def upload_csv_transactions(token: Annotated[str, Depends(oauth2_scheme)], file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type")

    data = []
    # read file as bytes and decode bytes into text stream
    file_bytes = file.file.read()
    buffer = StringIO(file_bytes.decode('utf-8-sig'))

    # process CSV
    csvReader = csv.DictReader(buffer)
    conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
    try:
        for row_num, row in enumerate(csvReader, start=1):
            try:
                # Validate CSV row data
                if 'Date' not in row or 'Payee' not in row or 'Amount' not in row or 'Memo' not in row or 'Account' not in row:
                    raise HTTPException(status_code=400, detail=f"Invalid CSV format at row {row_num}")
                if not row['Date'] or not row['Payee'] or not row['Amount'] or not row['Memo'] or not row['Account']:
                    raise HTTPException(status_code=400, detail=f"Missing data in CSV row {row_num}")

                # Open a cursor to perform database operations
                cur = conn.cursor()
                # Check if account exists
                cur.execute("SELECT id FROM accounts WHERE name = %s", (row['Account'],))
                account_id = cur.fetchone()
                if account_id is None:
                    raise HTTPException(status_code=400, detail=f"Account '{row['Account']}' not found at row {row_num}")

                # Check if category exists
                if row['Category']:
                    cur.execute("SELECT id FROM categories WHERE main_category_id IS NOT NULL and name = %s", (row['Category'],))
                    category_id = cur.fetchone()
                    if category_id is None:
                        raise HTTPException(status_code=400, detail=f"Category '{row['Category']}' not found at row {row_num}")
                else:
                    category_id = None

                # Check if payee exists, if not add one
                cur.execute("SELECT id FROM payees WHERE name = %s", (row['Payee'],))
                payee_id = cur.fetchone()
                if payee_id is None:
                    cur.execute("INSERT INTO payees (name) VALUES (%s) RETURNING id", (row['Payee'],))
                    payee_id = cur.fetchone()[0]
                else:
                    payee_id = payee_id[0]

                # Parse date with multiple formats
                date_formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(row['Date'], fmt).strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        parsed_date = None
                if not parsed_date:
                    raise HTTPException(status_code=400, detail=f"Invalid date format at row {row_num}: {row['Date']}")

                # Execute a command: add a transaction
                cur.execute(
                    "INSERT INTO transactions (date, account_id, payee_id, category_id, memo, amount) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                    (parsed_date, account_id[0], payee_id, category_id[0] if category_id else None, row['Memo'], row['Amount'])
                )
                # Get the id of the newly added transaction
                transaction_id = cur.fetchone()[0]
                data.append({
                    "id": transaction_id,
                    "date": parsed_date,
                    "account_name": row['Account'],
                    "payee_name": row['Payee'],
                    "category_name": row['Category'] if row['Category'] else None,
                    "memo": row['Memo'],
                    "amount": float(row['Amount'])
                })
                # Commit the transaction
                conn.commit()
                cur.close()
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing row {row_num}: {str(e)}")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    # close buffer and file
    buffer.close()
    file.file.close()

    return [Transaction(**item) for item in data]




