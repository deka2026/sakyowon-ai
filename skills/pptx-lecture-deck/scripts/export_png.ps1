# Export every slide of a PPTX to PNG using installed PowerPoint (COM).
# Rendering is the only reliable way to spot Korean text overflow in python-pptx decks.
#
#   powershell -File export_png.ps1 -Deck "D:\path\deck.pptx" -OutDir "C:\tmp\png1"
#
# Notes:
#   - Do NOT set $app.Visible = $true : PowerPoint COM expects MsoTriState, a boolean throws.
#   - Always export into a NEW folder per iteration; deleting old output may be blocked.
#   - Console may show Korean paths as mojibake; the files themselves are fine.

param(
    [Parameter(Mandatory = $true)][string]$Deck,
    [Parameter(Mandatory = $true)][string]$OutDir,
    [int]$Width = 1600,
    [int]$Height = 900
)

if (-not (Test-Path $Deck)) { throw "Deck not found: $Deck" }
New-Item -ItemType Directory -Force $OutDir | Out-Null

$app = New-Object -ComObject PowerPoint.Application
try {
    # Open(path, ReadOnly, Untitled, WithWindow)
    $pres = $app.Presentations.Open($Deck, $true, $false, $false)
    try {
        $pres.Export($OutDir, "PNG", $Width, $Height)
    }
    finally {
        $pres.Close()
    }
}
finally {
    $app.Quit()
}

Get-ChildItem $OutDir -Filter *.PNG | Measure-Object | ForEach-Object {
    Write-Output ("exported {0} slides -> {1}" -f $_.Count, $OutDir)
}
