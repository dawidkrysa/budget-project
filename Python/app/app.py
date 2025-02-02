from fastapi import Body, FastAPI
from pydantic import BaseModel
from typing import Annotated
import json
import os
from dotenv import load_dotenv
import psycopg2 as pg
from typing import List

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

# Simple GET endpoint to get all categories
@app.get("/categories/", response_model=List[Category])
async def get_all_categories():
    # Connect to an existing database
    conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
    # Open a cursor to perform database operations
    cur = conn.cursor()
    cur.execute("SELECT * FROM categories WHERE main_category_id IS NOT NULL")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Convert the result into a list of dictionaries
    # This assumes that you have column names in your query
    columns = [desc[0] for desc in cur.description]
    result = [dict(zip(columns, row)) for row in rows]
    return result
