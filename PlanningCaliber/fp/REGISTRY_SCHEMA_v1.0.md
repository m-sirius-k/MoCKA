# REGISTRY_SCHEMA_v1.0

KN-004: Registry Schema (KN-003の機械可読化)

対象: KN-003(REGISTRY_RECORD_SPEC_v1.0.md, docs/governance/REGISTRY_RECORD_SPEC_v1.0.md)
が定めたRecordの5情報カテゴリ(Identity/Reference/Classification/Lifecycle/Metadata)を
JSON Schemaとして機械可読形式に変換したものである。

但し書き: KN-004はKN-003の構造をそのまま変換したものであり、新たな設計判断を含まない。
KN-003に明示されていない制約(バリデーションルール等)はKN-005(Validation)の範囲であり、
本文書には含めない。Statusの詳細な状態遷移(遷移条件・許可方向)はKN-006の範囲であり、
本文書には含めない。

---

## JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MoCKA Registry Record Schema v1.0",
  "type": "object",
  "required": ["identity", "reference", "classification", "lifecycle", "metadata"],
  "properties": {
    "identity": {
      "type": "object",
      "description": "KN-003 1-1 Identity: Registry内でRecordを一意に識別するための情報",
      "required": ["identifier"],
      "properties": {
        "identifier": {
          "type": "string",
          "description": "Registry内でRecordを一意に識別する識別子(Identifier)。命名体系・形式の詳細はKN-003本文に具体的定義がなく、本文書でも未確定のまま残す"
        }
      }
    },
    "reference": {
      "type": "object",
      "description": "KN-003 1-2 Reference: Artifactの場所・参照先を示す情報",
      "required": ["location", "artifact_key"],
      "properties": {
        "location": {
          "type": "string",
          "description": "Artifactの格納場所を示す情報(ファイルパス・URL等)。具体的な形式制約(URI形式か等)はKN-003に明記がなく未確定"
        },
        "artifact_key": {
          "type": "string",
          "description": "Artifactを識別するための参照キー(Artifact固有の識別子等)"
        },
        "source_reference": {
          "type": "string",
          "description": "SourceがArtifactとして外部に存在する場合の参照情報。KN-003原文で条件付き(該当する場合)と明記されているため必須項目に含めない"
        }
      }
    },
    "classification": {
      "type": "object",
      "description": "KN-003 1-3 Classification: このRecordがどの種類のArtifactを指しているかを示す情報",
      "required": ["artifact_type", "category"],
      "properties": {
        "artifact_type": {
          "type": "string",
          "description": "Artifactの種別(KN-001セクション2の登録対象種別: DOCUMENT/EVENT/DECISION/POLICY/SPEC等)。KN-003原文が'等'としており列挙が非網羅的であることが明記されているため、closed enumにするかは本文書時点で未確定"
        },
        "category": {
          "type": "string",
          "description": "Artifactが属するCategory(DP/GV/KN等、KN-002で確立した体系に対応)。KN-003原文で'等'とあり非網羅的"
        },
        "series": {
          "type": "string",
          "description": "Artifactが属するSeries(KN-002で確立した体系に対応)。Category/Seriesは別階層の分類情報とKN-003に明記"
        },
        "series_number": {
          "type": "string",
          "description": "Series内での番号・順序に関する情報。KN-003原文で'該当する場合'と条件付きと明記されているため必須項目に含めない"
        }
      }
    },
    "lifecycle": {
      "type": "object",
      "description": "KN-003 1-4 Lifecycle: Recordの生存状態を管理する情報。Artifactのライフサイクルではなく、Record自身の生存状態を表す(KN-003原文で明記)",
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["Draft", "Review", "Approved", "Deprecated", "Archived"],
          "description": "Recordの状態。KN-001セクション5で予告されたDraft/Review/Approved/Deprecated/Archivedが基本形とKN-003に明記。詳細な状態遷移(遷移条件・許可方向)はKN-006の範囲であり本文書では扱わない"
        },
        "status_changed_at": {
          "type": "string",
          "description": "状態が変化した時点に関する情報。日時形式の制約はKN-003に明記がなく未確定"
        }
      }
    },
    "metadata": {
      "type": "object",
      "description": "KN-003 1-5 Metadata: Record自体の管理に必要な補助的情報。Artifactの内容に関する情報は含まない(KN-003原文で明記)",
      "required": ["created_at", "updated_at", "created_by"],
      "properties": {
        "created_at": {
          "type": "string",
          "description": "Recordが作成された日時に関する情報。日時形式の制約はKN-003に明記がなく未確定"
        },
        "updated_at": {
          "type": "string",
          "description": "Recordが最後に更新された日時に関する情報。日時形式の制約はKN-003に明記がなく未確定"
        },
        "created_by": {
          "type": "string",
          "description": "Recordを作成した主体に関する情報(くろこ等のAI識別子、または人間起草者)"
        }
      }
    }
  }
}
```

---

## 対応表(KN-003の記述からの導出根拠)

| フィールド | KN-003該当箇所(原文引用の要約) | required判定の根拠 |
|---|---|---|
| identity.identifier | 1-1 "Registryの中でRecordを一意に識別する識別子(Identifier)に関する情報" "IdentityがなければRecordを特定できず、検索・参照・更新のいずれも成立しない" | 必須。原文が特定・検索・参照・更新すべての前提と明記 |
| reference.location | 1-2 "Artifactの格納場所を示す情報(ファイルパス・URL等)" | 必須と判断(Referenceは"Recordの中核をなす情報カテゴリ"と明記されており、条件付きの記述がないため)。ただし必須である旨の直接的な明文はKN-003になく、本文書側の推定判断であることに留意 |
| reference.artifact_key | 1-2 "Artifactを識別するための参照キー(Artifact固有の識別子等)" | locationと同様、条件付きの記述がないため必須と判断。同様に推定判断である点に留意 |
| reference.source_reference | 1-2 "SourceがArtifactとして外部に存在する場合、その参照情報" | "場合"と条件付きが明記されているため任意 |
| classification.artifact_type | 1-3 "Artifact Type: Artifactの種別を示す情報(...DOCUMENT/EVENT/DECISION/POLICY/SPEC等)" | 必須と判断(分類の主軸であるため)。ただし必須の直接明文はなく推定判断 |
| classification.category | 1-3 "Category/Series: ArtifactがどのCategory(DP/GV/KN等)・Seriesに属するかを示す情報" | 同上、推定判断 |
| classification.series | 1-3 同上(Category/Seriesの記述内) | "該当する場合"の条件明記はseries_number側にのみあるため、seriesとseries_numberで扱いを分けたが、series自体の必須/任意もKN-003に明記なし。任意として扱った(推定判断) |
| classification.series_number | 1-3 "Series内での番号・順序に関する情報(該当する場合)" | "該当する場合"と条件付きが明記されているため任意 |
| lifecycle.status | 1-4 "Recordの状態(Status)に関する情報" "KN-001セクション5で予告されたDraft/Review/Approved/Deprecated/Archivedが基本形" | 必須。Lifecycleの目的そのものであるため |
| lifecycle.status_changed_at | 1-4 "状態が変化した時点に関する情報(いつ状態が変わったか)" | 必須/任意の直接明文なし。任意として扱った(推定判断) |
| metadata.created_at | 1-5 "Recordが作成された日時に関する情報" | 必須と判断(全Recordに作成日時は存在するため)。ただし必須の直接明文はなく推定判断 |
| metadata.updated_at | 1-5 "Recordが最後に更新された日時に関する情報" | 同上、推定判断 |
| metadata.created_by | 1-5 "Recordを作成した主体に関する情報(くろこ等のAI識別子、または人間起草者)" | 同上、推定判断 |

---

## 未確定事項(KN-005以降で扱う項目、内容には踏み込まない)

- Identifierの命名規則・形式の詳細(KN-003 Phase2 Scope Freeze表に"KN-004の範囲"と明記されているが、KN-003本文に具体的な命名規則の記述がないため、本文書でも未確定のまま)
- Reference(location)の形式制約(URI形式か等)
- artifact_type・categoryをclosed enumにするか非網羅なstring setとして扱うか(KN-003原文の'等'表記との整合)
- 日時フィールド(status_changed_at/created_at/updated_at)の具体的な日時形式
- reference/classification/metadataの各サブフィールドについて、上記対応表で"推定判断"と注記したrequired/optionalの妥当性確認
- Metadata"ラベル・タグ等の補助的な分類情報"はKN-003原文で"(将来検討)"と明記されているため、本スキーマには含めていない
- Validator・整合性検証ルール全般(KN-005の範囲)
- Statusの詳細な状態遷移(遷移条件・許可方向)(KN-006の範囲)
