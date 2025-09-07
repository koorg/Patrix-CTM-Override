# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Koorg
# 
# This script creates a package to override texture placeholders from Patrix resource packs
# that show the error message "ENABLE CONNECT TEXTURE".
# 
# PLEASE NOTE : If you can see this error message, it means that ANOTHER package is not 
# using the correct method to display the textures... 
# (e.g. PhysicsMod, when the grass block or the stone block is broken into pieces)
# 
# Usage : .\Create-PatrixOverride.ps1 -InputZip "Patrix_1.21.8_32x_basic.zip"
# => creates Patrix_32x_CTMOverride.zip that must be loaded on top of your resource packs.

param(
  [Parameter(Mandatory = $true)]
  [string]$InputZip
)

Add-Type -AssemblyName System.IO.Compression.FileSystem

if (-not (Test-Path $InputZip)) { Write-Error "Input file not found: $InputZip"; exit 1 }

$base = [System.IO.Path]::GetFileName($InputZip)
$match = [regex]::Match($base, '(^|[_\W-])(32|64|128|256)x($|[_\W-])', 'IgnoreCase')
if ($match.Success) { $res = $match.Groups[2].Value + 'x'; $dirName = "Patrix_{0}_CTMOverride" -f $res }
else { $dirName = "Patrix_CTMOverride" }

$tmp = Join-Path $env:TEMP ("patrix_override_" + [guid]::NewGuid())
$null = New-Item -ItemType Directory -Path $tmp -Force
$buildDir = Join-Path $tmp $dirName
$blockDir = Join-Path $buildDir "assets\minecraft\textures\block"
$null = New-Item -ItemType Directory -Path $blockDir -Force

$mcmeta = @{
  pack = @{
    pack_format = 64
    description = "Overrides for mods breaking CTM with Patrix `nBy Koorg"
  }
} | ConvertTo-Json -Depth 5
Set-Content -Path (Join-Path $buildDir "pack.mcmeta") -Value $mcmeta -Encoding UTF8

$zip = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path $InputZip))
try {
  function Find-Entry([System.IO.Compression.ZipArchive]$zip, [string]$tail) {
    $tail = $tail.Replace('\','/').ToLower()
    foreach ($e in $zip.Entries) {
      $p = $e.FullName.Replace('\','/').ToLower()
      if ($p.EndsWith($tail)) { return $e }
    }
    return $null
  }

  $gTail = 'assets/minecraft/optifine/ctm/patrix/grass/block/top/1.png'
  $sTail = 'assets/minecraft/optifine/ctm/patrix/stone/1.png'

  $gEntry = Find-Entry $zip $gTail
  $sEntry = Find-Entry $zip $sTail

  if (-not $gEntry) { throw "Missing '$gTail' in zip." }
  if (-not $sEntry) { throw "Missing '$sTail' in zip." }

  $gTarget = Join-Path $blockDir 'grass_block_top.png'
  $sTarget = Join-Path $blockDir 'stone.png'

  $gEntry.ExtractToFile($gTarget, $true)
  $sEntry.ExtractToFile($sTarget, $true)
}
finally {
  $zip.Dispose()
}

$outZip = Join-Path ([System.IO.Path]::GetDirectoryName((Resolve-Path $InputZip))) ("{0}.zip" -f $dirName)
if (Test-Path $outZip) { Remove-Item $outZip -Force }
Compress-Archive -Path (Join-Path $buildDir '*') -DestinationPath $outZip -CompressionLevel Optimal

Remove-Item $tmp -Recurse -Force

Write-Host "Created: $outZip"
