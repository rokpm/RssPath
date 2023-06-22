from flask import Flask, render_template
from feedparser import parse
from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures import ThreadPoolExecutor
from pytz import utc

app = Flask(__name__)

# RSS源列表
RSS_FEEDS = {
    'hecaitou':'https://www.hecaitou.com/feeds/posts/default',
    'ruanyifeng':'http://www.ruanyifeng.com/blog/atom.xml',
    'ezindie':'https://www.ezindie.com/feed/rss.xml',
    'williamlong':'https://www.williamlong.info/rss.xml',
    'louiscard':'https://louiscard.com/feed/',
}

# 全局变量
feeds_data = []

# 获取RSS数据
def get_feeds():
    feeds = []
    for key, url in RSS_FEEDS.items():
        feed = parse(url)
        feeds.append({
            'title': feed['feed']['title'],
            'link': feed['feed']['link'],
            'entries': feed['entries'],
        })
    return feeds

def update_feeds():
    global feeds_data
    with ThreadPoolExecutor() as executor:
        feeds_data = executor.submit(get_feeds).result()

# 初始化feeds数据
update_feeds()

# 创建定时任务
scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_job(update_feeds, 'interval', hours=1)
scheduler.start()

@app.route('/rss_detail/<feed_name>')
def rss_detail(feed_name):
    feed = None
    for f in feeds_data:
        if f.title == feed_name:
            feed = f
            break

    if not feed:
        return "Feed not found", 404

    return render_template('rss_detail.html', feed=feed)

@app.route('/')
def rss_home():
    return render_template('index.html', feeds=feeds_data)

if __name__ == '__main__':
    app.run()