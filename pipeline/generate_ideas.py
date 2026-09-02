"""集めたデータ(映画/金ロー/ゲーム/トレンド)を元に、
Claude が「ぷちぷち」チャンネルの鬼ごっこ企画ネタを自動生成する。

必要な環境変数:
  ANTHROPIC_API_KEY  … Claude API キー。https://console.anthropic.com/
公式 anthropic Python SDK を使用します（requirements.txt に記載）。
"""
import json
import re
import datetime as dt
import common as C

MODEL = "claude-opus-5"


def brief():
    """AI に渡す材料（現在のデータ）を短くまとめる。"""
    movies = C.read_current("movies")
    kinro = C.read_current("kinro")
    games = C.read_current("games")
    topics = C.read_current("topics")

    def lines(rows, fmt, limit=12):
        return "\n".join(fmt(r) for r in rows[:limit])

    parts = []
    parts.append("【公開中・公開予定の映画】\n" + lines(
        movies, lambda m: f"- {m.get('title')}（{m.get('release_date')}／{'公開中' if m.get('status')=='now' else '公開予定'}）"))
    parts.append("【金曜ロードショー放送予定】\n" + lines(
        kinro, lambda k: f"- {k.get('air_date')} {k.get('title')}"))
    parts.append("【発売予定ゲーム】\n" + lines(
        games, lambda g: f"- {g.get('title')}（{g.get('release_date')}）"))
    parts.append("【Minecraft/Roblox/ミームのトレンド】\n" + lines(
        topics, lambda t: f"- [{t.get('category')}] {t.get('name')}：{t.get('description','')}", limit=20))
    return "\n\n".join(parts)


PROMPT = """あなたは人気YouTubeチャンネル「ぷちぷち」の鬼ごっこ企画ブレーンです。
子ども〜ファミリー層に人気のMinecraftやRoblox実況・リアル鬼ごっこ系チャンネルという前提で、
下の最新トレンド情報をヒントに、新しい鬼ごっこ企画のネタを **8個** 考えてください。

条件:
- 各ネタは「今この時期に出すと伸びやすい」旬のもの（映画公開/金ロー放送/ゲーム発売/流行に便乗）
- 鬼ごっこ・かくれんぼ・逃走中・感染系など、追いかけっこ企画に落とし込むこと
- 実現しやすく、動画として絵になるもの
- score は 1〜5 のおすすめ度（旬・話題性・実現性の総合）

--- 最新トレンド情報 ---
{brief}
--- ここまで ---

出力は次のJSON配列のみ（前後に説明文やコードフェンスを付けない）:
[
  {{
    "title": "企画タイトル",
    "hook": "なぜ今これか（便乗する旬の理由）",
    "body": "ルールや見どころの説明（2〜3文）",
    "based_on": ["映画" or "金曜ロードショー" or "ゲーム" or "Minecraft" or "Roblox" or "ミーム" のうち該当するもの],
    "tags": ["感染鬼","かくれんぼ" など短いタグ2〜3個],
    "score": 1-5の整数
  }}
]
"""


def extract_json(text):
    text = text.strip()
    # コードフェンス除去
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("JSON配列が見つかりません:\n" + text[:500])
    return json.loads(text[start:end + 1])


def main():
    C.env("ANTHROPIC_API_KEY")  # 存在チェック
    from anthropic import Anthropic  # 遅延import（他スクリプトに影響させない）

    client = Anthropic()
    prompt = PROMPT.format(brief=brief())
    msg = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    ideas = extract_json(text)

    today = dt.date.today().isoformat()
    rows = []
    for i, it in enumerate(ideas, 1):
        rows.append({
            "id": f"idea-{today}-{i}",
            "title": it.get("title", ""),
            "hook": it.get("hook", ""),
            "body": it.get("body", ""),
            "based_on": it.get("based_on", []),
            "tags": it.get("tags", []),
            "score": int(it.get("score", 3)),
        })
    C.publish("ideas", "ideas", rows)


if __name__ == "__main__":
    main()
