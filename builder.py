import os, web
import courier

REPO_STORAGE = '/tmp/dudley_repo'
TMP_BUILDSERVER_NAME = 'sleepy-ocean-9027'

env = web.storage(os.environ)

def build(commit_hash):
    sh = courier.Courier()
    
    if not os.path.exists(REPO_STORAGE):
        sh.run('git', 'clone', env.GIT_URL, REPO_STORAGE)
    sh.cd(REPO_STORAGE)
    sh.run('git', 'pull')
    sh.run('git', 'push', '-f', TMP_BUILDSERVER_NAME, commit_hash + ':master')
    

if __name__ == "__main__":
    import sys
    build(sys.argv[1])
