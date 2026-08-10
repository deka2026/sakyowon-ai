param(
  [Parameter(Mandatory=$true)][string]$SourceHwpx,
  [Parameter(Mandatory=$true)][string]$UnpackedDir,
  [Parameter(Mandatory=$true)][string]$OutHwpx,
  [string[]]$Entries = @('Contents/section0.xml','Contents/header.xml')
)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

# validate all replacement files parse as XML
foreach ($e in $Entries) {
  $f = Join-Path $UnpackedDir ($e -replace '/','\')
  if (-not (Test-Path $f)) { throw "missing: $f" }
  $d = New-Object System.Xml.XmlDocument
  $d.Load($f) | Out-Null
}
Write-Output "All replacement XML files valid."

if (Test-Path $OutHwpx) { Remove-Item -Force $OutHwpx }
Copy-Item -LiteralPath $SourceHwpx -Destination $OutHwpx

$zip = [System.IO.Compression.ZipFile]::Open($OutHwpx, [System.IO.Compression.ZipArchiveMode]::Update)
try {
  foreach ($e in $Entries) {
    $src = Join-Path $UnpackedDir ($e -replace '/','\')
    $entry = $zip.GetEntry($e)
    if ($entry -eq $null) { throw "zip entry not found: $e" }
    $comp = $entry.CompressionLevel
    $entry.Delete()
    $new = $zip.CreateEntry($e, [System.IO.Compression.CompressionLevel]::Optimal)
    $bytes = [System.IO.File]::ReadAllBytes($src)
    $s = $new.Open()
    $s.Write($bytes, 0, $bytes.Length)
    $s.Close()
    Write-Output ("replaced: " + $e + "  (" + $bytes.Length + " bytes)")
  }
} finally { $zip.Dispose() }

Write-Output ("OK: " + $OutHwpx)
