"""英語→日本語の自動翻訳（無料・APIキー不要）。

Google の無償エンドポイント(translate_a/single)を使用します。非公式のため、
失敗時は元の英語をそのまま返す（サイトが壊れない）フォールバック付き。
"""
import json
import urllib.parse
import urllib.request

_CACHE = {}


def to_ja(text):
    text = (text or "").strip()
    if not text:
        return ""
    if text in _CACHE:
        return _CACHE[text]
    try:
        q = urllib.parse.quote(text)
        url = ("https://translate.googleapis.com/translate_a/single"
               f"?client=gtx&sl=en&tl=ja&dt=t&q={q}")
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
        out = "".join(seg[0] for seg in data[0] if seg and seg[0])
        out = out.strip() or text
    except Exception:
        out = text  # 失敗時は元の英語のまま
    _CACHE[text] = out
    return out


if __name__ == "__main__":
    for s in ["Hide and Seek", "Adds a friend to play hide and seek with!",
              "A high-performance rendering engine replacement for Minecraft."]:
        print(s, "->", to_ja(s))
