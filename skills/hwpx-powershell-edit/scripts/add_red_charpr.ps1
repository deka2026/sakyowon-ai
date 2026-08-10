param([Parameter(Mandatory=$true)][string]$HeaderPath, [int]$Offset = 41)
$ErrorActionPreference='Stop'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$x = [System.IO.File]::ReadAllText($HeaderPath, [System.Text.Encoding]::UTF8)

$mCnt = [regex]::Match($x, '<hh:charProperties itemCnt="(\d+)">')
if (-not $mCnt.Success) { throw "charProperties not found" }
$cnt = [int]$mCnt.Groups[1].Value
if ($cnt -ne $Offset) { throw "itemCnt ($cnt) != Offset ($Offset); aborting" }

$blockStart = $mCnt.Index + $mCnt.Length
$blockEnd = $x.IndexOf('</hh:charProperties>', $blockStart)
if ($blockEnd -lt 0) { throw "charProperties end not found" }
$block = $x.Substring($blockStart, $blockEnd - $blockStart)

$items = [regex]::Matches($block, '<hh:charPr id="(\d+)".*?</hh:charPr>')
if ($items.Count -ne $cnt) { throw "parsed $($items.Count) charPr but itemCnt=$cnt" }

$sb = New-Object System.Text.StringBuilder
foreach ($it in $items) {
  $src = $it.Value
  $id  = [int]$it.Groups[1].Value
  $new = [regex]::Replace($src, '^<hh:charPr id="\d+"', ('<hh:charPr id="' + ($id + $Offset) + '"'))
  if ($new -match 'textColor="[^"]*"') {
    $new = [regex]::Replace($new, 'textColor="[^"]*"', 'textColor="#FF0000"', 1)
  } else {
    $new = [regex]::Replace($new, '^(<hh:charPr id="\d+")', '$1 textColor="#FF0000"', 1)
  }
  [void]$sb.Append($new)
}

$x = $x.Remove($blockEnd, 0).Insert($blockEnd, $sb.ToString())
$x = $x.Replace('<hh:charProperties itemCnt="' + $cnt + '">', '<hh:charProperties itemCnt="' + ($cnt * 2) + '">')

$doc = New-Object System.Xml.XmlDocument
$doc.LoadXml($x) | Out-Null
[System.IO.File]::WriteAllText($HeaderPath, $x, $utf8NoBom)
Write-Output ("OK: added " + $cnt + " red charPr (id N -> N+" + $Offset + "), itemCnt now " + ($cnt*2))
