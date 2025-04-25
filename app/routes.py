# app/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User, Expense
from .forms import RegisterForm, LoginForm, ExpenseForm
from .extensions import db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("❌ Username is already taken. Please choose another.")
            return render_template('register.html', form=form)

        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("✅ Registered successfully! Please log in.")
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.upload'))  # Redirect if already logged in
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("✅ Logged in successfully!")
            return redirect(url_for('main.upload'))  # Corrected typo here
        else:
            flash("❌ Invalid username or password.")
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user() 
    return redirect(url_for('main.login'))

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = ExpenseForm()
    if form.validate_on_submit():
        for field_name in [
            'rent', 'utilities', 'groceries', 'eating_out', 'transport',
            'entertainment', 'subscriptions', 'health', 'education', 'insurance',
            'debt_repayment', 'travel', 'gifts_donations', 'savings_investments',
            'pets', 'other'
        ]:
            amount = getattr(form, field_name).data
            if amount and amount > 0:
                expense = Expense(
                    user_id=current_user.id,
                    month=form.month.data,
                    category=form[field_name].label.text,
                    amount=amount,
                    city=form.city.data
                )
                db.session.add(expense)
        db.session.commit()
        flash("Expenses uploaded!")
        return redirect(url_for('main.visualise'))
    return render_template('upload.html', form=form)

@main.route('/visualise')
@login_required
def visualise():
    user_expenses = Expense.query.filter_by(user_id=current_user.id).all()
    # Define what’s a need and what’s a want
    needs = ['Rent', 'Utilities', 'Groceries', 'Transport', 'Health', 'Education', 'Insurance', 'Debt Repayment']
    wants = ['Eating Out', 'Entertainment', 'Subscriptions', 'Travel', 'Gifts/Donations', 'Pets', 'Other', 'Savings/Investments']


    # 🟠 1. Category totals for pie chart
    category_totals = {}
    for exp in user_expenses:
        category_totals[exp.category] = category_totals.get(exp.category, 0) + exp.amount

    needs_total = sum(amount for cat, amount in category_totals.items() if cat in needs)
    wants_total = sum(amount for cat, amount in category_totals.items() if cat in wants)

    # Hardcoded budgets per category (in a real app this would be user input)
    budgets = {
    'Rent': 1500,
    'Utilities': 200,
    'Groceries': 400,
    'Eating Out': 250,
    'Transport': 180,
    'Entertainment': 150,
    'Subscriptions': 100,
    'Health': 120,
    'Education': 300,
    'Other': 100
    }

    actual = []
    budget = []
    categories_for_budget = []

    for cat in budgets:
        categories_for_budget.append(cat)
        budget.append(budgets[cat])
        actual.append(category_totals.get(cat, 0))  # 0 if no data


    # 🔵 2. Monthly totals for line chart
    from collections import defaultdict
    monthly_totals = defaultdict(float)
    for exp in user_expenses:
        monthly_totals[exp.month] += exp.amount

    # Sort by month
    sorted_months = sorted(monthly_totals.keys())
    monthly_values = [monthly_totals[month] for month in sorted_months]

    # 🔥 3. Top 3 categories
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    top_categories = sorted_categories[:3]
    top_labels = [item[0] for item in top_categories]
    top_values = [item[1] for item in top_categories]


    return render_template('visualise.html',
    labels=list(category_totals.keys()),
    values=list(category_totals.values()),
    months=sorted_months,
    monthly_totals=monthly_values,
    top_labels=top_labels,
    top_values=top_values,
    categories_for_budget=categories_for_budget,
    actual=actual,
    budget=budget,
    needs_total=needs_total,
    wants_total=wants_total

)



