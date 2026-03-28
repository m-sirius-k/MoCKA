import json

ecosystem = {
    "meta": {
        "generated": "2026-03-28",
        "generator": "Claude Sonnet - session investigation",
        "purpose": "MoCKA ecosystem complete mapping for AI context restoration",
        "version": "2.0"
    },
    "constitution": {
        "source": "mocka-joints/mocka-infield/identity/mocka_constitution.md",
        "principles": [
            "Event ledger is append only",
            "All decisions preserve 5W1H",
            "Infield is internal memory",
            "Outfield is collaborative interface",
            "Event history is the single source of truth"
        ]
    },
    "ai_roster": {
        "source": "mocka-joints/mocka-infield/identity/ai_roster.json",
        "members": ["ChatGPT", "Perplexity", "Gemini", "Claude"]
    },
    "repository_dependency_map": {
        "description": "MoCKA -> KG, CIV, TR, EB, CP / KG -> TR / TR -> CIV / EB -> KG",
        "source": "mocka-joints/mocka-ecosystem/_canon/docs/MOCKA_REPOSITORY_MAP.md",
        "edges": [
            ["MoCKA", "mocka-knowledge-gate"],
            ["MoCKA", "mocka-civilization"],
            ["MoCKA", "mocka-transparency"],
            ["MoCKA", "mocka-external-brain"],
            ["MoCKA", "mocka-core-private"],
            ["mocka-knowledge-gate", "mocka-transparency"],
            ["mocka-transparency", "mocka-civilization"],
            ["mocka-external-brain", "mocka-knowledge-gate"]
        ]
    },
    "repositories": {
        "MoCKA": {
            "path": "C:/Users/sirok/MoCKA",
            "remote": "git@github.com:m-sirius-k/MoCKA.git",
            "account": "m-sirius-k",
            "visibility": "public",
            "role": "heart",
            "role_jp": "心臓部・制度核",
            "files": 1770,
            "last_commit": "890f934 refactor: organize all root scripts",
            "language": "Python 90.2% / PowerShell 7.6%",
            "status": "active_main",
            "gitignore_excludes": [
                "keys/ *.pem *.key",
                "runtime/* (except engines/api/policy/ledger/main_loop)",
                "runtime/**/*.json (JSON state excluded)",
                "archive/ .wsl_ots_venv/ *.bak*"
            ],
            "key_components": {
                "ledger_canonical": "runtime/main/ledger.json",
                "schema": "schema/schema.py - 全スクリプト共通スキーマ基盤",
                "verify": "ledger_verify.py / verify_all.py - ALL CHECKS PASSED",
                "router": "interface/router.py - Gemini API接続済み",
                "providers": {
                    "google": "interface/providers/google_provider.py - 動作確認済み",
                    "azure": "interface/providers/azure_provider.py - ダミー実装"
                },
                "main_loop": "runtime/main_loop.py - 完全ループ動作確認済み",
                "civilization_engines": "runtime/civilization_*.py - 60本以上",
                "bridge": "runtime/civilization_bridge.py - 3世界統合",
                "anchor": "anchor_update.py - 自動封印スクリプト",
                "observer": "observer_logger.py - テストパック使用記録",
                "ecosystem_map": "MOCKA_ECOSYSTEM_MAP.json - 本ファイル"
            },
            "governance": {
                "anchor_record": "governance/anchor_record.json",
                "registry": "governance/registry.json - ed25519 v2",
                "root_key": "governance/keys/root_key_v2.ed25519.public.b64u",
                "role_policy": "governance/keys/role_policy.json",
                "approval_flow": "governance/approval_flow.json"
            },
            "run_commands": {
                "health_check": "python ledger_verify.py && python verify_all.py",
                "run_loop": "cd runtime && python main_loop.py",
                "infield_ingest": "python runtime/infield_ingestor.py",
                "seal": "python anchor_update.py MESSAGE",
                "observer_log": "python observer_logger.py PATH USER_ID"
            },
            "confirmed_working_2026_03_28": [
                "ledger_verify.py -> LEDGER OK",
                "verify_all.py -> ALL CHECKS PASSED",
                "python runtime/main_loop.py -> full loop",
                "python schema/schema.py -> VERIFY True",
                "python anchor_update.py -> auto seal + ALL CHECKS PASSED"
            ]
        },
        "mocka-civilization": {
            "path": "C:/Users/sirok/mocka-civilization",
            "remote": "https://github.com/nsjpkimura-del/mocka-civilization.git",
            "account": "nsjpkimura-del",
            "visibility": "public",
            "role": "blueprint",
            "role_jp": "設計思想・青写真層",
            "files": 132,
            "last_commit": "a21bc3e MoCKA Control Center update",
            "description": "MoCKAが長期的にどう進化すべきかを定義する設計図",
            "gitignore_excludes": [
                ".env *.key *.pem *.secret *.token",
                "keys/ secrets/ runtime/ ledger/ logs/ outbox/ inbox/",
                ".venv/ node_modules/"
            ],
            "phases": [
                "phase9","phase10","phase11","phase12","phase13","phase14",
                "phase15","phase16","phase17","phase18","phase19","phase20",
                "phase21","phase22","phase23","phase24","phase25","phase26",
                "phase27","phase28","phase29"
            ],
            "key_dirs": [
                "blueprint","civilization-integration","derived-civilizations",
                "docs","genesis","governance","lineage-registry","replication"
            ]
        },
        "mocka-transparency": {
            "path": "C:/Users/sirok/mocka-transparency",
            "remote": "https://github.com/nsjpkimura-del/mocka-transparency.git",
            "account": "nsjpkimura-del",
            "visibility": "public",
            "role": "transparency",
            "role_jp": "改ざん検知・署名検証デモ層",
            "files": 51,
            "last_commit": "43cfd93 MoCKA Control Center update",
            "description": "外部向け改ざん検知デモ。3分で体験できる署名検証",
            "gitignore_excludes": [
                "keys/*_private.pem (秘密鍵のみ除外、公開鍵はコミット可)",
                "sample04/observer_pack/"
            ],
            "key_components": {
                "samples": "sample01-04 署名検証デモ",
                "public_keys": "public_keys/observer1,2 / Outfield-Test-2026,2028 / Verifier-Test-2026",
                "private_keys": "keys/ (gitignore対象)",
                "scripts": "verify_one.ps1, tamper_demo.ps1"
            }
        },
        "mocka-external-brain": {
            "path": "C:/Users/sirok/mocka-external-brain",
            "remote": "https://github.com/nsjpkimura-del/mocka-external-brain.git",
            "account": "nsjpkimura-del",
            "visibility": "public",
            "role": "orchestrator_bus",
            "role_jp": "AIオーケストラ神経系・合議バス",
            "files": 5,
            "last_commit": "9b97564 MoCKA Control Center update",
            "description": "share/ask/reply/decideプロトコルによるAI合議バス",
            "gitignore_excludes": [
                ".env *.key *.pem runtime/ ledger/ logs/ outbox/ inbox/"
            ],
            "key_components": {
                "events_csv": "logs/bus/events.csv - AI合議イベントログ（hash付き）",
                "rounds": [
                    "logs/bus/rounds/round_2026-02-08-001.md",
                    "logs/bus/rounds/round_2026-02-08-002.md"
                ]
            },
            "protocol": {
                "share": "orchestrator_coreが全AIに共有",
                "ask": "意見募集（必須出力: 結論/根拠/リスク/代替案/次アクション）",
                "reply": "parent_event_idで木構造、member AIが回答",
                "decide": "evidence_refで採用根拠明示、orchestratorが決定"
            },
            "event_schema": {
                "fields": "event_id, timestamp, round_id, motion, actor, agent_name, kpa_id, content, content_ref, status, error_class, parent_event_id, evidence_ref, hash"
            },
            "importance": "router.pyと接続することが次の本質的ステップ",
            "confirmed_protocol": "Phase2-B: ask/reply/decide 2026-02-08に実装確認"
        },
        "mocka-core-private": {
            "path": "C:/Users/sirok/mocka-core-private",
            "remote": "https://github.com/nsjpkimura-del/mocka-core-private.git",
            "account": "nsjpkimura-del",
            "visibility": "private",
            "role": "experimental_core",
            "role_jp": "実装実験・検証環境（凍結中）",
            "files": 1002,
            "last_commit": "196c645 MoCKA Control Center update",
            "execution_policy": "FORBIDDEN: Use MoCKA/run_with_audit.py",
            "gitignore_excludes": [
                "secrets/ state/ logs/ outbox/ .env"
            ],
            "key_dirs": {
                "engine": "AIオーケストラ・文明エンジン群（80本以上）",
                "app/src/runner": "retry worker / DB migration / infield runner",
                "infield": "phase5-7の運用履歴 / state DB / phase11 knowledge.db",
                "src/mocka_audit": "audit_writer, contract_v1, signature_guard"
            },
            "key_engines": {
                "ai_gateway.py": "ai_providers.jsonからprovider読込、ask_all()で全AI呼び出し",
                "auto_loop.py": "executor->self_bridge->simple_bridge->policy_engine の無限ループ",
                "civilization_engine.py": "civilization_nodes.jsonからノード読込、council()でブロードキャスト",
                "share_ai.py": "outboxの最新ファイルをstate.jsonのlast_shareに保存",
                "vote_engine.py": "run_ai()でAI投票、explore/cycle/repairで多数決",
                "ledger_engine.py": "signal+policy+feedbackをハッシュチェーンでledger.jsonに記録"
            },
            "state_db": {
                "path": "engine/infield/state/mocka_state.db",
                "size": "32768 bytes",
                "last_modified": "2026-02-17"
            }
        },
        "mocka-public": {
            "path": "C:/Users/sirok/mocka-public",
            "remote": "https://github.com/m-sirius-k/mocka-public.git",
            "account": "m-sirius-k",
            "visibility": "public",
            "role": "public_docs",
            "role_jp": "公開ドキュメント・証明層",
            "files": 31,
            "last_commit": "20f2ee4 rewrite: README as verifiable system document",
            "gitignore_excludes": [
                "runtime/ engine/ *.env *.log *.pem *.key *.private*",
                "archive/ .venv/ __pycache__/"
            ],
            "key_docs": [
                "PROOF.md", "SEAL.md", "SECURITY.md",
                "SHADOW_MOVEMENT_PRINCIPLE.md",
                "PHASE0_TO_9C_SYSTEM_STATE.md",
                "PHASE13B_FREEZE.md", "PHASE17_STABLE_DECLARATION.md"
            ]
        },
        "mocka-knowledge-gate": {
            "path": "C:/Users/sirok/mocka-knowledge-gate",
            "remote": "https://github.com/nsjpkimura-del/MoCKA-KNOWLEDGE-GATE.git",
            "account": "nsjpkimura-del",
            "visibility": "public",
            "role": "institutional_memory",
            "role_jp": "制度的記憶層",
            "files": 334,
            "last_commit": "3df4985 EV-20260228-0004",
            "language": "JavaScript / TypeScript / Firebase / Docker",
            "description": "Firebase+JS+Dockerベースの制度的記憶保存システム",
            "note": "他がPythonなのに対し完全別スタック",
            "connection_protocol": {
                "rest_endpoint": "/api/v1/share",
                "graphql_endpoint": "/graphql",
                "auth": ["JWT token", "invite-code", "rod-number"],
                "mandatory_fields": ["ISSUE-ID", "rod-number", "TRUST_SCORE"],
                "external_integration": "Felo AI Search (bidirectional sync, OAuth2)"
            },
            "handshake_protocol": [
                "AI sends ISSUE-ID",
                "Gate validates rod-number",
                "Gate returns constitution excerpt",
                "AI adjusts settings"
            ],
            "gateway": {
                "server": "gateway/src/server.ts - Express/JWT/rate-limit",
                "endpoints": [
                    "GET /v1/status/ping",
                    "POST /v1/intention/submit (JWT required)"
                ]
            }
        },
        "mocka-outfield": {
            "path": "C:/Users/sirok/mocka-outfield",
            "remote": "https://github.com/m-sirius-k/mocka-outfield.git",
            "account": "m-sirius-k",
            "visibility": "public",
            "role": "public_network",
            "role_jp": "外野・公開ネットワーク層",
            "files": 14,
            "last_commit": "31de058 MoCKA Control Center update",
            "gitignore_excludes": [
                "*.pem *.key *.private *.secret infield mocka-infield keys secrets"
            ]
        },
        "mocka-runtime": {
            "path": "C:/Users/sirok/mocka-runtime",
            "remote": "https://github.com/m-sirius-k/mocka-runtime.git",
            "account": "m-sirius-k",
            "visibility": "public",
            "role": "docs_only",
            "role_jp": "ドキュメントのみ（実装なし）",
            "files": 3,
            "last_commit": "ce12518 Add comprehensive MoCKA Civilization Concepts"
        }
    },
    "joints": {
        "mocka-pythonbridge": {
            "path": "C:/Users/sirok/mocka-joints/mocka-pythonbridge",
            "remote": None,
            "role": "python_bridge",
            "role_jp": "Python橋渡し・ブラウザ操作・AI呼び出し層",
            "files": 20495,
            "last_commit": "3a0ab62 fix ledger_append newline and BOM issue",
            "description": "OCR・スクリーンショット・ブラウザ自動操作でAIと接続",
            "key_files": {
                "field_player.py": "cv2/pyautogui/pytesseract使用。OS操作・OCR・スクリーンショット",
                "bridge.py": "field_playerを呼び出すタスク実行エントリ",
                "bridge_ai.py": "Gemini(google-genai) + OpenAI(gpt-4o-mini) + Copilot(PS経由) ルーティング",
                "replan.py": "AIにos_screenshot/ocr_image/call_aiのフロー再計画を依頼",
                "bridge_watcher.py": "archive/*.receipt.txtを監視→ledger+registry自動追記→replan自動起動",
                "main_loop.py": "field_player.execute_jsonを使ったフロー実行ループ",
                "mocka.ps1": "event/ai/link/patch/weekly/auditコマンドのPowerShell統合インターフェース"
            },
            "ai_support": {
                "gemini": "google-genai SDK / gemini-2.0-flash",
                "openai": "openai SDK / gpt-4o-mini",
                "copilot": "PowerShell経由（API未対応）"
            },
            "ledger_files": {
                "Event_Ledger.csv": "ledger/Event_Ledger.csv",
                "Change_Registry.csv": "registry/Change_Registry.csv"
            }
        },
        "mocka-infield": {
            "path": "C:/Users/sirok/mocka-joints/mocka-infield",
            "remote": None,
            "role": "infield_memory",
            "role_jp": "内部記憶・イベント管理・状態DB",
            "files": 35,
            "description": "MoCKAの内部記憶システム。イベント・インシデント・文書を管理",
            "key_files": {
                "master_index.csv": "全ドキュメントのインデックス（id/type/title/timestamp/path/summary/tags）",
                "events/events_infield.csv": "イベント台帳（Date/EventID/EventType/Title/Summary/hash）",
                "identity/mocka_constitution.md": "MoCKA憲法",
                "identity/ai_roster.json": "AIメンバー: ChatGPT/Perplexity/Gemini/Claude",
                "identity/version_history.md": "バージョン履歴",
                "ledger/infield_ledger.jsonl": "infieldイベントledger",
                "ledger/Dream_Progress_Log.csv": "進捗ログ",
                "state/mocka_state.db": "SQLite状態DB",
                "state/current_status.json": "現在ステータス",
                "docs/chat": "チャット記録",
                "docs/incidents": "インシデント記録",
                "docs/documents": "文書（MoCKA文明史等）",
                "docs/decisions": "意思決定記録"
            }
        },
        "mocka-ecosystem": {
            "path": "C:/Users/sirok/mocka-joints/mocka-ecosystem",
            "remote": None,
            "role": "ecosystem_manager",
            "role_jp": "全リポジトリ横断管理・ドキュメント統合ツール",
            "files": 1435,
            "description": "全リポジトリの整合性チェック・ドキュメント適用・健全性確認",
            "key_tools": {
                "ecosystem_integrity_check.ps1": "git status/canonical docs/markdown links/mermaid/repo存在確認",
                "mocka_doctor.ps1": "システム健全性診断",
                "apply_docs.ps1": "ドキュメント一括適用",
                "repair_registry.ps1": "レジストリ修復"
            },
            "canon_docs": {
                "path": "_canon/docs/",
                "files": [
                    "MOCKA_ARCHITECTURE_DIAGRAM.md",
                    "MOCKA_ECOSYSTEM_DIAGRAM.md",
                    "MOCKA_REPOSITORY_MAP.md",
                    "SYSTEM_OVERVIEW.md",
                    "VERIFICATION_QUICKSTART.md",
                    "INTEGRITY_TRANSPARENCY_MODEL.md",
                    "AI_GOVERNANCE_REFERENCE_ARCHITECTURE.md",
                    "RESEARCH_POSITIONING.md"
                ]
            },
            "mocka_ecosystem_subfolder": {
                "description": "MoCKAリポジトリのミラー/スナップショット（.backup/.github/acceptance等含む）",
                "path": "mocka-ecosystem/MoCKA/"
            }
        }
    },
    "archive": {
        "path": "C:/Users/sirok/mocka-archive",
        "contents": [
            "MoCKA_phase22_anchored", "MoCKA_phase22_iso",
            "MoCKA_clean_test__FROZEN", "mocka_verify_tmp",
            "_mocka_phase22_checkout", "phase2c_verify",
            "verify_test", "MoCKA_node2", "mocka-node2",
            "mocka-organized", "ops_mocka", "tools_backup_20260215"
        ]
    },
    "external_hardware": {
        "observer_node": {
            "path": "F:/MoCKA_Observer_Node",
            "description": "テストパック・外部検証用（USBドライブ想定）",
            "contents": ["audit_pack_20260301", "observer_pack_latest"],
            "schema": "mocka.audit.event.v1",
            "integrity": "PGP署名(ASC) + SHA256",
            "phase2b_status": "JOINT_INTEGRITY_OK",
            "policy": {
                "append_only": True,
                "receiver_signature_required": True,
                "hash_mismatch_halt": True
            }
        }
    },
    "accounts": {
        "primary": "m-sirius-k",
        "legacy": "nsjpkimura-del",
        "note": "nsjpkimura-delはGoogle初期ログイン由来。m-sirius-kに統一予定"
    },
    "data_flow": {
        "description": "MoCKAのデータが流れる経路",
        "infield_to_main": "mocka-infield/events/* -> MoCKA/runtime/infield_ingestor.py -> runtime/input.json",
        "main_loop": "input.json -> intent -> goal -> plan -> action -> action_executor -> router.py -> Gemini",
        "civilization": "action -> civilization_bridge.py -> civilization_loop_engine.py -> civilization_*.json",
        "ledger": "全アクション -> runtime/main/ledger.json (SHA256チェーン)",
        "governance": "ledger -> verify_all.py -> governance/anchor_record.json (封印)",
        "external_brain": "share/ask/reply/decide -> mocka-external-brain/logs/bus/events.csv",
        "knowledge_gate": "REST POST /api/v1/share (ISSUE-ID + rod-number + TRUST_SCORE)",
        "pythonbridge": "OCR/screenshot -> bridge_ai.py -> Gemini/OpenAI -> replan -> field_player"
    },
    "next_actions": {
        "immediate": [
            "git push origin main（今日の作業をGitHubに反映）",
            "router.pyをmocka-external-brain events.csvプロトコルと接続"
        ],
        "short_term": [
            "Gemini APIクォータ回復後にrouter.py実動作確認",
            "azure_provider.pyにGPT API接続実装",
            "USB認証システムの実装（wmic diskdrive SerialNumber取得）"
        ],
        "medium_term": [
            "nsjpkimura-del -> m-sirius-k GitHub統合",
            "mocka-knowledge-gate（JS）とMoCKA（Python）の接続",
            "mocka-core-private/engine群をMoCKA/runtimeに統合検討"
        ]
    }
}

with open("MOCKA_ECOSYSTEM_MAP.json", "w", encoding="utf-8") as f:
    json.dump(ecosystem, f, indent=2, ensure_ascii=False)

print("SAVED: MOCKA_ECOSYSTEM_MAP.json")
print(f"repositories: {len(ecosystem['repositories'])}")
print(f"joints: {len(ecosystem['joints'])}")
print(f"data_flow entries: {len(ecosystem['data_flow'])}")
