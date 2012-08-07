import os, web
from courier import execute
env = web.storage(os.environ)

REPO_STORAGE = '/tmp/dudley_repo'
TMP_BUILDSERVER_NAME = 'sleepy-ocean-9027'

def build(commit_hash):
    if not os.path.exists(REPO_STORAGE):
        execute('git', 'clone', env.GIT_URL, REPO_STORAGE)
    execute('git', 'pull', cwd=REPO_STORAGE)
    execute('git', 'push', '-f', TMP_BUILDSERVER_NAME, commit_hash + ':master', cwd=REPO_STORAGE)
    

if __name__ == "__main__":
    import sys
    build(sys.argv[1])
