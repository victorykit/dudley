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

 - builder runs a real build process
   - check status codes to make sure build succeeded
   - HTMLize
     - Convert escape coded to HTML before printing to browser
 - Rebuild
   - Marks job uncompleted
   - But make sure we don't push to production
     - Don't `push -f` on production

 
