# Satellite Repository Architecture v1.0 - Constitution

位置づけ: 博士裁定(2026-07-03、SATELLITE_REPOSITORY_ARCHITECTURE_v1.0_DRAFT.md補強版=分類体系節+依存関係1行追記を含む版に基づく条件付き承認)に基づき確定。DRAFT.mdは削除せず、検討過程の参照履歴として保持する。

実装・コード変更は一切含まない。既存ファイルの上書きは行わない。

---

## 博士裁定ログ(承認記録)

2026-07-03、博士より以下の裁定が示された。DRAFT補強版に記載したくろこ提案6項目がそのまま採用された。

| 項目 | 裁定 | 備考 |
|---|---|---|
| mocka-civilization | Integration Policy = C(Boundary-Coexist) | |
| mocka-external-brain | Integration Policy = C(Boundary-Coexist) | |
| mocka-transparency | Integration Policy = C(Boundary-Coexist) | |
| MoCKA-KNOWLEDGE-GATE | Integration Policy = C(Boundary-Coexist) | |
| Prevention不在(5番目) | 診断B(本来欠落)+ アクション: 新規衛星リポジトリを追加する | 診断とアクションの階層分離を維持したまま確定 |
| Audit/Institutionalize(8番目)二重主張 | C(二層分離維持) | Task-I表記では選択肢A相当。ラベル不一致は本文(第3部)に明記 |

**必須条件注記(4衛星リポジトリ共通・省略不可):** Cは境界共存の暫定安定配置であり、最終確定状態ではない。Operational State(①)が将来確定した場合、Integration Policy(②)の意味解釈が変わりうる。本CONSTITUTIONはこの暫定性を前提として成立する。

---

## 分類体系

DRAFTから移行(変更なし)。

- **①Operational State(Task-I由来)**: 現役 / 統合済み・凍結 / 将来再利用 / 保守停止。Task-I第4部が4衛星リポジトリ共通の枠組みとして支持根拠・反証を整理済み。ただし、Task-Iはこの4選択肢についてリポジトリごとの支持・反証を整理したのみで、個別リポジトリへの確定当てはめは行っていない(Task-I第5部「最終的な当てはめの決定は博士が行う」と明記)。加えてTask-I第3部では、リポジトリごとに「候補1/候補2/候補3」という複数の暫定候補が未確定のまま列挙されている。したがって①には現時点で単一の確定値が存在しない
- **②Integration Policy(本CONSTITUTION由来)**: A=Active(コアへ統合)/ B=Frozen(凍結)/ C=Boundary-Coexist(境界明示による共存)。DECISION_RULE_LAYER_v1.0.md類型4(モジュール境界問題)の裁定語彙(統合/境界明示による共存/凍結)を、各衛星リポジトリに適用した軸
- **③Structural Attribute(補助・現状未使用)**: 通常 / 境界保持(overlay)。「通常」は当該リポジトリが単独で完結した実装単位であることを指す。「境界保持(overlay)」は、他リポジトリの機能に薄く重なる形で存在し、境界情報自体の保持・提示を主目的とする実装であることを指す。本節は定義のみを行い、今回の4衛星裁定では適用対象なし(4リポジトリいずれも「通常」に該当し、全て②Integration Policyの枠組みで完結する)

②Integration Policyは①Operational Stateの値に依存せず定義されるが、その意味解釈は①の値によって変化する(例: ①=現役×②=Boundary-Coexistは並列運用、①=保守停止×②=Boundary-Coexistは意味保持のみのアーカイブ構造、というように、同じ②の値でも①との組み合わせで解釈が異なる)。この暫定性ゆえに、以下の4リポジトリ裁定はいずれも「Cは暫定安定配置」という条件付きで確定する(①Operational Stateが未確定のため)。

---

## 第1部: 4衛星リポジトリのIntegration Policy - 確定

対象: mocka-civilization / mocka-external-brain / mocka-transparency / MoCKA-KNOWLEDGE-GATE(いずれも最終update 96日前・同一タイムスタンプ)。①Operational Stateは引き続き未確定(Task-I候補のまま)。

### mocka-civilization

①Operational State(Task-I候補、未確定): 候補1(Active Development) / 候補2(Stable) / 候補3(Frozen)。

確定: **Integration Policy = C(Boundary-Coexist)**(暫定安定配置)。理由: A(統合)・B(Frozen)いずれの判断材料も「要確認」のまま確定していない。判断材料が両側とも不十分な状態でA・Bいずれかに倒すより、現状維持+境界明示を取り、必要な追加調査(ディレクトリ中身・採番規則の確認)を別途行う方がリスクが小さい。

### mocka-external-brain

①Operational State(Task-I候補、未確定): 候補1(Active Development) / 候補2(Stable) / 候補3(Frozen)。

確定: **Integration Policy = C(Boundary-Coexist)**(暫定安定配置)。理由: 「合議プロトコル」という機能自体はコア側Decision Layerと異なる粒度(複数AI間の合議)を持つと考えられ、統合すると責務が混同される懸念がある。ただし語の重複(「Decision」)自体が境界の曖昧さを示す可能性もあり、この点は要確認のまま残る。

### mocka-transparency

①Operational State(Task-I候補、未確定): 候補1(Active Development) / 候補2(統合済み・凍結寄り) / 候補3(Frozen)。

確定: **Integration Policy = C(Boundary-Coexist)**(暫定安定配置)。理由: 4リポジトリの中で最も統合(重複)の具体的根拠(SHA256ハッシュチェーンの技術一致)があるからこそ、外部監査ログとしての独立性(コア内部プロセスと同一実装であっても、外部から独立して参照・検証できること自体に価値がある)を優先し、技術重複の検証は別途行う方が安全。

### MoCKA-KNOWLEDGE-GATE

①Operational State(Task-I候補、未確定): 候補1(Active Development) / 候補2(将来再利用) / 候補3(Frozen)。

確定: **Integration Policy = C(Boundary-Coexist)**(暫定安定配置)。理由: 技術スタックの相違(参考情報、要確認: JavaScript/Firebase/Docker vs コア本体Python)は統合コストの高さを示唆しており、記録監査専用レイヤーとして独立運用する方が現実的。ただし裏付けがローカル管理文書由来のみであるため、確認の余地を残す。

---

## 第2部: Prevention不在(5番目)の裁定 - 確定

診断: **B(本来欠落)**。他の7段階すべてに対応する衛星リポジトリが存在する中、5番目だけが実装(コア内`preventive_rule_engine`)はあるがリポジトリを持たないという非対称性は、Cのように他リポジトリへの分散内包で説明するには裏付けが不足しており、Aのように意図的設計と見るには他段階との対称性の欠如を説明できない。

アクション: **新規衛星リポジトリを追加する**。本体統合(選択肢Aの延長)は本体の過密化を招く。既存衛星への分散内包(選択肢Cの延長)は機能の所在を不可視化する。独立した新規レイヤーとして明示的に追加する方が、他の7段階との対称性を保てる。

診断とアクションは階層の異なる別問題として分離したまま確定する(診断=なぜ不在か、アクション=今後どうするか)。新規衛星リポジトリの具体名・実装着手は本CONSTITUTIONの範囲外であり、別途裁定を要する。

---

## 第3部: Audit/Institutionalize(8番目)の二重主張の裁定 - 確定

確定: **C(二層分離維持)**。AuditとInstitutionalizeは性質の異なる作業であり、統合すると両者の意味が失われる。番号の再整理(Task-I選択肢B)はREADME変更という実装作業を伴い本裁定の範囲を超えるため、性質の違いを明文化した上で両者を維持する。

ラベル対応の注記: 本項の「C(二層分離維持)」は、Task-I(SATELLITE_REPOSITORY_POSITIONING_OPTIONS_v0.1.md)の選択肢A(「8番目は内部の制度化と外部への公開という2つの並行した出力先を持つ意図的な設計」)に相当する。Task-I自身の選択肢Cとは異なる内容である点に注意。

---

## 改訂履歴

- v1.0(2026-07-03): 博士裁定を反映し確定。SATELLITE_REPOSITORY_ARCHITECTURE_v1.0_DRAFT.md(補強版)からの移行。DRAFT.mdは参照履歴として保持。
