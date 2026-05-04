from flask import Flask, render_template, request, redirect
import feedparser
import re

app = Flask(__name__)

# YahooニュースのRSSに変更（記事が豊富なので政治がゼロになるのを防ぐ）
RSS_SOURCES = [
    "https://news.yahoo.co.jp/rss/topics/top-picks.xml",
    "https://news.yahoo.co.jp/rss/topics/domestic.xml",
    "https://news.yahoo.co.jp/rss/topics/world.xml",
    "https://news.yahoo.co.jp/rss/topics/sports.xml"
]

# キーワードを少し強化
KEYWORDS = {
    "sports": ["試合", "選手", "優勝", "監督", "五輪", "大谷", "勝利", "得点", "野球", "サッカー", "バスケ", "テニス", "スタジアム", "連勝", "打者", "ホームラン", "スポーツ"],
    "politics": ["首相", "大臣", "選挙", "政府", "国会", "外交", "会談", "大統領", "首脳", "自民", "立憲", "米軍", "条約", "政策", "法案", "政治", "議員", "バイデン", "岸田"]
}

def get_categorized_news(target_category, search_query=None):
    all_news = []
    seen_links = set()

    for url in RSS_SOURCES:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if entry.link in seen_links:
                continue
            seen_links.add(entry.link)

            title = entry.title
            summary = re.sub(r'<.*?>', '', entry.get('summary', '')).strip()

            # 判定を「タイトルだけ」に変更して誤爆を防止！
            is_politics = any(k in title for k in KEYWORDS["politics"])
            is_sports = any(k in title for k in KEYWORDS["sports"])

            determined_cat = "others"
            if is_politics:
                determined_cat = "politics"
            elif is_sports:
                determined_cat = "sports"

            if determined_cat != target_category:
                continue

            if search_query and search_query.lower() not in title.lower():
                continue

            img_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80"
            if 'links' in entry:
                for link in entry.links:
                    if 'image' in link.get('type', ''):
                        img_url = link.get('href')
                        break

            all_news.append({
                "title": title,
                "link": entry.link,
                "summary": summary, # 画面には出さないが、AI要約ボタンのために裏で持っておく
                "img_url": img_url
            })
    
    return all_news[:15]

@app.route('/')
def home():
    return redirect('/sports')

@app.route('/<category>')
def show_news(category):
    if category not in ["sports", "politics", "others"]:
        return redirect('/sports')
    
    search_query = request.args.get('q', '')
    news = get_categorized_news(category, search_query)
    
    return render_template('index.html', news=news, mode=category, search_query=search_query)

if __name__ == "__main__":
    app.run(debug=True)
