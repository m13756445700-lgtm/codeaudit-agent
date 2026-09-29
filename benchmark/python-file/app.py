from flask import Flask, request
app = Flask(__name__)
from pathlib import Path
@app.get("/file")
def file():
    name = request.args["name"]
    return (Path("/srv/files") / name).read_text()
