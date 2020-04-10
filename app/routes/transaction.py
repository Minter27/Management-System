import json
from flask import Flask, render_template, redirect, request, jsonify, make_response
from datetime import datetime
from app.models import User, Client, Inventory, Transaction, TransactionDetail
from app import db, app
from app.app import getNextTransactionId, CASH_CLIENT_ID


@app.route("/transaction", methods=["GET", "POST"])
def transaction():
  if request.method == "POST":
    try:
      transactionId = int(request.form.get('transactionId'))
      clientId = int(request.form.get('clientId'))
      description = str(request.form.get('description'))
      total = float(request.form.get('total'))
      paid = float(request.form.get('paid'))
      receivedItems = json.loads(request.form.get('items'))
    except Exception as e:
      print("Unexpected error: ", e)
      return "الرجاء التأكد من تعبئة النموذج كاملاً 201"

    if False or '' in (transactionId, clientId, total):
      return "الرجاء التأكد من تعبئة النموذج كاملاً 202"

    if len(receivedItems) == 0:
      return "الرجاء التأكد من تعبئة النموذج كاملاً 203"

    if clientId == 1 and paid == 0:
      return "لا يمكن دفع ذمم عندما يكون الدفع نقدي"

    if total - paid < 0:
      return "لا يمكن دفع اكثر من المبلغ المطلوب. اذا اردت الايداع ، الرجاء الاستعانة بخاصية حركة مالية"

    items = []
    for receivedItem in receivedItems:
      if False or '' in (receivedItem['itemId'], receivedItem['weight'], receivedItem['price']):
        return "الرجاء التأكد من تعبئة النموذج كاملاً"
      item = {"itemId":None, "weight":None, "price":None}
      item['itemId'] = int(receivedItem['itemId'])
      item['weight'] = float(receivedItem['weight'])
      item['price'] = float(receivedItem['price'])
      items.append(item)
    
    currTime = datetime.now()
    newTransaction = Transaction(transaction_Id = transactionId, client_Id = clientId, total = total, paid = paid, type_Id = "S", type_name = "بيع", date=currTime, description = description)
    db.session.add(newTransaction)
    for item in items:
      print(item)
      newTransactionDetails = TransactionDetail(transaction_Id = transactionId, item_Id = item['itemId'], price = item['price'], quantity = item['weight'])
      db.session.add(newTransactionDetails)
      itemStock = Inventory.query.get(item['itemId'])
      itemStock.item_stock = itemStock.item_stock - item['weight']

    client = Client.query.get(clientId)
    client.client_balance = client.client_balance - (total - paid)

    cashClient = Client.query.get(CASH_CLIENT_ID)
    cashClient.client_balance = cashClient.client_balance + paid

    db.session.commit()

    return "/transaction"
  else:   
    return render_template("transactionForm.html", transactionId=getNextTransactionId())
