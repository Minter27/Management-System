# Header files (Import all needed libraries)
from flask import Flask, render_template, redirect, request, session, jsonify, flash, abort
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

from datetime import datetime
from random import randint
from sqlite3 import connect

import re
import time
import os

# Configure flask app
app = Flask(__name__)

# Configure the database's connection with python
db = connect("website.db", check_same_thread=False)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
  response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
  response.headers["Expires"] = 0
  response.headers["Pragma"] = "no-cache"
  return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():
  return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  # Forget any user_id
  session.clear()
  
  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")
    query = db.execute("SELECT * FROM users WHERE username = (?)", [username]).fetchone()
    if not query or not check_password_hash(query[2], password):
      return "كلمة السر او اسم المستخدم خاطئ"

    # Remember which user has logged in
    session["user_id"] = query[0]

    # Redirect user to home page
    return "/"
  else:
    return render_template("login.html")


@app.route("/transaction", methods=["GET", "POST"])
@login_required
def transaction():
  #transactionIdQ = db.execute("SELECT MAX(transactionId) FROM transactions").fetchone()
  if request.method == "POST":
    transactionId = int(request.form.get('transactionId'))
    clientId = int(request.form.get('clientId'))
    clientName = str(request.form.get('clientName'))
    itemId = int(request.form.get('itemId'))
    weight = float(request.form.get('weight'))
    descreption = str(request.form.get('descreption'))
    price = float(request.form.get('price'))
    total = float(request.form.get('total'))
    paid = float(request.form.get('paid'))

    if False or '' in (transactionId, clientId, clientName, itemId, weight, price, total):
      return "الرجاء التأكد من تعبئة النموذج كاملاً"

    if clientId == 1 and paid == 0:
      return "لا يمكن عد الدفع عندما يكون الدفع نقدي"
    
    # Under questioning
    total -= paid
    if total < 0:
      return "لا يمكن دفع اكثر من المبلغ المطلوب. اذا اردت الايداع ، الرجاء الاستعانة بخاصية حركة مالية"
    

    currTime = datetime.now().strftime("%Y-%m-%d")
    db.execute("INSERT INTO transactions (transactionId, clientId, itemId, weight, descreption, price, total, paid, date)"
              + "VALUES ((?), (?), (?), (?), (?), (?), (?), (?), (?))", 
              [transactionId, clientId, itemId, weight, descreption, price, total, paid, currTime])
    db.commit()

    currBalance = db.execute("SELECT client_balance FROM clients WHERE clientId =(?)", [clientId]).fetchone()[0]
    currBalance -= total
    db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = (?)", [currBalance, clientId])
    db.commit()

    currStock = db.execute("SELECT item_stock FROM inventory WHERE itemId = (?)", [itemId]).fetchone()[0]
    currStock -= weight
    db.execute("UPDATE inventory SET item_stock = (?) WHERE itemId = (?)", [currStock, itemId])
    db.commit()

    return "/transaction"
  else:
    transactionId = db.execute("SELECT transactionId FROM transactions ORDER BY transactionId DESC LIMIT 1").fetchone()[0]
    return render_template("transactionForm.html", transactionId=(transactionId + 1))

@app.route("/transactionLog", methods=["GET"])
@login_required
def transactionLog():
  transactions = []
  query = db.execute("SELECT * FROM transactions ORDER BY transactionId DESC").fetchall()
  for record in query:
    print(record)
    itemNameQuery = db.execute("SELECT item_name FROM inventory WHERE itemId = (?)", [record[2]]).fetchone()
    transactions.append({ 
      'transactionId': record[0], 
      'clientId': record[1],
      'itemName': itemNameQuery[0],
      'weight': record[3],
      'descreption': record[4],
      'price': record[5],
      'total': record[6],
      'paid': record[7],
      'date': record[8]  
    })
  print(transactions)
  return render_template('transactionLog.html', transactions=transactions)

# Info gathering routes
@app.route("/getClients")
def getClientId():
  query = db.execute("SELECT client_name FROM clients ORDER BY clientId").fetchall()
  return jsonify( { 'clientArr': list(query) } )
