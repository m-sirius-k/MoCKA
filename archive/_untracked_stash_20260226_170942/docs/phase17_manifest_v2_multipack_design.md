Phase17 Manifest v2 多pack決定規則設計

1\. authoritative pack 選定規則



freeze\_manifest.verify\_packs 配列順を優先順位とする



"authoritative": true を持つ pack が存在すれば最優先



重複 row\_id 発生時：



authoritative pack 優先



同順位の場合は sha256 昇順固定



2\. row 重複解決規則



同一 row\_id が複数packに存在する場合：



決定キー：

(

pack\_priority,

pack\_sha256,

row\_sha256

)



最小辞書順を正とする



3\. summary\_matrix 決定性保証



入力：



freeze\_manifest.json



verify\_packs 内 pack 群



各 pack 内 row



出力：



summary\_matrix.json



同一入力 → 同一出力（hash一致）



4\. 破壊検知条件



以下が変化した場合 FAIL：



pack順序



authoritative指定



row内容



sha256不一致



5\. 次実装対象

verify/manifest\_resolver.py 新規作成



工程2：resolver骨格実装

