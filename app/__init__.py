from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import os

# Configure flask app
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///website.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from app import models
from app.app import *
from app.routes.transaction import *
from app.routes.transactionLog import *
from app.routes.print import *
from app.routes.editTransaction import *
