<#
.SYNOPSIS
    Mengambil salinan cadangan konfigurasi, persona, memori, catatan, jadwal, dan sesi WhatsApp Akari dari Tablet ke PC.
.DESCRIPTION
    Skrip ini:
    1. Menyalin data dari tablet (192.168.1.18) via SSH/SCP ke direktori backup lokal di PC.
    2. Menyinkronkan berkas catatan terstruktur `Akari_Notes.md` ke folder `notes/` di workspace PC (untuk Obsidian).
    3. Menjaga retensi 14 folder backup terbaru di PC (menghapus backup yang lebih lama secara otomatis).
    Tidak mencatat API key di layar atau repository.
#>

[CmdletBinding()]
param(
    [string]$TabletIp = "192.168.1.18",
    [int]$Port = 8022,
    [string]$User = "u0_a251",
    [string]$KeyPath = "$HOME\.ssh\id_termux",
    [string]$DestFolder = "$env:LOCALAPPDATA\hermes\backups\tablet",
    [string]$ObsidianNotesDir = "d:\Program Files\AI-Assistant\notes",
    [int]$KeepBackups = 14
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
    ".hermes/plugin-data/akari_notes",
    ".hermes/plugins/akari_notes",
    ".hermes/scripts",
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

# Sinkronkan Akari_Notes.md ke folder notes/ di workspace Obsidian PC jika ada
$backedUpNotesMd = Join-Path $targetDir ".hermes\plugin-data\akari_notes\Akari_Notes.md"
if (Test-Path $backedUpNotesMd) {
    if (-not (Test-Path $ObsidianNotesDir)) {
        New-Item -ItemType Directory -Path $ObsidianNotesDir -Force | Out-Null
    }
    $obsidianTarget = Join-Path $ObsidianNotesDir "Akari_Notes.md"
    Copy-Item -Path $backedUpNotesMd -Destination $obsidianTarget -Force
    Write-Host "-> Disinkronkan ke Obsidian: $obsidianTarget" -ForegroundColor Cyan
}

# Retensi backup lokal: simpan $KeepBackups folder backup-* terbaru
if ($KeepBackups -gt 0 -and (Test-Path $DestFolder)) {
    $allBackups = Get-ChildItem -Path $DestFolder -Directory -Filter "backup-*" | Sort-Object Name -Descending
    if ($allBackups.Count -gt $KeepBackups) {
        $toRemove = $allBackups | Select-Object -Skip $KeepBackups
        foreach ($old in $toRemove) {
            Write-Host "-> Menghapus backup lama (retensi $KeepBackups): $($old.Name)" -ForegroundColor DarkGray
            Remove-Item -Path $old.FullName -Recurse -Force
        }
    }
}

Write-Host "== Backup Selesai! Data disimpan di: $targetDir ==" -ForegroundColor Green
