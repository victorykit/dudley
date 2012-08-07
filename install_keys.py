import sys, subprocess, os
import heroku

heroku_token = sys.argv[1]

subprocess.Popen(['heroku', 'config:add', 'HEROKU_TOKEN=' + heroku_token]).wait()

subprocess.Popen(['ssh-keygen', '-t', 'rsa', '-f', 'tmpkey', '-N', '']).wait()

cloud = heroku.from_key(heroku_token)
cloud.keys.add(file('tmpkey.pub').read())
subprocess.Popen(['heroku', 'config:add', 'SSH_PRIVKEY='+file('tmpkey').read()]).wait()

os.unlink('tmpkey')
os.unlink('tmpkey.pub')
