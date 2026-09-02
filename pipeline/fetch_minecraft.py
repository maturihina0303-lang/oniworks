"""Minecraft の鬼ごっこ向き MOD を Modrinth から取得（API キー不要）。

人気順そのままだと軽量化・ライブラリ系ばかりになるため、
鬼ごっこ/かくれんぼ企画に使えるテーマで検索して集めます。
"""
import urllib.parse
import common as C
import translate

API = "https://api.modrinth.com/v2/search"

# ぷちぷちの鬼ごっこ企画に使えそうなテーマ検索
QUERIES = ["horror", "hide and seek", "parkour", "backrooms",
           "doors", "mob", "morph", "maze", "tag"]

# 軽量化・ライブラリ等の“ネタにならない”カテゴリは除外
EXCLUDE = {"optimization", "library", "utility"}


def search(query, limit=8):
    facets = '[["project_type:mod"]]'
    q = urllib.parse.urlencode({"query": query, "facets": facets,
                                "index": "relevance", "limit": limit})
    return C.http_json(f"{API}?{q}").get("hits", [])


def to_row(h):
    dl = h.get("downloads", 0)
    metric = f"DL {dl/1_000_000:.1f}M" if dl >= 1_000_000 else f"DL {dl/1000:.0f}K"
    slug = h.get("slug") or h.get("project_id")
    name = (h.get("title") or "").strip()
    desc = (h.get("description") or "").strip()
    return {
        "id": f"modrinth-{h.get('project_id')}",
        "category": "minecraft",
        "name": name,                      # 原題（Modrinthの識別名）
        "name_ja": translate.to_ja(name),  # 自動翻訳した日本語名
        "type": "MOD",
        "url": f"https://modrinth.com/mod/{slug}",
        "metric": metric,
        "downloads": dl,                   # 並び替え用のDL数(数値)
        "updated": (h.get("date_modified") or "")[:10] or None,
        "description": translate.to_ja(desc)[:180],  # 日本語訳の説明
        "image": h.get("icon_url") or "",
        "source": "Modrinth",
    }


def main():
    seen, hits = set(), []
    for q in QUERIES:
        for h in search(q):
            pid = h.get("project_id")
            cats = set(h.get("categories") or [])
            if pid in seen or cats & EXCLUDE:
                continue
            if h.get("downloads", 0) < 5000:   # あまりに無名すぎるものは除外
                continue
            seen.add(pid)
            hits.append(h)
    # ダウンロード数の多い順に上位30件
    hits.sort(key=lambda h: -h.get("downloads", 0))
    rows = [to_row(h) for h in hits[:30]]
    C.publish_topics_partial("minecraft", rows)


if __name__ == "__main__":
    main()
