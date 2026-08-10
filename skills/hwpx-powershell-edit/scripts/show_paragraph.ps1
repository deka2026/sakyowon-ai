param([string]$SectionPath, [int[]]$Idx)
$ErrorActionPreference='Stop'
$xml=[System.IO.File]::ReadAllText($SectionPath,[System.Text.Encoding]::UTF8)
$ts=[regex]::Matches($xml,'<hp:t>([^<]*)</hp:t>')
foreach($i in $Idx){
  $m=$ts[$i]
  $s=$xml.LastIndexOf('<hp:p ',$m.Index)
  $e=$xml.IndexOf('</hp:p>',$m.Index)
  $frag=$xml.Substring($s,$e+7-$s)
  $frag=[regex]::Replace($frag,'<hp:linesegarray>.*?</hp:linesegarray>','[LSA]')
  Write-Output "=== [$i] ==="
  Write-Output $frag
  Write-Output ""
}
