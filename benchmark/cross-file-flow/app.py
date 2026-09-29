from flask import Flask, request
from service import report
app = Flask(__name__)

@app.get('/report')
def generate():
    name = request.args.get('name', '')
    return report(name)
