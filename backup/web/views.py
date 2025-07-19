#!/usr/bin/env python3
from flask import Blueprint, render_template
from collections import defaultdict
from models import Transaction, Category, Budget, Month
from backend.Python import db
from sqlalchemy import desc
import datetime
import calendar

web = Blueprint('web', __name__)


@web.route('/')
def home():
    budget = Budget.query.first() # TODO: To be replaced
    x = datetime.datetime.now()
    current_month = Month.query.filter_by(year=x.year, month=x.month, deleted=False, budget_id=budget.id).first()
    all_months = Month.query.filter_by(deleted=False, budget_id=budget.id).order_by(Month.year.desc(),Month.month.desc()).all()

    result = {}
    for month in all_months:

        categories_data = Category.query.filter_by(
            budget_id= budget.id,
            deleted= False,
            hidden= False,
            month_id = month.id
        ).all()

        tmp = defaultdict(list)
        for c in categories_data:
            tmp[c.category_group.name].append(c)

        result[f"{calendar.month_name[month.month]} {month.year}"] = dict(tmp)

    return render_template('home.html',
                           active_page='home',
                           all_categories = result,
                           budget_id = budget.id,
                           to_be_budgeted = current_month.to_be_budgeted)

@web.route('/transactions')
def transactions():
    try:
        # ORM query
        budget = Budget.query.first() # TODO: To be replaced
        transactions_data = Transaction.query.filter_by(
        budget_id= budget.id,
        deleted= False
        ).order_by(desc(Transaction.date)).all()

        headings = ('Date', 'Account', 'Payee', 'Category', 'Note', 'Amount')
        data = tuple(
            (t.date, t.account.name, t.payee.name, t.category.category_name.name, t.memo, t.amount)
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
            budget_id = budget.id,
            active_page='transactions'
        )

@web.route('/reports')
def reports():
    return render_template('reports.html', active_page='reports')

@web.route('/settings')
def settings():
    return render_template('settings.html', active_page='settings')