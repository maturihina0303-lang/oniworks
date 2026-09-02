"""日本で急上昇中のゲーム動画を YouTube Data API v3 から取得。

chart=mostPopular × regionCode=JP × videoCategoryId=20(ゲーム) で、
日本のゲーム系トレンド動画を取得します。

必要な環境変数:
  YOUTUBE_API_KEY  … YouTube Data API v3 のキー（Google Cloud で無料発行）
"""
import common as C

API = "https://www.googleapis.com/youtube/v3/videos"


def fmt_views(n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        return ""
    if n >= 100_000_000:
        return f"{n/100_000_000:.1f}億回"
    if n >= 10_000:
        return f"{n//10_000}万回"
    return f"{n}回"


def best_thumb(thumbs):
    for k in ("maxres", "standard", "high", "medium", "default"):
        if thumbs.get(k):
            return thumbs[k]["url"]
    return ""


def main():
    key = C.env("YOUTUBE_API_KEY")
    url = (f"{API}?part=snippet,statistics&chart=mostPopular"
           f"&regionCode=JP&videoCategoryId=20&maxResults=30&key={key}")
    data = C.http_json(url)
    rows = []
    for v in data.get("items", []):
        sn = v.get("snippet", {})
        st = v.get("statistics", {})
        vid = v.get("id")
        rows.append({
            "id": f"yt-{vid}",
            "title": sn.get("title", ""),
            "channel": sn.get("channelTitle", ""),
            "url": f"https://www.youtube.com/watch?v={vid}",
            "thumbnail": best_thumb(sn.get("thumbnails", {})),
            "views": fmt_views(st.get("viewCount")),
            "published": (sn.get("publishedAt") or "")[:10],
            "source": "YouTube",
        })
    if not rows:
        print("[WARN] YouTube動画を取得できませんでした。")
    C.publish("youtube", "youtube", rows)


if __name__ == "__main__":
    main()
