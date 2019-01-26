# Header files (Import all needed libraries)
from flask import Flask, render_template, redirect, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

from datetime import datetime
from sqlite3 import connect

import re

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
def index():
  return render_template("index.html")


@app.route("/transaction", methods=["GET", "POST"])
def transaction():
  if request.method == "POST":
    try:
      transactionId = int(request.form.get('transactionId'))
      clientId = int(request.form.get('clientId'))
      clientName = str(request.form.get('clientName'))
      itemId = int(request.form.get('itemId'))
      weight = float(request.form.get('weight'))
      descreption = str(request.form.get('descreption'))
      price = float(request.form.get('price'))
      total = float(request.form.get('total'))
      paid = float(request.form.get('paid'))
    except:
      return "الرجاء التأكد من تعبئة النموذج كاملاً"

    if False or '' in (transactionId, clientId, clientName, itemId, weight, price, total):
      return "الرجاء التأكد من تعبئة النموذج كاملاً"

    if clientId == 1 and paid == 0:
      return "لا يمكن دفع ذمم عندما يكون الدفع نقدي"

    if total - paid < 0:
      return "لا يمكن دفع اكثر من المبلغ المطلوب. اذا اردت الايداع ، الرجاء الاستعانة بخاصية حركة مالية"

    currTime = datetime.now().strftime("%Y-%m-%d")
    db.execute("INSERT INTO transactions (transactionId, clientId, itemId, weight,"
              + "descreption, price, total, paid, typeId, typeName, date)"
              + "VALUES ((?), (?), (?), (?), (?), (?), (?), (?), (?), (?), (?))",
              [transactionId, clientId, itemId, weight, descreption, price, total, paid, "S", "بيع", currTime])
    db.commit()

    db.execute("INSERT INTO cash (transactionId, clientId, amount, typeId, type_name, date)"
              + "VALUES ((?), (?), (?), (?), (?), (?))", [transactionId, clientId, paid, "S", "بيع", currTime])
    db.commit()

    total -= paid

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
def transactionLog():
  dateStart = request.args.get('start')
  dateEnd = request.args.get('end')
  if not dateStart and not dateEnd:
    transactions = []
    query = db.execute("SELECT * FROM transactions ORDER BY transactionId DESC").fetchall()
    for record in query:
      print(record)
      itemNameQuery = db.execute("SELECT item_name FROM inventory WHERE itemId = (?)", [record[2]]).fetchone()
      transactions.append({
        'transactionId': record[0],
        'clientId': record[1],
        'itemName': itemNameQuery[0] if itemNameQuery else "",
        'weight': record[3],
        'descreption': record[4],
        'price': record[5],
        'total': record[6],
        'paid': record[7],
        'type': record[9],
        'date': record[10]
      })
    return render_template('transactionLog.html', transactions=transactions, dateNow=datetime.now().strftime("%Y-%m-%d"))
  else:
    transactions = []
    query = db.execute("SELECT * FROM transactions WHERE date >= (?) AND date <= (?) ORDER BY transactionId DESC",
      [dateStart, dateEnd]).fetchall()
    if not query:
      return "لا يوجد حركات بهذه الفترة"
    for record in query:
      print(record)
      itemNameQuery = db.execute("SELECT item_name FROM inventory WHERE itemId = (?)", [record[2]]).fetchone()
      transactions.append({
        'transactionId': record[0],
        'clientId': record[1],
        'itemName': itemNameQuery[0] if itemNameQuery else "",
        'weight': record[3],
        'descreption': record[4],
        'price': record[5],
        'total': record[6],
        'paid': record[7],
        'type': record[9],
        'date': record[10]
      })
      print(transactions)
    return jsonify({ 'transactions': transactions })


@app.route("/clients", methods=["GET", "POST"])
def clients():
  if request.method == "POST":
    try:
      id = int(request.form.get("id"))
      name = str(request.form.get("name"))
      phone = str(request.form.get("phone"))
      balance = float(request.form.get("balance"))
      print(id, name, phone, balance)
    except:
      return "الرجاء التأكد من تعبئة النموذج كاملاً"

    if (None in (id, name, phone)) or (len(name) < 3):
      return "الرجاء التأكد من تعبئة النموذج كاملاً"

    db.execute("INSERT INTO clients (clientId, client_name, client_phone, client_balance)"
              + "VALUES ((?), (?), (?), (?))", [id, name, phone, balance])
    db.commit()

    return "/clients"

  else:
    clients = []
    query = db.execute('SELECT * FROM clients ORDER BY clientId').fetchall()
    for record in query:
      clients.append({
        'id': record[0],
        'name': record[1],
        'phone': record[2],
        'balance': record[3]
      })
    return render_template('clients.html', clients=clients)

@app.route("/u/<clientId>")
def client(clientId):
  clientId = int(clientId)
  print(clientId)
  if clientId == 1:
    return redirect("/cash")

  if clientId:
    clientQ = db.execute("SELECT * FROM clients WHERE clientId = (?)", [clientId]).fetchone()
    client = {
      'id': clientQ[0],
      'name': clientQ[1], # problem on this line, jinja not rendering the full name
      'phone': clientQ[2],
      'balance': clientQ[3]
    }
    transactions = []
    transactionQ = db.execute("SELECT * FROM transactions WHERE clientId = (?) ORDER BY transactionId", [clientId]).fetchall()
    for record in transactionQ:
      itemNameQuery = db.execute("SELECT item_name FROM inventory WHERE itemId = (?)", [record[2]]).fetchone()
      transactions.append({
        'transactionId': record[0],
        'itemName': itemNameQuery[0] if itemNameQuery else "",
        'weight': record[3],
        'descreption': record[4],
        'price': record[5],
        'total': record[6],
        'paid': record[7],
        'type': record[9],
        'date': record[10]
      })
  return render_template('client.html', client=client, transactions=transactions)


@app.route("/addItems", methods=["GET", "POST"])
def addItems():
  if request.method == "POST":
    try:
      transactionId = int(request.form.get('transactionId'))
      itemId = int(request.form.get('itemId'))
      itemPrice = float(request.form.get('itemPrice'))
      itemStock = float(request.form.get('itemStock'))
      total = float(request.form.get('total'))
    except:
      return "الرجاء التأكد من تعبئة النموذج كاملاً"


    if None in (itemId, itemPrice, itemStock):
      return "تأكد من تعبة النموذج كاملاً"

    stock = db.execute("SELECT item_stock FROM inventory WHERE itemId = (?)",[itemId]).fetchone()[0]
    stock += itemStock
    db.execute("UPDATE inventory SET item_stock = (?) WHERE itemId = (?)", [stock, itemId])
    db.commit()

    currTime = datetime.now().strftime("%Y-%m-%d")
    db.execute("INSERT INTO transactions (transactionId, clientId, itemId, weight,"
              + "descreption, price, total, paid, typeId, typeName, date)"
              + "VALUES ((?), 1, (?), (?), '', (?), (?), (?), (?), (?), (?))",
              [transactionId, itemId, itemStock, itemPrice, total, total, "B", "شراء", currTime])
    db.commit()

    db.execute("INSERT INTO cash (transactionId, clientId, amount, typeId, type_name, date)"
              + "VALUES ((?), 1, (?), (?), (?), (?))", [transactionId, -total, "B", "شراء", currTime])
    db.commit()


    balance = db.execute("SELECT client_balance FROM clients WHERE clientId = 1").fetchone()[0]
    balance -= total
    db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = 1", [balance])
    db.commit()

    return "/addItems"
  else:
    transactionId = db.execute("SELECT transactionId FROM transactions ORDER BY transactionId DESC LIMIT 1").fetchone()[0]
    return render_template("addItems.html", transactionId=(transactionId+1))


@app.route('/repayDebt', methods=["GET", "POST"])
def repayDebt():
  if request.method == "POST":
    try:
      transactionId = int(request.form.get('transactionId'))
      clientId = int(request.form.get('clientId'))
      amount = float(request.form.get('amount'))
    except:
      return "الرجاء التأكد من تعبئة النموذج صحيحاَ"

    if None or False in (transactionId, clientId, amount):
      return "الرجاء التأكد من تعبئة النموذج صحيحاَ"


    currTime = datetime.now().strftime("%Y-%m-%d")
    db.execute("INSERT INTO transactions (transactionId, clientId, itemId, weight,"
              + "descreption, price, total, paid, typeId, typeName, date)"
              + "VALUES ((?), (?), '', '', '', '', '', (?), (?), (?), (?))",
              [transactionId, clientId, amount, "R", "سداد ذمم", currTime])
    db.commit()

    db.execute("INSERT INTO cash (transactionId, clientId, amount, typeId, type_name, date)"
              + "VALUES ((?), (?), (?), (?), (?), (?))", [transactionId, clientId, amount, "R", "سداد ذمم", currTime])
    db.commit()


    clientCash = db.execute("SELECT client_balance FROM clients WHERE clientId = (?)", [clientId]).fetchone()[0]
    clientCash += amount
    db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = (?)", [clientCash, clientId])
    db.commit()

    cash = db.execute("SELECT client_balance FROM clients WHERE clientId = 1").fetchone()[0]
    cash += amount
    db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = 1", [cash])
    db.commit()

    return "/repayDebt"
  else:
    transactionId = db.execute("SELECT transactionId FROM transactions ORDER BY transactionId DESC LIMIT 1").fetchone()[0]
    return render_template('repayDebt.html', transactionId=(transactionId+1))


@app.route("/cash")
def cash():
  stats = {
    'total': 0,
    'balance': db.execute("SELECT client_balance FROM clients WHERE clientId = 1").fetchone()[0]
  }
  transactions = []
  query = db.execute("SELECT * FROM cash ORDER BY transactionId DESC").fetchall()
  for record in query:
    stats['total'] += record[2]
    transactions.append({
      'id': record[0],
      'clientId': record[1],
      'amount': record[2],
      'descreption': str("حركة " + str(record[4]) +  " بيد عميل رقم " + "(" +str(record[1]) + ")" + " حركة رقم " + "(" + str(record[0]) + ")"),
      'type': record[4],
      'date': record[5]
    })
  return render_template('cash.html', transactions=transactions, stats=stats)


@app.route("/expense", methods=["GET", "POST"])
def expense():
  if request.method == "POST":
    try:
      transactionId = int(request.form.get('transactionId'))
      descreption = str(request.form.get('descreption'))
      amount = float(request.form.get('amount'))
    except:
      return "الرجاء التأكد من تعبئة النموذج صحيحاَ"

    if None or False in (transactionId, descreption, amount):
      return "الرجاء التأكد من تعبئة النموذج صحيحاَ"

    currTime = datetime.now().strftime("%Y-%m-%d")
    db.execute("INSERT INTO transactions (transactionId, clientId, itemId, weight,"
              + "descreption, price, total, paid, typeId, typeName, date)"
              + "VALUES ((?), 1, '', '', (?), '', '', (?), (?), (?), (?))",
              [transactionId, descreption, amount, "E", "مصروفات", currTime])
    db.commit()

    db.execute("INSERT INTO cash (transactionId, clientId, amount, typeId, type_name, date)"
              + "VALUES ((?), 1, (?), (?), (?), (?))", [transactionId, -amount, "E", "مصروفات", currTime])
    db.commit()

    cash = db.execute("SELECT client_balance FROM clients WHERE clientId = 1").fetchone()[0]
    cash -= amount
    db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = 1", [cash])
    db.commit()

    return "/expense"
  else:
    transactionId = db.execute("SELECT transactionId FROM transactions ORDER BY transactionId DESC LIMIT 1").fetchone()[0]
    return render_template('expense.html', transactionId=(transactionId+1))

@app.route("/inventory")
def inventory():
  items = []
  query = db.execute("SELECT * FROM inventory ORDER BY itemId").fetchall()
  for record in query:
    items.append({
      'id': record[0],
      'name': record[1],
      'stock': record[2]
    })
  return render_template('inventory.html', items=items)


# Info gathering routes
@app.route("/getClients")
def getClientId():
  query = db.execute("SELECT client_name FROM clients ORDER BY clientId").fetchall()
  return jsonify( { 'clientArr': list(query) } )

@app.route("/getTransactionsByType")
def getTransactionsByType():
  transactions = []
  query = db.execute("SELECT * FROM cash WHERE typeId = (?)", [request.args.get('typeId')]).fetchall()
  for record in query:
    transactions.append({
      'id': record[0],
      'clientId': record[1],
      'amount': record[2],
      'descreption': str("حركة " + str(record[4]) +  " بيد عميل رقم " + "(" +str(record[1]) + ")" + " حركة رقم " + "(" + str(record[0]) + ")"),
      'type': record[4],
      'date': record[5]
    })
  return jsonify(transactions)