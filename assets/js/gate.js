// 合言葉ロック（かんたんな閲覧制限）
// ※静的サイトのため“ソフトロック”です。一般の人の閲覧を防ぐ用途向け。
(function () {
  const cfg = window.ONIWORKS_CONFIG || {};
  const HASH = (cfg.PASS_HASH || "").trim().toLowerCase();
  const KEY = "oniworks_unlocked";
  if (!HASH) return; // ロック未設定 → 何もしない

  async function sha256(s) {
    // かな等でも一致するよう Unicode 正規化(NFC)してからハッシュ化
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s.normalize("NFC")));
    return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
  }

  // すでに解錠済み（同じ合言葉）なら通す
  try {
    if (localStorage.getItem(KEY) === HASH) return;
  } catch (e) { /* localStorage不可でも続行 */ }

  function build() {
    document.documentElement.style.overflow = "hidden";
    const ov = document.createElement("div");
    ov.id = "gate";
    ov.innerHTML = `
      <div class="gate-box">
        <div class="gate-mask">👹</div>
        <h1>オニ<b>Works</b></h1>
        <p class="gate-msg">合言葉を入力してください</p>
        <input id="gate-input" type="text" lang="ja" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" placeholder="合言葉（かな入力OK）" autofocus>
        <button id="gate-btn">入る</button>
        <p id="gate-err" class="gate-err" hidden>合言葉がちがいます</p>
      </div>`;
    document.body.appendChild(ov);

    const input = ov.querySelector("#gate-input");
    const err = ov.querySelector("#gate-err");
    const submit = async () => {
      const h = await sha256(input.value);
      if (h === HASH) {
        try { localStorage.setItem(KEY, HASH); } catch (e) {}
        document.documentElement.style.overflow = "";
        ov.remove();
      } else {
        err.hidden = false;
        input.value = "";
        input.focus();
      }
    };
    ov.querySelector("#gate-btn").addEventListener("click", submit);
    // IME変換中(かな変換の確定など)のEnterでは送信しない
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.isComposing && e.keyCode !== 229) submit();
    });
    input.focus();
  }

  if (document.body) build();
  else document.addEventListener("DOMContentLoaded", build);
})();
