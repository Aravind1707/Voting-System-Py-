# db.py

from flask_mysqldb import MySQL

mysql = MySQL()

def init_app(app):
    # MySQL Configuration
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'root'  # Change to your MySQL password
    app.config['MYSQL_DB'] = 'voting_system1'
    
    mysql.init_app(app)

def get_cursor():
    return mysql.connection.cursor()
