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
    d = json.loads(request.form.keys()[0])
    if d['branch_name'] != 'master': return "skipping\n"
    job_id = db.insert('jobs', commit_hash=d['commit']['id'], message=d['commit']['message'], author=d['commit']['author_name'])
    builder.buildqueue.put(job_id)
    return "queued\n"


from datetime import datetime
@app.template_filter('timesince')
def friendly_time(dt, past_="ago", 
    future_="from now", 
    default="just now"):
    """
    Returns string representing "time since"
    or "time until" e.g.
    3 days ago, 5 hours from now etc.
    """
    if dt is None or isinstance(dt, jinja2.runtime.Undefined): return None
    
    now = datetime.utcnow()
    if now > dt:
        diff = now - dt
        dt_is_past = True
    else:
        diff = dt - now
        dt_is_past = False

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:

        if period:
            return "%d %s %s" % (period, 
                singular if period == 1 else plural, 
                past_ if dt_is_past else future_)

    return default


if __name__ == "__main__":
    simplethread.spawn(lambda: builder.watchdb(db))
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
