import os, urllib, json
from flask import Flask, request, make_response, g
import web

app = Flask(__name__)
app.config['DEBUG'] = bool(os.environ.get('DEBUG'))
db = web.database()

@app.route("/")
def index():
    return "Hello, world!"

@app.route("/hook", methods=["POST"])
def hook():
    #d = json.loads(request.data)
    d = request.json
    if d['ref'] != 'refs/heads/master': return "skipping\n"
    db.insert('jobs', commit_hash=d['after'])
    return "queued\n"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
