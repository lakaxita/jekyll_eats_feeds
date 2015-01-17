#!/bin/env python

from collections import namedtuple
from git import Repo
import os
from tempfile import mkdtemp

import feedparser
from slugify import slugify
import yaml


BaseArticle = namedtuple('Article',
                         ('title', 'link', 'description', 'pub_date'))


class Article(BaseArticle):
    def gen_filename(self):
        date = '{t.tm_year}-{t.tm_mon}-{t.tm_mday}'.format(t=self.pub_date)
        title = slugify(self.title)
        return '-'.join((date, title))


class FeedParser(object):
    def __init__(self, url):
        self.url = url

    def get_uuid(self, item):
        guid, domain = item['guid'].split('at')
        return guid.strip()

    def articles(self):
        parsed = feedparser.parse(self.url)
        for item in parsed['items']:
            uuid = self.get_uuid(item)
            article = Article(title=item['title'], link=item['link'],
                              description=item['description'],
                              pub_date=item['published_parsed'])
            yield uuid, article


Post = namedtuple('Post', ('filename', 'metadata', 'content'))


class JekyllGenerator(object):
    EXTENSION = '.html'
    SEPARATOR = '---'

    def __init__(self, directory, metadata=None):
        self.directory = directory
        self.metadata = {} if metadata is None else metadata

    def filenames(self):
        return (f for f in os.listdir(self.directory)
                if os.path.isfile(f) and f.endswith(self.EXTENSION))

    def posts(self):
        for filename in self.filenames():
            with open(filename) as post:
                data = post.read()
            _, metadata, content = data.split(self.SEPARATOR)
            metadata = yaml.load(metadata)
            uuid = metadata.get('uuid', None)
            if uuid is not None:
                yield uuid, Post(filename, metadata, content)

    def get_metadata(self, uuid, article):
        metadata = self.metadata.copy()
        metadata['uuid'] = uuid
        metadata['title'] = article.title
        metadata['link'] = article.link
        return metadata

    def get_contents(self, uuid, article):
        metadata = self.get_metadata(uuid, article)
        metadata = yaml.dump(metadata, default_flow_style=False)
        return '---\n'.join(('', metadata, article.description))

    def write(self, uuid, article, post=None):
        if post is None:
            filename = article.gen_filename() + self.EXTENSION
        else:
            filename = post.filename
        path = os.path.join(self.directory, filename)
        contents = self.get_contents(uuid, article)
        with open(path, 'w') as fd:
            fd.write(contents.encode('utf-8'))
        return filename

    def generate(self, articles):
        posts = dict(self.posts())
        for uuid, article in articles:
            if uuid in posts:  # Post already exists
                yield self.write(uuid, article, posts[uuid])
            else:  # Post has to be created
                yield self.write(uuid, article)


class Repository(object):
    def __init__(self, url, directory=None, message=None):
        self.url = url
        self.directory = mkdtemp() if directory is None else directory
        self.message = "Latest articles" if message is None else message
        self.repo = None

    def download(self):
        try:
            self.repo = Repo(self.directory)
        except:
            self.repo = Repo.clone_from(self.url, self.directory)
        else:
            self.repo.remote().pull()

    def commit(self, filenames):
        for filename in filenames:
            self.repo.git.add(filename)
        self.repo.git.commit(m=self.message)

    def upload(self):
        self.repo.git.push('origin', 'master')


def sync(feed, repository, directory, posts_dir, metadata):
    message = "Latest articles from {}".format(feed)
    repo = Repository(repository, directory, message)
    repo.download()
    parser = FeedParser(feed)
    path = os.path.join(directory, posts_dir)
    generator = JekyllGenerator(path, metadata)
    filenames = generator.generate(parser.articles())
    filenames = (os.path.join(posts_dir, f) for f in filenames)
    repo.commit(filenames)
    repo.upload()


if __name__ == '__main__':
    import sys

    OUTPUT = sys.argv[1]
    FEED = 'http://angulaberria.info/eu/taxonomy/term/1/feed'
    REPO = 'git@github.com:lakaxita/lakaxita.github.io.git'
    POSTS_DIR = '_posts'
    METADATA = {
        'layout': 'post',
        'published': True,
        'categories': 'lakaxita',
    }

    sync(FEED, REPO, OUTPUT, POSTS_DIR, METADATA)
