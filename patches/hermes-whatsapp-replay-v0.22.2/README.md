# Patch replay WhatsApp Hermes v0.22.2

Patch ini dibuat untuk instalasi Hermes `v0.22.2`, commit `d923a5eb487a17c0a68801bba9ef0f56c81040a8`.

## Isi perubahan

- Menolak event history Baileys (`append`) pada mode bot terpisah.
- Menambahkan ledger fingerprint ID inbound yang terbatas dan persisten lintas restart.
- Menambahkan uji untuk pesan baru, history, pesan sendiri, duplikat, dan restart.

Patch tidak mengubah persona, API/model, konfigurasi WhatsApp, kredensial, sesi, atau riwayat pesan.

## Cadangan pertama

File asli dan metadata Git sebelum perubahan tersimpan di:

`C:\Users\Akari\AppData\Local\hermes\backups\pre-whatsapp-replay-fix-20261017-224510`

## Setelah Hermes diperbarui

Periksa dulu apakah versi baru sudah mempunyai filter history dan deduplikasi inbound persisten. Jika belum, dari PowerShell jalankan pemeriksaan berikut:

```powershell
$repo = Join-Path $env:LOCALAPPDATA 'hermes\hermes-agent'
$patch = 'D:\Program Files\AI-Assistant\patches\hermes-whatsapp-replay-v0.22.2\hermes-whatsapp-replay-v0.22.2.patch'
git -C $repo apply --check $patch
```

Hanya jika pemeriksaan berhasil tanpa keluaran error, terapkan:

```powershell
git -C $repo apply $patch
```

Jika `--check` gagal, jangan paksa. Versi upstream mungkin sudah berubah dan patch perlu ditinjau ulang.

## Verifikasi lokal tanpa model

```powershell
$bridge = Join-Path $env:LOCALAPPDATA 'hermes\hermes-agent\scripts\whatsapp-bridge'
Set-Location $bridge
node --check bridge.js
node --check inbound_message_gate.js
node --test *.test.mjs
```
