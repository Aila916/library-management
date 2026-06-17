import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="sale"   # MUST match Workbench exactly
)

cursor = db.cursor()