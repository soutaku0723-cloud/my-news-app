from flask import Flask, render_template, request, redirect
import feedparser
import re

app = Flask(__name__)

# NHKを卒業して、無料で読めるハフポストなどのRSSに切り替え
RSS_URLS = {
    "politics": "https://www.huffingtonpost.jp/feeds/verticals/politics/index.xml", # 政治
    "sports": "https://www.huffingtonpost.jp/feeds/verticals/sports/index.xml",     # スポーツ
    "others": "https://www.huffingtonpost.jp/feeds/index.xml"                     # 総合（その他）
}

def get_clean_news(category, search_query=None):
    feed = feedparser.parse(RSS_URLS[category])
    news_list = []
    
    for entry in feed.entries:
        title = entry.title
        summary = re.sub(r'<.*?>', '', entry.get('summary', '')).strip()
        
        # 検索機能
        if search_query and search_query.lower() not in (title + summary).lower():
            continue

        # 画像取得（ハフポスト用）
        img_url = None
        if 'links' in entry:
            for link in entry.links:
                if 'image' in link.get('type', ''):
                    img_url = link.get('href')
                    break
        
        # 画像が見つからない場合の予備（Unsplashのカッコいいニュース画像）
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
    
    search_query = request.args.get('q', '')
    news = get_clean_news(category, search_query)
    
    return render_template('index.html', news=news, mode=category, search_query=search_query)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
