from flask import Flask, render_template, request, redirect
import feedparser
import re

app = Flask(__name__)

# カテゴリとURLを整理
RSS_URLS = {
    "politics": "https://www.nhk.or.jp/rss/news/cat1.xml", # 政治
    "sports": "https://www.nhk.or.jp/rss/news/cat5.xml",   # スポーツ
    "others": "https://www.nhk.or.jp/rss/news/cat7.xml"    # その他(IT/科学など)
}

def get_clean_news(category):
    feed = feedparser.parse(RSS_URLS[category])
    news_list = []
    
    for entry in feed.entries:
        img_url = None
        # 画像取得ロジック（最強版を維持）
        if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
            img_url = entry.media_thumbnail[0]['url']
        if not img_url and 'links' in entry:
            for link in entry.links:
                if 'image' in link.get('type', '') or 'enclosure' in link.get('rel', ''):
                    img_url = link.get('href')
                    break
        if not img_url:
            # ニュースらしい代わりの画像
            img_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80"

        summary = entry.get('summary', '')
        summary = re.sub(r'<.*?>', '', summary).strip() 

        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "img_url": img_url
        })
    return news_list

@app.route('/')
def home():
    return redirect('/sports') # 最初はスポーツを表示

@app.route('/<category>')
def show_news(category):
    if category not in RSS_URLS:
        return redirect('/sports')
    news = get_clean_news(category)
    return render_template('index.html', news=news, mode=category)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
