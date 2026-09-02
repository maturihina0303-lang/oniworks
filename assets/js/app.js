// オニWorks メインロジック
(function () {
  const cfg = window.ONIWORKS_CONFIG || {};
  const TODAY = new Date();
  const store = {}; // key -> {items, updated_at}

  // ---------- ユーティリティ ----------
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const parseDate = (s) => (s ? new Date(s + "T00:00:00") : null);
  const daysFromToday = (s) => {
    const d = parseDate(s);
    if (!d) return null;
    return Math.round((d - TODAY) / 86400000);
  };
  const fmtDate = (s) => {
    const d = parseDate(s);
    if (!d) return "日付未定";
    const w = ["日", "月", "火", "水", "木", "金", "土"][d.getDay()];
    return `${d.getMonth() + 1}/${d.getDate()}(${w})`;
  };
  const relLabel = (s) => {
    const n = daysFromToday(s);
    if (n === null) return "";
    if (n === 0) return "今日";
    if (n > 0) return `あと${n}日`;
    return `${-n}日前`;
  };
  const inRange = (s) => {
    const n = daysFromToday(s);
    if (n === null) return true;
    return n >= -(cfg.RANGE_DAYS_BACK ?? 100) && n <= (cfg.RANGE_DAYS_FORWARD ?? 100);
  };

  // ---------- レンダリング部品 ----------
  function badge(text, cls = "") {
    return `<span class="badge ${cls}">${esc(text)}</span>`;
  }
  function chipList(arr, cls = "") {
    if (!arr || !arr.length) return "";
    return arr.map((x) => `<span class="chip ${cls}">${esc(x)}</span>`).join("");
  }
  function scoreStars(n) {
    n = Number(n) || 0;
    return "★".repeat(n) + "☆".repeat(Math.max(0, 5 - n));
  }
  function emptyMsg(text) {
    return `<div class="empty">${esc(text)}</div>`;
  }
  function thumb(url, cls = "") {
    return url ? `<img class="thumb ${cls}" src="${esc(url)}" alt="" loading="lazy" onerror="this.remove()">` : "";
  }
  function monthsOf(items, field) {
    return [...new Set(items.filter((x) => inRange(x[field]))
      .map((x) => String(x[field] || "").slice(0, 7)).filter(Boolean))].sort();
  }
  function monthSelect(id, items, field) {
    const opts = ['<option value="all">すべての月</option>'].concat(
      monthsOf(items, field).map((m) => {
        const [y, mo] = m.split("-");
        return `<option value="${m}">${y}年${+mo}月</option>`;
      })).join("");
    return `<select class="month-sel" id="${id}">${opts}</select>`;
  }
  const matchMonth = (val, month) => month === "all" || String(val || "").startsWith(month);

  // ---------- 各セクション ----------
  function renderIdeas(mount) {
    const items = (store.ideas?.items || []).slice().sort((a, b) => (b.score || 0) - (a.score || 0));
    if (!items.length) return (mount.innerHTML = emptyMsg("まだネタがありません。"));
    mount.innerHTML = items.map((it) => `
      <article class="card idea">
        <div class="idea-head">
          <h3>${esc(it.title)}</h3>
          <div class="stars" title="おすすめ度">${scoreStars(it.score)}</div>
        </div>
        <p class="hook">${esc(it.hook || "")}</p>
        <p class="body">${esc(it.body || "")}</p>
        <div class="chips">${chipList(it.tags, "tag")}${chipList(it.based_on, "src")}</div>
      </article>`).join("");
  }

  function renderMovies(mount, status, month) {
    let items = (store.movies?.items || []).filter((x) => inRange(x.release_date));
    if (status && status !== "all") items = items.filter((x) => x.status === status);
    if (month) items = items.filter((x) => matchMonth(x.release_date, month));
    items.sort((a, b) => (parseDate(a.release_date) || 0) - (parseDate(b.release_date) || 0));
    if (!items.length) return (mount.innerHTML = emptyMsg("該当する映画がありません。"));
    mount.innerHTML = items.map((it) => `
      <article class="card row">
        <div class="date-col">
          <div class="d">${fmtDate(it.release_date)}</div>
          <div class="rel">${relLabel(it.release_date)}</div>
        </div>
        ${thumb(it.poster, "tall")}
        <div class="main-col">
          <div class="title-line">
            <h3>${esc(it.title)}</h3>
            ${it.status === "now" ? badge("公開中", "now") : badge("公開予定", "soon")}
          </div>
          <div class="chips">${chipList(it.genre, "genre")}</div>
          <p class="overview">${esc(it.overview || "")}</p>
        </div>
      </article>`).join("");
  }

  function renderKinro(mount, month) {
    let items = (store.kinro?.items || []).filter((x) => inRange(x.air_date));
    if (month) items = items.filter((x) => matchMonth(x.air_date, month));
    items.sort((a, b) => (parseDate(a.air_date) || 0) - (parseDate(b.air_date) || 0));
    if (!items.length) return (mount.innerHTML = emptyMsg("放送予定がありません。"));
    mount.innerHTML = items.map((it) => {
      const past = (daysFromToday(it.air_date) ?? 0) < 0;
      return `
      <article class="card row ${past ? "past" : ""}">
        <div class="date-col">
          <div class="d">${fmtDate(it.air_date)}</div>
          <div class="rel">${relLabel(it.air_date)}</div>
        </div>
        ${thumb(it.image, "tall")}
        <div class="main-col">
          <div class="title-line"><h3>${esc(it.title)}</h3>${it.note ? badge(it.note) : ""}</div>
        </div>
      </article>`;
    }).join("");
  }

  function renderGames(mount, month) {
    let items = (store.games?.items || []).filter((x) => inRange(x.release_date));
    if (month) items = items.filter((x) => matchMonth(x.release_date, month));
    items.sort((a, b) => (parseDate(a.release_date) || 0) - (parseDate(b.release_date) || 0));
    if (!items.length) return (mount.innerHTML = emptyMsg("該当するゲームがありません。"));
    mount.innerHTML = items.map((it) => `
      <article class="card row">
        <div class="date-col">
          <div class="d">${fmtDate(it.release_date)}</div>
          <div class="rel">${relLabel(it.release_date)}</div>
        </div>
        ${thumb(it.image)}
        <div class="main-col">
          <div class="title-line"><h3>${esc(it.title)}</h3>${it.price ? badge(it.price, "metric") : ""}</div>
          <div class="chips">${chipList(it.platforms, "platform")}${chipList(it.genre, "genre")}</div>
        </div>
      </article>`).join("");
  }

  function renderTopics(mount, category) {
    let items = (store.topics?.items || []).filter((x) => x.category === category);
    items.sort((a, b) => (parseDate(b.updated) || 0) - (parseDate(a.updated) || 0));
    if (!items.length) return (mount.innerHTML = emptyMsg("トピックがありません。"));
    mount.innerHTML = items.map((it) => `
      <article class="card topic">
        ${thumb(it.image)}
        <div class="tcontent">
          <div class="title-line">
            <h3>${it.url ? `<a href="${esc(it.url)}" target="_blank" rel="noopener">${esc(it.name)}</a>` : esc(it.name)}</h3>
            ${it.type ? badge(it.type) : ""}
          </div>
          <div class="meta">${it.metric ? badge(it.metric, "metric") : ""}${it.updated ? `<span class="upd">更新 ${fmtDate(it.updated)}</span>` : ""}</div>
          <p class="body">${esc(it.description || "")}</p>
        </div>
      </article>`).join("");
  }

  function renderYoutube(mount) {
    const items = (store.youtube?.items || []);
    if (!items.length) return (mount.innerHTML = emptyMsg("動画がありません。"));
    mount.innerHTML = items.map((it) => `
      <a class="card yt" href="${esc(it.url)}" target="_blank" rel="noopener">
        ${it.thumbnail ? `<img class="ytthumb" src="${esc(it.thumbnail)}" alt="" loading="lazy" onerror="this.remove()">` : `<div class="ytthumb"></div>`}
        <div class="ytbody">
          <h3>${esc(it.title)}</h3>
          <div class="ytmeta">${esc(it.channel || "")}${it.views ? ` ・ ${esc(it.views)}再生` : ""}</div>
        </div>
      </a>`).join("");
  }

  // ---------- ルーティング ----------
  const VIEWS = {
    home: (mount) => {
      mount.innerHTML = `<div class="section-head"><h2>🔥 今週のおすすめ鬼ごっこネタ</h2><p class="sub">最新の映画・ゲーム・トレンドから自動生成した企画案</p></div><div id="ideas-list" class="grid"></div>`;
      renderIdeas($("#ideas-list", mount));
    },
    movies: (mount) => {
      const movies = store.movies?.items || [];
      mount.innerHTML = `
        <div class="section-head"><h2>🎬 公開中・公開予定の映画</h2><p class="sub">追いかけっこ・逃走系の元ネタ探しに</p></div>
        <div class="controls">
          <div class="tabs" data-tabs="movies">
            <button class="tab active" data-f="all">すべて</button>
            <button class="tab" data-f="now">公開中</button>
            <button class="tab" data-f="upcoming">公開予定</button>
          </div>
          ${monthSelect("movies-month", movies, "release_date")}
        </div>
        <div id="movies-list" class="list"></div>`;
      const state = { status: "all", month: "all" };
      const draw = () => renderMovies($("#movies-list", mount), state.status, state.month);
      draw();
      $$('[data-tabs="movies"] .tab', mount).forEach((b) =>
        b.addEventListener("click", () => {
          $$('[data-tabs="movies"] .tab', mount).forEach((x) => x.classList.remove("active"));
          b.classList.add("active");
          state.status = b.dataset.f;
          draw();
        }));
      $("#movies-month", mount).addEventListener("change", (e) => { state.month = e.target.value; draw(); });
    },
    kinro: (mount) => {
      const items = store.kinro?.items || [];
      mount.innerHTML = `<div class="section-head"><h2>📺 金曜ロードショー 放送予定</h2><p class="sub">放送日に合わせた投稿でバズを狙う</p></div>
        <div class="controls">${monthSelect("kinro-month", items, "air_date")}</div>
        <div id="kinro-list" class="list"></div>`;
      renderKinro($("#kinro-list", mount), "all");
      $("#kinro-month", mount).addEventListener("change", (e) => renderKinro($("#kinro-list", mount), e.target.value));
    },
    games: (mount) => {
      const items = store.games?.items || [];
      mount.innerHTML = `<div class="section-head"><h2>🎮 ゲーム発売日</h2><p class="sub">話題のゲームに便乗した企画に</p></div>
        <div class="controls">${monthSelect("games-month", items, "release_date")}</div>
        <div id="games-list" class="list"></div>`;
      renderGames($("#games-list", mount), "all");
      $("#games-month", mount).addEventListener("change", (e) => renderGames($("#games-list", mount), e.target.value));
    },
    minecraft: (mount) => {
      mount.innerHTML = `<div class="section-head"><h2>⛏️ Minecraft トレンド</h2><p class="sub">流行りのMOD・キャラでステージ作り</p></div><div id="mc-list" class="grid"></div>`;
      renderTopics($("#mc-list", mount), "minecraft");
    },
    roblox: (mount) => {
      mount.innerHTML = `<div class="section-head"><h2>🟦 Roblox トレンド</h2><p class="sub">人気ゲーム・キャラを鬼ごっこに翻訳</p></div><div id="rb-list" class="grid"></div>`;
      renderTopics($("#rb-list", mount), "roblox");
    },
    meme: (mount) => {
      mount.innerHTML = `<div class="section-head"><h2>😂 ネットミーム</h2><p class="sub">鬼役の見た目・効果音・演出ネタに</p></div><div id="mm-list" class="grid"></div>`;
      renderTopics($("#mm-list", mount), "meme");
    },
    youtube: (mount) => {
      mount.innerHTML = `<div class="section-head"><h2>📹 YouTube ゲーム急上昇</h2><p class="sub">日本で今バズっているゲーム動画。企画のヒントに</p></div><div id="yt-list" class="ytgrid"></div>`;
      renderYoutube($("#yt-list", mount));
    }
  };

  function go(view) {
    const mount = $("#view");
    (VIEWS[view] || VIEWS.home)(mount);
    $$(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.view === view));
    location.hash = view;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // ---------- 起動 ----------
  async function boot() {
    const status = $("#status");
    try {
      const keys = ["ideas", "movies", "kinro", "games", "topics", "youtube"];
      const results = await Promise.all(keys.map((k) => window.OniData.load(k)));
      keys.forEach((k, i) => (store[k] = results[i]));
      const src = window.OniData.useSupabase ? "Supabase(自動更新)" : "毎日自動更新";
      status.textContent = src;
    } catch (e) {
      status.textContent = "データ読み込みエラー: " + e.message;
      console.error(e);
    }
    $$(".nav-item").forEach((b) => b.addEventListener("click", () => go(b.dataset.view)));
    window.addEventListener("hashchange", () => go((location.hash || "#home").slice(1)));
    go((location.hash || "#home").slice(1));
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
