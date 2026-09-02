"""手動編集した curated/roblox.json・curated/meme.json を反映する。

Roblox・ネットミームは自動取得に適したAPIが無いため、
curated/ のJSONを編集 → このスクリプトで topics テーブルへ反映します。
"""
import os
import json
import datetime as dt
import common as C

CURATED = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "curated"))
MAX_AGE_DAYS = 100  # 更新日がこれより古い項目は自動で表示から外す（≒3ヶ月）


def load(name):
    path = os.path.join(CURATED, f"{name}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("items", [])


def is_recent(item):
    """updated が MAX_AGE_DAYS 以内なら True。日付が無い/壊れている場合は残す。"""
    u = item.get("updated")
    if not u:
        return True
    try:
        return (C.TODAY - dt.date.fromisoformat(u)).days <= MAX_AGE_DAYS
    except ValueError:
        return True


def main():
    cutoff = (C.TODAY - dt.timedelta(days=MAX_AGE_DAYS)).isoformat()
    for category in ("roblox", "meme"):
        rows = load(category)
        for r in rows:
            r["category"] = category
            r.pop("_note", None)
        fresh = [r for r in rows if is_recent(r)]
        dropped = len(rows) - len(fresh)
        if dropped:
            print(f"[INFO] {category}: 更新日が{cutoff}より古い {dropped} 件を除外しました。")
        C.publish_topics_partial(category, fresh)


if __name__ == "__main__":
    main()
