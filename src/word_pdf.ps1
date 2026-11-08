param([string]$Docx, [string]$Pdf)
$w = New-Object -ComObject Word.Application
try {
$w.Visible = $false
$w.DisplayAlerts = 0
$d = $w.Documents.Open($Docx)
foreach ($n in @(-20,-21)) { $st = $d.Styles.Item($n); $st.ParagraphFormat.SpaceAfter = 0; $st.ParagraphFormat.SpaceBefore = $(if ($n -eq -20) { 3 } else { 0 }); $st.Font.Size = 10.5; $st.Font.Name = 'Garamond'; $st.Font.Bold = $(if ($n -eq -20) { 1 } else { 0 }); $st.ParagraphFormat.LineSpacingRule = 0 }
$d.Fields.Update() | Out-Null
foreach ($t in $d.TablesOfContents) { $t.Update() }
$d.Repaginate()
$d.Save()
$d.ExportAsFixedFormat($Pdf, 17)
"Paginas: " + $d.ComputeStatistics(2)
"Palabras: " + $d.ComputeStatistics(0)
$d.Close(0)
} finally { try { $w.Quit() } catch {} }
