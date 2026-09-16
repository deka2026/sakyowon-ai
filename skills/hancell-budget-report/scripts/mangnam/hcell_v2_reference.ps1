$ErrorActionPreference = "Continue"
$p = "D:\2026 사업\월간보고\8월\망남 어촌신활력증진사업_예산 집행현황(2023~2026).xlsx"
$out = "D:\2026 사업\월간보고\8월\망남 어촌신활력증진사업_예산 집행현황(2023~2026).cell"
$app = New-Object -ComObject HCell.Application
$app.Visible = $false; $app.DisplayAlerts = $false
$wb = $app.Workbooks.Open($p)
"opened: sheets=" + (($wb.Worksheets | ForEach-Object { $_.Name }) -join ", ")
$app.CalculateFull()
$err = 0; $mism = 0
foreach ($sh in $wb.Worksheets) {
  foreach ($cell in $sh.UsedRange.Cells) {
    $t = [string]$cell.Text
    if ($cell.HasFormula -and $t.StartsWith("#")) { $err++; if ($err -le 15) { "ERR $($sh.Name)!$($cell.Address(0,0)) $t  [$($cell.Formula)]" } }
    if ($t -eq "불일치") { $mism++; "MISMATCH $($sh.Name)!$($cell.Address(0,0))" }
  }
}
"formula errors: $err ; mismatch cells: $mism"
function Dump($ws, $r0, $r1, $nc) { for ($r=$r0; $r -le $r1; $r++) { $line=@(); for ($c=1; $c -le $nc; $c++) { $line += [string]$ws.Cells.Item($r,$c).Text }; $j=($line -join " | "); if ($j.Trim(" |") -ne "") { "$r`: $j" } } }
"--- 총괄"; Dump $wb.Worksheets.Item("총괄") 6 40 16
"--- 2024예산"; Dump $wb.Worksheets.Item("2024예산") 5 19 9

$wb.Worksheets.Item("총괄").Activate()
$wb.SaveAs($out); "saved: $out"
$wb.Close($false); $app.Quit(); "done"