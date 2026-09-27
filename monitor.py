import os
import requests
from bs4 import BeautifulSoup

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
URL = "https://aquafocus.base.shop/categories/5809345"

def check_stock():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 商品ブロックを取得
        items = soup.find_all(["li", "div"], class_=lambda c: c and ("item" in c.lower() or "product" in c.lower()))
        
        for item in items:
            text = item.get_text()
            if "アパレイオドン" in text:
                # SOLD OUTの表記がないかチェック
                if "SOLD OUT" not in text.upper() and "完売" not in text:
                    send_discord(f"AquaFocusでアパレイオドンの在庫（販売中）を検知しました！\n{URL}")
                    return
    except Exception as e:
        print(f"Error: {e}")

def send_discord(msg):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": f"@everyone 🐟 **入荷検知！**\n{msg}"})

if __name__ == "__main__":
    send_discord("📢 テスト通知：監視システムは正常に繋がっています！")
    check_stock()
