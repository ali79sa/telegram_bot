import sqlite3

connection = sqlite3.connect('main.db')

crsr = connection.cursor()

sql_create_user = 'CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, tel_id INTEGER NOT NULL, username TEXT, name TEXT, first_use TEXT);'
sql_create_book = 'CREATE TABLE books (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, name TEXT, description TEXT, status TEXT, price INTEGER, category INTEGER, photo TEXT);'



crsr.execute(sql_create_user)
crsr.execute(sql_create_book)

connection.commit()

connection.close()