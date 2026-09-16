# Export a .pptx (PowerPoint COM) or .docx (Word COM) to PDF. ASCII only.
#   powershell -NoProfile -File export_pdf.ps1 -Src "D:\x.pptx" -Out "D:\x.pdf"
param([Parameter(Mandatory=$true)][string]$Src, [Parameter(Mandatory=$true)][string]$Out)
if (-not (Test-Path $Src)) { throw "not found: $Src" }
$ext = [IO.Path]::GetExtension($Src).ToLower()
if ($ext -eq '.pptx') {
    $app = New-Object -ComObject PowerPoint.Application
    try {
        $p = $app.Presentations.Open($Src, $true, $false, $false)
        try { $p.SaveAs($Out, 32) } finally { $p.Close() }   # 32 = ppSaveAsPDF
    } finally { $app.Quit() }
} elseif ($ext -eq '.docx') {
    $app = New-Object -ComObject Word.Application
    $app.Visible = $false
    try {
        $d = $app.Documents.Open($Src, $false, $true)
        try {
            $d.SaveAs2($Out, 17)                                  # 17 = wdFormatPDF
            Write-Output ("pages=" + $d.ComputeStatistics(2))     # 2 = wdStatisticPages
        } finally { $d.Close(0) }
    } finally { $app.Quit() }
} else { throw "unsupported: $ext" }
Write-Output ("pdf=" + $Out)
