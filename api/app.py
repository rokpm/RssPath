import feedparser
import os
from flask import Flask, render_template
from datetime import datetime
from urllib.parse import urlparse
from dateutil.parser import parse
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

rss_urls = [
    'https://www.hecaitou.com/feeds/posts/default',
    'http://www.ruanyifeng.com/blog/atom.xml',
    'https://www.ezindie.com/feed/rss.xml',
    'https://www.williamlong.info/rss.xml',
    'https://louiscard.com/feed/',
]

def days_since_entry(entry):
    entry_date = parse(entry.updated)
    delta = datetime.now(entry_date.tzinfo) - entry_date
    return delta.days

def get_domain_root(url):
    parsed_url = urlparse(url)
    domain_root = f"{parsed_url.scheme}://{parsed_url.hostname}"
    return domain_root

def fetch_rss_info(url, idx):
    feed = feedparser.parse(url)
    domain_root = get_domain_root(url)

    # Convert latest_update to a datetime object
    latest_update = parse(feed.entries[0].updated)

    return {
        'id': idx,
        'title': feed.feed.title,
        'url': url,
        'icon': f'{domain_root}/favicon.ico',
        'latest_article': feed.entries[0].title,
        'latest_update': latest_update,  # Use the datetime object instead of the original string
        'recent_articles_count': sum(1 for entry in feed.entries if days_since_entry(entry) <= 7),
        'entries': feed.entries
    }

rss_sources = [fetch_rss_info(url, idx) for idx, url in enumerate(rss_urls)]

@app.route('/')
def index():
    return render_template('index.html', rss_sources=rss_sources)

@app.route('/rss_detail/<int:rss_id>')
def rss_detail(rss_id):
    source = rss_sources[rss_id]
    return render_template('rss_detail.html', rss_title=source['title'], articles=source['entries'])

if __name__ == '__main__':
    app.run(debug=True)