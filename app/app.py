# pylint: disable= no-member

# Header files (Import all needed libraries)
import sys
import json

from flask import Flask, render_template, redirect, request, jsonify, make_response

from logging import FileHandler, WARNING

from datetime import datetime
from time import strftime

from app.models import User, Client, Inventory, Transaction, TransactionDetail, RequestLog
from app import db, app
from app.routes.helper import prepareTransactions, prepareTransactionsTotals

CASH_CLIENT_ID = 1
CASH_CLIENT_NAME = "Cash"

@app.before_first_request
def setup():
  if db.session.query(Client).filter_by(client_Id=CASH_CLIENT_ID).count() == 0:
    cash = Client(client_Id=CASH_CLIENT_ID, client_name = CASH_CLIENT_NAME, client_balance = 0)
    db.session.add(cash)
    db.session.commit()

# Ensure responses aren't cached
@app.after_request
def after_request(response):
  timestamp = datetime.now()
  if request.method == "POST":
    requestLog = RequestLog(timestamp = timestamp, remote_addr = request.remote_addr, method = request.method, scheme = request.scheme,
      path = request.path, query_string = request.query_string, form = json.dumps(request.form), data = request.data, response_status = response.status )
    db.session.add(requestLog)
    db.session.commit()
  response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
  response.headers["Expires"] = 0
  response.headers["Pragma"] = "no-cache"
  return response

# Error logging
file_handler = FileHandler('py_error.txt')
file_handler.setLevel(WARNING)
app.logger.addHandler(file_handler)

@app.route("/")
def index():
  return render_template("index.html")

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

    newClient = Client(client_Id = id, client_name = name, client_phone = phone, client_balance = balance)
    db.session.add(newClient)
    db.session.commit()
    return "/clients"

  else:
    clients, totalCredit = getAndPrepareAllClients()
    return render_template('clients.html', clients=clients, totalCredit=totalCredit)

@app.route("/u/<clientId>", methods=["GET", "POST"])
def client(clientId):
  clientId = int(clientId)
  print(clientId)
  if clientId == CASH_CLIENT_ID:
    return redirect("/cash")
  if request.method == "POST":
    try:
      balance = float(request.form.get('balance'))
    except:
      return "حدث خطأ. الرجاء اعادة الحاولة مع التأكد من الرصيد المدخل"
    print(balance)
    clientQuery = Client.query.get(clientId)
    clientQuery.client_balance = balance
    db.session.commit()
    return "/u/{}".format(clientId)
  else:
    if clientId:
      clientQ = Client.query.get(clientId)
      client = {
        'id': clientQ.client_Id,
        'name': clientQ.client_name,
        'phone': clientQ.client_phone,
        'balance': clientQ.client_balance
      }
      
      transactionQ = Transaction.query.filter_by(client_Id = clientId).all()
      transactions = prepareTransactions(transactionQ)
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

    currentTime = datetime.now()
    newTransaction = Transaction(transaction_Id = transactionId, client_Id = CASH_CLIENT_ID, total = total, paid = total, type_Id = "B", type_name = "شراء", date=currentTime)
    newTransactionDetails = TransactionDetail(transaction_Id = transactionId, item_Id = itemId, price = itemPrice, quantity = itemStock)
    db.session.add(newTransaction)
    db.session.add(newTransactionDetails)

    # db.execute("INSERT INTO cash (transactionId, clientId, amount, typeId, type_name, date)"
    #           + "VALUES ((?), 1, (?), (?), (?), (?))", [transactionId, -total, "B", "شراء", currTime])

    cashClient = Client.query.get(CASH_CLIENT_ID)
    cashClient.client_balance -= total

    itemInventory = Inventory.query.get(itemId)
    itemInventory.item_stock += itemStock
    db.session.commit()
    return "/addItems"
  else:
    return render_template("addItems.html", transactionId=getNextTransactionId())

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

    currentTime = datetime.now()
    newTransaction = Transaction(transaction_Id = transactionId, client_Id = clientId, total = amount, paid = amount, type_Id = "R", type_name = "سداد ذمم", date=currentTime)
    db.session.add(newTransaction)

    # db.execute("INSERT INTO cash (transactionId, clientId, amount, typeId, type_name, date)"
    #           + "VALUES ((?), (?), (?), (?), (?), (?))", [transactionId, clientId, amount, "R", "سداد ذمم", currTime])
    # db.commit()

    clientUpdate = Client.query.get(clientId)
    clientUpdate.client_balance += amount

    cashClient = Client.query.get(CASH_CLIENT_ID)
    cashClient.client_balance += amount
    db.session.commit()
    return "/repayDebt"
  else:
    return render_template('repayDebt.html', transactionId=getNextTransactionId())

@app.route("/cash", methods=["GET"])
def cash():
  query = Transaction.query.order_by(Transaction.transaction_Id.desc()).all()
  stats = {
    'total': 0,
    'balance': Client.query.get(CASH_CLIENT_ID).client_balance
  }
  transactions,total = prepareTransactionsTotals(query)
  stats['total'] = total
  return render_template('cash.html', transactions=transactions, stats=stats)

@app.route("/expense", methods=["GET", "POST"])
def expense():
  if request.method == "POST":
    try:
      transactionId = int(request.form.get('transactionId'))
      description = str(request.form.get('description'))
      amount = float(request.form.get('amount'))
    except:
      return "الرجاء التأكد من تعبئة النموذج صحيحاَ"

    if None or False in (transactionId, description, amount):
      return "الرجاء التأكد من تعبئة النموذج صحيحاَ"

    currentTime = datetime.now()
    newTransaction = Transaction(transaction_Id = transactionId, client_Id=CASH_CLIENT_ID, description = description, total = amount, paid = amount, type_Id = "E", type_name = "مصروفات", date=currentTime)
    db.session.add(newTransaction)

    # db.execute("INSERT INTO cash (transactionId, clientId, amount, typeId, type_name, date)"
    #           + "VALUES ((?), 1, (?), (?), (?), (?))", [transactionId, -amount, "E", "مصروفات", currTime])

    cashClient = Client.query.get(CASH_CLIENT_ID)
    cashClient.client_balance -= amount
    db.session.commit()
    return "/expense"
  else:
    return render_template('expense.html', transactionId=getNextTransactionId())

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
    
    newItem = Inventory(item_Id = id, item_name = name, item_stock = 0)
    db.session.add(newItem)
    db.session.commit()
    return "/inventory"

  else:
    items = []
    query = Inventory.query.order_by(Inventory.item_Id).all()
    for record in query:
      items.append({
        'id': record.item_Id,
        'name': record.item_name,
        'stock': record.item_stock
      })
    print(items)
    return render_template('inventory.html', items=items)

# Info gathering routes
@app.route("/getClients", methods=["GET"])
def getClientId():
  clients = []
  query = Client.query.order_by(Client.client_Id).all()
  print(query)
  for record in query:
    clients.append({
      'id': record.client_Id,
      'name': record.client_name
    })
  return jsonify(clients)

@app.route("/getTypes", methods=["GET"])
def getTypes():
  types = []
  query = Inventory.query.order_by(Inventory.item_Id).all()
  for record in query:
    types.append({
      'id': record.item_Id,
      'name': record.item_name
    })
  return jsonify(types)

@app.route("/getTransactionsByType", methods=["GET"])
def getTransactionsByType():
  typeId = request.args.get('typeId');
  query = Transaction.query.filter_by(type_Id = typeId).all()
  transactions,total = prepareTransactionsTotals(query)
  return jsonify(transactions)

@app.route("/getTransactionById", methods=["GET"])
def getTransactionById():
  transactionId = request.args.get('transactionId');
  record = Transaction.query.get(transactionId)
  if not record:
    return jsonify({ 'status': "لا يوجد حركة بهذا الرقم" })
  clientNameQuery = Client.query.get(record.client_Id)
  transactionDetails = TransactionDetail.query.filter_by(transaction_Id = record.transaction_Id).all()
  allItemsList = Inventory.query.all()
  transaction = {
    'transactionId': record.transaction_Id,
    'clientId': record.client_Id,
    'clientName': clientNameQuery.client_name if clientNameQuery else "",
    'total': record.total,
    'paid': record.paid,
    'type': record.type_name,
    'typeId': record.type_Id,
    'date': record.date.strftime("%Y-%m-%d %H:%M"),
    'description': record.description,
    'items': []
  }
  items = []
  for detail in transactionDetails:
    item = {
      'detailId': detail.transaction_detail_Id,
      'itemId': detail.item_Id,
      'itemName': next((x.item_name for x in allItemsList if x.item_Id == detail.item_Id), None),
      'price': detail.price,
      'weight': detail.quantity
    }
    items.append(item)
  transaction['items'] = items
  return jsonify(transaction)

# Javascript error handler
@app.route('/onJSError/<e>', methods=["GET"])
def onJSError(e):
  print(e)
  path = request.args.get('path')
  print(path)
  f = open('js_error.txt', 'a')
  f.write('[{}]:\n'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
  f.write('  ' + str(e) + '\n')
  f.write('  ' + str(path) + '\n')
  f.close()
  return 'None'

def getNextTransactionId():
  lastTransaction = Transaction.query.order_by(Transaction.transaction_Id.desc()).limit(1).first()
  transactionId = lastTransaction.transaction_Id if lastTransaction else 0
  return transactionId + 1

def getAndPrepareAllClients():
  clients = []
  totalCredit = 0 
  clientQuery = Client.query.order_by(Client.client_Id).all()
  for record in clientQuery:
    if record.client_Id != CASH_CLIENT_ID and record.client_balance < 0:
      totalCredit -= record.client_balance
    clients.append({
      'id': record.client_Id,
      'name': record.client_name,
      'phone': record.client_phone,
      'balance': record.client_balance
    })
  return clients, totalCredit
