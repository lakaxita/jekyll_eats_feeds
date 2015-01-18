Little utility that parses a RSS/Atom feed, creates/updates Jekyll posts from it
and pushes the changes.

It first downloads parses a RSS/Atom feed, extracts the UUIDs from the feeds and
creates a `{UUID: article}` dictionary.

Then it does the same with the Jekyll posts: it clones the repo and parses all
the posts, extracts their UUIDs and creates a `{UUID: post}` dictionary.

It iterates over every article creating a post if it doesn't exist and updating
it if it does exist and hasn't `locked: true` in its metadata.

Finally, the changes are committed and pushed to the `origin` remote's `master`
branch unless `PUSH = False` is specified in the config file.


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
        'posts': 'metadata header',
    }
    PUSH = True  # Push the created commits to origin


Execution
---------

Once configured, it can be executed with:

    python sync.py config.py
