# Pra-instalasi Hermes untuk Akari di Windows

Tanggal pemeriksaan: 17 Oktober 2026  
Status: instalasi dasar dan uji chat Gemini free-tier selesai; WhatsApp, gateway, dan auto-start belum dikonfigurasi

## Hasil pemeriksaan PC

| Komponen | Hasil | Penilaian |
|---|---|---|
| Sistem operasi | Windows 10 Pro 22H2, build 19045, AMD64 | Didukung Tier 1 oleh Hermes native Windows |
| PowerShell | 5.1.19041.6456 | Cukup untuk installer PowerShell resmi |
| Git | 2.55.0.windows.5 | Tersedia; installer tidak perlu bootstrap Git portabel |
| Python sistem | 3.14.7 | Tersedia, tetapi Hermes tetap mengelola runtime versinya sendiri |
| Node.js sistem | 24.21.0 | Tersedia, tetapi Hermes PM memilih Node terkelola dari lockfile-nya |
| Ruang kosong drive workspace | sekitar 87,2 GB | Memadai untuk instalasi sumber dan tool terkelola |
| Perintah `hermes` | Hermes Agent v0.22.2, stable | Launcher dan bantuan CLI terverifikasi |
| `%LOCALAPPDATA%\hermes` | Terpasang | Lokasi default yang disetujui |

## Jalur resmi yang paling sesuai

Untuk PC ini, kandidat paling sederhana adalah instalasi CLI/source **native Windows** melalui `install.ps1` resmi pada channel `stable`. WSL2, Docker, dan MSIX tidak diperlukan untuk pilot awal.

Alasannya:

- Native Windows 10 x86_64 termasuk platform Tier 1.
- CLI, gateway pesan termasuk WhatsApp, scheduler cron, dan auto-start melalui Scheduled Task didukung native.
- Paket MSIX Desktop membutuhkan Windows 11 22H2 atau lebih baru, sehingga bukan jalur untuk PC Windows 10 ini.
- Installer native tidak memerlukan hak administrator, memakai `%LOCALAPPDATA%\hermes` secara default, dan menambahkan launchernya ke User PATH.
- Installer/PM mengelola Python 3.14, Node.js, npm, ripgrep, FFmpeg, uv, dan dependensi Hermes berdasarkan pin/lock milik proyek. Runtime Python/Node sistem yang sudah ada bukan sumber kebenaran instalasi Hermes.

Perintah instalasi resmi terdokumentasi adalah:

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

Perintah resmi telah dijalankan dengan `-NonInteractive -Channel stable`. Installer memilih rilis `v0.22.2` dan commit `d923a5eb487a17c0a68801bba9ef0f56c81040a8`. Verifikasi `hermes --version` dan `hermes --help` selesai dengan exit code 0. User PATH sudah memuat `%LOCALAPPDATA%\hermes\bin`.

Tidak ditemukan Scheduled Task gateway, direktori gateway, atau proses Hermes yang tertinggal setelah verifikasi. Installer tidak menjalankan setup model/API, pairing WhatsApp, atau pendaftaran auto-start.

## Hasil uji Gemini terminal

Konfigurasi Hermes dicadangkan sebelum perubahan. Hanya `model.provider`, `model.default`, dan `model.base_url` yang diubah menjadi provider native Gemini, model `gemini-3.8-flash`, dan endpoint `https://generativelanguage.googleapis.com/v1beta`.

Key disimpan lokal di `%LOCALAPPDATA%\hermes\.env` dan tidak dicatat di repositori atau log. Models API mengonfirmasi bahwa `gemini-3.8-flash`, `gemini-3.1-flash-lite`, dan `gemini-2.5-flash` dapat diakses oleh key. Satu uji terminal dalam safe mode berhasil dengan balasan `Halo dari Akari.` dan exit code 0. Tidak ada gateway, auto-start, atau WhatsApp yang diaktifkan.

## WhatsApp pada jalur Hermes

Hermes menyediakan bridge WhatsApp bawaan berbasis Baileys. Ini tetap jalur tidak resmi yang meniru WhatsApp Web, sehingga risiko pembatasan akun dan kerusakan akibat perubahan protokol tetap berlaku. Keputusan Akari untuk memakai nomor khusus tetap cocok dengan anjuran Hermes.

Setelah Hermes dan model dasar terbukti bekerja, urutan minimum yang disarankan adalah:

1. Jalankan pemeriksaan instalasi (`hermes doctor` dan `hermes pm doctor`).
2. Konfigurasikan model gratis yang dipilih; jangan mengaktifkan langganan Nous Portal atau fallback berbayar otomatis.
3. Buktikan satu percakapan langsung Hermes berhasil.
4. Jalankan wizard WhatsApp (`hermes whatsapp` atau `hermes gateway setup`), pilih mode nomor bot khusus, isi allowlist pemilik, lalu pairing melalui QR.
5. Uji satu pesan dari nomor yang diizinkan menghasilkan satu balasan.
6. Scheduler, sapaan, pengingat, service auto-start, dan migrasi tablet baru diperiksa setelah vertical slice lulus.

Gateway yang berjalan sebagai Scheduled Task tidak membuat PC kebal terhadap mati, tidur, hibernasi, atau kehilangan jaringan. Tahap PC tetap tidak menjanjikan operasi 24 jam.

## Keputusan yang masih terbuka

- Kapan gateway boleh didaftarkan sebagai Scheduled Task; jangan dilakukan pada instalasi dasar tanpa persetujuan.

## Sumber resmi

- Instalasi: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/getting-started/installation.md
- Panduan native Windows: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/windows-native.md
- Dukungan platform: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/getting-started/platform-support.md
- WhatsApp Baileys: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/messaging/whatsapp.md
- Installer PowerShell: https://github.com/NousResearch/hermes-agent/blob/main/scripts/install.ps1
- Rilis: https://github.com/NousResearch/hermes-agent/releases
