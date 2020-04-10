from flask import Flask, render_template, redirect, request, jsonify, make_response
from app.models import User, Client, Inventory, Transaction, TransactionDetail
from app import db, app
from app.routes.helper import prepareTransactions, prepareTransactionsTotals
from app.app import getAndPrepareAllClients

import pdfkit

@app.route("/print/<page>/<client>", methods=["GET"])
def printPDF(page, client):
  if page == "clientsAll":
    clients,totalCredit = getAndPrepareAllClients()
    rendered = render_template("pdfs/clientsPDF.html", clients=clients, totalCredit=totalCredit, title="سـجـل الـعـمـلاء")
  elif page == "transactions":
    transactions = []
    dateStart = request.args.get('dateStart')
    dateEnd = request.args.get('dateEnd')
    queriedTransactions = Transaction.query.filter(Transaction.date>=dateStart).filter(Transaction.date<=dateEnd).order_by(Transaction.transaction_Id.desc()).all()
    transactions = prepareTransactions(queriedTransactions)
    rendered = render_template('pdfs/transactionsPDF.html', 
      transactions=transactions,
      title="سجل الحركات من تاريخ " + dateStart + " الى تاريخ " + dateEnd
    )
  elif page == "u" and int(client) > 0:
    clientId = int(client)
    print(clientId)
    if clientId == 1:
      typeId = request.args.get('typeId') or '_'
      total = 0
      transactions = []
      query = Transaction.query.filter(Transaction.type_Id.like(typeId)).order_by(Transaction.transaction_Id.desc()).all()
      
      transactions,total = prepareTransactionsTotals(query)
      rendered = render_template("pdfs/cashPDF.html", total=total, transactions=transactions)
    else:
      clientQ = Client.query.get(clientId)
      client = {
        'id': clientQ.client_Id,
        'name': clientQ.client_name,
        'phone': clientQ.client_phone,
        'balance': clientQ.client_balance
      }
      transactionQ = Transaction.query.filter_by(client_Id = clientId).all()
      transactions = prepareTransactions(transactionQ)
      rendered = render_template('pdfs/clientPDF.html', client=client, transactions=transactions)
  elif page == "inventory":
    inventory = []
    query = Inventory.query.order_by(Inventory.item_Id).all()
    for record in query:
      inventory.append({
        'id': record.item_Id,
        'name': record.item_name,
        'stock': record.item_stock
      })
    rendered = render_template("pdfs/inventoryPDF.html", inventory=inventory)

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
