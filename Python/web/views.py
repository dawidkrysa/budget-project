#!/usr/bin/env python3
from flask import Blueprint, render_template
from sys import path
from models.models import Transaction

web = Blueprint('web', __name__)

@web.route('/')
def home():
    return render_template('home.html', active_page='home')

@web.route('/transactions')
def transactions():
    try:
        # ORM query
        transactions_view = Transaction.query.all()

        headings = ('Date', 'Account', 'Payee', 'Category', 'Note', 'Amount')
        data = tuple(
            (t.date, t.account_name, t.payee_name, t.category_name, t.memo, t.amount)
            for t in transactions_view
        )

        return render_template(
            "transactions.html",
            transaction_headings=headings,
            transaction_data=data,
            active_page='transactions'
        )

    except Exception as e:
        print("Database error:", e)
        return render_template(
            "transactions.html",
            transaction_headings=None,
            transaction_data=None,
            active_page='transactions'
        )

@web.route('/reports')
def reports():
    return render_template('reports.html', active_page='reports')

@web.route('/settings')
def settings():
    return render_template('settings.html', active_page='settings')