import os, urllib, json
from flask import Flask, request, make_response


app = Flask(__name__)
app.config['DEBUG'] = bool(os.environ.get('DEBUG'))

@app.route("/")
def index():
    return "Hello, world!"

@app.route("/hook", methods=["POST"])
def hook():
    d = json.loads(request.data)
    return "taking %s from %s to %s" % (
      d['after'], d['before'], d['ref']
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
