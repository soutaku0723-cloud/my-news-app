from flask import Flask, render_template, request
import feedparser

app = Flask(__name__)

# ボタンごとにどのニュースURLを使うかのリスト
RSS_URLS = {
    "it": "https://news.yahoo.co.jp/rss/topics/it.xml",
    "sports": "https://news.yahoo.co.jp/rss/topics/sports.xml",
    "science": "https://news.yahoo.co.jp/rss/topics/science.xml"
}

@app.route('/')
def index():
    # どのボタンが押されたかチェック（最初はITを表示）
    mode = request.args.get('mode', 'it')
    target_url = RSS_URLS.get(mode, RSS_URLS['it'])
    
    # ニュースデータを取ってくる
    feed = feedparser.parse(target_url)
    
    news_list = []
    for entry in feed.entries:
        score = 50
        # AIとか特定の言葉が入ってたらスコアアップ！
        if "AI" in entry.title or "大谷" in entry.title: score += 100
        news_list.append({"title": entry.title, "link": entry.link, "score": score})
    
   # templates/index.html にニュースデータを渡して表示させる
    return render_template('index.html', news=news_list, mode=mode)

if __name__ == "__main__":
    # host='0.0.0.0' を入れることで、同じWi-Fi内の他のデバイスからも見れるようになります
    app.run(debug=True, host='0.0.0.0')
