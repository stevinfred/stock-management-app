# Stock Management App

A simple web application for small shops to manage products, record sales and track stock levels. Built with Flask and SQLite.

## Features

- Add, edit and delete products (name, price, quantity, alert threshold)
- Record sales (stock decreases automatically)
- Low stock alert when a product reaches its threshold
- Sales history with total revenue and sale cancellation
- Login with two roles:
  - **Manager**: full access
  - **Seller**: can view products and record sales

## Tech stack

- Python 3.13
- Flask, Flask-SQLAlchemy, Flask-Login
- SQLite
- HTML (Jinja2 templates)

## Installation

```
git clone https://github.com/stevinfred/stock-management-app.git
cd stock-management-app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Demo accounts

| Role    | Username | Password   |
|---------|----------|------------|
| Manager | manager  | manager123 |
| Seller  | seller   | seller123  |

These accounts are for demonstration only. Change them before any real use.

## Roadmap

- Export sales to PDF/Excel
- Dashboard with charts
- Responsive design
- Mobile money payment integration