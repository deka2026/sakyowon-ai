param(
  [Parameter(Mandatory=$true)][string]$SourceHwpx,
  [Parameter(Mandatory=$true)][string]$SectionPath,
  [Parameter(Mandatory=$true)][string]$OutHwpx
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

if ([System.IO.Path]::GetFullPath($OutHwpx) -eq [System.IO.Path]::GetFullPath($SourceHwpx)) {
  throw "OutHwpx must differ from SourceHwpx - never overwrite the original."
}

# Validate XML well-formedness before packing
$doc = New-Object System.Xml.XmlDocument
$doc.Load($SectionPath)
Write-Output "XML valid. Root: $($doc.DocumentElement.Name)"

Copy-Item $SourceHwpx $OutHwpx -Force
$zip = [System.IO.Compression.ZipFile]::Open($OutHwpx, 'Update')
try {
  $entry = $zip.GetEntry('Contents/section0.xml')
  if ($entry) { $entry.Delete() }
  $newEntry = $zip.CreateEntry('Contents/section0.xml', [System.IO.Compression.CompressionLevel]::Optimal)
  $stream = $newEntry.Open()
  $bytes = [System.IO.File]::ReadAllBytes($SectionPath)
  $stream.Write($bytes, 0, $bytes.Length)
  $stream.Close()
}
finally { $zip.Dispose() }
Write-Output "Repacked: $OutHwpx ($((Get-Item $OutHwpx).Length) bytes)"

# Post-check: re-extract and count text runs
$zip2 = [System.IO.Compression.ZipFile]::OpenRead($OutHwpx)
try {
  $e = $zip2.GetEntry('Contents/section0.xml')
  $reader = New-Object System.IO.StreamReader($e.Open(), [System.Text.Encoding]::UTF8)
  $xml2 = $reader.ReadToEnd(); $reader.Close()
  $n = [regex]::Matches($xml2, '<hp:t>').Count
  Write-Output "Post-check: $n <hp:t> runs readable in repacked file."
}
finally { $zip2.Dispose() }
