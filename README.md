Little utility that parses a RSS/Atom feed, creates/updates Jekyll posts from it
and pushes the changes.

Installation
------------

pip install -r requirements.txt


Settings
--------

You have to create some config file as follows:

    FEED = 'http://domain.tld/some/path/to/the/rss/feeds'
    OUTPUT = 'repo_checkout_dir'
    REPO = 'https://domain.tld/some/git/repo/with/your/jekyll/site.git'
    POSTS_DIR = '_posts'
    METADATA = {
        'inserted': True,
        'in': 'every',
        'post': 'metadata header',
    }


Execution
---------

Once everything is ready, execute it with:

    python sync.py config.py
