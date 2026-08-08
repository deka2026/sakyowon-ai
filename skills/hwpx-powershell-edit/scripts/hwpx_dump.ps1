param(
  [Parameter(Mandatory=$true)][string]$HwpxPath,
  [Parameter(Mandatory=$true)][string]$WorkDir
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

$unpacked = Join-Path $WorkDir 'unpacked'
if (Test-Path $unpacked) { Remove-Item -Recurse -Force $unpacked }
New-Item -ItemType Directory -Force $WorkDir | Out-Null
[System.IO.Compression.ZipFile]::ExtractToDirectory($HwpxPath, $unpacked)

$secPath = Join-Path $unpacked 'Contents\section0.xml'
$xml = [System.IO.File]::ReadAllText($secPath, [System.Text.Encoding]::UTF8)

# Quote convention check (straight U+0027 vs curly U+2018/2019)
$straight = ($xml.Length - $xml.Replace([string][char]0x0027, '').Length)
$curlyL = ($xml.Length - $xml.Replace([string][char]0x2018, '').Length)
$curlyR = ($xml.Length - $xml.Replace([string][char]0x2019, '').Length)
Write-Output "Quote check: straight(U+0027)=$straight curly-left(U+2018)=$curlyL curly-right(U+2019)=$curlyR"

# BOM check
$bytes = [System.IO.File]::ReadAllBytes($secPath)
if ($bytes[0] -eq 0xEF) { Write-Output "BOM: present (UTF-8 BOM)" } else { Write-Output "BOM: none" }

# Dump all hp:t with indices
$ts = [regex]::Matches($xml, '<hp:t>([^<]*)</hp:t>')
$out = for ($i = 0; $i -lt $ts.Count; $i++) { "[$i] $($ts[$i].Groups[1].Value)" }
$dumpPath = Join-Path $WorkDir 'text_dump.txt'
[System.IO.File]::WriteAllLines($dumpPath, $out, [System.Text.Encoding]::UTF8)
Write-Output "Extracted: $unpacked"
Write-Output "Dumped $($ts.Count) text runs to: $dumpPath"
