param(
  [string]$Root = "docs",
  [int]$MinBytes = 512KB,
  [int]$MaxWidth = 1600,
  [int]$JpegQuality = 6
)

$ErrorActionPreference = "Stop"

function Compress-JpegFile {
  param(
    [string]$FilePath,
    [int]$MaxWidth,
    [int]$JpegQuality
  )

  $tempPath = "$FilePath.__tmp__.jpg"

  if (Test-Path $tempPath) {
    Remove-Item $tempPath -Force
  }

  & ffmpeg -y -loglevel error -i $FilePath -vf "scale='min($MaxWidth,iw)':-2" -q:v $JpegQuality -frames:v 1 $tempPath

  if (-not (Test-Path $tempPath)) {
    throw "ffmpeg failed to generate: $tempPath"
  }

  $source = Get-Item $FilePath
  $temp = Get-Item $tempPath

  if ($temp.Length -lt $source.Length) {
    Move-Item $tempPath $FilePath -Force
    return [pscustomobject]@{
      FilePath = $FilePath
      BeforeMB = [math]::Round($source.Length / 1MB, 2)
      AfterMB = [math]::Round($temp.Length / 1MB, 2)
      SavedMB = [math]::Round(($source.Length - $temp.Length) / 1MB, 2)
      Changed = $true
    }
  }

  Remove-Item $tempPath -Force
  return [pscustomobject]@{
    FilePath = $FilePath
    BeforeMB = [math]::Round($source.Length / 1MB, 2)
    AfterMB = [math]::Round($source.Length / 1MB, 2)
    SavedMB = 0
    Changed = $false
  }
}

$files = Get-ChildItem $Root -Recurse -File |
  Where-Object {
    $_.FullName -notmatch '\\.vitepress\\dist\\' -and
    $_.Length -ge $MinBytes -and
    @(".jpg", ".jpeg") -contains $_.Extension.ToLowerInvariant()
  } |
  Sort-Object Length -Descending

$results = New-Object System.Collections.Generic.List[object]
$index = 0

foreach ($file in $files) {
  $index += 1
  Write-Host ("[{0}/{1}] {2}" -f $index, $files.Count, $file.FullName)
  $results.Add((Compress-JpegFile -FilePath $file.FullName -MaxWidth $MaxWidth -JpegQuality $JpegQuality))
}

$changed = $results | Where-Object { $_.Changed }
$savedMB = [math]::Round((($changed | Measure-Object SavedMB -Sum).Sum), 2)

Write-Host ""
Write-Host ("Processed: {0}" -f $results.Count)
Write-Host ("Changed:   {0}" -f $changed.Count)
Write-Host ("Saved MB:  {0}" -f $savedMB)
