# MoCKA Paper — Section 2.4: Related Work
# Generated: 2026-04-03 | Updated: 2026-04-05

## 2.4 Related Work

MoCKA は以下の4つの研究領域と関わりを持つが、それぞれの限界を超える独自の立場を取る。

### 2.4.1 説明可能AI（Explainable AI / XAI）

説明可能AIは、ブラックボックスモデルの意思決定過程を人間に理解可能な形で提示することを目的とする研究領域である [Mersha et al., 2024]。SHAP・LIMEを代表とするpost-hoc説明手法は、個別の予測に対して事後的な解釈を与えるが、意思決定の経緯そのものを制度的に記録・追跡する機能を持たない。

Swamy et al. (2023) は、post-hoc説明アプローチの限界を指摘し、「解釈可能性はモデル設計に内在すべき」と主張する。MoCKAはこの方向性をさらに推し進め、説明可能性を事後的付加機能ではなく、システム設計の中核原則として実装する。

**MoCKAの差異：** XAIはモデルの出力を説明するが、MoCKAはモデルが関与した全決定ループを記録する。説明ではなく証拠の製造が目的である。

### 2.4.2 AIガバナンスフレームワーク

NIST AI Risk Management Framework (AI RMF 1.0, 2023) は、AIシステムのリスクを Govern / Map / Measure / Manage の4機能で管理する自発的フレームワークである [Tabassi, 2023]。説明責任・透明性・追跡可能性を核心的特性として規定する。

**MoCKAの差異：** NIST RMFを参照基準として位置づけつつ、MoCKAはその原則を events.csv + SHA-256ハッシュチェーン + Ed25519ガバナンス署名という具体的技術スタックに落とし込んだ実装事例である。ポリシーをコードに変換する。

### 2.4.3 マルチエージェントシステムのガバナンス

マルチエージェントシステムは2026年現在、企業AIの主要アーキテクチャとなりつつある [Databricks, 2026]。複数の専門エージェントが分業・連携するアーキテクチャは、単一エージェントを超えた説明責任の問題を生む。

**MoCKAの差異：** MoCKAの4AI並列合議システム（mocka_orchestra）は、各AI（Claude / GPT / Gemini / Copilot）の出力に対してスコアリング関数（Score = Accuracy×w1 + Consistency×w2 + Novelty×w3 + Safety×w4）を適用し、合議結果をevents.csvに記録する。複数AIの協働を制度化した実装レベルの回答である。

### 2.4.4 知識の永続化と外部記憶

LLMは本質的に会話コンテキスト外の記憶を持たない。RAGや外部データベース統合は検索の効率化に主眼を置き、記録の制度化には踏み込まない。

**MoCKAの差異：** MoCKAは知識を「検索対象」としてではなく、「文明的資産」として扱う。四種の記憶型（手続き的・意味的・技能的・エピソード的）を明示的に分類し、ガバナンス署名によって記録の真正性を保証する。知識の制度的継承を目指す設計である。

### 2.4.5 本研究の位置づけ

「AIを信じるな、システムで縛れ（Do Not Trust AI; Constrain It by System）」というMoCKAの核心命題は、既存フレームワークがAIシステムへの信頼を前提として改善を図る（trust-and-verify）のに対し、信頼そのものを設計の対象外に置く（distrust-and-institutionalize）という根本的な立場の転換を示す。この転換点がMoCKAの最大の新規性である。

## References

1. Mersha, M. et al. (2024). Explainable Artificial Intelligence: A Survey of Needs, Techniques, Applications, and Future Direction. arXiv:2409.00265.
2. Swamy, V. et al. (2023). The future of human-centric eXplainable Artificial Intelligence (XAI) is not post-hoc explanations. arXiv:2307.00364.
3. Bilal, A. et al. (2025). LLMs for Explainable AI: A Comprehensive Survey. arXiv:2504.00125.
4. Tabassi, E. (2023). Artificial Intelligence Risk Management Framework (AI RMF 1.0). NIST AI 100-1.
5. NIST. (2024). AI Risk Management Framework: Generative AI Profile. NIST AI 600-1.
6. Databricks. (2026). State of AI Agents 2026: Lessons on Governance, Evaluation and Scale.
7. AIGOV @ AAAI. (2026). 3rd International Workshop on AI Governance: Alignment, Morality, Law, and Design.
