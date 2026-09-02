"""金曜ロードショー(金曜ロードシネマクラブ)の放送予定を取得。

公式 https://kinro.ntv.co.jp/lineup はサーバー描画HTMLなので、
正規表現でラインナップ(<div class="date">…放送</div><div class="title">…)を抽出します。
※公式サイトのHTML構造が変わったら正規表現の調整が必要です。
"""
import re
import common as C

URL = "https://kinro.ntv.co.jp/lineup"
PAT = re.compile(
    r'<img src="([^"]+)"[^>]*/>\s*</a>\s*</div>\s*<div class="cap">\s*'
    r'<div class="date">\s*(20\d\d)\.(\d{1,2})\.(\d{1,2})\s*放送\s*</div>\s*'
    r'<div class="title">\s*<a[^>]*>([^<]+)</a>',
    re.S,
)


def fetch_html(url):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (OniWorks)"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", "ignore")


def main():
    html = fetch_html(URL)
    seen, rows = set(), []
    for img, y, m, d, title in PAT.findall(html):
        date = f"{y}-{int(m):02d}-{int(d):02d}"
        title = title.strip()
        key = (date, title)
        if key in seen:
            continue
        seen.add(key)
        rows.append({
            "id": f"kinro-{y}{int(m):02d}{int(d):02d}",
            "air_date": date,
            "title": title,
            "note": "金曜ロードショー",
            "image": img.strip(),
            "source": "kinro.ntv.co.jp",
        })
    rows.sort(key=lambda r: r["air_date"])
    if not rows:
        print("[WARN] 金ローの放送予定を抽出できませんでした。HTML構造が変わった可能性があります。")
    C.publish("kinro", "kinro", rows)


if __name__ == "__main__":
    main()
