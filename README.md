# オニWorks 👹

ぷちぷちチャンネルの**鬼ごっこ企画ネタ**を、映画・金曜ロードショー・ゲーム・Minecraft・Roblox・ネットミームのトレンドから自動収集し、AIが企画案を提案するサイトです。

- 情報はすべて **前後3ヶ月ぶん** を表示
- **GitHub Pages** で公開し、**GitHub Actions** が毎日自動でデータを更新します

---

## 📦 構成

```
オニWorks/
├─ index.html              サイト本体（GitHub Pagesで公開）
├─ assets/                 デザイン(css)・動作(js)
│   └─ js/config.js        ★ Supabase接続設定を書く場所
├─ data/*.json             データ（Supabase未設定でもこれで動く）
├─ curated/                Roblox・ミームの手動編集ファイル
├─ pipeline/*.py           データ取得スクリプト（GitHub Actionsが実行）
├─ supabase/schema.sql     DBテーブル定義
└─ .github/workflows/      毎日自動更新の設定
```

## データソース一覧

| セクション | 取得元 | 自動/手動 | 必要なキー |
|---|---|---|---|
| 映画（公開中/公開予定） | TMDB API（日本・日本語） | 自動 | `TMDB_API_KEY` |
| 金曜ロードショー | kinro.ntv.co.jp | 自動（スクレイピング） | 不要 |
| ゲーム発売日 | ファミ通（日本の発売日・日本語） | 自動（スクレイピング） | 不要 |
| Minecraft | Modrinth API | 自動 | 不要 |
| Roblox | `curated/roblox.json` | 手動編集 | 不要 |
| ネットミーム | `curated/meme.json` | 手動編集 | 不要 |
| おすすめネタ | Claude (AI) | 自動生成 | `ANTHROPIC_API_KEY` |

> キーが未設定の項目は自動でスキップされるので、**まずキー無しでも動きます**（映画・ゲーム・AIネタが空になるだけ）。

---

## 🖥 まずローカルで見る

Pythonの簡易サーバーで開きます（`file://` だと動きません）。

```bash
cd 作業場
py -3 -m http.server 8765
```

ブラウザで `http://127.0.0.1:8765/` を開く。

データを手元で更新したいとき（キー不要の分だけ）:

```bash
cd pipeline
py -3 fetch_kinro.py       # 金曜ロードショー
py -3 fetch_minecraft.py   # Minecraft
py -3 push_curated.py      # Roblox・ミーム（curated/を編集後）
```

---

## 🚀 本番公開の手順

> アカウント作成（GitHub / Supabase）はご自身で行ってください。

### 1. GitHubに置いて Pages で公開

1. GitHubで新しいリポジトリを作成（例 `oniworks`）。
2. この `作業場` フォルダの中身をpush。
   ```bash
   cd 作業場
   git init
   git add .
   git commit -m "first"
   git branch -M main
   git remote add origin https://github.com/<あなた>/oniworks.git
   git push -u origin main
   ```
3. リポジトリの **Settings → Pages** で、Source を `main` ブランチ `/ (root)` に設定 → 数分で `https://<あなた>.github.io/oniworks/` が公開されます。

### 2. Supabase をセットアップ

1. [supabase.com](https://supabase.com) でプロジェクトを新規作成。
2. 左メニュー **SQL Editor** に `supabase/schema.sql` の中身を貼り付けて **Run**（テーブルが作られます）。
3. **Settings → API** で以下2つを控える:
   - **Project URL**（例 `https://xxxx.supabase.co`）
   - **anon public** キー（閲覧用・公開OK）
   - **service_role** キー（書き込み用・**秘密**。GitHubにのみ登録）

### 3. フロントにSupabaseを接続

`assets/js/config.js` を編集:

```js
window.ONIWORKS_CONFIG = {
  SUPABASE_URL: "https://xxxx.supabase.co",
  SUPABASE_ANON_KEY: "eyJhbGciOi...(anon public キー)",
  ...
};
```
編集してpushすると、サイトはSupabaseから読むようになります。

### 4. APIキーを取得（無料）

- **TMDB**（映画）: [themoviedb.org](https://www.themoviedb.org) 登録 → Settings → API → APIキー(v3)
- **Anthropic**（AIネタ生成）: [console.anthropic.com](https://console.anthropic.com) → API Keys
- ゲーム（ファミ通）はキー不要です。

### 5. GitHub Secrets に登録

リポジトリの **Settings → Secrets and variables → Actions → New repository secret** で登録:

| 名前 | 値 |
|---|---|
| `TMDB_API_KEY` | TMDBキー（映画） |
| `ANTHROPIC_API_KEY` | Anthropicキー（AIネタ・任意） |
| `SUPABASE_URL` | （Supabaseを使う場合のみ）Project URL |
| `SUPABASE_SERVICE_KEY` | （Supabaseを使う場合のみ）service_role キー |

### 6. 自動更新を実行

- **Actions** タブ →「オニWorks データ自動更新」→ **Run workflow** で手動実行して動作確認。
- 以降は毎日 **朝7時（日本時間）** に自動でデータが更新されます。

---

## ✏️ Roblox・ミームの更新（手動）

信頼できる自動取得APIが無いため、この2つは手動です。

1. `curated/roblox.json` / `curated/meme.json` を編集（流行のキャラ/ゲームを追記）。
2. push すると、次の自動更新時に反映されます。すぐ反映したい場合はローカルで:
   ```bash
   cd pipeline && py -3 push_curated.py   # Supabaseに直接反映
   ```

> 💡 流行の調べ方に迷ったら、Claudeに「今Robloxで流行っている鬼ごっこ系ゲーム/キャラを教えて」と聞いて `curated/*.json` に書き足すのが楽です。

---

## ⚙️ カスタマイズ

- **表示期間**: `assets/js/config.js` の `RANGE_DAYS_BACK` / `RANGE_DAYS_FORWARD`（日数）。
- **更新時刻**: `.github/workflows/update-data.yml` の `cron`（UTC表記）。
- **AIネタの個数・方向性**: `pipeline/generate_ideas.py` の `PROMPT` を編集。
- **Minecraftの検索テーマ**: `pipeline/fetch_minecraft.py` の `QUERIES`。

---

## 🛠 メンテナンス上の注意

- **金曜ロードショー**は公式サイトのHTMLを解析しています。サイトの作りが変わると取得できなくなるので、その時は `pipeline/fetch_kinro.py` の正規表現を調整してください（取得0件のときは警告が出ます）。
- データは毎回まるごと入れ替える方式なので、古い情報は自動的に消えます。
