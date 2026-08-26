# hwpx_pagecount.ps1 - measure page count of an .hwpx via Hangul COM, optionally export PDF
#
#   & scripts\hwpx_pagecount.ps1 -HwpxPath "out.hwpx"
#   & scripts\hwpx_pagecount.ps1 -HwpxPath "out.hwpx" -Pdf
#   & scripts\hwpx_pagecount.ps1 -HwpxPath "out.hwpx" -Pdf -PdfPath "check.pdf"
#
# Requires Hangul (HWPFrame.HwpObject) installed. ASCII only - no Korean literals in .ps1.
# One file per invocation: a foreach loop over several files hangs the COM server.

param(
    [Parameter(Mandatory = $true)][string]$HwpxPath,
    [switch]$Pdf,
    [string]$PdfPath,
    [switch]$KillStale
)

$ErrorActionPreference = 'Stop'

$full = (Resolve-Path -LiteralPath $HwpxPath).Path
if (-not $PdfPath) { $PdfPath = [System.IO.Path]::ChangeExtension($full, '.pdf') }

if ($KillStale) {
    try { Get-Process Hwp -ErrorAction SilentlyContinue | Stop-Process -Force } catch {}
    Start-Sleep -Seconds 2
}

$hwp = New-Object -ComObject HWPFrame.HwpObject
try { $hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule") } catch {}

try {
    $opened = $hwp.Open($full, "HWPX", "forceopen:true")
    if (-not $opened) { throw "Open failed: $full" }

    $pages = $hwp.PageCount
    Write-Output ("pages=" + $pages)

    if ($Pdf) {
        if (Test-Path -LiteralPath $PdfPath) { Remove-Item -LiteralPath $PdfPath -Force }
        $null = $hwp.SaveAs($PdfPath, "PDF", "")
        Write-Output ("pdf=" + $PdfPath)
    }
}
finally {
    try { $hwp.Quit() } catch {}
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($hwp) | Out-Null
}
