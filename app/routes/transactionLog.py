from flask import Flask, render_template, redirect, request, jsonify, make_response
from app.models import User, Client, Inventory, Transaction, TransactionDetail
from app import db, app
from app.app import getNextTransactionId, CASH_CLIENT_ID
from app.routes.helper import prepareTransactions
from datetime import datetime


@app.route("/transactionLog", methods=["GET"])
def transactionLog():
  dateStart = request.args.get('start')
  dateEnd = request.args.get('end')
  if not dateStart and not dateEnd:
    allTransactions = Transaction.query.order_by(Transaction.transaction_Id.desc()).all()
    transactions = prepareTransactions(allTransactions)
    return render_template('transactionLog.html', transactions=transactions, dateNow=datetime.now().strftime("%Y-%m-%d"))
  else:
    transactions = []
    queriedTransactions = Transaction.query
    if dateStart:
      queriedTransactions = queriedTransactions.filter(Transaction.date >= dateStart)
    if dateStart:
      queriedTransactions = queriedTransactions.filter(Transaction.date <= dateEnd)
    queriedTransactions = queriedTransactions.all()
    print(queriedTransactions)
    if not queriedTransactions:
      return jsonify({'error': "لا يوجد حركات بهذه الفترة"})
    transactions = prepareTransactions(queriedTransactions)
    return jsonify({ 'transactions': transactions })
