# hwp_verify.ps1 - reopen a legacy .hwp and report page count + text length. ASCII only.
param([Parameter(Mandatory = $true)][string]$HwpxPath)
$ErrorActionPreference = 'Stop'
$full = (Resolve-Path -LiteralPath $HwpxPath).Path
$hwp = New-Object -ComObject HWPFrame.HwpObject
try { $hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule") } catch {}
try {
    $opened = $hwp.Open($full, "HWP", "forceopen:true")
    if (-not $opened) { throw "Open failed" }
    Write-Output ("pages=" + $hwp.PageCount)
    $txt = [System.IO.Path]::ChangeExtension($full, '.verify.txt')
    $null = $hwp.SaveAs($txt, "TEXT", "")
    Write-Output ("txt=" + $txt)
}
finally {
    try { $hwp.Quit() } catch {}
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($hwp) | Out-Null
}
