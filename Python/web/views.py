from flask import Blueprint, render_template
import psycopg2 as pg
import os

web = Blueprint('web', __name__)

@web.route('/')
def home():
    return render_template('home.html', active_page='home')

@web.route('/transactions')
def transactions():
    try:
        conn = pg.connect(f"host=db dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}")
        cursor = conn.cursor()

        # simple all row query
        cursor.execute("""
                       SELECT date AS DATE,
                              account_name                                  AS ACCOUNT,
                              payee_name                                    AS PAYEE,
                              category_name                                 AS CATEGORY,
                              memo                                          AS NOTE,
                              amount                                        AS AMOUNT
                       FROM transactions_view
                       """)

        # get all headings and data
        headings = tuple([desc[0].capitalize() for desc in cursor.description])
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("transactions.html", transaction_headings=headings, transaction_data=data, active_page='transactions')
    except pg.Error as e:
        print("Database error:", e)
        return render_template("transactions.html", transaction_headings=None, transaction_data=None, active_page='transactions')

@web.route('/reports')
def reports():
    return render_template('reports.html', active_page='reports')

@web.route('/settings')
def settings():
    return render_template('settings.html', active_page='settings')