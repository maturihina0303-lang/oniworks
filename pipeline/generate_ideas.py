"""集めたデータから鬼ごっこ企画ネタを自動生成する（AI不使用・費用ゼロ）。

映画/金曜ロードショー/ゲーム/Minecraft/Roblox/ミームの実データを、
鬼ごっこ企画のテンプレに当てはめてネタを作ります。
"""
import datetime as dt
import common as C

TODAY = C.TODAY


def days_from_today(s):
    try:
        return (dt.date.fromisoformat(s) - TODAY).days
    except Exception:
        return None


def fmt_md(s):
    try:
        d = dt.date.fromisoformat(s)
        w = "月火水木金土日"[d.weekday()]
        return f"{d.month}/{d.day}({w})"
    except Exception:
        return s


# --- 映画のジャンルから鬼ごっこルールを決める（複数候補を返す） ---
RULES = {
    "感染鬼": "鬼に捕まったら仲間になって鬼が増えていく『感染ルール』。最後の1人まで逃げ切れるか！？",
    "ケイドロ": "警察 vs 泥棒の全力逃走。捕まったら牢屋、仲間がタッチで救出できる王道ルール。",
    "能力者鬼": "鬼だけが使える特殊能力（ワープ・透明化など）を設定してSF風に。",
    "なりきり鬼": "作品のキャラになりきって鬼ごっこ。コスプレや小道具で盛り上げよう。",
    "かくれんぼ": "作品の舞台をイメージした隠れんぼ。制限時間で見つけ合うドキドキ企画。",
    "増え鬼": "捕まったら鬼が増えていく王道の増え鬼。だんだん逃げ場がなくなるスリル。",
}


def movie_rule_candidates(genres):
    g = set(genres or [])
    order = []
    if g & {"ホラー", "スリラー", "謎", "ミステリー"}:
        order += ["感染鬼", "かくれんぼ"]
    if g & {"アクション", "戦争", "犯罪"}:
        order += ["ケイドロ", "能力者鬼"]
    if g & {"サイエンスフィクション"}:
        order += ["能力者鬼"]
    if g & {"アニメーション", "ファミリー", "コメディ", "ファンタジー", "音楽", "ロマンス"}:
        order += ["なりきり鬼", "かくれんぼ"]
    order += ["増え鬼", "なりきり鬼", "ケイドロ"]  # 予備
    # 重複を除いて順序維持
    seen, out = set(), []
    for r in order:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def idea(title, hook, body, based_on, tags, score):
    return {"title": title, "hook": hook, "body": body,
            "based_on": based_on, "tags": tags, "score": int(score)}


def from_kinro(rows):
    out = []
    for k in sorted(rows, key=lambda r: r.get("air_date", "")):
        n = days_from_today(k.get("air_date", ""))
        if n is None or n < -3 or n > 45:
            continue
        t = k.get("title", "")
        out.append(idea(
            f"金ロー『{t}』放送記念 かくれんぼ",
            f"{fmt_md(k.get('air_date'))} の金曜ロードショー放送に合わせて",
            f"『{t}』の放送日に合わせて投稿すると検索・話題で伸びやすい。作品の世界観でかくれんぼ or 鬼ごっこに。",
            ["金曜ロードショー"], ["季節ネタ", "かくれんぼ"], 5))
    return out[:2]


def from_movies(rows):
    out = []
    rows = [m for m in rows if days_from_today(m.get("release_date", "")) is not None]
    rows.sort(key=lambda m: -(m.get("popularity") or 0))
    used = {}  # ルールが偏らないよう使用回数を記録
    for m in rows[:8]:
        if len(out) >= 3:
            break
        cands = movie_rule_candidates(m.get("genre"))
        rule = min(cands, key=lambda r: used.get(r, 0))  # まだ使ってないルール優先
        used[rule] = used.get(rule, 0) + 1
        soon = m.get("status") == "upcoming"
        out.append(idea(
            f"映画『{m.get('title')}』便乗 {rule}",
            ("公開予定の話題作に先回りして" if soon else "公開中の話題作に便乗して"),
            RULES[rule],
            ["映画"], [rule, (m.get("genre") or ["話題作"])[0]],
            5 if (m.get("popularity") or 0) > 100 else 4))
    return out


def from_games(rows):
    out = []
    up = [g for g in rows if (days_from_today(g.get("release_date", "")) or -999) >= 0]
    up.sort(key=lambda g: days_from_today(g.get("release_date", "")))
    for g in up[:4]:
        plat = "/".join(g.get("platforms", []) or [])
        out.append(idea(
            f"『{g.get('title')}』発売記念 なりきり鬼ごっこ",
            f"{fmt_md(g.get('release_date'))} 発売の新作ゲームに便乗",
            f"話題の新作（{plat}）のキャラ・世界観でリアル鬼ごっこ。発売日に合わせて投稿すると伸びやすい。",
            ["ゲーム"], ["新作便乗", "なりきり鬼"], 4))
    return out[:2]


def from_topics(rows):
    out = []
    mc = [t for t in rows if t.get("category") == "minecraft"]
    for t in mc[:3]:
        out.append(idea(
            f"マイクラ『{t.get('name')}』で鬼ごっこ",
            "Minecraftで流行中のMODを使って",
            f"{t.get('description','')} … このMODを鬼役や逃走ステージに使うと本格的な鬼ごっこに。",
            ["Minecraft"], ["マイクラ", "MOD活用"], 4))
    for cat, label in (("roblox", "Roblox"), ("meme", "ミーム")):
        items = [t for t in rows if t.get("category") == cat]
        if items:
            t = items[0]
            out.append(idea(
                f"『{t.get('name')}』ごっこ鬼ごっこ",
                f"{label}で話題のネタに便乗",
                f"{t.get('description','')} … 見た目や設定を鬼ごっこに取り入れて話題性アップ。",
                [label], [label, "トレンド"], 3))
    return out


def main():
    movies = C.read_current("movies")
    kinro = C.read_current("kinro")
    games = C.read_current("games")
    topics = C.read_current("topics")

    ideas = from_kinro(kinro) + from_movies(movies) + from_games(games) + from_topics(topics)
    ideas.sort(key=lambda x: -x["score"])

    today = TODAY.isoformat()
    rows = []
    for i, it in enumerate(ideas, 1):
        it = dict(it)
        it["id"] = f"idea-{today}-{i}"
        rows.append(it)
    C.publish("ideas", "ideas", rows)


if __name__ == "__main__":
    main()
