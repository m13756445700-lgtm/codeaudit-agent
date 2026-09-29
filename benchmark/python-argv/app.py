from flask import Flask, request
app = Flask(__name__)
import subprocess
@app.get("/echo")
def echo():
    name = request.args["name"]
    return subprocess.check_output(["/bin/echo", "--", name], text=True)
