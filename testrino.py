import sqlite3
db = sqlite3.connect("website.db", check_same_thread=False)
recordsNew = []
records = """1|حديد مشكل|10485.0
2|حديد 10|1940.0
3|حديد 8|662.0
4|اسمنت|107.0
5|اسمنت ابيض اردني|100.0
6|اسمنت ابيض اجنبي|21.0
7|شيد|416.0
8|سلك ناعم|165.0
9|سلك مجدول|88.0
10|مسامير عادي|199.0
11|مسامير باطون|279.0
12|كانات|0.0
13|اسافين|91.0
14|ستوك اردتي|16.0
15|ستوك اجنبي|4.0""".split("\n")
for record in records:
  REC = record.split("|")
  recordsNew.append([int(REC[0]), str(REC[1]), float(REC[2])])
print(recordsNew)
inventory = []
for record in recordsNew:
  if record[0] != 12:
    if record[0] > 12:
      record[0] -= 1
    inventory.append(record)
print(inventory)
kanat = ["مثلث صغير", "مربع", "مثلث", "60x15", "50x15", "50x18", "48x15", "45x15", "40x18", "40x15", "30x18", 
  "30x15"]

stock = [400, 700, 1250, 200, 280, 778, 700, 240, 840, 150, 300, 320]
for record in inventory:
  db.execute("INSERT INTO inventory (itemId, item_name, item_stock)" 
            + "VALUES ((?), (?), (?))", [record[0], record[1], record[2]])

for index, record in enumerate(kanat):
  db.execute("INSERT INTO inventory (itemId, item_name, item_stock)" 
            + "VALUES ((?), (?), (?))", [index+15, "كانات"+" "+record, stock[index]])
  db.commit()