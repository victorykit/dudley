import os, urllib
from flask import Flask, request, make_response


app = Flask(__name__)
#app.config['DEBUG'] = True

@app.route("/")
def index(output):
    return "Hello, world!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
