$root="C:\Users\sirok\MoCKA"

$mainLedger="$root\ledger\main\ledger.csv"
$shadowLedger="$root\ledger\shadow\ledger.csv"

Write-Host "MoCKA Shadow Observer START"

$last = (Get-Content $shadowLedger).Count

while($true){

 if(Test-Path $mainLedger){

  $mainLines = Get-Content $mainLedger

  if($mainLines.Count -gt $last){

   $newLines = $mainLines[$last..($mainLines.Count-1)]

   foreach($line in $newLines){
    Add-Content $shadowLedger $line
   }

   Write-Host "SYNC:" $newLines.Count "events"

   $last = $mainLines.Count
  }

 }

 Start-Sleep 2
}
