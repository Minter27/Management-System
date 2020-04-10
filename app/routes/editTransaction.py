import json
from flask import Flask, render_template, redirect, request, jsonify, make_response
from app.models import User, Client, Inventory, Transaction, TransactionDetail
from app import db, app
from app.app import CASH_CLIENT_ID
from app.routes.helper import prepareTransactions
from datetime import datetime


@app.route("/editTransactionForm", methods=["GET", "POST"])
def editTransactionForm():
  if request.method == "POST":
    try:
      transactionId = int(request.form.get('transactionId'))
      typeId = str(request.form.get('typeId'))
      typeName = str(request.form.get('typeName'))
      clientId = int(request.form.get('clientId'))
      description = str(request.form.get('description'))
      total = float(request.form.get('total'))
      paid = float(request.form.get('paid'))
      receivedItems = json.loads(request.form.get('items'))
      next = str(request.form.get('next'))
    except Exception as e:
      print("Unexpected error: ", e)
      return "الرجاء التأكد من تعبئة النموذج كاملاً 101"

    if None or False in (transactionId, typeId, typeName, clientId):
      return "الرجاء التأكد من تعبئة النموذج كاملاً 102"

    if clientId == CASH_CLIENT_ID and paid == 0:
      return "لا يمكن دفع ذمم عندما يكون الدفع على حساب نقدي"

    recordTransaction = Transaction.query.get(transactionId)
    if not recordTransaction:
      return jsonify({ 'status': "لا يوجد حركة بهذا الرقم" })
    
    if (typeId == "B" or typeId == "E") and clientId != recordTransaction.client_Id:
      return "لا يمكن تغيير العميل عندما تكون الحركة شراء او نفقة"

    if typeId != recordTransaction.type_Id:
      return "لا يمكن تغيير نوع الحركة"

    try:

      items = []
      for receivedItem in receivedItems:
        detailId = int(receivedItem['detailId'])
        itemId = int(receivedItem['itemId'])
        weight = float(receivedItem['weight'])
        price = float(receivedItem['price'])
        recordTransactionDetail = TransactionDetail.query.get(detailId)
        itemInventory = Inventory.query.get(recordTransactionDetail.item_Id)
        if itemId != recordTransactionDetail.item_Id:
          itemInventoryNew = Inventory.query.get(itemId)
          if typeId == "S":
            itemInventory.item_stock += recordTransactionDetail.quantity
            itemInventoryNew.item_stock -= weight
          elif typeId == "B":
            itemInventory.item_stock -= recordTransactionDetail.quantity
            itemInventoryNew.item_stock += weight
        else:
          if typeId == "S":
            itemInventory.item_stock += recordTransactionDetail.quantity - weight
          elif typeId == "B":
            itemInventory.item_stock += weight - recordTransactionDetail.quantity

        recordTransactionDetail.item_Id = itemId
        recordTransactionDetail.quantity = weight
        recordTransactionDetail.price = price

      cashClient = Client.query.get(CASH_CLIENT_ID)
      if typeId == "S": #Sale
        if total - paid < 0:
          return "لا يمكن دفع اكثر من المبلغ المطلوب. اذا اردت الايداع ، الرجاء الاستعانة بخاصية حركة مالية"

        if clientId != recordTransaction.client_Id:
          oldClient = Client.query.get(recordTransaction.client_Id)
          oldClient.client_balance += (recordTransaction.total - recordTransaction.paid)
          
          newClient = Client.query.get(clientId)
          newClient.client_balance -= (total - paid)
        else:
          client = Client.query.get(recordTransaction.client_Id)
          client.client_balance += (recordTransaction.total - recordTransaction.paid) - (total - paid)

        cashClient.client_balance += paid - recordTransaction.paid
        
      elif typeId == "B": # Buy
        paid = total
        cashClient.client_balance += recordTransaction.total - total

      elif typeId == "R": # Repay
        total = paid
        if clientId != recordTransaction.client_Id:
          oldClient = Client.query.get(recordTransaction.client_Id)
          oldClient.client_balance -= recordTransaction.paid
          
          newClient = Client.query.get(clientId)
          newClient.client_balance += paid
        else:
          client = Client.query.get(recordTransaction.client_Id)
          client.client_balance += paid - recordTransaction.paid

        cashClient.client_balance += paid - recordTransaction.paid

      elif typeId == "E": #Expense
        total = paid
        cashClient.client_balance += recordTransaction.paid - paid
      
      recordTransaction.client_Id = clientId
      recordTransaction.description = description
      recordTransaction.total = total
      recordTransaction.paid = paid
      recordTransaction.date_last_update = datetime.now()
    
    except Exception as e:
      print("Unexpected error: ", e)
      db.session.rollback()

    db.session.commit()

    if not next.startswith("/"):
      next = "/" + next
    print("next: ", next)
    return next
  else:
    return render_template("editForm.html")
