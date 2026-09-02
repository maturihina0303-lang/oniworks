"""手動編集した curated/roblox.json・curated/meme.json を反映する。

Roblox・ネットミームは自動取得に適したAPIが無いため、
curated/ のJSONを編集 → このスクリプトで topics テーブルへ反映します。
"""
import os
import json
import common as C

CURATED = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "curated"))


def load(name):
    path = os.path.join(CURATED, f"{name}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("items", [])


def main():
    for category in ("roblox", "meme"):
        rows = load(category)
        for r in rows:
            r["category"] = category
            r.pop("_note", None)
        C.publish_topics_partial(category, rows)


if __name__ == "__main__":
    main()
