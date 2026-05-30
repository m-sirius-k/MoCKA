# vasAI Caliber作成ガイド

## Caliberとは

企業の社内システムとvasAIを繋ぐアダプター層。
`BaseCALIBER` を継承して5つのメソッドを実装するだけで完成する。

## 最小実装

```python
from caliber.base_caliber import BaseCALIBER
from core.models import ApprovalRule, Artifact, RiskLevel

class MyCompanyCALIBER(BaseCALIBER):

    def get_caliber_id(self) -> str:
        return "my_company_v1"

    def classify_event(self, raw_data: dict) -> str:
        # 自社のイベント種別 → ArtifactType
        return "message"

    def get_approval_rules(self) -> list[ApprovalRule]:
        return [
            ApprovalRule(rule_id="r1", risk_level=RiskLevel.NORMAL, auto_approve=True),
            ApprovalRule(rule_id="r2", risk_level=RiskLevel.HIGH, auto_approve=False,
                         approver_role="MANAGER"),
        ]

    def format_for_intranet(self, artifact: Artifact) -> dict:
        return {"system": "MY_SYSTEM", "data": artifact.content}

    def receive_from_intranet(self, data: dict) -> Artifact:
        return Artifact(
            artifact_type=self.classify_event(data),
            source_app="MY_SYSTEM",
            source_service="my_company",
            content=data,
        )
```

## 登録と使用

```python
from caliber.base_caliber import register
from my_caliber import MyCompanyCALIBER

register(MyCompanyCALIBER())

# 処理実行
caliber = MyCompanyCALIBER()
result = caliber.process_intranet_request({"key": "value"})
```

## 注意事項

- `send_to_vasai()` と `receive_from_vasai()` はオーバーライド禁止
- `get_caliber_id()` は一意な文字列を返すこと
- 全データはUTF-8で渡すこと
