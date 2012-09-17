import os, urllib, json
from flask import Flask, request, make_response, render_template
import web, pusher, jinja2
import simplethread, builder

app = Flask(__name__)
app.config['DEBUG'] = bool(os.environ.get('DEBUG'))
db = web.database()

@app.route("/")
def index():
    jobs = db.select('jobs', order='id desc')
    return render_template("index.html", jobs=jobs)

@app.route('/jobs/<int:job_id>')
def show_job(job_id):
    job = db.select('jobs', where='id = $job_id', vars=locals())[0]
    builds = db.select('builds', where='job_id=$job_id', order='id asc', vars=locals()).list()
    pusher_key = pusher.url2options(os.environ['PUSHER_URL'])['key']
    return render_template("job.html", **locals())

@app.template_filter('unconsole')
def unconsole_filter(s):
    jm = jinja2.Markup
    return jm.escape(s).replace('\033[1m', jm('<b>')).replace('\033[0m', jm('</b>'))

@app.route("/hook", methods=["POST"])
def github_hook():
    #d = json.loads(request.data)
    d = request.json
    if d['ref'] != 'refs/heads/master': return "skipping\n"
    job_id = db.insert('jobs', commit_hash=d['after'])
    builder.buildqueue.put(job_id)
    return "queued\n"

@app.route('/semaphore_hook', methods=["POST"])
def semaphore_hook():
    d = request.json
    if d['branch_name'] != 'master': return "skipping\n"
    job_id = db.insert('jobs', commit_hash=d['commit']['id'])
    builder.buildqueue.put(job_id)
    return "queued\n"

if __name__ == "__main__":
    simplethread.spawn(lambda: builder.watchdb(db))
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
