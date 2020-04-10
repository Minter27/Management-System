from app.models import User, Client, Inventory, Transaction, TransactionDetail
from app import db, app

def prepareTransactions(allTransactions):
  transactions = []
  allItemsList = Inventory.query.all()

  for record in allTransactions:
    clientNameQuery = Client.query.get(record.client_Id)
    transactionDetails = TransactionDetail.query.filter_by(transaction_Id = record.transaction_Id).all()
    
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
    }
    transactions.append(transaction)
    
    first = True
    for detail in transactionDetails:
      if first:
        first = False
        transaction['itemName'] = next((x.item_name for x in allItemsList if x.item_Id == detail.item_Id), None)
        transaction['price'] = detail.price
        transaction['weight'] = detail.quantity
      else:
        transactions.append({
          'transactionId': '',
          'clientId': '',
          'clientName': '',
          'total': '',
          'paid': '',
          'type': '',
          'date': '',
          'description': '',
          'itemName': next((x.item_name for x in allItemsList if x.item_Id == detail.item_Id), None),
          'price': detail.price,
          'weight': detail.quantity,
        })
  return transactions


def prepareTransactionsTotals(transactionsQuery):
  transactions = []
  total = 0
  for record in transactionsQuery:
    client = Client.query.get(record.client_Id)
    total += record.total
    transactions.append({
      'id': record.transaction_Id,
      'clientId': record.client_Id,
      'clientName': client.client_name if client else "",
      'amount': record.total,
      'description': str("حركة " + str(record.type_name) +  " بيد عميل رقم " + "(" +str(record.client_Id) + ")" + " حركة رقم " + "(" + str(record.transaction_Id) + ")"),
      'type': record.type_name,
      'date': record.date.strftime("%Y-%m-%d %H:%M")
    })
  return (transactions, total)  