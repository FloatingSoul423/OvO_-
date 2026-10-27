param(
  [Parameter(Mandatory=$true)][string]$Source,
  [Parameter(Mandatory=$true)][string]$Output
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $Output | Out-Null
$app = New-Object -ComObject PowerPoint.Application
$deck = $null
try {
  $deck = $app.Presentations.Open($Source, $true, $false, $false)
  $records = [System.Collections.Generic.List[object]]::new()
  foreach ($slide in $deck.Slides) {
    $shapes = [System.Collections.Generic.List[object]]::new()
    foreach ($shape in $slide.Shapes) {
      $txt = ''
      try { if ($shape.HasTextFrame -and $shape.TextFrame.HasText) { $txt = $shape.TextFrame.TextRange.Text } } catch {}
      $shapes.Add([pscustomobject]@{id=$shape.Id;name=$shape.Name;type=$shape.Type;text=$txt;left=$shape.Left;top=$shape.Top;width=$shape.Width;height=$shape.Height})
    }
    $notes = ''
    foreach ($shape in $slide.NotesPage.Shapes) {
      try { if ($shape.HasTextFrame -and $shape.TextFrame.HasText) { $notes += $shape.TextFrame.TextRange.Text + "`n" } } catch {}
    }
    $records.Add([pscustomobject]@{number=$slide.SlideIndex;notes=$notes;shapes=$shapes})
    $png = Join-Path $Output ('slide-{0:D2}.png' -f $slide.SlideIndex)
    $slide.Export($png, 'PNG', 1600, 900)
  }
  $records | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $Output 'content.json') -Encoding UTF8
  [pscustomobject]@{slides=$deck.Slides.Count;width=$deck.PageSetup.SlideWidth;height=$deck.PageSetup.SlideHeight} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Output 'deck.json') -Encoding UTF8
} finally {
  if ($deck) { $deck.Close() }
  $app.Quit()
}
