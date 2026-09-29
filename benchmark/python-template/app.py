from flask import Flask, request
app = Flask(__name__)
from flask import render_template_string
@app.get("/render")
def render():
    template = request.args["template"]
    return render_template_string(template)
