"""全データ取得をまとめて実行する。

各ステップは独立して try/except で囲み、
1つが失敗しても他は動くようにしています（キー未設定はスキップ）。
"""
import os
import importlib
import traceback

# (モジュール名, 必要な環境変数 or None)
STEPS = [
    ("fetch_movies", "TMDB_API_KEY"),
    ("fetch_games", "RAWG_API_KEY"),
    ("fetch_minecraft", None),
    ("fetch_kinro", None),
    ("push_curated", None),
    ("generate_ideas", "ANTHROPIC_API_KEY"),  # 最後：他データを元に生成
]


def main():
    for mod_name, need in STEPS:
        if need and not os.environ.get(need):
            print(f"[SKIP] {mod_name}（{need} 未設定）")
            continue
        print(f"\n===== {mod_name} =====")
        try:
            mod = importlib.import_module(mod_name)
            mod.main()
        except Exception:
            print(f"[FAIL] {mod_name}")
            traceback.print_exc()


if __name__ == "__main__":
    main()
