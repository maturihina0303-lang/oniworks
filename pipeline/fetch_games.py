"""前後3ヶ月に日本で発売されるゲームを、ファミ通の発売スケジュールから取得。

日本の発売日・日本語タイトル・機種が得られます（APIキー不要）。
URL: https://www.famitsu.com/schedule/all-platforms/YYYYMM （月別・サーバー描画HTML）
※ファミ通のHTML構造が変わったら、下の正規表現の調整が必要です。
"""
import re
import html
import datetime as dt
import common as C

BASE = "https://www.famitsu.com/schedule/all-platforms/"

HDR = re.compile(
    r'ScheduleList_listTitle__[^"]*">(\d{4})年(\d{1,2})月(\d{1,2})日（.）発売</h2>')
RE_ID = re.compile(r'href="/game/title/(\d+)')
RE_IMG = re.compile(r'image\.kagali\.kgl-systems\.io/item/(\d+)/([A-Za-z0-9]+)')
RE_PLAT = re.compile(r'gamePlatformTag__[^"]*">([^<]*)</span>')
RE_TITLE = re.compile(r'gameTitleName__[^"]*">([^<]*)</b>')
RE_PRICE = re.compile(r'<p>([^<]*円[^<]*)</p>')


def img_url(seg):
    m = RE_IMG.search(seg)
    if not m:
        return ""
    return f"https://image.kagali.kgl-systems.io/item/{m.group(1)}/{m.group(2)}?w=200&h=200&func=bound&q=80"


def fetch_html(url):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", "ignore")


def months_around(today, back=3, fwd=3):
    """今月の前後 back〜fwd ヶ月の YYYYMM リスト。"""
    ms = []
    for off in range(-back, fwd + 1):
        m = today.month - 1 + off
        y = today.year + m // 12
        ms.append(f"{y}{(m % 12) + 1:02d}")
    return ms


def parse(page_html):
    heads = list(HDR.finditer(page_html))
    out = []
    for i, h in enumerate(heads):
        y, mo, d = h.group(1), int(h.group(2)), int(h.group(3))
        date = f"{y}-{mo:02d}-{d:02d}"
        seg = page_html[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(page_html)]
        # カード単位に分割（1ゲーム=1カード）
        for chunk in seg.split('ScheduleCard_scheduleCard__')[1:]:
            mid = RE_ID.search(chunk)
            mt = RE_TITLE.search(chunk)
            if not (mid and mt):
                continue
            mp = RE_PLAT.search(chunk)
            mpr = RE_PRICE.search(chunk)
            out.append({
                "id": f"fami-{mid.group(1)}",
                "title": html.unescape(mt.group(1).strip()),
                "release_date": date,
                "platforms": [mp.group(1).strip()] if mp and mp.group(1).strip() else [],
                "genre": [],
                "price": html.unescape(mpr.group(1).strip()) if mpr else "",
                "image": img_url(chunk),
                "source": "ファミ通",
            })
    return out


def main():
    lo, hi = C.date_range()
    seen, rows = set(), []
    for ym in months_around(C.TODAY):
        try:
            page = fetch_html(BASE + ym)
        except Exception as e:
            print(f"[WARN] {ym} 取得失敗: {e}")
            continue
        for r in parse(page):
            if r["id"] in seen:
                continue
            if not (lo.isoformat() <= r["release_date"] <= hi.isoformat()):
                continue
            seen.add(r["id"])
            rows.append(r)
    rows.sort(key=lambda r: r["release_date"])
    if not rows:
        print("[WARN] ゲーム情報を抽出できませんでした。HTML構造が変わった可能性があります。")
    C.publish("games", "games", rows)


if __name__ == "__main__":
    main()
