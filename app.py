# Header files (Import all needed libraries)
from flask import Flask, render_template, redirect, request, session, jsonify, make_response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime
from sqlite3 import connect

import pdfkit

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
def index():
  return render_template("index.html")


@app.route("/transaction", methods=["GET", "POST"])
def transaction():
  if request.method == "POST":
    try:
      transactionId = int(request.form.get('transactionId'))
      clientId = int(request.form.get('clientId'))
      itemId = int(request.form.get('itemId'))
      weight = float(request.form.get('weight'))
      descreption = str(request.form.get('descreption'))
      price = float(request.form.get('price'))
      total = float(request.form.get('total'))
      paid = float(request.form.get('paid'))
    except:
      return "الرجاء التأكد من تعبئة النموذج كاملاً"

    if False or '' in (transactionId, clientId, itemId, weight, price, total):
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

    currBalance = db.execute("SELECT client_balance FROM clients WHERE clientId = (?)", [clientId]).fetchone()[0]
    currBalance -= (total - paid)
    db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = (?)", [currBalance, clientId])
    db.commit()

    cashBlanace = db.execute("SELECT client_balance FROM clients WHERE clientId = 1").fetchone()[0]
    cashBlanace += paid
    db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = 1", [cashBlanace])
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
      cleintNameQuery = db.execute("SELECT client_name FROM clients WHERE clientId = (?)", [record[1]]).fetchone()
      itemNameQuery = db.execute("SELECT item_name FROM inventory WHERE itemId = (?)", [record[2]]).fetchone()
      transactions.append({
        'transactionId': record[0],
        'clientId': record[1],
        'clientName': cleintNameQuery[0] if cleintNameQuery else "",
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
    except:
      return "الرجاء التأكد من تعبئة النموذج كاملاً"

    if (None in (id, name, )) or (len(name) < 3):
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

@app.route("/u/<clientId>", methods=["GET"])
def client(clientId):
  clientId = int(clientId)
  print(clientId)
  if clientId == 1:
    return redirect("/cash")

  if clientId:
    clientQ = db.execute("SELECT * FROM clients WHERE clientId = (?)", [clientId]).fetchone()
    client = {
      'id': clientQ[0],
      'name': clientQ[1],
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

    stock = db.execute("SELECT item_stock FROM inventory WHERE itemId = (?)",[itemId]).fetchone()[0]
    stock += itemStock
    db.execute("UPDATE inventory SET item_stock = (?) WHERE itemId = (?)", [stock, itemId])
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


@app.route("/cash", methods=["GET"])
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

@app.route("/inventory", methods=["GET", "POST"])
def inventory():
  if request.method == "POST":
    try:
      id = int(request.form.get("id"))
      name = str(request.form.get("name"))
    except:
      return "الرجاء التأكد من تعبئة النموذج كاملاً"

    if None in (id, name):
      return "الرجاء التأكد من تعبئة النموذج كاملاً"
    
    db.execute("INSERT INTO inventory (itemId, item_name, item_stock) VALUES ((?), (?), 0)", [id, name])
    db.commit()

    return "/inventory"

  else:
    items = []
    query = db.execute("SELECT * FROM inventory ORDER BY itemId").fetchall()
    for record in query:
      items.append({
        'id': record[0],
        'name': record[1],
        'stock': record[2]
      })
    return render_template('inventory.html', items=items)

@app.route("/print/<page>/<client>", methods=["GET"])
def printPDF(page, client):
  if page == "clientsAll":
    clients = []
    query = db.execute('SELECT * FROM clients ORDER BY clientId').fetchall()
    for record in query:
      clients.append({
        'id': record[0],
        'name': record[1],
        'phone': record[2],
        'balance': record[3]
      })
    rendered = render_template("pdfs/clientsPDF.html", clients=clients)
  elif page == "transactions":
    transactions = []
    query = db.execute("SELECT * FROM transactions WHERE date >= (?) AND date <= (?) ORDER BY transactionId DESC",
      [request.args.get('dateStart'), request.args.get('dateEnd')]).fetchall()
    for record in query:
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
    rendered = render_template('pdfs/transactionsPDF.html', 
      transactions=transactions,
      date="سجل الحركات من تاريخ " + request.args.get('dateStart') + " الى تاريخ " + request.args.get('dateEnd')
    )
  elif page == "u" and int(client) > 0:
    clientId = int(client)
    print(clientId)
    if clientId == 1:
      typeId = request.args.get('typeId') or '_'
      total = 0
      transactions = []
      query = db.execute("SELECT * FROM cash WHERE typeId LIKE (?) ORDER BY transactionId DESC", [typeId]).fetchall()
      for record in query:
        total += record[2]
        transactions.append({
          'id': record[0],
          'clientId': record[1],
          'amount': record[2],
          'descreption': str("حركة " + str(record[4]) +  " بيد عميل رقم " + "(" +str(record[1]) + ")" + " حركة رقم " + "(" + str(record[0]) + ")"),
          'type': record[4],
          'date': record[5]
        })
      rendered = render_template("pdfs/cashPDF.html", total=total, transactions=transactions)
    else:
      clientQ = db.execute("SELECT * FROM clients WHERE clientId = (?)", [clientId]).fetchone()
      client = {
        'id': clientQ[0],
        'name': clientQ[1],
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
      rendered = render_template('pdfs/clientPDF.html', client=client, transactions=transactions)
  

  options = {
    'page-size': 'A4',
    'margin-top': '0.50in',
    'margin-right': '0.40in',
    'margin-bottom': '0.50in',
    'margin-left': '0.40in',
    'encoding': "UTF-8",
  }
  
  pdf = pdfkit.from_string(rendered, False, options=options)

  response = make_response(pdf)
  response.headers['Content-Type'] = 'application/pdf'
  response.headers['Content-Disposition'] = 'inline;'

  return response

@app.route("/editTransactionForm", methods=["GET", "POST"])
def editTransactionForm():
  if request.method == "POST":
    try:
      transactionId = int(request.form.get('transactionId'))
      typeId = str(request.form.get('typeId'))
      typeName = str(request.form.get('typeName'))
      clientId = int(request.form.get('clientId'))
      itemId = int(request.form.get('itemId'))
      weight = float(request.form.get('weight'))
      descreption = str(request.form.get('descreption'))
      price = float(request.form.get('price'))
      total = float(request.form.get('total'))
      paid = float(request.form.get('paid'))
      next = str(request.form.get('next'))
    except:
      return "الرجاء التأكد من تعبئة النموذج كاملاً"

    if None or False in (transactionId, typeId, typeName, clientId):
      return "الرجاء التأكد من تعبئة النموذج كاملاً"

    if clientId == 1 and paid == 0:
      return "لا يمكن دفع ذمم عندما يكون الدفع على حساب نقدي"

    initialQuery = db.execute("SELECT transactionId, clientId, itemId, weight, total, paid FROM transactions WHERE transactionId = (?)", [transactionId]).fetchone()
    initial = {
      'transactionId': initialQuery[0],
      'clientId': initialQuery[1],
      'itemId': initialQuery[2],
      'weight': initialQuery[3],
      'total': initialQuery[4],
      'paid': initialQuery[5]
    }

    if transactionId != initial['transactionId']:
      return "لا يمكن تغيير رقم الحركة"

    
    if (typeId == "B" or typeId == "E") and clientId != initial['clientId']:
      return "لا يمكن تغيير العميل عندما تكون الحركة شراء او نفقة"


    currTime = datetime.now().strftime("%Y-%m-%d")
    db.execute("UPDATE transactions SET clientId = (?), itemId = (?), weight = (?),"
              + "descreption = (?), price = (?), total = (?), paid = (?), typeId = (?),"
              + "typeName = (?), date = (?) WHERE transactionId = (?)",
              [clientId, itemId, weight, descreption, price, total, paid, typeId, 
              typeName, currTime, transactionId])
    db.commit()

    if typeId == "S":
      if clientId == 1 and paid == 0:
        return "لا يمكن دفع ذمم عندما يكون الدفع على حساب نقدي"

      if total - paid < 0:
        return "لا يمكن دفع اكثر من المبلغ المطلوب. اذا اردت الايداع ، الرجاء الاستعانة بخاصية حركة مالية"

      db.execute("UPDATE cash SET clientId = (?), amount = (?), typeId = (?),"
                + "type_name = (?), date = (?) WHERE transactionId = (?)", 
                [clientId, paid, typeId, typeName, currTime, transactionId])
      db.commit()

      if clientId != initial['clientId']:
        currBalance = db.execute("SELECT client_balance FROM clients WHERE clientId = (?)", [initial['clientId']]).fetchone()[0]
        currBalance += (initial['total'] - initial['paid'])
        db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = (?)", [currBalance, initial['clientId']])
        db.commit()

        currBalance = db.execute("SELECT client_balance FROM clients WHERE clientId = (?)", [clientId]).fetchone()[0]
        currBalance -= (total - paid)
        db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = (?)", [currBalance, clientId])
        db.commit()
      else:
        currBalance = db.execute("SELECT client_balance FROM clients WHERE clientId = (?)", [clientId]).fetchone()[0]
        currBalance += (initial['total'] - initial['paid']) - (total - paid)
        db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = (?)", [currBalance, clientId])
        db.commit()

      cashBlanace = db.execute("SELECT client_balance FROM clients WHERE clientId = 1").fetchone()[0]
      cashBlanace += (paid - initial['paid'])
      db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = 1", [cashBlanace])
      db.commit()

      if itemId != initial['itemId']:
        currStock = db.execute("SELECT item_stock FROM inventory WHERE itemId = (?)", [initial['itemId']]).fetchone()[0]
        currStock += initial['weight']
        db.execute("UPDATE inventory SET item_stock = (?) WHERE itemId = (?)", [currStock, initial['itemId']])

        currStock = db.execute("SELECT item_stock FROM inventory WHERE itemId = (?)", [itemId]).fetchone()[0]
        currStock -= weight
        db.execute("UPDATE inventory SET item_stock = (?) WHERE itemId = (?)", [currStock, itemId])
        db.commit()
      else:
        currStock = db.execute("SELECT item_stock FROM inventory WHERE itemId = (?)", [itemId]).fetchone()[0]
        currStock += (initial['weight'] - weight)
        db.execute("UPDATE inventory SET item_stock = (?) WHERE itemId = (?)", [currStock, itemId])
        db.commit()
    elif typeId == "B":
      db.execute("UPDATE cash SET clientId = (?), amount = (?), typeId = (?),"
                + "type_name = (?), date = (?) WHERE transactionId = (?)", 
                [clientId, -total, typeId, typeName, currTime, transactionId])
      db.commit()

      cashBlanace = db.execute("SELECT client_balance FROM clients WHERE clientId = 1").fetchone()[0]
      cashBlanace += (initial['total'] - total)
      db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = 1", [cashBlanace])
      db.commit()

      if itemId != initial['itemId']:
        currStock = db.execute("SELECT item_stock FROM inventory WHERE itemId = (?)", [initial['itemId']]).fetchone()[0]
        currStock -= initial['weight']
        db.execute("UPDATE inventory SET item_stock = (?) WHERE itemId = (?)", [currStock, initial['itemId']])

        currStock = db.execute("SELECT item_stock FROM inventory WHERE itemId = (?)", [itemId]).fetchone()[0]
        currStock -= weight
        db.execute("UPDATE inventory SET item_stock = (?) WHERE itemId = (?)", [currStock, itemId])
        db.commit()
      else:
        currStock = db.execute("SELECT item_stock FROM inventory WHERE itemId = (?)", [itemId]).fetchone()[0]
        currStock += (weight - initial['weight'])
        db.execute("UPDATE inventory SET item_stock = (?) WHERE itemId = (?)", [currStock, itemId])
        db.commit()
    elif typeId == "R":
      db.execute("UPDATE cash SET clientId = (?), amount = (?), typeId = (?),"
                + "type_name = (?), date = (?) WHERE transactionId = (?)", 
                [clientId, paid, typeId, typeName, currTime, transactionId])
      db.commit()

      currBalance = db.execute("SELECT client_balance FROM clients WHERE clientId = (?)", [clientId]).fetchone()[0]
      currBalance += (paid - initial['paid'])
      db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = (?)", [currBalance, clientId])
      db.commit()

      cashBlanace = db.execute("SELECT client_balance FROM clients WHERE clientId = 1").fetchone()[0]
      cashBlanace += (paid - initial['paid'])
      db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = 1", [cashBlanace])
      db.commit()
    elif typeId == "E": 
      db.execute("UPDATE cash SET clientId = (?), amount = (?), typeId = (?),"
                + "type_name = (?), date = (?) WHERE transactionId = (?)", 
                [clientId, -paid, typeId, typeName, currTime, transactionId])
      db.commit()

      cashBlanace = db.execute("SELECT client_balance FROM clients WHERE clientId = 1").fetchone()[0]
      cashBlanace += (initial['paid'] - paid)
      db.execute("UPDATE clients SET client_balance = (?) WHERE clientId = 1", [cashBlanace])
      db.commit()
    return next
  else:
    return render_template("editForm.html")

# Info gathering routes
@app.route("/getClients", methods=["GET"])
def getClientId():
  query = db.execute("SELECT client_name FROM clients ORDER BY clientId").fetchall()
  return jsonify( { 'clientArr': list(query) } )

@app.route("/getTransactionsByType", methods=["GET"])
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

@app.route("/getTransactionById", methods=["GET"])
def getTransactionById():
  query = db.execute("SELECT * FROM transactions WHERE transactionId = (?)", [request.args.get('transactionId')]).fetchone()
  
  if not query:
    return jsonify({ 'status': "لا يوجد حركة بهذا الرقم" })
  
  return jsonify({
    'clientId': query[1],
    'itemId': query[2],
    'weight': query[3],
    'descreption': query[4],
    'price': query[5],
    'total': query[6],
    'paid': query[7],
    'typeId': query[8],
  })