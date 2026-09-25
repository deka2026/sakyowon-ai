# hwpx_to_hwp.ps1 - convert .hwpx to legacy .hwp via Hangul COM. ASCII only.
param(
    [Parameter(Mandatory = $true)][string]$HwpxPath,
    [string]$HwpPath
)
$ErrorActionPreference = 'Stop'
$full = (Resolve-Path -LiteralPath $HwpxPath).Path
if (-not $HwpPath) { $HwpPath = [System.IO.Path]::ChangeExtension($full, '.hwp') }

$hwp = New-Object -ComObject HWPFrame.HwpObject
try { $hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule") } catch {}
try {
    $opened = $hwp.Open($full, "HWPX", "forceopen:true")
    if (-not $opened) { throw "Open failed: $full" }
    Write-Output ("pages=" + $hwp.PageCount)
    if (Test-Path -LiteralPath $HwpPath) { Remove-Item -LiteralPath $HwpPath -Force }
    $null = $hwp.SaveAs($HwpPath, "HWP", "")
    Write-Output ("hwp=" + $HwpPath)
}
finally {
    try { $hwp.Quit() } catch {}
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($hwp) | Out-Null
}
