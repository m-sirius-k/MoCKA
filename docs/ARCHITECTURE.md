# MoCKA Architecture Diagram



## Architecture Overview



`mermaid
flowchart TB

subgraph INFIELD\["INFIELD Deterministic Domain"]

A\[MoCKA Core]
B\[Decision Engine]
C\[Artifact Generator]

A --> B
B --> C

end



subgraph MEMORY\["Institutional Memory"]

D\[Knowledge Gate]
E\[Reasoning Trace]
F\[Decision Records]

D --> E
E --> F

end



subgraph OUTFIELD\["Transparency Domain"]

G\[Transparency Repository]
H\[Verification Packs]
I\[Public Audit]

G --> H
H --> I

end



subgraph EXTERNAL\["External Interaction"]

J\[External Brain]
K\[External Systems]

J --> K

end



C --> G
F --> G
I --> J

ENGLISH EXPLANATION

MoCKA separates operational domains in order to guarantee deterministic governance and independent verification.

Infield

The canonical execution environment where decisions and artifacts are generated.

Institutional Memory

The knowledge preservation layer that records reasoning traces and governance artifacts.

Outfield

The transparency layer where artifacts are published and independently verified.

External Brain

A controlled interoperability gateway for interaction with external systems.

日本語説明

MoCKA アーキテクチャは決定論的統治と独立検証を保証するために運用領域を分離する。

Infield

意思決定と成果物が生成される正本実行環境。

Institutional Memory

推論過程と統治成果物を保存する制度的記憶層。

Outfield

成果物が公開され外部検証が行われる透明性層。

External Brain

外部システムとの安全な接続を管理する相互運用ゲート。

