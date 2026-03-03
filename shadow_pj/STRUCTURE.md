========================
Shadow Project Structure
========================

ENGLISH VERSION
------------------------

Directory Layout

shadow_pj/
笏・笏懌楳笏 README.md
笏懌楳笏 GOVERNANCE.md
笏懌楳笏 STRUCTURE.md
笏・笏披楳笏 visual/
    笏懌楳笏 VAR_INDEX.json
    笏懌楳笏 *.md
    笏披楳笏 *.svg

Purpose of Each Layer

README.md
High-level explanation and entry point.

GOVERNANCE.md
Non-interference rules and promotion discipline.

STRUCTURE.md
Defines boundaries and folder intent.

visual/
Contains the Visual Asset Registry (VAR).
Purely descriptive and deterministic artifacts.

Isolation Guarantee

This project:
- does not modify MoCKA core
- does not inject runtime hooks
- does not alter CI pipelines
- does not contain operational secrets

All outputs must remain byte-stable.


==================================================
譌･譛ｬ隱樒沿
==================================================

繝・ぅ繝ｬ繧ｯ繝医Μ讒矩

shadow_pj/
笏・笏懌楳笏 README.md
笏懌楳笏 GOVERNANCE.md
笏懌楳笏 STRUCTURE.md
笏・笏披楳笏 visual/
    笏懌楳笏 VAR_INDEX.json
    笏懌楳笏 蜷・ｨｮ .md
    笏披楳笏 蜷・ｨｮ .svg

蜷・ｱ､縺ｮ諢丞袖

README.md
蜈･蜿｣隱ｬ譏弱よ晄Φ縺ｨ讎りｦ√・
GOVERNANCE.md
髱槫ｹｲ貂芽ｦ丞ｾ九→譏・ｼ譚｡莉ｶ縲・
STRUCTURE.md
蠅・阜螳｣險譖ｸ縲よｧ矩諢丞峙縺ｮ譏守､ｺ縲・
visual/
蜿ｯ隕冶ｳ・肇繝ｬ繧ｸ繧ｹ繝医Μ縲・豎ｺ螳夂噪縺ｧ隱ｬ譏主ｰら畑縺ｮ謌先棡迚ｩ縺ｮ縺ｿ菫晄戟縲・
髫秘屬菫晁ｨｼ

譛ｬ繝励Ο繧ｸ繧ｧ繧ｯ繝医・・・
繝ｻMoCKA譛ｬ菴薙ｒ螟画峩縺励↑縺・繝ｻ繝ｩ繝ｳ繧ｿ繧､繝縺ｫ繝輔ャ繧ｯ縺励↑縺・繝ｻCI繧呈隼螟峨＠縺ｪ縺・繝ｻ遘伜ｯ・ュ蝣ｱ繧貞性縺ｾ縺ｪ縺・
蜈ｨ謌先棡迚ｩ縺ｯ繝舌う繝亥ｮ牙ｮ壹〒縺ｪ縺代ｌ縺ｰ縺ｪ繧峨↑縺・・
