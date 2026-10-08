from flask import Flask, request, render_template_string
app = Flask(__name__)

@app.get("/welcome")
def welcome():
    caption = request.args.get("caption", "visitor")
    return render_template_string("<p>{{ caption }}</p>", caption=caption)
