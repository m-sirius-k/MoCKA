function New-MockaEventID {
    $date = Get-Date -Format "yyyyMMdd"
    $file = "C:\Users\sirok\MoCKA\runtime\event_counter.txt"

    if(!(Test-Path $file)){
        Set-Content $file 0
    }

    $n = [int](Get-Content $file)
    $n++

    Set-Content $file $n

    return "EV-$date-{0:D5}" -f $n
}

$eid = New-MockaEventID
$ts = [int](Get-Date -UFormat %s)

"$eid,system,heartbeat,ok,$ts" | Add-Content C:\Users\sirok\MoCKA\ledger\main\ledger.csv
