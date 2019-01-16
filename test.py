from sqlite3 import connect

db = connect("website.db", check_same_thread=False)

items = ["حديد مشكل", "حديد 10", "حديد 8", "اسمنت", "اسمنت ابيض اردني", "اسمنت ابيض اجنبي",
  "شيد", "سلك ناعم", "سلك مجدول", "مسامير عادي", "مسامير باطون", "كانات", "اسافين", "ستوك اردتي",
  "ستوك اجنبي"]

for index, item in enumerate(items):
  db.execute("INSERT INTO inventory (itemId, item_name, item_stock) VALUES ((?), (?), 0)",[(index + 1), item])
  db.commit()