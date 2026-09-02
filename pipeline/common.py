"""オニWorks データ取得の共通ユーティリティ。

Supabase への書き込み（全置換）と、日付・環境変数のヘルパーをまとめています。
環境変数:
  SUPABASE_URL          … https://xxxx.supabase.co
  SUPABASE_SERVICE_KEY  … service_role キー（書き込み用・GitHub Secrets に保存）
"""
import os
import json
import sys
import datetime as dt
import urllib.request
import urllib.parse
import urllib.error

TODAY = dt.date.today()


def env(name, required=True, default=None):
    v = os.environ.get(name, default)
    if required and not v:
        print(f"[ERROR] 環境変数 {name} が未設定です。", file=sys.stderr)
        sys.exit(1)
    return v


def date_range(days_back=100, days_forward=100):
    return (TODAY - dt.timedelta(days=days_back),
            TODAY + dt.timedelta(days=days_forward))


def http_json(url, headers=None, method="GET", data=None):
    """簡易 HTTP。requests に依存せず標準ライブラリで完結。"""
    body = None
    hdrs = {"User-Agent": "OniWorks/1.0 (github pipeline)"}
    if headers:
        hdrs.update(headers)
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            raw = res.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")
        raise RuntimeError(f"HTTP {e.code} {url}\n{detail}") from e


# -------------------- Supabase 書き込み --------------------

def _sb_base():
    url = env("SUPABASE_URL")
    key = env("SUPABASE_SERVICE_KEY")
    return url.rstrip("/"), key


def replace_table(table, rows):
    """テーブルを全消去してから rows を投入する（全置換）。

    外部データを毎回まるごと入れ替えるので、古い情報が残りません。
    """
    base, key = _sb_base()
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    # 1) 全削除（id が null でない行 = 全行）
    del_url = f"{base}/rest/v1/{table}?id=not.is.null"
    http_json(del_url, headers=headers, method="DELETE")
    # 2) まとめて挿入
    if rows:
        ins_url = f"{base}/rest/v1/{table}"
        h = dict(headers)
        h["Prefer"] = "return=minimal"
        http_json(ins_url, headers=h, method="POST", data=rows)
    print(f"[OK] {table}: {len(rows)} 件を投入しました。")


def save_local(name, rows):
    """Supabase 未設定でもローカル data/*.json を更新できるようにする。"""
    out = os.path.join(os.path.dirname(__file__), "..", "data", f"{name}.json")
    out = os.path.abspath(out)
    payload = {"_note": "自動生成", "updated_at": TODAY.isoformat(), "items": rows}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[OK] data/{name}.json を更新しました（{len(rows)} 件）。")


def publish(table, name, rows):
    """Supabase があれば Supabase へ、無ければローカル JSON へ保存。"""
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY"):
        replace_table(table, rows)
    else:
        print(f"[INFO] Supabase 未設定のためローカル保存します（{name}）。")
        save_local(name, rows)


def read_current(name, table=None):
    """現在のデータを読み込む。Supabase があればそこから、無ければ data/*.json。"""
    table = table or name
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY"):
        base, key = _sb_base()
        headers = {"apikey": key, "Authorization": f"Bearer {key}"}
        return http_json(f"{base}/rest/v1/{table}?select=*", headers=headers) or []
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", f"{name}.json"))
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("items", [])
    except FileNotFoundError:
        return []


def _sb_delete_where(table, filt, headers):
    http_json(f"{table}?{filt}", headers=headers, method="DELETE")


def publish_topics_partial(category, rows):
    """topics テーブルの特定カテゴリだけを置換する（他カテゴリは残す）。

    minecraft / roblox / meme を別々のスクリプトから更新するため。
    """
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY"):
        base, key = _sb_base()
        headers = {"apikey": key, "Authorization": f"Bearer {key}",
                   "Content-Type": "application/json"}
        http_json(f"{base}/rest/v1/topics?category=eq.{category}",
                  headers=headers, method="DELETE")
        if rows:
            h = dict(headers)
            h["Prefer"] = "return=minimal"
            http_json(f"{base}/rest/v1/topics", headers=h, method="POST", data=rows)
        print(f"[OK] topics/{category}: {len(rows)} 件を投入しました。")
    else:
        out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "topics.json"))
        try:
            with open(out, encoding="utf-8") as f:
                cur = json.load(f).get("items", [])
        except FileNotFoundError:
            cur = []
        kept = [x for x in cur if x.get("category") != category]
        payload = {"_note": "自動生成", "updated_at": TODAY.isoformat(), "items": kept + rows}
        with open(out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"[OK] data/topics.json の {category} を更新（{len(rows)} 件）。")
