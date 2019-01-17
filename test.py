from sqlite3 import connect

db = connect("website.db", check_same_thread=False)

items = ["حديد مشكل", "حديد 10", "حديد 8", "اسمنت", "اسمنت ابيض اردني", "اسمنت ابيض اجنبي",
  "شيد", "سلك ناعم", "سلك مجدول", "مسامير عادي", "مسامير باطون", "كانات", "اسافين", "ستوك اردتي",
  "ستوك اجنبي"]

s = db.execute("SELECT * FROM transactions WHERE transactionId = 9").fetchall()
for r in s:
  print(r)