param(
  [Parameter(Mandatory=$true)][string]$SpecPath,
  [Parameter(Mandatory=$true)][string]$OutPath
)
$ErrorActionPreference = 'Stop'
$lines = [IO.File]::ReadAllLines($SpecPath, [Text.Encoding]::UTF8)
$sb = New-Object System.Text.StringBuilder
$tblId = 1900000001
$zOrder = 1

function Cell($text, $col, $row, $w, $isHeader) {
  if ($isHeader) { $bf = '9'; $pp = '20'; $cp = '21' } else { $bf = '3'; $pp = '24'; $cp = '28' }
  $c = '<hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="' + $bf + '">'
  $c += '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
  $c += '<hp:p id="0" paraPrIDRef="' + $pp + '" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="' + $cp + '"><hp:t>' + $text + '</hp:t></hp:run></hp:p>'
  $c += '</hp:subList><hp:cellAddr colAddr="' + $col + '" rowAddr="' + $row + '"/><hp:cellSpan colSpan="1" rowSpan="1"/><hp:cellSz width="' + $w + '" height="1382"/><hp:cellMargin left="510" right="510" top="141" bottom="141"/></hp:tc>'
  return $c
}

$i = 0
while ($i -lt $lines.Count) {
  $line = $lines[$i]
  $i++
  if ($line.Trim() -eq '') { continue }
  $parts = $line.Split('|')
  $kind = $parts[0]
  switch ($kind) {
    'H1' {
      [void]$sb.Append('<hp:p id="0" paraPrIDRef="17" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="1"><hp:t>' + $parts[1] + '</hp:t></hp:run></hp:p>')
    }
    'H1PB' {
      [void]$sb.Append('<hp:p id="0" paraPrIDRef="17" styleIDRef="0" pageBreak="1" columnBreak="0" merged="0"><hp:run charPrIDRef="1"><hp:t>' + $parts[1] + '</hp:t></hp:run></hp:p>')
    }
    'H2' {
      [void]$sb.Append('<hp:p id="0" paraPrIDRef="19" styleIDRef="15" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="2"><hp:t>' + $parts[1] + '</hp:t></hp:run></hp:p>')
    }
    'P' {
      [void]$sb.Append('<hp:p id="0" paraPrIDRef="22" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="15"><hp:t>' + $parts[1] + '</hp:t></hp:run></hp:p>')
    }
    'TBL' {
      $widths = $parts[1].Split(',') | ForEach-Object { [int]$_ }
      $colCnt = $widths.Count
      $rows = @()
      while ($i -lt $lines.Count -and $lines[$i].Split('|')[0] -eq 'R') {
        $cells = $lines[$i].Split('|')
        $rows += ,@($cells[1..($cells.Count-1)])
        $i++
      }
      if ($i -lt $lines.Count -and $lines[$i].Trim() -eq 'END') { $i++ }
      $rowCnt = $rows.Count
      $sum = ($widths | Measure-Object -Sum).Sum
      if ($sum -ne 47622) { throw "col widths sum $sum != 47622 at table line" }
      $t = '<hp:p id="0" paraPrIDRef="22" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="15">'
      $t += '<hp:tbl id="' + $tblId + '" zOrder="' + $zOrder + '" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="1" rowCnt="' + $rowCnt + '" colCnt="' + $colCnt + '" cellSpacing="0" borderFillIDRef="3" noAdjust="0">'
      $t += '<hp:sz width="47622" widthRelTo="ABSOLUTE" height="' + ($rowCnt * 1382) + '" heightRelTo="ABSOLUTE" protect="0"/>'
      $t += '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
      $t += '<hp:outMargin left="283" right="283" top="283" bottom="283"/><hp:inMargin left="510" right="510" top="141" bottom="141"/>'
      for ($r = 0; $r -lt $rowCnt; $r++) {
        $t += '<hp:tr>'
        $rowCells = $rows[$r]
        if ($rowCells.Count -ne $colCnt) { throw ("row " + $r + " has " + $rowCells.Count + " cells, expected " + $colCnt) }
        for ($c = 0; $c -lt $colCnt; $c++) {
          $t += Cell $rowCells[$c] $c $r $widths[$c] ($r -eq 0)
        }
        $t += '</hp:tr>'
      }
      $t += '</hp:tbl></hp:run></hp:p>'
      [void]$sb.Append($t)
      $tblId++
      $zOrder++
    }
    default { throw "unknown kind: $kind" }
  }
}
[IO.File]::WriteAllText($OutPath, $sb.ToString(), (New-Object Text.UTF8Encoding($false)))
Write-Output ("fragment written: " + $OutPath)
