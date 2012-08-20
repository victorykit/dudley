import os, time
import web, pusher
import courier, simplethread

REPO_STORAGE = '/tmp/dudley_repo'
NOW = web.sqlliteral('now()')
pushcloud = pusher.pusher_from_url()
env = web.storage(os.environ)
buildqueue = simplethread.Queue()

def watchdb(db):
    while 1:
        try: buildqueue.get(timeout=60)
        except simplethread.Empty: pass
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
        db.query("UPDATE builds SET log = log || $text, updated_at = now() WHERE id=$build_id", vars=locals())
        pushcloud['build_' + str(build_id)].trigger('update', {'text': text, 'build_id': build_id})
    
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
        try: os.mkdir('/app/.ssh')
        except OSError: pass # directory already exists
        file('/app/.ssh/known_hosts', 'a').write("heroku.com,50.19.85.132 ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAu8erSx6jh+8ztsfHwkNeFr/SZaSOcvoa8AyMpaerGIPZDB2TKNgNkMSYTLYGDK2ivsqXopo2W7dpQRBIVF80q9mNXy5tbt1WE04gbOBB26Wn2hF4bk3Tu+BNMFbvMjPbkVlC2hcFuQJdH4T2i/dtauyTpJbD/6ExHR9XYVhdhdMs0JsjP/Q5FNoWh2ff9YbZVpDQSTPvusUp4liLjPfa/i0t+2LpNCeWy8Y+V9gUlDWiyYwrfMVI0UwNCZZKHs1Unpc11/4HLitQRtvuk0Ot5qwwBxbmtvCDKZvj1aFBid71/mYdGRPYZMIxq1zgP1acePC1zfTG/lvuQ7d0Pe0kaw==\n")
        file('/app/.ssh/id_rsa', 'w').write(env.SSH_PRIVKEY)
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
