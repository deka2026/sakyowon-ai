# Recalculate a workbook in Hancell (HCell.Application COM), scan for formula errors
# and "mismatch" check cells, then save as .cell (or any extension Hancell supports).
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File hcell_recalc.ps1 -In "<path.xlsx>" -Out "<path.cell>" [-MismatchText "<text>"] [-DumpSheet <index> -DumpRows 40 -DumpCols 9]
# Notes: save this file as UTF-8 with BOM; keep non-ASCII literals out of this script (pass them as parameters).
param(
  [Parameter(Mandatory=$true)][string]$In,
  [Parameter(Mandatory=$true)][string]$Out,
  [string]$MismatchText = "",
  [int]$DumpSheet = 0,
  [int]$DumpRows = 0,
  [int]$DumpCols = 9
)
$ErrorActionPreference = "Continue"
if (-not (Test-Path $In)) { Write-Output "ERROR: input not found: $In"; exit 2 }
$app = New-Object -ComObject HCell.Application
$app.Visible = $false; $app.DisplayAlerts = $false
$wb = $app.Workbooks.Open($In)
if ($null -eq $wb) { Write-Output "ERROR: open failed"; $app.Quit(); exit 3 }
Write-Output ("opened: " + $wb.Name + " sheets=" + (($wb.Worksheets | ForEach-Object { $_.Name }) -join ", "))
$app.CalculateFull()
$err = 0; $mism = 0
foreach ($sh in $wb.Worksheets) {
  foreach ($cell in $sh.UsedRange.Cells) {
    $t = [string]$cell.Text
    if ($cell.HasFormula -and $t.StartsWith("#")) { $err++; if ($err -le 20) { Write-Output ("ERR " + $sh.Name + "!" + $cell.Address(0,0) + " " + $t + " [" + $cell.Formula + "]") } }
    if ($MismatchText -ne "" -and $t -eq $MismatchText) { $mism++; Write-Output ("MISMATCH " + $sh.Name + "!" + $cell.Address(0,0)) }
  }
}
Write-Output ("formula errors: " + $err + " ; mismatch cells: " + $mism)
if ($DumpSheet -gt 0 -and $DumpRows -gt 0) {
  $ws = $wb.Worksheets.Item($DumpSheet)
  Write-Output ("--- dump sheet " + $ws.Name)
  for ($r = 1; $r -le $DumpRows; $r++) {
    $line = @(); for ($c = 1; $c -le $DumpCols; $c++) { $line += [string]$ws.Cells.Item($r, $c).Text }
    $j = ($line -join " | "); if ($j.Trim(" |") -ne "") { Write-Output ("" + $r + ": " + $j) }
  }
}
$wb.Worksheets.Item(1).Activate()
$wb.SaveAs($Out)
Write-Output ("saved: " + $Out)
$wb.Close($false)
$app.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
if ($err -gt 0 -or $mism -gt 0) { exit 1 }
exit 0
