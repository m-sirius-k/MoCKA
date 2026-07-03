# Satellite Repository Positioning - Options v0.1

位置づけ: くろこ作業指示(2026-07-03、Task-I)に基づき新規作成。Task-H(`REPOSITORY_STATUS_VOCABULARY_v0.1.md`)で定義した標準7段階語彙が確定していることを前提として着手する。対象は mocka-civilization / mocka-external-brain / mocka-transparency / MoCKA-KNOWLEDGE-GATE の4リポジトリ(いずれも最終update 96日前・同一タイムスタンプ2026-03-29 03:01)。

目的は「現役」「統合済み・凍結」「将来再利用」「保守停止」のいずれに該当するかを制度として決定するための整理案の作成であり、決定そのものは博士が行う。本ファイルは選択肢の提示にとどめ、いずれか一つを結論として採用することはしない。実装・コード変更は一切含まない。既存ファイルの上書きは行わない。v0.1とし、v1.0は名乗らない。

Level分離の明記: 第1部・第2部・第3部の記載事実は、GitHub公開情報(README本文・push日時・ディレクトリ構成)に基づくLevel1の範囲にとどめる。1件のみ、MOCKA_OVERVIEW.json(ローカル管理文書、当該ファイル自身が"PRIVATE - ローカルのみ管理"と明記)由来の情報を参考として使うが、これはGitHub公開情報ではないため、該当箇所に明示的に注記して分離する。

---

## 第1部: 対象4リポジトリの現状(Task-Hからの再掲)

| リポジトリ | Loop上の自称位置 | README表記 | 最終push | 7段階への当てはめ(Task-H時点) |
|---|---|---|---|---|
| mocka-civilization | 8番目(Audit -> Institutionalize) | "Active Development" | 96日前 | 対応不能(Ambiguity-1、本ファイルで仮当てはめを行う) |
| mocka-external-brain | 6番目(Decision) | "Active Development" | 96日前 | 同上 |
| mocka-transparency | 3-4番目(Incident/Recurrence) | "Active Development" | 96日前 | 同上 |
| MoCKA-KNOWLEDGE-GATE | 2番目(Record) | "v1.0.0 - Active Development" | 96日前 | 同上 |

---

## 第2部: Civilization Loop 8段階マッピングの再確認

MoCKAコアのREADMEが定義するループは以下の8段階である(README原文の英語版見出しに基づく)。

1. Observation
2. Record
3. Incident
4. Recurrence
5. Prevention
6. Decision
7. Action
8. Audit

各衛星リポジトリのREADMEにある「Position in mocka_Movement」図は、この8段階のうち特定の番号に「YOU ARE HERE」を割り当てている。mocka-outfield=1番目、MoCKA-KNOWLEDGE-GATE=2番目、mocka-transparency=3-4番目、mocka-external-brain=6番目、mocka-runtime=7番目、mocka-civilization=8番目、mocka-public=8番目(後述)。5番目(Prevention)にはどのリポジトリの図にも「YOU ARE HERE」の記載がない。

### 2.1 5番目(Prevention)の担当リポジトリ不在について

観察事実: MoCKAコアのREADMEには、Governance Layerの構成要素として`preventive_rule_engine`(「障害の事前防止」)という項目が記載されている。これはMoCKAコア自身のリポジトリ内の構成要素として記載されており、衛星リポジトリとしては存在しない。

この観察事実から考えられる選択肢は以下の3つであり、本ファイルではいずれかに決定しない。

- 選択肢A: Preventionの機能は最初からMoCKAコア内の`preventive_rule_engine`として実装される設計であり、衛星リポジトリを持たないことは意図的な設計である
- 選択肢B: 衛星リポジトリとして独立させる計画があったが未着手であり、本来は欠落である
- 選択肢C: 他の衛星リポジトリ(例: mocka-transparencyの再発検知機能)の一部として実質的にカバーされているが、README上は明示されていない

いずれの選択肢が正しいかは、`preventive_rule_engine`の実装内容を確認するLevel2以降の調査が必要であり、本ファイルでは判定しない。

### 2.2 8番目(Audit/Institutionalize)の二重主張について

観察事実: mocka-civilizationのREADMEは8番目を"Audit -> Institutionalize"とし、下流を「全レイヤーが検証済み知見を上位に送る/原則が全レイヤーに流れ下りる」という内部還流として記載している。一方、mocka-publicのREADMEも8番目を"Audit output"とし、下流を「一般公開・第三者監査人・将来のエージェント」という外部公開として記載している。両者とも図中で「YOU ARE HERE」を8番目に置いているが、いずれの図も線形(分岐なし)で描かれており、8番目が枝分かれすることは図の表記からは読み取れない。

考えられる選択肢は以下の3つである。

- 選択肢A: 8番目は「内部の制度化(mocka-civilization)」と「外部への公開(mocka-public)」という2つの並行した出力先を持つ意図的な設計であり、矛盾ではない。この場合、図を分岐形式に改める余地がある
- 選択肢B: 表記の重複であり、どちらか一方が本来別の番号(例: mocka-publicは9番目相当の「公開」として8番目とは別立てにする)に整理されるべきである
- 選択肢C: 現状の表記のまま許容し、対応不要とする

---

## 第3部: 4リポジトリそれぞれの7段階語彙 仮当てはめ

Task-Hで定義した標準7段階語彙(Research / Active Development / Active / Stable / Frozen / Deprecated / Archived)を用い、各リポジトリについて現状もっとも近いと考えられるステータスを複数候補として仮当てはめする。根拠が確認できていない候補には「要確認」を付す。

### mocka-civilization

- 観察事実: README表記"Active Development"。最終push 96日前。ルートに phase9 から phase29 まで21個のディレクトリが存在する(Repository Health Report v1.0作成時点ではディレクトリ名のみ確認、中身のファイル構成は未取得)
- MoCKAコアREADMEとの関係: MoCKAコア側にも「Self-Audit Layer(Phase 3-1)」「Feedback Loop(Phase 3-2)」「Self-Learning Kernel(Phase 4-1)」等、Phase番号を冠した層がコア内実装として記載されている。mocka-civilization側のphase9-29という番号体系と、MoCKAコア側のPhase 2-1/3-1/3-2/4-1という番号体系が同一の採番規則を指すのか、無関係の並行した採番なのかは本ファイルでは確認できていない(要確認)
- 候補1(Active Development): README表記をそのまま採用。根拠は表記のみで、96日間の更新間隔とは整合しない
- 候補2(Stable): 21フェーズ分の設計文書が存在し、大きな構造変更を伴わずに保守されている可能性。根拠は更新間隔の長さのみであり、実際に保守作業が行われているかは未確認(要確認)
- 候補3(Frozen): 意図的に更新を止めている可能性。根拠: 96日前の最終pushが4リポジトリ同一タイムスタンプであることから、何らかの区切り作業と同時に行われた可能性があるが、当該コミットのメッセージ内容は本ファイルでは未取得(要確認)

### mocka-external-brain

- 観察事実: README表記"Active Development"。最終push 96日前。「AI Orchestra Bus」としてChatGPT/Gemini/Claude/Perplexityの合議を担うと記載
- MoCKAコアREADMEとの関係: MoCKAコア側に「Decision Layer(Phase 2-2)」がコア内実装として記載されている(`decision_registry.py`・`priority_scorer.py`・`risk_analyzer.py`・`decision_engine.py`等)。mocka-external-brainが担うと自称する「Decision」という役割名と、MoCKAコア内Decision Layerの役割名は同一の語を使用している。両者が同一責務を指すのか、複数AIの合議(external-brain)と単一プロセス内の意思決定ロジック(コアのDecision Layer)という別粒度の話なのかは本ファイルでは確認できていない(要確認)
- 候補1(Active Development): README表記のまま。96日間の更新間隔とは整合しない
- 候補2(Stable): 「合議プロトコル(share/ask/reply/decide)」という設計自体は完成しており、大きな変更なく維持されている可能性(要確認)
- 候補3(Frozen): mocka-civilizationと同様、96日前の一括最終更新が区切りを伴っていた可能性(要確認)

### mocka-transparency

- 観察事実: README表記"Active Development"。最終push 96日前。「Ed25519デジタル署名」「SHA256ハッシュチェーン」による改ざん検知を担うと記載
- MoCKAコアREADMEとの関係: MoCKAコア側に「Event Integrity Framework(Phase5-2)」がコア内実装として記載されており、`phi_os/integrity.py`が「Event Signature + SHA256 Hash Chain + Verification」を提供すると明記されている。使用技術名(SHA256ハッシュチェーン)がmocka-transparencyの自称する機能と一致しており、4リポジトリの中では最もMoCKAコア内実装との重複可能性を示す具体的な記述が見つかった(要確認: 重複か、それとも異なるレイヤーでの並行実装かは未検証)
- 候補1(Active Development): README表記のまま。96日間の更新間隔とは整合しない
- 候補2(統合済み・凍結寄り): MoCKAコアのEvent Integrity Framework(Phase5-2)が同等機能を内包した結果、mocka-transparency側の更新が止まった可能性(要確認、時期的な前後関係は未確認)
- 候補3(Frozen): 同上の一括最終更新の区切り仮説

### MoCKA-KNOWLEDGE-GATE

- 観察事実: README表記"v1.0.0 - Active Development"。最終push 96日前。「acceptor:infield」の実体であると自称
- MoCKAコアREADMEとの関係: MoCKAコア側にも「Memory Layer(Phase 2-3)」がコア内実装として記載されており(`memory_store.py`・`memory_index.py`等)、「infield」という語もMoCKAコアREADME内で「acceptor:infield」として繰り返し使われている
- 参考(ローカル管理文書由来、GitHub公開情報ではない): MOCKA_OVERVIEW.json(分類: PRIVATE - ローカルのみ管理)には、mocka-knowledge-gateの使用言語が「JavaScript/Firebase/Docker」と記載されている。これはMoCKAコア本体の主要言語(Python)と異なる。この情報はGitHub公開情報から得たものではなく、ローカル管理文書からの参考情報であることを明記する。もし技術スタックが実際に異なるのであれば、コア内Memory Layerとは独立した別実装である可能性を示唆するが、本ファイルではこの点をLevel1の確定事実としては扱わない(要確認)
- 候補1(Active Development): README表記のまま。96日間の更新間隔とは整合しない
- 候補2(将来再利用): 技術スタックがコアと異なる(参考情報)ため、コアのMemory Layerに統合されず、独立した用途で将来再利用される位置づけの可能性(要確認)
- 候補3(Frozen): 同上の一括最終更新の区切り仮説

---

## 第4部: 選択肢の提示(現役/統合済み・凍結/将来再利用/保守停止)

博士が決定するための選択肢を、4リポジトリ共通の枠組みで整理する。決定案ではない。

| 選択肢 | 意味 | 4リポジトリで支持されうる観察事実 | 反する観察事実 |
|---|---|---|---|
| 現役 | README表記どおり、実際に開発・保守が継続している | README表記が"Active Development"で統一されている | 96日間pushがない。4リポジトリとも同一タイムスタンプで最終更新が止まっている |
| 統合済み・凍結 | 機能がMoCKAコア内の対応するPhase実装に吸収され、衛星リポジトリ側は凍結された | mocka-transparency(Event Integrity Framework/Phase5-2)・mocka-external-brain(Decision Layer/Phase2-2)・MoCKA-KNOWLEDGE-GATE(Memory Layer/Phase2-3)について、コア側に同名または類似役割の実装がREADME上確認できる | 吸収の時期的前後関係(コア側実装が先か、衛星側の更新停止が先か)は未確認。吸収を明言する記述はどちらのREADMEにもない |
| 将来再利用 | 現時点では動いていないが、設計資産として保持されている | mocka-civilizationのphase9-29ディレクトリ群など、将来のフェーズ番号を先取りした構造がある | ディレクトリの中身(実装の有無)は未確認 |
| 保守停止 | 実質的に開発が止まっており、README表記の更新もされていない | 96日間の無更新という事実そのもの | README表記自体は"Active Development"のままであり、保守停止を示す明示的な記述(Deprecated等)はどのリポジトリにもない |

---

## 第5部: 未確定事項

- 4リポジトリの96日前・同一タイムスタンプのコミットメッセージ内容は本ファイルでは未取得。取得できれば「区切り」の性質(凍結宣言か、単なる一括メンテナンスか)の手がかりになる可能性がある
- mocka-civilizationのphase9-29ディレクトリの中身(空か、実装済みか)は未確認
- MoCKAコア側のPhase番号体系(2-1/2-2/2-3/3-1/3-2/4-1/5-2)と、mocka-civilization側のPhase番号体系(9-29)が同一の採番規則を指すかどうかは要確認。指すのであれば「統合済み」仮説の裏付けが強まるが、本ファイルでは検証していない
- MoCKA-KNOWLEDGE-GATEの技術スタック(JavaScript/Firebase/Docker)に関する記載はローカル管理文書由来であり、GitHub公開情報での裏付けは本ファイルでは取っていない
- 第4部の4選択肢は排他的ではなく、リポジトリごとに複数該当しうる。最終的な当てはめの決定は博士が行う

---

## 改訂履歴

- v0.1(2026-07-03): くろこ作業指示Task-Iに基づき新規作成。Task-H確定を前提として着手。
