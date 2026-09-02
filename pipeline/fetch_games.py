"""前後3ヶ月に発売されるゲームを RAWG から取得。

必要な環境変数:
  RAWG_API_KEY  … RAWG の API キー。https://rawg.io/apidocs
"""
import common as C


def main():
    key = C.env("RAWG_API_KEY")
    lo, hi = C.date_range()
    url = (
        "https://api.rawg.io/api/games"
        f"?key={key}&dates={lo.isoformat()},{hi.isoformat()}"
        "&ordering=-added&page_size=40"
    )
    data = C.http_json(url)
    rows = []
    for g in data.get("results", []):
        rows.append({
            "id": f"rawg-{g['id']}",
            "title": g.get("name"),
            "release_date": g.get("released") or None,
            "platforms": [p["platform"]["name"] for p in (g.get("platforms") or [])],
            "genre": [x["name"] for x in (g.get("genres") or [])],
            "image": g.get("background_image") or "",
            "popularity": g.get("added", 0),
            "source": "RAWG",
        })
    rows.sort(key=lambda r: r["release_date"] or "9999")
    C.publish("games", "games", rows)


if __name__ == "__main__":
    main()
