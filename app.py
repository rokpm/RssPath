import feedparser
import datetime
from flask import Flask, render_template

app = Flask(__name__)

rss_urls = [
    'https://www.hecaitou.com/feeds/posts/default',
    'http://www.ruanyifeng.com/blog/atom.xml',
    'https://www.ezindie.com/feed/rss.xml',
    'https://www.williamlong.info/rss.xml',
    'https://louiscard.com/feed/',
    # 添加更多的RSS订阅源URL
]

def get_feeds():
    feeds_data = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        if feed.entries:
            latest_entry = feed.entries[0]
            icon_url = feed.feed.icon if hasattr(feed.feed, 'icon') else None
            last_week_count = sum(1 for entry in feed.entries if (datetime.datetime.now() - datetime.datetime(*entry.published_parsed[:6])).days <= 7)
            feeds_data.append({
                'icon': icon_url,
                'title': feed.feed.title,
                'link': feed.feed.link,
                'latest_entry_title': latest_entry.title,
                'latest_entry_published': datetime.datetime(*latest_entry.published_parsed[:6]).strftime('%Y-%m-%d'),
                'last_week_count': last_week_count,
                'entries': feed.entries
            })
    return feeds_data

@app.route('/')
def rss_home():
    feeds = get_feeds()
    return render_template('index.html', feeds=feeds)

@app.route('/detail/<feed_name>', endpoint='detail')
def rss_detail(feed_name):
    feed = None
    feeds_data = get_feeds()
    for f in feeds_data:
        if f['title'] == feed_name:
            feed = f
            break

    if not feed:
        return "Feed not found", 404

    return render_template('detail.html', feed=feed, datetime=datetime)

if __name__ == '__main__':
    app.run(debug=True)