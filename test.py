from flask import Flask, render_template, request, redirect
import feedparser
import re

app = Flask(__name__)

RSS_URLS = {
    "politics": "https://www.nhk.or.jp/rss/news/cat1.xml",
    "sports": "https://www.nhk.or.jp/rss/news/cat5.xml",
    "others": "https://www.nhk.or.jp/rss/news/cat7.xml"
}

def get_clean_news(category, search_query=None):
    feed = feedparser.parse(RSS_URLS[category])
    news_list = []
    
    for entry in feed.entries:
        title = entry.title
        summary = re.sub(r'<.*?>', '', entry.get('summary', '')).strip()
        
        # 検索ワードがある場合、タイトルか説明文に含まれていない記事は飛ばす
        if search_query and search_query.lower() not in (title + summary).lower():
            continue

        img_url = None
        if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
            img_url = entry.media_thumbnail[0]['url']
        if not img_url and 'links' in entry:
            for link in entry.links:
                if 'image' in link.get('type', '') or 'enclosure' in link.get('rel', ''):
                    img_url = link.get('href')
                    break
        if not img_url:
            img_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80"

        news_list.append({
            "title": title,
            "link": entry.link,
            "summary": summary,
            "img_url": img_url
        })
    return news_list

@app.route('/')
def home():
    return redirect('/sports')

@app.route('/<category>')
def show_news(category):
    if category not in RSS_URLS:
        return redirect('/sports')
    
    # 検索窓からの入力を受け取る
    search_query = request.args.get('q', '')
    news = get_clean_news(category, search_query)
    
    return render_template('index.html', news=news, mode=category, search_query=search_query)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
