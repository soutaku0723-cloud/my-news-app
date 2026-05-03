from flask import Flask, render_template, request, redirect
import feedparser
import re

app = Flask(__name__)

# NHKのRSS URL（これらは画像URLが含まれています！）
RSS_URLS = {
    "it": "https://www.nhk.or.jp/rss/news/cat7.xml",
    "sports": "https://www.nhk.or.jp/rss/news/cat5.xml",
    "science": "https://www.nhk.or.jp/rss/news/cat6.xml"
}

@app.route('/')
def index():
    # どのボタンが押されたかチェック（最初はITを表示）
    mode = request.args.get('mode', 'it')
    if mode not in RSS_URLS:
        mode = 'it'
    
    target_url = RSS_URLS[mode]
    
    # ニュースデータを取ってくる
    feed = feedparser.parse(target_url)
    
    news_list = []
    for entry in feed.entries:
        # --- ここから画像URLを探す魔法 ---
        img_url = None
        
        # パターン1: linksの中から画像を探す
        if 'links' in entry:
            for link in entry.links:
                if 'image' in link.get('type', ''):
                    img_url = link.get('href')
                    break
        
        # パターン2: 説明文（summary）の中から <img> タグを探す
        if not img_url and 'summary' in entry:
            match = re.search(r'src="(.*?)"', entry.summary)
            if match:
                img_url = match.group(1)

        # パターン3: どうしても無いときはダミー画像
        if not img_url:
            img_url = "https://via.placeholder.com/300x200.png?text=No+Image"
        # --- 画像取得ここまで ---

        # スコア計算（あなたのアイデアを継承！）
        score = 50
        if "AI" in entry.title or "大谷" in entry.title:
            score += 100
            
        news_list.append({
            "title": entry.title, 
            "link": entry.link, 
            "score": score,
            "img_url": img_url # これをHTMLに渡す
        })
    
    return render_template('index.html', news=news_list, mode=mode)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
