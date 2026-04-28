# MoCKA パターン登録 UTF-8版
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$great_items = @(
    "経営の最適解と現場の環境改善を同時に叶える",
    "ともに悩み、終決まで伴走し、経験値と自信につなげる",
    "技術より先に目的を教える",
    "情報の可用性が担保されている環境こそ戦略基盤になる",
    "今の事業に納得することなく、業界を牽引できる企業にしたい",
    "単一の方法では顧客要求は満たせない",
    "現場の暗黙知を理解し、机上の空論を防ぐ",
    "技術と人の間をつなぐ力を育てる",
    "技術者としての信頼感を保ちつつ、親しみやすい語り口",
    "道具が仕事に寄り添うという理想像",
    "意図を明確に伝えるための指令テンプレートを作る",
    "直感的に知識がなくとも利用できるUIで創造的に楽しみながら操作できる",
    "不確実な情報は書かない、知らないことは書かなくて良い",
    "情報に隠れた内容も深追いし、それを見つけ出せる",
    "制度・技術・信頼の三位一体設計",
    "設計段階から条例審査基準を反映する",
    "組織が大きくなれば管理コストが少なくなる",
    "トレーサビリティ問題はスケールと制度効率の関係として捉える",
    "ISO22000とトレーサビリティの共通目的はリスク低減と信頼性向上",
    "構造化贈答法による信頼設計"
)

$hint_items = @(
    "小さな成功体験を積ませる",
    "仮説思考を促す",
    "現場同行で空気・制約・動きを体感させる",
    "複数案を比較検討する力を養う",
    "文章を編集する際の文法・指令一覧を作る",
    "導入を短く、結論を先に、箇条書きにする構成指令",
    "断定を避けつつ丁寧に説明する",
    "専門用語に簡単な補足を加える",
    "BIMとトレーサビリティを連携させると視覚化と検索性が向上する",
    "内部記録と外部表示の役割を分けて考える",
    "制度・技術・装置を設計段階から儀式的に組み込む",
    "安全設計・制度対応・BCP評価を統合する",
    "地域条例との整合性を初期段階で確保",
    "深掘り要求は段階的にLayer1→2→3と宣言して展開する",
    "予算上限を固定し、その範囲内で最適化する方式に統一"
)

$incident_items = @(
    "単一企業では市場変化・技術革新に対応できない限界がある",
    "専用施設を作れば良いという短絡的発想は本末転倒",
    "現場の負担増加で優秀な人材が離れていく",
    "情報の鮮度が低いと判断が遅れ、機会損失が発生する",
    "外部情報がMoCKA文脈に混入した",
    "一般的な説明を先に返し、ユーザーの意図確認を怠った",
    "技術者が目的より手段を優先してしまう",
    "合計額が予算を超過し、再計算が複数回必要になった",
    "開発費の急激な削減は品質・納期リスクを伴う",
    "制度情報と技術情報が混在し、思想抽出が難しくなった"
)

function Send-Pattern($text, $type, $label, $endpoint) {
    $bodyObj = @{
        text      = $text
        what_type = $type
        source    = "past_chat_batch"
        label     = $label
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    }
    $bodyJson = [System.Text.Encoding]::UTF8.GetBytes(($bodyObj | ConvertTo-Json -Compress))
    try {
        $req = [System.Net.WebRequest]::Create("http://localhost:5000/$endpoint")
        $req.Method = "POST"
        $req.ContentType = "application/json; charset=utf-8"
        $req.ContentLength = $bodyJson.Length
        $stream = $req.GetRequestStream()
        $stream.Write($bodyJson, 0, $bodyJson.Length)
        $stream.Close()
        $res = $req.GetResponse()
        $res.Close()
        Write-Host "OK [$label] $($text.Substring(0,[Math]::Min(30,$text.Length)))..."
    } catch {
        Write-Host "NG [$label] $($text.Substring(0,[Math]::Min(20,$text.Length)))"
    }
    Start-Sleep -Milliseconds 300
}

Write-Host "`n== グレイト！送信中 =="
foreach ($t in $great_items) { Send-Pattern $t "success_great" "グレイト！" "success" }

Write-Host "`n== ヒント！送信中 =="
foreach ($t in $hint_items)  { Send-Pattern $t "success_hint"  "ヒント！"  "success" }

Write-Host "`n== インシデント！送信中 =="
foreach ($t in $incident_items) { Send-Pattern $t "incident" "インシデント！" "collect" }

Write-Host "`n== 完了 =="
Write-Host "グレイト: $($great_items.Count)件"
Write-Host "ヒント:   $($hint_items.Count)件"
Write-Host "インシデント: $($incident_items.Count)件"
