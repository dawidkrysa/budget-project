#!/usr/bin/env python3
from flask import Blueprint, render_template
from sys import path
from models.models import Transaction, Category, Budget, db
from sqlalchemy import desc, func, extract
web = Blueprint('web', __name__)

@web.route('/')
def home():
    year = 2025
    month = 7

    categories_data = Category.query.filter(Category.main_category_id.isnot(None)).all()

    result = {}

    for c in categories_data:
        main_cat_name = c.main_category.name
        if main_cat_name not in result:
            result[main_cat_name] = []

        # Find budget for this category with year=2025, month=7
        budget = Budget.query.filter_by(category_id=c.id, year=year, month=month).first()
        assigned = budget.assigned if budget else None

        # Get activity sum from transactions in this category for year/month
        activity = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)) \
            .filter(Transaction.category_id == c.id) \
            .filter(extract('year', Transaction.date) == year) \
            .filter(extract('month', Transaction.date) == month) \
            .scalar()

        cat_info = {
            "name": c.name,
            "assigned": assigned,
            "available": assigned - activity,
            "activity": activity
        }

        result[main_cat_name].append(cat_info)


    return render_template('home.html', active_page='home', main_categories = result)

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