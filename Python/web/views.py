#!/usr/bin/env python3
from flask import Blueprint, render_template
from sys import path
from models.models import Transaction
from sqlalchemy import desc
web = Blueprint('web', __name__)

@web.route('/')
def home():
    return render_template('home.html', active_page='home')

@web.route('/transactions')
def transactions():
    try:
        # ORM query
        transactions_data = Transaction.query.order_by(desc(Transaction.date)).all()

        headings = ('Date', 'Account', 'Payee', 'Category', 'Note', 'Amount')
        data = tuple(
            (t.date, t.account.name, t.payee.name, t.category.name, t.memo, t.amount)
            for t in transactions_data
        )

        ids = [t.id for t in transactions_data]

        return render_template(
            "transactions.html",
            transaction_headings=headings,
            transaction_data=list(zip(data, ids)),
            active_page='transactions'
        )

    except Exception as e:
        print("Database error:", e)
        return render_template(
            "transactions.html",
            transaction_headings=[],
            transaction_data=[],
            transactions_ids=[],
            active_page='transactions'
        )

@web.route('/reports')
def reports():
    return render_template('reports.html', active_page='reports')

@web.route('/settings')
def settings():
    return render_template('settings.html', active_page='settings')