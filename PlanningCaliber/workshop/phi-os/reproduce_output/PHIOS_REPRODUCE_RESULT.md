# PHIOS_REPRODUCE_RESULT.md

**PHI-OS v1.0.0 — Proof of Reproducibility**

- 実行日時: 2026-05-31 13:48:36
- 実行環境: Python 3.13.13

## 試験結果

| ID | 名称 | 結果 | 詳細 |
|----|------|------|------|
| P-S-01-a | SCHEMA_VERSION='1.0.0' in background.js | PASS | background.js に SCHEMA_VERSION='1.0.0' あり |
| P-S-01-b | KNOWN_PRODUCTS=['relay','orchestra','mem | PASS | KNOWN_PRODUCTS 確認  |
| P-S-01-c | ensureSchemaVersion() 関数定義あり | PASS | ensureSchemaVersion() 関数あり=True |
| P-S-01-d | registerProduct() 関数定義あり | PASS | registerProduct() 関数あり=True |
| P-S-02 | message: PHI_HEARTBEAT | PASS | 'PHI_HEARTBEAT' case あり=True |
| P-S-02 | message: PHI_COMMIT_DONE | PASS | 'PHI_COMMIT_DONE' case あり=True |
| P-S-02 | message: PHI_REGISTER_PRODUCT | PASS | 'PHI_REGISTER_PRODUCT' case あり=True |
| P-S-02 | message: PHI_OPEN_POPUP | PASS | 'PHI_OPEN_POPUP' case あり=True |
| P-S-02 | message: PHI_PANEL_MODE_CHANGED | PASS | 'PHI_PANEL_MODE_CHANGED' case あり=True |
| P-S-02 | message: PHI_GET_STATUS | PASS | 'PHI_GET_STATUS' case あり=True |
| P-S-02 | message: PHI_CLEAR_OLD_DATA | PASS | 'PHI_CLEAR_OLD_DATA' case あり=True |
| P-S-02-x | PHI_HEARTBEAT: ok:true,ts レスポンス | PASS | PHI_HEARTBEAT response ok:true あり=True |
| P-S-03 | storage key: phi_schema_version | PASS | 'phi_schema_version' キーあり=True |
| P-S-03 | storage key: phi_product_id_ | PASS | 'phi_product_id_' キーあり=True |
| P-S-03 | storage key: phi_commit_index | PASS | 'phi_commit_index' キーあり=True |
| P-S-03 | storage key: phi_last_commit_ts | PASS | 'phi_last_commit_ts' キーあり=True |
| P-S-03 | storage key: phi_panel_mode | PASS | 'phi_panel_mode' キーあり=True |
| P-S-03-x | 全ストレージキーがphi_プレフィックス | FAIL | 全ストレージキーがphi_プレフィックス (非phi_: ['{', '{', '{']) |
| P-S-04-a | PHI_I18N オブジェクト定義あり | PASS | PHI_I18N定数あり=True |
| P-S-04 | i18n: ja | PASS | 言語'ja'あり=True |
| P-S-04 | i18n: en | PASS | 言語'en'あり=True |
| P-S-04 | i18n: zh | PASS | 言語'zh'あり=True |
| P-S-04 | i18n: ko | PASS | 言語'ko'あり=True |
| P-S-04 | options.html lang-select: ja | PASS | options.html lang=ja あり=True |
| P-S-04 | options.html lang-select: en | PASS | options.html lang=en あり=True |
| P-S-04 | options.html lang-select: zh | PASS | options.html lang=zh あり=True |
| P-S-04 | options.html lang-select: ko | PASS | options.html lang=ko あり=True |
| P-S-04 | options.html lang-select: es | PASS | options.html lang=es あり=True |
| P-S-05-a | Manifest Version = 3 | PASS | MV=3 |
| P-S-05-b | name に 'PHI' を含む | PASS | name='PHI OS' |
| P-S-05-c | 必須パーミッション (storage/tabs/sidePanel) | PASS | permissions={'sidePanel', 'storage', 'tabs'} |
| P-S-05-d | claude.ai host_permission | PASS | claude.ai host_permission=True |
| P-S-05-e | service_worker = background.js | PASS | service_worker=background.js |
| P-S-05-f | side_panel.default_path = ui/sidepanel.h | PASS | side_panel.default_path=ui/sidepanel.html |
| P-S-05-g | action.default_popup = ui/options.html | PASS | action.default_popup=ui/options.html |
| P-S-06 | 存在: background.js | PASS | background.js あり |
| P-S-06 | 存在: content.js | PASS | content.js あり |
| P-S-06 | 存在: manifest.json | PASS | manifest.json あり |
| P-S-06 | 存在: ui/options.html | PASS | ui/options.html あり |
| P-S-06 | 存在: ui/sidepanel.html | PASS | ui/sidepanel.html あり |
| P-S-06 | 存在: ui/options.css | PASS | ui/options.css あり |
| P-S-06 | 存在: ui/options.js | PASS | ui/options.js あり |
| P-S-06 | 存在: core/state-store.js | PASS | core/state-store.js あり |
| P-S-06 | 存在: core/commit-engine.js | PASS | core/commit-engine.js あり |
| P-S-06 | 存在: core/restore-engine.js | PASS | core/restore-engine.js あり |
| P-S-06 | 存在: core/event-bus.js | PASS | core/event-bus.js あり |
| P-S-06 | 存在: core/i18n.js | PASS | core/i18n.js あり |
| P-S-06 | 存在: adapters/relay-adapter.js | PASS | adapters/relay-adapter.js あり |
| P-S-06 | 存在: adapters/orchestra-adapter.js | PASS | adapters/orchestra-adapter.js あり |
| P-S-06 | 存在: adapters/memory-adapter.js | PASS | adapters/memory-adapter.js あり |
| P-S-06 | 存在: debug/health-check.js | PASS | debug/health-check.js あり |
| P-S-07 | 構文: background.js | PASS | 構文エラーなし |
| P-S-07 | 構文: content.js | PASS | 構文エラーなし |
| P-S-08 | 構文: core/auto-trigger.js | FAIL | (node:15952) Warning: Failed to load the ES module: C:\Users |
| P-S-08 | 構文: core/commit-engine.js | FAIL | (node:16840) Warning: Failed to load the ES module: C:\Users |
| P-S-08 | 構文: core/event-bus.js | FAIL | (node:19952) Warning: Failed to load the ES module: C:\Users |
| P-S-08 | 構文: core/i18n.js | FAIL | (node:6176) Warning: Failed to load the ES module: C:\Users\ |
| P-S-08 | 構文: core/permission-manager.js | FAIL | (node:19404) Warning: Failed to load the ES module: C:\Users |
| P-S-08 | 構文: core/restore-engine.js | FAIL | (node:3560) Warning: Failed to load the ES module: C:\Users\ |
| P-S-08 | 構文: core/schema-registry.js | FAIL | (node:2920) Warning: Failed to load the ES module: C:\Users\ |
| P-S-08 | 構文: core/state-store.js | FAIL | (node:18532) Warning: Failed to load the ES module: C:\Users |
| P-S-09 | 構文: adapters/memory-adapter.js | FAIL | (node:6060) Warning: Failed to load the ES module: C:\Users\ |
| P-S-09 | 構文: adapters/orchestra-adapter.js | FAIL | (node:2856) Warning: Failed to load the ES module: C:\Users\ |
| P-S-09 | 構文: adapters/phi-adapter.js | FAIL | (node:20804) Warning: Failed to load the ES module: C:\Users |
| P-S-09 | 構文: adapters/relay-adapter.js | FAIL | (node:3268) Warning: Failed to load the ES module: C:\Users\ |
| P-S-10 | 構文: debug/debug-panel.js | FAIL | (node:7236) Warning: Failed to load the ES module: C:\Users\ |
| P-S-10 | 構文: debug/error-reporter.js | FAIL | (node:7504) Warning: Failed to load the ES module: C:\Users\ |
| P-S-10 | 構文: debug/health-check.js | FAIL | (node:21412) Warning: Failed to load the ES module: C:\Users |
| P-S-10 | 構文: ui/options.js | FAIL | (node:20792) Warning: Failed to load the ES module: C:\Users |
| P-S-10 | 構文: ui/panel-switch.js | FAIL | (node:18660) Warning: Failed to load the ES module: C:\Users |
| P-S-11-a | storage set/get ラウンドトリップ | PASS | got="phi_os_2026" |
| P-S-11-b | phi_schema_version の読み書き | PASS | got=1.0.0 |
| P-S-11-c | phi_commit_index 配列の永続化 | PASS | got=["commit_001","commit_002"] |
| P-S-11-d | storage.remove() 削除確認 | PASS | after remove=undefined |
| P-S-12-a | PHI_HEARTBEAT → ok:true,ts | PASS | ok=true ts=1780202911466 |
| P-S-12-b | PHI_GET_STATUS → commit_count,last_commi | PASS | commit_count=2 last_ts=null |
| P-S-12-c | PHI_REGISTER_PRODUCT → ok:true | PASS | ok=true |
| P-S-12-d | PHI_PANEL_MODE_CHANGED (sidepanel) → ok: | PASS | ok=true |
| P-S-12-e | PHI_PANEL_MODE_CHANGED (popup) → ok:true | PASS | ok=true |
| P-S-12-f | PHI_CLEAR_OLD_DATA → ok:true,deleted | PASS | ok=true deleted=0 |
| P-S-12-g | 不明typeはerrorを返す | PASS | res={"error":"Unknown type: PHI_UNKNOWN_9999"} |
| P-S-13-a | ui/options.html ロード成功 | PASS | URL starts with chrome-extension://bieancjajjieckhmgkmcpigpa |
| P-S-13-b | PHI-OS ダッシュボード必須要素確認 | PASS | 全要素あり |
| P-S-13-c | lang-select: 5言語オプション (ja/en/zh/ko/es) | PASS | options=["ja","en","zh","ko","es"] missing=[] |
| P-S-13-d | PHI-OS ロゴ/ヘッダー存在確認 | PASS | PHI OS ヘッダーあり=true |
| P-S-14-a | ui/sidepanel.html ロード成功 | PASS | URL=true |
| P-S-14-b | sidepanel: body要素あり | PASS | body.innerHTML.length=981 |
| P-S-14-c | sidepanel: スクリプトまたはリンクあり | PASS | script/link count=1 |
| P-S-15 | SW関数: ensureSchemaVersion() | PASS | ensureSchemaVersion typeof=function |
| P-S-15 | SW関数: registerProduct() | PASS | registerProduct typeof=function |
| P-S-15 | SW関数: handleMessage() | PASS | handleMessage typeof=function |
| P-S-15-d | SCHEMA_VERSION = "1.0.0" | PASS | SCHEMA_VERSION=1.0.0 |
| P-S-15-e | KNOWN_PRODUCTS 配列長 = 3 | PASS | KNOWN_PRODUCTS.length=3 |
| P-S-15-f | KNOWN_PRODUCTS に 'relay' 含む | PASS | includes('relay')=true |
| P-S-16-a | phi_schema_version: 拡張起動後に設定済み | PASS | phi_schema_version=1.0.0 |
| P-S-16-b | PHI_GET_STATUS: commit_count は数値 | PASS | commit_count=2 |
| P-S-16-c | phi_product_id_relay 登録後に読み取り可能 | PASS | phi_product_id_relay=e2e_relay_id |

## サマリー

| 項目 | 値 |
|-----|---|
| PASS | 79 |
| FAIL | 18 |
| SKIP | 0 |
| TOTAL | 97 |
| 実行時間 | 19.23s |

## 証明レベル

| レベル | 達成 |
|-------|-----|
| L1 | ✅ |
| L2 | ✅ |
| L3 | ❌ |
| L4 | ❌ |

## Reproduction Hash

```
sha256:8822ed9d250ed1c12b598a2eeed752223ed93f6124d4b91d5a256c90b070a1a0
```
