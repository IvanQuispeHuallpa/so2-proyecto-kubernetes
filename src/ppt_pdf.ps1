param([string]$Pptx, [string]$Pdf)
$p = New-Object -ComObject PowerPoint.Application
$d = $p.Presentations.Open($Pptx, $true, $false, $false)
$d.SaveAs($Pdf, 32)
$d.Close()
$p.Quit()
