"""公開中・公開予定の映画を TMDB から取得（日本・日本語）。

- 公開中(now)   : /movie/now_playing（region=JP）
- 公開予定(upcoming): /discover/movie で「今日〜約5ヶ月先」を期間指定取得
  （upcoming エンドポイントは直近しか返さないため discover を使用）

必要な環境変数:
  TMDB_API_KEY  … TMDB の API キー(v3)。https://www.themoviedb.org/settings/api
"""
import datetime as dt
import common as C

BASE = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"
FORWARD_DAYS = 150  # 何日先までの公開予定を取るか


def genre_map(key):
    data = C.http_json(f"{BASE}/genre/movie/list?api_key={key}&language=ja")
    return {g["id"]: g["name"] for g in data.get("genres", [])}


def to_row(m, status, gmap):
    return {
        "id": f"tmdb-{m['id']}",
        "title": m.get("title") or m.get("original_title"),
        "release_date": m.get("release_date") or None,
        "status": status,
        "genre": [gmap.get(gid) for gid in m.get("genre_ids", []) if gmap.get(gid)],
        "overview": m.get("overview") or "",
        "poster": (IMG + m["poster_path"]) if m.get("poster_path") else "",
        "popularity": round(m.get("popularity", 0), 1),
        "source": "TMDB",
    }


def now_playing(key, gmap, pages=2):
    rows = []
    for p in range(1, pages + 1):
        url = f"{BASE}/movie/now_playing?api_key={key}&language=ja-JP&region=JP&page={p}"
        for m in C.http_json(url).get("results", []):
            rows.append(to_row(m, "now", gmap))
    return rows


def upcoming(key, gmap, pages=5):
    """discover で 明日〜FORWARD_DAYS 先 の日本公開作を人気順に取得。"""
    lo = (C.TODAY + dt.timedelta(days=1)).isoformat()
    hi = (C.TODAY + dt.timedelta(days=FORWARD_DAYS)).isoformat()
    rows = []
    for p in range(1, pages + 1):
        url = (f"{BASE}/discover/movie?api_key={key}&language=ja-JP&region=JP"
               f"&sort_by=popularity.desc&with_release_type=2%7C3"
               f"&release_date.gte={lo}&release_date.lte={hi}&page={p}")
        data = C.http_json(url)
        for m in data.get("results", []):
            rows.append(to_row(m, "upcoming", gmap))
        if p >= data.get("total_pages", 1):
            break
    return rows


def main():
    key = C.env("TMDB_API_KEY")
    gmap = genre_map(key)
    # now を後に置いて重複時に now を優先
    merged = {}
    for r in upcoming(key, gmap) + now_playing(key, gmap):
        merged[r["id"]] = r
    lo = (C.TODAY - dt.timedelta(days=100)).isoformat()
    hi = (C.TODAY + dt.timedelta(days=FORWARD_DAYS)).isoformat()
    rows = [r for r in merged.values()
            if not r["release_date"] or lo <= r["release_date"] <= hi]
    rows.sort(key=lambda r: r["release_date"] or "9999")
    C.publish("movies", "movies", rows)


if __name__ == "__main__":
    main()
