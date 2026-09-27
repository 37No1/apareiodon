import os
import requests
from bs4 import BeautifulSoup

# GitHubの設定からDiscordのURLを読み込む
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 監視したいショップのリスト
TARGET_SITES = [
    {"name": "AquaFocus", "url": "https://aquafocus.base.shop/categories/5809345"},
    {"name": "Aqua shop Flumen", "url": "https://aquashop-flumen.com/project/%E3%82%A2%E3%83%91%E3%83%AC%E3%82%A4%E3%82%AA%E3%83%89%E3%83%B3-%E3%83%9E%E3%82%AF%E3%83%AA%E3%82%B7%E3%83%BC%E3%83%88%E3%82%AB%E3%83%B3%E3%83%81%E3%83%B3%E3%82%B95-6%E3%8E%9D/"},
    {"name": "アクアショップ魚力", "url": "https://a-uoriki.com/wp/13217/"},
]

def check_stock():
    # スマホやPCからのアクセスに見せかけるための設定
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    available_shops = []
    
    for site in TARGET_SITES:
        try:
            # ページを取得
            res = requests.get(site["url"], headers=headers, timeout=15)
            res.encoding = res.apparent_encoding # 文字化け防止
            soup = BeautifulSoup(res.text, "html.parser")
            
            # ページ内の文字をすべて大文字にして取得（小文字・大文字のブレをなくすため）
            page_text = soup.get_text().upper()
            
            # 売り切れを示すキーワード
            out_of_stock_words = ["SOLD OUT", "完売", "在庫切れ", "売り切れ", "在庫なし"]
            
            # ページ内に「アパレイオドン」という文字が存在するか
            if "アパレイオドン" in page_text:
                # 商品ごとの枠（ブロック）を探す
                items = soup.find_all(["li", "div"], class_=lambda c: c and any(w in c.lower() for w in ["item", "product", "list"]))
                
                found = False
                
                if items:
                    # 複数商品が並ぶページ（Flumen, AquaFocusなど）
                    for item in items:
                        item_text = item.get_text().upper()
                        # その枠の中にアパレイオドンがあり、かつ売り切れワードがないか
                        if "アパレイオドン" in item_text:
                            if not any(word in item_text for word in out_of_stock_words):
                                found = True
                                break
                else:
                    # 単独の商品ページ（魚力、ペットバルーンなど）
                    if not any(word in page_text for word in out_of_stock_words):
                        found = True
                        
                if found:
                    available_shops.append(f"【{site['name']}】\n{site['url']}")
                    
        except Exception as e:
            print(f"{site['name']}のチェック中にエラー: {e}")

    # もし1つでも在庫あり判定のお店があればDiscordへまとめて通知
    if available_shops:
        msg = "以下のショップでアパレイオドンが販売中（在庫あり）の可能性があります！\n\n" + "\n\n".join(available_shops)
        send_discord(msg)

def send_discord(msg):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": f"@everyone 🐟 **入荷検知！**\n{msg}"})

if __name__ == "__main__":
    check_stock()
