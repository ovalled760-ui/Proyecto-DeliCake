from flask import Flask, render_template, request, redirect, flash
import mysql.connector
from dataBase.models import *

app = Flask(__name__)
app.secret_key = 'clave_secreta'


"""db = mysql.connector.connect(
    host="127.0.0.1",
    port="3306",   
    user="root_mysql",
    password="",
    database="DeliCake_db"
)"""

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root_mysql:127.0.0.1:3306/DeliCake_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clave_secreta'  

# Rutas
@app.route('/')
def publica():
    return render_template('index.html')

if __name__ == '__main__':
            

    app.run(debug=True)
    
