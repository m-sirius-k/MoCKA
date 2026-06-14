"""
MoCKA Core Kernel — prism.models.schema_version

責務:
  Prism出力モデル(Context/Observation/CognitiveState/SemanticAnnotation)
  共通のスキーマバージョン定数。

  各モデルのto_dict()はこのバージョンを"version"フィールドとして含む。
  モデルの構造を変更する場合は、このバージョンを更新すること。
"""

PRISM_OUTPUT_SCHEMA_VERSION = "1.0"
