from flask import Flask, render_template, request, redirect
import feedparser
import re

app = Flask(__name__)

# ニュースソース（ここから全部取ってくる）
RSS_SOURCES = [
    "https://www.huffingtonpost.jp/feeds/index.xml",
    "https://www.huffingtonpost.jp/feeds/verticals/politics/index.xml",
    "https://www.huffingtonpost.jp/feeds/verticals/sports/index.xml"
]

# 仕分け用キーワードリスト
KEYWORDS = {
    "sports": ["試合", "選手", "優勝", "監督", "五輪", "大谷", "勝利", "得点", "野球", "サッカー", "バスケ", "テニス", "スタジアム"],
    "politics": ["首相", "大臣", "選挙", "政府", "国会", "外交", "会談", "大統領", "首脳", "自民", "立憲", "米軍", "条約", "政策"]
}

def get_categorized_news(target_category, search_query=None):
    all_news = []
    seen_links = set() # 重複チェック用

    for url in RSS_SOURCES:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if entry.link in seen_links:
                continue
            seen_links.add(entry.link)

            title = entry.title
            summary = re.sub(r'<.*?>', '', entry.get('summary', '')).strip()
            text_for_judge = (title + summary).lower()

            # --- 仕分けロジック ---
            # 1. 政治外交キーワードが含まれるか？
            is_politics = any(k in text_for_judge for k in KEYWORDS["politics"])
            # 2. スポーツキーワードが含まれるか？
            is_sports = any(k in text_for_judge for k in KEYWORDS["sports"])

            # 最終的な判定
            determined_cat = "others"
            if is_politics:
                determined_cat = "politics"
            elif is_sports:
                determined_cat = "sports"

            # ユーザーが選んだカテゴリと一致するか確認
            if determined_cat != target_category:
                continue

            # 検索窓のフィルタ
            if search_query and search_query.lower() not in text_for_judge:
                continue

            # 画像取得
            img_url = None
            if 'links' in entry:
                for link in entry.links:
                    if 'image' in link.get('type', ''):
                        img_url = link.get('href')
                        break
            if not img_url:
                img_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80"

            all_news.append({
                "title": title,
                "link": entry.link,
                "summary": summary,
                "img_url": img_url
            })
    
    return all_news[:15] # 最新15件を返す

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
