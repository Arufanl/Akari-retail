[CmdletBinding()]
param(
    [switch]$AllowlistOnly
)

$ErrorActionPreference = 'Stop'

$hermesRoot = Join-Path $env:LOCALAPPDATA 'hermes'
$hermesExe = Join-Path $hermesRoot 'bin\hermes.exe'
$envPath = Join-Path $hermesRoot '.env'

if (-not (Test-Path -LiteralPath $hermesExe)) {
    throw "Hermes tidak ditemukan di $hermesExe"
}

if (-not (Test-Path -LiteralPath $envPath)) {
    throw "Konfigurasi lokal Hermes tidak ditemukan di $envPath"
}

Write-Host 'Masukkan nomor WhatsApp PEMILIK yang boleh menghubungi Akari.'
Write-Host 'Gunakan kode negara tanpa tanda +, spasi, atau tanda hubung. Contoh format: 62812...'
$secureOwnerNumber = Read-Host 'Nomor pemilik' -AsSecureString
$numberPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureOwnerNumber)

try {
    $ownerNumber = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($numberPointer)
    if ($ownerNumber -notmatch '^\d{8,15}$') {
        throw 'Format nomor tidak valid. Gunakan 8-15 digit dengan kode negara dan tanpa tanda +.'
    }

    $backupRoot = Join-Path $hermesRoot 'backups'
    $backupDir = Join-Path $backupRoot ('pre-whatsapp-pairing-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    Copy-Item -LiteralPath $envPath -Destination (Join-Path $backupDir '.env')
    $configPath = Join-Path $hermesRoot 'config.yaml'
    if (Test-Path -LiteralPath $configPath) {
        Copy-Item -LiteralPath $configPath -Destination (Join-Path $backupDir 'config.yaml')
    }

    $settings = [ordered]@{
        WHATSAPP_ENABLED                = if ($AllowlistOnly) { 'true' } else { 'false' }
        WHATSAPP_MODE                   = 'bot'
        WHATSAPP_ALLOWED_USERS          = $ownerNumber
        WHATSAPP_ALLOW_ALL_USERS        = 'false'
        WHATSAPP_DM_POLICY              = 'allowlist'
        WHATSAPP_GROUP_POLICY           = 'disabled'
        WHATSAPP_FORWARD_OWNER_MESSAGES = 'false'
    }

    $lines = [Collections.Generic.List[string]]::new()
    foreach ($line in [IO.File]::ReadAllLines($envPath)) {
        $key = if ($line -match '^([A-Za-z_][A-Za-z0-9_]*)=') { $Matches[1] } else { $null }
        if (-not $key -or -not $settings.Contains($key)) {
            $lines.Add($line)
        }
    }
    foreach ($entry in $settings.GetEnumerator()) {
        $lines.Add("$($entry.Key)=$($entry.Value)")
    }

    $tempPath = "$envPath.tmp.$PID"
    $utf8NoBom = New-Object Text.UTF8Encoding($false)
    [IO.File]::WriteAllLines($tempPath, $lines, $utf8NoBom)
    Move-Item -LiteralPath $tempPath -Destination $envPath -Force

    Write-Host 'Allowlist lokal dan kebijakan privat sudah disiapkan.'
    if ($AllowlistOnly) {
        Write-Host 'Allowlist diperbaiki tanpa mengubah atau mengulang pairing WhatsApp.'
        return
    }
    Write-Host 'Wizard akan menampilkan QR hanya di terminal ini. Jangan salin atau kirim QR tersebut.'
    Write-Host 'Jika ditanya Update allowed users, tekan Enter untuk mempertahankan nomor tadi.'
    Write-Host ''

    & $hermesExe whatsapp
    if ($LASTEXITCODE -ne 0) {
        throw "Wizard Hermes berhenti dengan exit code $LASTEXITCODE"
    }

    $sessionCandidates = @(
        (Join-Path $hermesRoot 'whatsapp\session\creds.json'),
        (Join-Path $hermesRoot 'platforms\whatsapp\session\creds.json')
    )
    if ($sessionCandidates | Where-Object { Test-Path -LiteralPath $_ }) {
        Write-Host 'Pairing selesai dan kredensial sesi tersimpan lokal. Gateway belum dijalankan.'
    }
    else {
        Write-Warning 'Kredensial sesi belum ditemukan. Jalankan helper ini lagi untuk mencoba ulang.'
    }
}
finally {
    if ($numberPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($numberPointer)
    }
    Remove-Variable ownerNumber,secureOwnerNumber -ErrorAction SilentlyContinue
}
