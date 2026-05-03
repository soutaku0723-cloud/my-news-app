from flask import Flask, render_template, request, redirect
import feedparser
import re

app = Flask(__name__)

RSS_URLS = {
    "it": "https://www.nhk.or.jp/rss/news/cat7.xml",
    "sports": "https://www.nhk.or.jp/rss/news/cat5.xml",
    "science": "https://www.nhk.or.jp/rss/news/cat6.xml"
}

def get_clean_news(category):
    feed = feedparser.parse(RSS_URLS[category])
    news_list = []
    
    for entry in feed.entries:
        # --- 画像取得 (さらに強化版) ---
        img_url = None
        # 1. media_thumbnailを探す
        if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
            img_url = entry.media_thumbnail[0]['url']
        # 2. linksからenclosure(画像)を探す
        if not img_url and 'links' in entry:
            for link in entry.links:
                if 'image' in link.get('type', ''):
                    img_url = link.get('href')
                    break
        # 3. どうしても無い時のダミー
        if not img_url:
            img_url = "https://via.placeholder.com/800x450.png?text=No+Image"

        # --- 説明文の掃除 (HTMLタグを消す) ---
        summary = entry.get('summary', '')
        summary = re.sub(r'<.*?>', '', summary) # <img...> などを消して文字だけにする

        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "img_url": img_url
        })
    return news_list

# 404を防ぐためのルーティング設定
@app.route('/')
def home():
    return redirect('/it')

@app.route('/<category>')
def show_news(category):
    if category not in RSS_URLS:
        return redirect('/it')
    
    news = get_clean_news(category)
    return render_template('index.html', news=news, mode=category)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
