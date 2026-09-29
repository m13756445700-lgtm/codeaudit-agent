from flask import Flask, request
app = Flask(__name__)
import sqlite3
@app.get("/lookup")
def lookup():
    q = request.args["name"]
    con = sqlite3.connect("app.db")
    return str(con.execute("SELECT name FROM users WHERE name='" + q + "'").fetchall())
