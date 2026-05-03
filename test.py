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
        img_url = None
        
        # --- 画像URLを探す最強パターン ---
        # A. media_thumbnail (一番標準的)
        if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
            img_url = entry.media_thumbnail[0]['url']
        
        # B. linksの中の画像用URL (NHKで多いパターン)
        if not img_url and 'links' in entry:
            for link in entry.links:
                if 'image' in link.get('type', '') or 'enclosure' in link.get('rel', ''):
                    img_url = link.get('href')
                    break
        
        # C. 概要(summary)の中のimgタグから抽出
        if not img_url and 'summary' in entry:
            match = re.search(r'src=["\'](.*?\.(?:jpg|png|gif|jpeg).*?)["\']', entry.summary, re.IGNORECASE)
            if match:
                img_url = match.group(1)

        # D. それでも無い場合の最終予備 (NHKのロゴなどを避けるためのダミー)
        if not img_url or "logo" in img_url.lower():
            img_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80"

        # --- 説明文の掃除 ---
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
    return redirect('/it')

@app.route('/<category>')
def show_news(category):
    if category not in RSS_URLS:
        return redirect('/it')
    news = get_clean_news(category)
    return render_template('index.html', news=news, mode=category)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
