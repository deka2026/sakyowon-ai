param(
  [Parameter(Mandatory=$true)][string]$SectionPath,
  [Parameter(Mandatory=$true)][string]$EditsPath,
  [int]$RedOffset = 41,
  [switch]$NoRed,
  [switch]$KeepLineSegs
)
$ErrorActionPreference = 'Stop'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$xml  = [System.IO.File]::ReadAllText($SectionPath, [System.Text.Encoding]::UTF8)
$data = [System.IO.File]::ReadAllText($EditsPath,   [System.Text.Encoding]::UTF8)

$ts = [regex]::Matches($xml, '<hp:t>([^<]*)</hp:t>')
Write-Output ("Text runs found: " + $ts.Count)

function BadXmlChars([string]$s) {
  if ($s -match '[<>]') { return $true }
  $t = $s -replace '&(amp|lt|gt|quot|apos|#\d+);', ''
  if ($t.Contains('&')) { return $true }
  return $false
}

# charPrIDRef of the <hp:run> that encloses text-run #i
function RunCharPr([string]$doc, [int]$tIndex) {
  $rs = $doc.LastIndexOf('<hp:run ', $tIndex)
  if ($rs -lt 0) { return $null }
  $m = [regex]::Match($doc.Substring($rs, [Math]::Min(200, $doc.Length - $rs)), 'charPrIDRef="(\d+)"')
  if (-not $m.Success) { return $null }
  return [int]$m.Groups[1].Value
}

$ops = New-Object System.Collections.ArrayList
$errors = @()

$blocks = [regex]::Split($data, "\r?\n@@@\r?\n")
foreach ($block in $blocks) {
  $b = $block.Trim("`r", "`n")
  if ($b.Length -eq 0) { continue }
  $parts = [regex]::Split($b, "\r?\n%%%\r?\n")
  if ($parts.Count -lt 2) { $errors += "malformed block: $($b.Substring(0,[Math]::Min(70,$b.Length)))"; continue }
  $head = $parts[0].Trim()
  $body = $parts[1]
  $hp = $head.Split(' ')
  $op = $hp[0]
  if ($hp.Count -lt 2) { $errors += "no index: $head"; continue }
  $idx = [int]$hp[1]
  if ($idx -lt 0 -or $idx -ge $ts.Count) { $errors += "index out of range: $head"; continue }
  $m = $ts[$idx]
  $g = $m.Groups[1]

  if ($op -eq 'REPLIN' -or $op -eq 'SET') {
    if ($op -eq 'REPLIN' -and $parts.Count -lt 3) { $errors += "REPLIN [$idx] needs old fragment"; continue }
    if (BadXmlChars $body) { $errors += "$op [$idx] bad xml char in new text"; continue }

    $cur = $g.Value
    if ($op -eq 'REPLIN') {
      $old = $parts[2]
      if ($old.Length -eq 0) { $errors += "REPLIN [$idx] empty old"; continue }
      $c = [int](($cur.Length - $cur.Replace($old,'').Length) / $old.Length)
      if ($c -ne 1) { $errors += "REPLIN [$idx] fragment occurs $c times: $($old.Substring(0,[Math]::Min(50,$old.Length)))"; continue }
      $pos = $g.Index + $cur.IndexOf($old)
      $len = $old.Length
    } else {
      if ($parts.Count -ge 3 -and $g.Value -ne $parts[2]) { $errors += "SET [$idx] verify failed. actual<$($g.Value)>"; continue }
      $pos = $g.Index
      $len = $cur.Length
    }

    if ($NoRed) {
      [void]$ops.Add([pscustomobject]@{ Pos=$pos; Len=$len; Text=$body })
    } else {
      $cp = RunCharPr $xml $m.Index
      if ($cp -eq $null) { $errors += "$op [$idx] enclosing hp:run charPrIDRef not found"; continue }
      $red = $cp + $RedOffset
      $repl = '</hp:t></hp:run><hp:run charPrIDRef="' + $red + '"><hp:t>' + $body + '</hp:t></hp:run><hp:run charPrIDRef="' + $cp + '"><hp:t>'
      [void]$ops.Add([pscustomobject]@{ Pos=$pos; Len=$len; Text=$repl })
    }
  }
  elseif ($op -eq 'INS_AFTER' -or $op -eq 'INS_BEFORE') {
    if ($parts.Count -ge 3 -and $g.Value -ne $parts[2]) { $errors += "$op [$idx] verify failed. actual<$($g.Value)>"; continue }
    if ($op -eq 'INS_AFTER') {
      $pEnd = $xml.IndexOf('</hp:p>', $m.Index)
      if ($pEnd -lt 0) { $errors += "no </hp:p> after [$idx]"; continue }
      [void]$ops.Add([pscustomobject]@{ Pos=($pEnd+7); Len=0; Text=$body })
    } else {
      $pStart = $xml.LastIndexOf('<hp:p ', $m.Index)
      if ($pStart -lt 0) { $errors += "no <hp:p before [$idx]"; continue }
      [void]$ops.Add([pscustomobject]@{ Pos=$pStart; Len=0; Text=$body })
    }
  }
  else { $errors += "unknown op: $op" }
}

if ($errors.Count -gt 0) {
  Write-Output "FAILED (file NOT written):"
  $errors | ForEach-Object { Write-Output " - $_" }
  exit 1
}

$sorted = $ops | Sort-Object Pos
for ($i=1; $i -lt $sorted.Count; $i++) {
  if ($sorted[$i].Pos -lt ($sorted[$i-1].Pos + $sorted[$i-1].Len)) {
    Write-Output "FAILED: overlapping edits at pos $($sorted[$i].Pos)"; exit 1
  }
}

$desc = $ops | Sort-Object Pos -Descending
foreach ($o in $desc) { $xml = $xml.Remove($o.Pos, $o.Len).Insert($o.Pos, $o.Text) }
Write-Output ("Applied " + $ops.Count + " edits.")

if (-not $KeepLineSegs) {
  $n = [regex]::Matches($xml, '<hp:linesegarray>').Count
  $xml = [regex]::Replace($xml, '<hp:linesegarray>.*?</hp:linesegarray>', '')
  Write-Output "Stripped $n hp:linesegarray layout caches."
}

$doc = New-Object System.Xml.XmlDocument
$doc.LoadXml($xml) | Out-Null
Write-Output "XML valid."

[System.IO.File]::WriteAllText($SectionPath, $xml, $utf8NoBom)
Write-Output "OK: wrote $SectionPath"
