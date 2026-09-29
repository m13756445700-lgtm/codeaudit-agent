from flask import Flask, request
app = Flask(__name__)
import requests
@app.get("/fetch")
def fetch():
    target = request.args["url"]
    return requests.get(target, timeout=3).text
