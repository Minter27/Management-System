from app import db

class User(db.Model):
  __tablename__ = 'users'
  user_Id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  password_hash = db.Column(db.String(128))

  def __repr__(self):
    return '<User {}>'.format(self.username)

class Client(db.Model):
  __tablename__ = 'clients'
  client_Id = db.Column(db.Integer, primary_key=True)
  client_name = db.Column(db.String(255), index=True, unique=True)
  client_phone = db.Column(db.Integer, index=True, unique=True)
  client_balance = db.Column(db.Float())

  def __repr__(self):
    return '<Client {}>'.format(self.client_name)

class Inventory(db.Model):
  __tablename__ = 'inventory'
  item_Id = db.Column(db.Integer, primary_key=True)
  item_name = db.Column(db.String(255), index=True, unique=True)
  item_stock = db.Column(db.Float())

  def __repr__(self):
    return '<Inventory Item: {}>'.format(self.item_name)

class Transaction(db.Model):
  __tablename__ = 'transactions'
  transaction_Id = db.Column(db.Integer, primary_key=True)
  client_Id = db.Column(db.Integer, db.ForeignKey('clients.client_Id'), nullable=True)
  total = db.Column(db.Float(), nullable=False)
  paid = db.Column(db.Float(), nullable=False)
  type_Id = db.Column(db.String(1), nullable=False)
  type_name = db.Column(db.String(255), nullable=False)
  date = db.Column(db.DateTime, nullable=True)
  date_last_updated = db.Column(db.DateTime, nullable=True)
  description = db.Column(db.String(255), nullable=True)
  
  def __repr__(self):
    return '<Transaction: {}>'.format(self.transaction_Id)
    
class TransactionDetail(db.Model):
  __tablename__ = 'transactionDetails'
  transaction_detail_Id = db.Column(db.Integer, primary_key=True)
  transaction_Id = db.Column(db.Integer, db.ForeignKey('transactions.transaction_Id'), nullable=False)
  item_Id = db.Column(db.Integer, db.ForeignKey('inventory.item_Id'), nullable=False)
  price = db.Column(db.Float(), nullable=False)
  quantity = db.Column(db.Float(), nullable=False)
  
  def __repr__(self):
    return '<Transaction Details: {}>'.format(self.item_Id)

class RequestLog(db.Model):
  __tablename__ = 'requestLog'
  # Autoincrement id field
  id = db.Column(db.Integer, primary_key=True) 
  timestamp = db.Column(db.DateTime, nullable=True)
  remote_addr = db.Column(db.String(20), nullable=True)
  method = db.Column(db.String(10), nullable=True)
  scheme = db.Column(db.String(10), nullable=True)
  path = db.Column(db.Text, nullable=True)
  query_string = db.Column(db.Text, nullable=True)
  form = db.Column(db.Text, nullable=True)
  data = db.Column(db.Text, nullable=True)
  response_status = db.Column(db.Text, nullable=True)


db.create_all()