from flask import Flask, request
app = Flask(__name__)
import requests
@app.get("/fetch")
def fetch():
    kind = request.args.get("kind")
    target = "https://example.org/a" if kind == "a" else "https://example.org/b"
    return requests.get(target, timeout=3, allow_redirects=False).text
