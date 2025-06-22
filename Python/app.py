from dotenv import load_dotenv
import psycopg2 as pg
from flask import Flask, render_template, request, redirect, url_for

load_dotenv("/app/.env")
app = Flask(__name__)
@app.route("/")
def home():
    return render_template("index.html")

#     conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")