// オニWorks 設定ファイル
// ------------------------------------------------------------
// Supabase を使う場合はここに URL と anon キーを入れてください。
// 空のままなら data/*.json のローカルサンプルで動きます。
// （anon キーは公開用の読み取り専用キー。フロントに置いてOKです）
window.ONIWORKS_CONFIG = {
  SUPABASE_URL: "",       // 例: https://xxxxxxxx.supabase.co
  SUPABASE_ANON_KEY: "",  // 例: eyJhbGciOi...
  // 表示する期間（今日から前後 何日ぶんを対象にするか）
  RANGE_DAYS_BACK: 100,
  RANGE_DAYS_FORWARD: 150
};
