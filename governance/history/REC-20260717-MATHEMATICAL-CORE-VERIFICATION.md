# REC-20260717-MATHEMATICAL-CORE-VERIFICATION

- 記録日: 2026-07-17
- 記録者: Claude-fable-5（制度書記官・独立検証、R02系）
- 種別: 監査記録（新規変更ではない。論文本文・実装コードへの変更なし）
- 関連イベント: E20260717_854655848ebe9 (CHANGE_START)
- 関連指示: きむら博士 2026-07-17（MoCKA論文最終固定監査 / Mathematical Core Final Confirmation / Next Step 2）

## 1. 目的

AAAI 2027投稿論文（Paper ID 1024, anonymous submission）の数学核（Formal Core）について、
提出前に (a) 何が存在するか、(b) 何を採用しなかったか、(c) なぜ数学を増やさなかったか
を固定し、未来の査読対応・開発者へ判断根拠を残す。

## 2. 対象ファイル（凍結点）

- パス: X:\down\MoCKA2027.tex
- SHA-256: 20406ea6d5c64400655d1d77a9721e404ad5814811afd2963f7a9a27ee46f559
- サイズ: 21,866 bytes
- 更新日時: 2026-07-17 12:09:49 JST

### Canonical Source Status: PENDING

Overleaf本体（Paper ID 1024）との同一性照合は未完了。
理由: 照合実施時点（2026-07-17夜）でOverleafが検証環境のChromeで未ログインであり、
検証エージェントは認証代行を行えないため。
上記SHA-256はローカル固定版の凍結点であり、Overleafエクスポートとの
ハッシュ一致確認後に VERIFIED へ更新すること（置換せず別名保存で比較する。
例: X:\down\MoCKA2027_overleaf_export.tex）。

## 3. 正本数学核（数式全数）

論文中の番号付き数式は以下の2本のみ。これが形式核の全てである。

    (式1)  S_DTS = <E, P, V>
    (式2)  V = Verified ==> E = 1 AND P = 1 AND NOT C

補助記法（数式番号なし・散文内）: 遷移ラベル T: Observation -> Action（1回のみ使用）。

係数・重み付きスコア・リスク計算式・最適化表現・確率モデルは一切含まれない
（Decorative Math監査 2026-07-17 で全項目不検出を確認済み）。

## 4. 記号対応表

| 記号 | 意味 | 本文内役割 | 実装対応 |
|---|---|---|---|
| S_DTS | Decision Transition State（3要素タプル） | 式1で定義、評価節の分類枠組み | 不足（serialized tupleを構築するコードは不存在） |
| E in {0,1} | Evidence Sufficiency | 式1成分、式2条件 | 部分（自動判定なし。approve_promotionのdecision_evidence_consistency等、人間確認に依存） |
| P in {0,1} | Provenance Integrity | 式1成分、式2条件 | 対応あり・部分（seal chain: phi_os/integrity.py seal_baseline、SHA-256ハッシュ、GL7 encoding検査、audit/ed25519） |
| V | 3値判定 {Verified, Unverified, Conflicted} | 式1成分、式2左辺、Table 1分類軸 | 不足（3値分類エンジンはコード全文検索で不存在） |
| C | 意味的競合の有無 {True, False} | 式2条件 | 部分（自動競合検出器なし。台帳status不一致の運用検知例のみ: IC_20260707_006） |
| T | 遷移ラベル | 散文1回、形式的未使用 | 形式核外 |

## 5. 未採用概念（存在確認の結果）

以下は2026-07-17時点の論文正本候補に存在しない。未採用として記録する。

- delta（部分遷移関数 delta: S x E x A -> S'（partial））: 未採用
- Dom(delta): 未採用
- S_t = <X_t, H_t, I_t, A_t, P_t>（5要素状態タプル）: 未採用
- H_t（Immutable Evidence History の形式記号）: 未採用
- X_t / I_t / A_t / P_t: 未採用

判定: 5要素タプルは既存核 S_DTS = <E, P, V> の再表現ではなく理論拡張案である。
根拠: S_DTSは証拠述語（E, P）と判定結果（V）のみで構成され、
履歴（H_t）・解釈（I_t）を状態成分として持たない。
A_t / P_t 相当は散文（Human Gate / policy）には存在するが形式核には不在。

探索範囲の限定: 上記の不存在判定はX:\down配下の全論文候補（MoCKA2027.tex /
2027.tex / AuthorKit27）およびC:\Users\sirok\MoCKA\docsに対するもの。
Overleaf本体は範囲外（PENDING）。

## 6. なぜ数学を増やさなかったか

1. 実装に単一の遷移関数は存在しない。実体は複数ゲートの合成
   （GL7 / Human Gate / mocka_git_safe_commit）であり、単一のdeltaを形式化すると
   その関数はコードのどこにあるかという再現性攻撃を自ら招く。
2. I_t（解釈状態）は実装では永続状態ではなく導出物である
   （phi_os/human_gate.py get_state はevent列走査で毎回再構築する）。
   状態成分として形式化すると実装と1対1でなくなる。
3. E・Cの判定は現実装では人間確認に依存する。自動判定を示唆する形式化は
   式2の防御を崩す。
4. 現在の核（式1・式2のみ、装飾数学ゼロ）は、それ自体が最強の査読防御である。
   最大リスクは、良いアイデアを追加して既存の実証可能な核を壊すこと。

## 7. 実装対応範囲（証跡で防御可能な主張）

1. append-only Decision Ledgerの非否認性（superseded_by 0/109 実測、DC_20260714_001裁定）
2. 未定義遷移の遷移対象外扱い（GL7 abort時DENY記録＋後続不実行、
   Human Gate許可集合（TRANSITIONS）外の実行拒否）
3. 検証失敗時の停止＋人間待ち（AUTO_SEAL_PENDING、app.py。
   ただし当初設計ではなく事後改修である旨を必ず併記すること:
   IC_20260707_006 / IC_20260708_001 / IC_20260708_002）
4. ポリシー版の監査記録への埋込（GATE_POLICY_VERSION、phi_os/event_gate.py）
5. seal chainによる完全性封印（phi_os/integrity.py）

## 8. 査読防御方針（Reviewer #2対応）

- Claim: MoCKA does not introduce a new mathematical formalism.
- Contribution: MoCKA provides an operational governance discipline where
  evidence sufficiency, provenance integrity, and conflict detection define
  whether a decision transition is eligible for execution.
- Boundary: Failed conditions are not mapped to undefined mathematical states,
  but are preserved as auditable non-executable events requiring human review.

詳細な想定問答はリポジトリ外の査読対応資料に分離
（X:\down\AAAI2027_PhaseA\reviewer2_response_draft_v0.1.md。
anonymous submission期間中はリポジトリへ収録しない）。

## 9. 分離事項（本監査に含まないもの）

- 評価数値の処分（4.2ms / 15,552 / 86 / 100% / Table内訳）はPriority 2として
  数学核監査から分離。2026-07-17時点で全て証跡なしまたはFreeze不能
  （X:\down\AAAI2027_PhaseA\phaseA_tasks_v0.1.md T-4 / T-7参照）。
- 本記録は数学核の存在確認のみを扱い、数値の採否判断を含まない。

## 10. 工程状態

    Phase:   Mathematical Core Audit
    Status:  PASS
    Blocker: Overleaf Canonical Verification (PENDING)
    Next:    Canonical Source Seal（ハッシュ一致確認後にVERIFIEDへ更新）
