// データ取得レイヤー
// Supabase 設定があれば Supabase から、無ければ data/*.json から読み込む。
(function () {
  const cfg = window.ONIWORKS_CONFIG || {};
  const useSupabase = !!(cfg.SUPABASE_URL && cfg.SUPABASE_ANON_KEY);

  // Supabase テーブル名 -> ローカルJSONファイルの対応
  const SOURCES = {
    movies: { table: "movies", file: "data/movies.json" },
    kinro: { table: "kinro", file: "data/kinro.json" },
    games: { table: "games", file: "data/games.json" },
    topics: { table: "topics", file: "data/topics.json" },
    youtube: { table: "youtube", file: "data/youtube.json" },
    ideas: { table: "ideas", file: "data/ideas.json" }
  };

  async function fetchLocal(file) {
    const res = await fetch(file, { cache: "no-store" });
    if (!res.ok) throw new Error(`読み込み失敗: ${file}`);
    const json = await res.json();
    return { items: json.items || [], updated_at: json.updated_at || null };
  }

  async function fetchSupabase(table) {
    const url = `${cfg.SUPABASE_URL}/rest/v1/${table}?select=*`;
    const res = await fetch(url, {
      headers: {
        apikey: cfg.SUPABASE_ANON_KEY,
        Authorization: `Bearer ${cfg.SUPABASE_ANON_KEY}`
      }
    });
    if (!res.ok) throw new Error(`Supabase取得失敗: ${table} (${res.status})`);
    const rows = await res.json();
    return { items: rows, updated_at: null };
  }

  window.OniData = {
    useSupabase,
    async load(key) {
      const src = SOURCES[key];
      if (!src) throw new Error("不明なデータ: " + key);
      try {
        return useSupabase ? await fetchSupabase(src.table) : await fetchLocal(src.file);
      } catch (e) {
        // Supabase 失敗時はローカルへフォールバック
        if (useSupabase) {
          console.warn("Supabase失敗、ローカルに切替:", e);
          return await fetchLocal(src.file);
        }
        throw e;
      }
    }
  };
})();
