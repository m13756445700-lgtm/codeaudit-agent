from flask import Flask, request
app = Flask(__name__)
from pathlib import Path
@app.get("/file")
def file():
    kind = request.args.get("name")
    name = "help.txt" if kind == "help" else "index.txt"
    return (Path("/srv/files") / name).read_text()
