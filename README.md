## Installation


1. Install the software:

        git clone $DUDLEY_URL
        cd dudley
        heroku create
        heroku addons:add heroku-postgresql:dev
        heroku pg:promote HEROKU_POSTGRESQL_TEAL # or whatever color [@@automatable?]
        heroku pg:psql < schema.sql
        heroku addons:add pusher:sandbox
        
        heroku config:add GIT_URL=[path to your git repo]

2. Visit <https://api.heroku.com/signup> and create a new Heroku account.
3. Validate your email and then visit <https://api.heroku.com/account> to get your API key. Then run:

        sudo pip install heroku
        python install_keys.py [put your API key here]

4. Add the new user to your app:

        heroku sharing:add [put your new user's email here]

5. Start your server:
    
        git push heroku master

## todo

 - bold doesn't work when pushed via pusher
 - builder runs a real build process
   - check status codes to make sure build succeeded
   - HTMLize
     - Convert escape coded to HTML before printing to browser
 - cancel builds
 - Rebuild
   - Marks job uncompleted
   - But make sure we don't push to production
     - Don't `push -f` on production
 - cleanup script to run by scheduler
   - pushes web to run watchdb
 - have watchdb look for dead jobs
   - select * from jobs where active = 't' and last_update > now() - interval '1 minute'
   - mark them as dead
   - spawn a new builder thread
 - build a new buildserver if none available?
 - improve design
 - easy install instructions
 - optimize build speed
 - figure out what to do with branches
