// MoCKA Gateway — クライアント設定
// Phase1: localhost:5010 / Phase2以降: Cloudflare Workers URL

const MOCKA_CONFIG = {
  BASE_URL:   "https://mocka-api.nsjpkimura-mocka.workers.dev",
  API_KEY:    "OPR-XXXXXXXX",   // X-MoCKA-Key ヘッダー値
  MODE:       "compact",         // Orchestra注入用: compact / standard / extended
  TIMEOUT_MS: 5000,
};

// フリーズして外部から書き換え不可にする
Object.freeze(MOCKA_CONFIG);
