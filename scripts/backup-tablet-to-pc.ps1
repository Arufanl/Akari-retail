<#
.SYNOPSIS
    Mengambil salinan cadangan konfigurasi, persona, memori, dan sesi WhatsApp Akari dari Tablet ke PC.
.DESCRIPTION
    Skrip ini menyalin data dari tablet (192.168.1.18) via SSH/SCP ke direktori backup lokal di PC.
    Tidak mencatat API key di layar atau repository.
#>

[CmdletBinding()]
param(
    [string]$TabletIp = "192.168.1.18",
    [int]$Port = 8022,
    [string]$User = "u0_a251",
    [string]$KeyPath = "$HOME\.ssh\id_termux",
    [string]$DestFolder = "$env:LOCALAPPDATA\hermes\backups\tablet"
)

$ErrorActionPreference = 'Stop'

Write-Host "== [AKARI] Memulai Backup Data Tablet ($TabletIp) ==" -ForegroundColor Cyan

$stamp = (Get-Date).ToString("yyyyMMdd-HHmmss")
$targetDir = Join-Path $DestFolder "backup-$stamp"
New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

$itemsToBackup = @(
    ".hermes/config.yaml",
    ".hermes/SOUL.md",
    ".hermes/.env",
    ".hermes/memories",
    ".hermes/cron",
    ".hermes/whatsapp/session",
    ".9router/db/data.sqlite"
)

foreach ($item in $itemsToBackup) {
    Write-Host "-> Mengambil: $item" -ForegroundColor Gray
    $destSub = Join-Path $targetDir ($item -replace '/', '\')
    $parent = Split-Path $destSub -Parent
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    
    $remotePath = "${User}@${TabletIp}:${item}"
    try {
        & scp -i $KeyPath -P $Port -r -o BatchMode=yes -o ConnectTimeout=10 $remotePath $destSub 2>$null
    } catch {
        # Abaikan jika berkas opsional belum terbentuk di tablet
    }
}

Write-Host "== Backup Selesai! Data disimpan di: $targetDir ==" -ForegroundColor Green
