"""公開中・公開予定の映画を TMDB から取得（日本・日本語）。

必要な環境変数:
  TMDB_API_KEY  … TMDB の API キー(v3)。https://www.themoviedb.org/settings/api
"""
import common as C

BASE = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"


def genre_map(key):
    data = C.http_json(f"{BASE}/genre/movie/list?api_key={key}&language=ja")
    return {g["id"]: g["name"] for g in data.get("genres", [])}


def fetch(endpoint, key, status, gmap, pages=2):
    rows = []
    for p in range(1, pages + 1):
        url = f"{BASE}/movie/{endpoint}?api_key={key}&language=ja-JP&region=JP&page={p}"
        data = C.http_json(url)
        for m in data.get("results", []):
            rows.append({
                "id": f"tmdb-{m['id']}",
                "title": m.get("title") or m.get("original_title"),
                "release_date": m.get("release_date") or None,
                "status": status,
                "genre": [gmap.get(gid) for gid in m.get("genre_ids", []) if gmap.get(gid)],
                "overview": m.get("overview") or "",
                "poster": (IMG + m["poster_path"]) if m.get("poster_path") else "",
                "popularity": round(m.get("popularity", 0), 1),
                "source": "TMDB",
            })
    return rows


def main():
    key = C.env("TMDB_API_KEY")
    gmap = genre_map(key)
    now = fetch("now_playing", key, "now", gmap)
    up = fetch("upcoming", key, "upcoming", gmap)
    # id 重複は now を優先
    merged = {}
    for r in up + now:  # now を後に置いて上書き
        merged[r["id"]] = r
    lo, hi = C.date_range()
    rows = [r for r in merged.values()
            if not r["release_date"] or lo.isoformat() <= r["release_date"] <= hi.isoformat()]
    rows.sort(key=lambda r: r["release_date"] or "9999")
    C.publish("movies", "movies", rows)


if __name__ == "__main__":
    main()
