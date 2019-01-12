# Header files (Import all needed libraries)
from flask import Flask, render_template, redirect, request, session, jsonify, flash, abort
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

from datetime import datetime
from random import randint
from sqlite3 import connect

import re
import time
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
@login_required
def index():
  return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  # Forget any user_id
  session.clear()
  
  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    print("yuclke")
    username = request.form.get("username")
    password = request.form.get("password")

    query = db.execute("SELECT * FROM users WHERE username = (?)", [username])

    if (not check_password_hash(query[2], password)):
      flash("Passowrd and/or username aren't correct")
      return redirect("/")

      # Remember which user has logged in
    session["user_id"] = query[0]

    # Redirect user to home page
    return redirect("/")
  else:
    return render_template("login.html")
