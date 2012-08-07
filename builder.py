import os, time
import web
import courier, simplethread

REPO_STORAGE = '/tmp/dudley_repo'
NOW = web.sqlliteral('now()')

env = web.storage(os.environ)

def watchdb(db):
    for job in db.select('jobs', where="builder is null and done='f'"):
        simplethread.spawn(lambda: start_build(db, job))

def get_buildserver(db, build_id):
    buildservers = db.select('buildservers', where="building is null", limit=1).list()
    if buildservers and db.update('buildservers', building=build_id, where="building is null and id=$buildservers[0].id", vars=locals()):
        return buildservers[0]
    else:
        return False

def claim_job(db, job_id, build_id):
    return db.update('jobs', builder=build_id, where="id=$job_id and builder is null", vars=locals())

def start_build(db, job):
    build_id = db.insert('builds', job_id=job.id, updated_at=NOW)
    if not claim_job(db, job.id, build_id):
        # someone else is already building this job
        db.delete('builds', where="build_id=$build_id", vars=locals())
        return False
    
    def update_build_log(text=''):
        build_id # pulls from parent function
        db.query("UPDATE builds SET log = log || $text, updated_at = now() WHERE id=$build_id", vars=locals())
    
    sh = courier.Courier(update_build_log)
    
    buildserver = get_buildserver(db, build_id)
    if not buildserver:
        update_build_log("Couldn't find a free buildserver. You might try adding some more.\n")
        update_build_log("Sleeping until we find one...\n")
        while not buildserver:
            time.sleep(60)
            update_build_log()
            buildserver = get_buildserver(db, build_id)
    
    do_build(job.commit_hash, sh, buildserver)
    db.update('builds', where="id=$build_id", done=True, vars=locals())
    db.update('jobs', where="id=$job.id", done=True, vars=locals())
    db.update('buildservers', where='id=$buildserver.id', building=None, vars=locals())

def do_build(commit_hash, sh, buildserver):
    if not os.path.exists(REPO_STORAGE):
        sh.run('git', 'clone', env.GIT_URL, REPO_STORAGE)
    sh.cd(REPO_STORAGE)
    sh.run('git', 'remote', 'add', buildserver.short_name, buildserver.git_url)
    sh.run('git', 'pull')
    sh.run('git', 'push', '-f', buildserver.short_name, commit_hash + ':master')

if __name__ == "__main__":
    import sys
    #INSERT INTO buildservers (short_name, git_url) VALUES('sleepy-ocean-9027', 'git@heroku.com:sleepy-ocean-9027.git');
    
    db = web.database()
    job = web.storage(commit_hash=sys.argv[1])
    job.id = db.insert('jobs', **job)
    start_build(db, job)
