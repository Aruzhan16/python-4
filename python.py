from contextlib import _RedirectStream 
from sqlite3 import Cursor
from flask import Flask, render_template, request,url_for, redirect
from flask import Flask
from flask import request
import psycopg2
import requests

class User(object):
    def __init__(self, name, status):
        self.name = name
        self.status = status
    def getStatus(self):
        return self.status
    def setStatus(self, status):
        self.status = status
    def setName(self, name):
        self.name = name
    def getName(self):
        return self.name
    def logIn(self):
        self.status = True
    def logOut(self):
        self.status = False

user = User('username', False)
app = Flask(__name__)

db = psycopg2.connect(dbname='dbpython', user='postgres', password='212552', host='localhost')
cur = db.cursor()

@app.route('/index') 
def index(): 
    if user.getStatus():
        return render_template("index.html") 
    else:
        return redirect(url_for('login'), 302)


@app.route('/login', methods = ['POST', "GET"]) 
def login(): 
    user.logOut()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute('SELECT * FROM users')
        rows = cur.fetchall()
        for row in rows:
            if row[0] == username and row[1] == password:
                user.logIn()
                user.setName(username)
                return redirect(url_for('index'), 301)
        return render_template('login.html')
    return render_template('login.html') 
 
@app.route("/registration", methods = ['POST', "GET"])
def registration():
    user.logOut()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute('INSERT INTO users (name, pass)'
                    'VALUES (%s, %s)',
                    (username, password))
        db.commit()
        return redirect(url_for('login'), 302)
    return render_template('reg.html')

@app.route('/nft', methods=['POST', 'GET']) 
def nft(): 
    if user.getStatus():
        output = request.form.to_dict()
        adress = output["adress"]
        headers = {

            "accept": "application/json",
            "X-API-Key": "SWnpmagdLrYt67aFhsaBRRzoubD59cdQkydkZLeljvVREBpWGmpLktfRLZXcvudp"

        }
        url = 'https://solana-gateway.moralis.io/nft/mainnet/' + adress + '/metadata'
        
        
        cur.execute("SELECT * FROM address WHERE addres = %s", (adress,))
        ans = cur.fetchall()
        response = requests.get(url, headers=headers)
        print(ans)
        if ans != []:
            print('from db')
            return render_template("result.html", result = response.text) 
        else:
            cur.execute("INSERT INTO address (addres, info) VALUES (%s, %s)", (adress, response.text))
            db.commit()
            print('to db')
            return render_template("result.html", result = response.text)
    else:
        return redirect(url_for('login'), 302)

if __name__ == '__main__':
    app.run(debug=True)
