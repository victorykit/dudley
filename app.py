import os, urllib, json, datetime
from flask import Flask, request, make_response, render_template, url_for
import web, pusher, jinja2
import simplethread, builder

app = Flask(__name__)
app.config['DEBUG'] = bool(os.environ.get('DEBUG'))
db = web.database()

@app.route("/")
def index():
    jobs = db.select('jobs', order='id desc')
    return render_template("index.html", jobs=jobs, ci_link=os.environ.get('CI_LINK'))

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
    d = json.loads(request.form['payload'])
    if d['ref'] != 'refs/heads/master': return "skipping\n"
    
    for commit in d['commits']:
        announce("%s: %s\n%s" % (commit['author']['name'], commit['message'], commit['url'][:-40+7]))
    
    return "announced\n"

@app.route('/semaphore_hook', methods=["POST"])
def semaphore_hook():
    d = json.loads(request.form.keys()[0])
    if d['branch_name'] != 'master': return "skipping\n"
    
    if d['result'] != 'passed':
        announce("%s broke the build!\n%s" % (d['commit']['author_name'], d['build_url']))
        return "announced\n"
    
    job_id = db.insert('jobs', commit_hash=d['commit']['id'], message=d['commit']['message'], author=d['commit']['author_name'])
    builder.buildqueue.put(job_id)
    
    announce("Deploying: %s\n%s" % (d['commit']['message'], url_for('show_job', job_id=job_id, _external=True)))
    return "queued\n"

@app.route('/announcements.json')
def announcements():
    last_check = request.args.get('since')
    
    if last_check:
        print last_check
        r = db.select('announcements', where="created_at > $last_check", order='created_at asc', vars=locals())
    else:
        r = db.select('announcements', order='created_at asc', limit=10)
    
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
    return json.dumps(r.list(), default=dthandler)

@app.route('/airbrake_hook', methods=["POST"])
def airbrake_hook():
    try:
        d = json.loads(request.form.keys()[0])
        error_message = d['error_message']
    except Exception, e:
        announce("Failed to handle Airbrake webhook: %s\n%s" % (e, request.form))
    else:
        announce("Via Airbrake: %s" % error_message)
    return "announced\n"

def announce(announcement):
    return db.insert('announcements', content=announcement)

import utils
app.template_filter('timesince')(utils.friendly_time)

if __name__ == "__main__":
    simplethread.spawn(lambda: builder.watchdb(db))
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
