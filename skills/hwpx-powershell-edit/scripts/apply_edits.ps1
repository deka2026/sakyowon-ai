param(
  [Parameter(Mandatory=$true)][string]$SectionPath,
  [Parameter(Mandatory=$true)][string]$EditsPath,
  [switch]$NoQuoteNormalize,
  [switch]$KeepLineSegs
)
$ErrorActionPreference = 'Stop'

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$xml = [System.IO.File]::ReadAllText($SectionPath, [System.Text.Encoding]::UTF8)
$data = [System.IO.File]::ReadAllText($EditsPath, [System.Text.Encoding]::UTF8)

# Normalize curly quotes in edit data to straight apostrophe (most hwpx use straight).
# Pass -NoQuoteNormalize if the target document uses curly quotes.
if (-not $NoQuoteNormalize) {
  $lq = [string][char]0x2018; $rq = [string][char]0x2019
  $data = $data.Replace($lq, "'").Replace($rq, "'")
}

function CountOcc([string]$hay, [string]$needle) {
  if ($needle.Length -eq 0) { return 0 }
  return [int](($hay.Length - $hay.Replace($needle, '').Length) / $needle.Length)
}

$blocks = [regex]::Split($data, "\r?\n@@@\r?\n")
$errors = @()
$applied = 0
foreach ($block in $blocks) {
  $b = $block.Trim("`r", "`n")
  if ($b.Length -eq 0) { continue }
  $parts = [regex]::Split($b, "\r?\n%%%\r?\n")
  $op = $parts[0].Trim()
  if ($op -eq 'REPL') {
    $old = $parts[1]; $new = $parts[2]
    $c = CountOcc $xml $old
    if ($c -ne 1) { $errors += "REPL match count $c for: $($old.Substring(0, [Math]::Min(60, $old.Length)))"; continue }
    $xml = $xml.Replace($old, $new); $applied++
  }
  elseif ($op -eq 'INS_BEFORE_P') {
    $anchor = $parts[1]; $content = $parts[2]
    $idx = $xml.IndexOf($anchor)
    if ($idx -lt 0) { $errors += "INS_BEFORE_P anchor not found: $anchor"; continue }
    $pStart = $xml.LastIndexOf('<hp:p ', $idx)
    if ($pStart -lt 0) { $errors += "INS_BEFORE_P no <hp:p before anchor: $anchor"; continue }
    $xml = $xml.Insert($pStart, $content); $applied++
  }
  elseif ($op -eq 'INS_AFTER_P') {
    $anchor = $parts[1]; $content = $parts[2]
    $idx = $xml.IndexOf($anchor)
    if ($idx -lt 0) { $errors += "INS_AFTER_P anchor not found: $anchor"; continue }
    $pEnd = $xml.IndexOf('</hp:p>', $idx)
    if ($pEnd -lt 0) { $errors += "INS_AFTER_P no </hp:p> after anchor: $anchor"; continue }
    $xml = $xml.Insert($pEnd + 7, $content); $applied++
  }
  else { $errors += "Unknown op: $op" }
}

if ($errors.Count -gt 0) {
  Write-Output "FAILED CHECKS (file NOT written):"
  $errors | ForEach-Object { Write-Output " - $_" }
  exit 1
}

# Strip ALL layout caches so Hangul recomputes line layout on open.
# Stale linesegarray on paragraphs whose text length changed renders as
# overlapping/garbled lines (verified 2026-08-08). Absence is always safe.
if (-not $KeepLineSegs) {
  $n = [regex]::Matches($xml, '<hp:linesegarray>').Count
  $xml = [regex]::Replace($xml, '<hp:linesegarray>.*?</hp:linesegarray>', '')
  Write-Output "Stripped $n hp:linesegarray layout caches (pass -KeepLineSegs to disable)."
}

[System.IO.File]::WriteAllText($SectionPath, $xml, $utf8NoBom)
Write-Output "OK: applied $applied edits to $SectionPath"
