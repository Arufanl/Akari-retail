# Catatan perubahan: migrasi Akari ke tablet

Zona waktu: Asia/Jakarta (UTC+7). Tidak ada key atau kredensial yang dicatat di sini.

Jenis: **[BACA]** hanya membaca, **[TULIS]** mengubah sesuatu.

## 2026-11-05

### Keputusan (sesi tanya jawab)
- Operasional harian hanya di tablet (Hermes + 9Router di Termux). PC untuk pengembangan dan backup.
- Auto-start (Termux:Boot) dan wake-lock untuk target 24 jam, dinyalakan setelah patch bridge lulus tes.
- Bug replay WhatsApp: buat patch baru untuk bridge tablet (ledger persisten), uji dengan tes tiruan dahulu.
- Sesi WhatsApp: pairing baru di tablet dengan nomor Akari yang sama, lalu logout sesi PC.
- Tahap 1: chat teks saja, tanpa tool terminal/web/file. Catatan, pengingat, memori, dan self-awareness bertahap.
- Model: pakai combo `hermes-fallback`; cek isi dan uji fallback.
- Backup berkala tablet ke PC lewat SSH, di luar repo.

### Perubahan
| Waktu | Jenis | Lokasi | Perubahan | Pemulihan |
|---|---|---|---|---|
| 01:07 | BACA | PC | Port 20128, proses, scheduled task, startup: Hermes dan 9Router PC tidak berjalan dan tidak ada auto-start. | - |
| 01:11 | BACA | Tablet 192.168.1.18 | Ping, port 8022 dan 20128 terbuka; 9Router menjawab 401 tanpa key. | - |
| 01:16 | BACA | Tablet | Isi `~/.hermes`, blok `model:` di `config.yaml`, nama variabel `.env` (tanpa nilai). | - |
| 01:20 | BACA | Tablet | Proses (9Router, Hermes, gateway) dan `errors.log`: `nemo_relay` tidak terpasang, tidak ada platform pesan aktif. | - |
| 01:26 | TULIS | Tablet `~/.hermes/SOUL.md.bak-pre-akari-2026-11-05` | Backup `SOUL.md` tablet lama (667 byte). | - |
| 01:26 | TULIS | Tablet `~/.hermes/SOUL.md` | Diganti dengan `hermes/SOUL.md` dari workspace (4.488 byte, hash SHA-256 sama dengan PC). | Salin balik berkas backup. |
| 01:30 | TULIS | PC `C:\Users\Akari\.gemini\config\skills` | Pasang 38 skill dari `D:\Program Files\AI-Skills\mattpocock\skills` (salinan). | Hapus foldernya. |
| 01:39 | TULIS | PC `...\config\skills\ponytail` | Pasang skill `ponytail` dari GitHub (DietrichGebert/ponytail), 3.496 byte, MIT. | Hapus foldernya. |
| 01:41 | BACA | Tablet | Daftar model 9Router lewat key Hermes (HTTP 200). `hermes-fallback` terdaftar. Key tidak dicetak. | - |
| 01:42 | BACA* | Tablet | Satu permintaan pendek ke `hermes-fallback`: HTTP 200, dijawab `claude-opus-4-6-thinking`. Memakai kuota model. | - |
| 01:42 | TULIS | PC scratch (luar workspace) | `test_fallback.sh` di folder scratch percakapan. Berisi nama variabel key, bukan nilainya. | Hapus berkas. |
| 01:45 | TULIS | Workspace `docs/` | Berkas catatan ini dibuat. | Hapus berkas. |
| 01:48 | BACA | Tablet SQLite 9Router | Baca tabel `combos` mode read-only via Python. Ditemukan isi model combo `hermes-fallback` (total 36 model). | - |
| 02:02 | BACA | Tablet `whatsapp-bridge` | Unit test bawaan `node --test *.test.mjs`: 21 pass, 2 fail karena `node_modules` belum terpasang (`@whiskeysockets/baileys`). | - |
| 02:18 | TULIS | Tablet `whatsapp-bridge` | Jalankan `npm install` (139 paket terpasang dalam 32 detik). Seluruh 26 unit test bawaan upstream lulus (100% pass). | Hapus `node_modules`. |
| 02:36 | TULIS | Tablet `whatsapp-bridge` | Cadangkan `bridge.js` ke `bridge.js.bak-pre-dedup-20261105`. Terapkan modul `inbound_message_gate.js` dan integrasi deduplikasi persisten (SHA-256 ledger). 32 dari 32 unit test lulus (100% pass). | Kembalikan dari backup. |
| 02:43 | TULIS | Workspace `patches/` | Dokumentasi dan patch tablet diekspor ke `patches/hermes-whatsapp-replay-tablet/` (`hermes-whatsapp-replay-tablet.patch` & `README.md`). | Hapus folder. |
| 03:03 | TULIS | Workspace `docs/` | Buat panduan arsitektur & operasional tablet `docs/Akari_Hermes_Tablet.md`. | Hapus berkas. |
| 03:04 | TULIS | Workspace `scripts/` | Buat dan uji skrip backup berkala tablet ke PC `scripts/backup-tablet-to-pc.ps1`. Backup perdana sukses di `$env:LOCALAPPDATA\hermes\backups\tablet`. | Hapus berkas. |
| 03:22 | TULIS | Tablet `~/.hermes/whatsapp/session` | Pengguna menyelesaikan `hermes whatsapp` (pairing QR Code). Sesi Baileys terbentuk. | Hapus folder `session`. |
| 03:35 | TULIS | Tablet `~/.hermes/config.yaml` & `.env` | Cadangkan ke `backups/pre-akari-guardrails-20261105-033514`. Terapkan pembatasan `platform_toolsets` (`cli: []`, `whatsapp: []`), matikan `auxiliary.title_generation` & `background_review`, setel `dm_policy: allowlist`, `group_policy: disabled`, serta tambahkan varian kode negara `628...` pada `WHATSAPP_ALLOWED_USERS`. | Kembalikan dari backup. |
| 03:35 | TULIS | PC `%LOCALAPPDATA%\hermes` | Nonaktifkan `WHATSAPP_ENABLED=false` di `.env` PC dan pindahkan `whatsapp\session` lama PC ke `backups\pc-whatsapp-retired-20261105-033536\session` agar tidak berebut sesi dengan tablet. | Kembalikan dari folder backup. |
| 03:36 | TULIS | Tablet `~/.termux/boot/start-akari.sh` | Aktifkan `termux-wake-lock` dan pasang skrip auto-start `Termux:Boot` (menyalakan `sshd`, `9router`, dan `hermes gateway`). | Hapus `start-akari.sh`. |
| 03:39 | TULIS | Tablet Python 3.14 | Pasang paket `aiohttp` (`3.14.5`) yang dibutuhkan adapter WhatsApp Hermes, lalu restart gateway. Bridge WhatsApp (`port 3000`, `mode: bot`) terhubung (`✓ whatsapp connected`). | `pip uninstall aiohttp` |
| 03:40 | TULIS | PC `%LOCALAPPDATA%\hermes\backups\tablet` | Jalankan ulang `scripts/backup-tablet-to-pc.ps1` untuk mencadangkan sesi WhatsApp baru (`backup-20261105-033958`). | Hapus folder backup. |
| 03:57 | BACA | Tablet WhatsApp End-to-End | Pengguna mengonfirmasi chat WhatsApp dengan Akari di tablet sudah berfungsi normal. | - |
| 06:19 | TULIS | Tablet `~/Hermes-Agent` | Pasang modul `reply_quotes.py` dan patch `adapter.py` (cadangan `adapter.py.bak-pre-adaptive-20261105`) untuk fitur *Adaptive Quote-Reply* (membalas biasa jika 1 pesan; mengutip/quote jika ada beberapa pesan beruntun). Aktifkan `reply_quote_mode: adaptive` di `config.yaml`. | Kembalikan dari backup. |
| 06:29 | TULIS | PC Windows Task Scheduler | Daftarkan Scheduled Task `AkariTabletDailyBackup` (harian jam 12:00, background/hidden, auto-retry jika PC mati). Uji perdana menghasilkan backup `backup-20261105-063059`. | `Unregister-ScheduledTask AkariTabletDailyBackup` |
| 13:50 | TULIS | Tablet `~/.hermes/SOUL.md` | Cadangkan ke `SOUL.md.bak-pre-memory-20261105`. Perbarui aturan kemampuan: buka akses memori personal & profil Bos (`target: user` & `target: memory`) secara natural, batasi privasi tanpa kredensial. | Kembalikan dari backup. |
| 13:54 | TULIS | Tablet `~/.hermes/config.yaml` | Cadangkan ke `backups/pre-akari-memory-20261105-135418`. Tambahkan konfigurasi `memory:` dan izinkan tool `memory` di `platform_toolsets.whatsapp`. Gateway direstart dan WhatsApp terhubung kembali. | Kembalikan dari backup. |
| 14:44 | TULIS | PC `%LOCALAPPDATA%\hermes\backups\tablet` | Perbarui `scripts/backup-tablet-to-pc.ps1` menyertakan folder `.hermes/memories`. Backup berhasil di `backup-20261105-144447`. | Hapus folder backup. |
| 15:25 | BACA | Tablet `~/.hermes/memories/USER.md` | Uji memori: sesi lama (dibuat sebelum memori aktif) tidak memanggil tool `memory`. Setelah `/new`, permintaan "ingat ya akari aku suka menggambar" memanggil tool `memory` dan `USER.md` berisi "Suka menggambar.". | - |
| 15:42 | TULIS | Tablet `~/.hermes/config.yaml` & `SOUL.md` | Cadangkan ke `backups/pre-akari-timestamps-20261105-154228`. Aktifkan `gateway.message_timestamps.enabled: true` (zona waktu tablet terverifikasi `WIB`) dan tambahkan aturan kesadaran waktu di `SOUL.md` (Tahap 2.2). | Kembalikan dari backup. |
| 15:46 | BACA | Tablet WhatsApp End-to-End | Verifikasi Tahap 2.2: pesan masuk menerima prefix `[Thu 2026-11-05 15:46:09 WIB]` dan Akari menjawab jam saat ini + hobi menggambar (`USER.md`) dengan tepat dalam 1 panggilan API. | - |
| 15:51 | TULIS | Tablet `~/.hermes/config.yaml`, `SOUL.md` & `backup-tablet-to-pc.ps1` | Cadangkan ke `backups/pre-akari-cronjob-20261105-155107`. Aktifkan toolset `cronjob` (`cronjob_manage`) di `platform_toolsets.whatsapp`, sinkronkan panduan pengingat di `SOUL.md` (`enabled_toolsets: []`), dan tambahkan `.hermes/cron` ke skrip backup (Tahap 2.3). | Kembalikan dari backup. |
| 15:57 | BACA | Tablet WhatsApp End-to-End | Verifikasi Tahap 2.3: permintaan "ingatkan aku 2 menit lagi untuk makan ya" (15:54) berhasil membuat job `f376a0618c89` (`once in 2m`, `enabled_toolsets: []`), dieksekusi pada 15:57:14 WIB (5.102 input token, 99 output token), dan terkirim kembali ke WhatsApp pemilik dengan status `delivered`/`read`. | - |

*Tidak mengubah konfigurasi, tapi memakai kuota.

### Status Terkini
1. **Server Utama Aktif 24 Jam**: Tablet Termux (`192.168.1.18`) dengan `termux-wake-lock` dan skrip auto-start `~/.termux/boot/start-akari.sh`.
2. **Karakter & Kemampuan Akari (Tahap 1–2.3)**: `SOUL.md` tersinkronisasi 100%, toolset WhatsApp terbatas hanya pada `memory` + `cronjob`, kesadaran waktu lokal (`WIB`) aktif, grup dinonaktifkan, dan allowlist pemilik aktif (format `08...` dan `628...`).
3. **Model & Fallback**: `hermes-fallback` terverifikasi di 9Router tablet.
4. **WhatsApp Bridge Aktif**: Terhubung pada `port 3000` (`mode: bot`), diproteksi dari bug replay dengan ledger SHA-256 persisten (`32/32` unit test lulus), dan sesi lama di PC sudah dipensiunkan.
5. **Backup Persisten**: Seluruh konfigurasi dan sesi WhatsApp tablet terbaru telah tercadangkan di PC (`%LOCALAPPDATA%\hermes\backups\tablet`).
