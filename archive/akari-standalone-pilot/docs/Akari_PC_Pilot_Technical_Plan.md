# Rencana Teknis Pilot Akari di PC Tanpa Hermes

Tanggal: 17 Oktober 2026  
Status: vertical slice awal diimplementasikan; pairing WhatsApp dan panggilan Gemini nyata menunggu konfigurasi lokal pengguna

## Keputusan dan batas yang berlaku

- Pilot pertama dijalankan di PC Windows.
- Target akhir tetap tablet melalui Termux.
- Integrasi WhatsApp memakai Baileys dengan nomor khusus Akari dan hanya nomor pemilik yang diizinkan.
- Model memakai Gemini API gratis dan tidak boleh beralih otomatis ke layanan berbayar.
- Penyimpanan utama lokal; riwayat percakapan, memori, dan catatan dikelola terpisah.
- Scheduler program menangani pengingat dan sapaan; model tidak memeriksa waktu terus-menerus.
- Companion anime tetap ditunda.
- Selama server berada di PC, Akari berhenti ketika PC mati, tidur, hibernasi, kehilangan jaringan, atau proses dihentikan. Tahap ini tidak menjanjikan operasi 24 jam.

## Kesimpulan kelayakan

Pilot tanpa Hermes layak dibuat sebagai satu aplikasi Node.js. Baileys dan SDK Gemini resmi sama-sama membutuhkan Node.js 20 atau lebih baru. Node.js 24 LTS dipilih sebagai baseline pengembangan PC; tablet saat pemeriksaan memiliki Node.js 26.4.0. Kode harus diuji pada kedua major version sebelum migrasi.

SQLite bawaan Node (`node:sqlite`) menghindari addon native seperti `better-sqlite3` yang dapat menambah masalah kompilasi di Termux. Modul tersebut berstatus release candidate pada Node.js 24, sehingga penggunaannya harus dibungkus di satu adapter penyimpanan dan dilindungi dengan uji migrasi/backup. Untuk beban single-user Akari, API sinkronnya dapat diterima selama query kecil dan pekerjaan jaringan tidak dilakukan di dalam transaksi.

## Arsitektur yang diusulkan

```text
WhatsApp nomor Akari
        |
        v
Baileys transport
  - pairing dan reconnect
  - filter pesan baru
  - tolak grup/nomor lain
        |
        v
Application service
  - validasi dan deduplikasi
  - orkestrasi percakapan
  - aturan privasi
        |
        +--------> Gemini adapter
        |           - API gratis saja
        |           - model dari konfigurasi
        |           - timeout dan error eksplisit
        |
        +--------> SQLite adapter
        |           - pesan dan status proses
        |           - memori, catatan, pengingat
        |           - outbox dan audit minimal
        |
        +--------> Scheduler
                    - polling item jatuh tempo
                    - perhitungan WIB deterministik
                    - catch-up setelah proses hidup kembali
```

Tidak ada web server atau port publik pada vertical slice pertama.

## Pemisahan kode, konfigurasi, kredensial, dan data

Repositori aplikasi yang boleh masuk version control:

```text
akari-app/
  src/
    app/
    whatsapp/
    llm/
    storage/
    scheduler/
    policy/
  prompts/
  migrations/
  test/
  config/
    default.json
  .env.example
  package.json
  package-lock.json
```

State runtime berada di lokasi terpisah yang ditentukan oleh `AKARI_HOME`:

```text
akari-state/
  config/akari.json
  secrets/.env
  auth/baileys/
  data/akari.sqlite
  backups/
  logs/
```

Aturan pemisahan:

- `src`, prompt, migrasi, tes, dan konfigurasi default tidak berisi rahasia atau data pengguna.
- API key Gemini hanya berada di `secrets/.env` melalui `GEMINI_API_KEY`.
- Nomor allowlist dan model dapat berada di konfigurasi runtime, bukan ditanam di kode.
- Folder autentikasi Baileys berisi kunci Signal jangka panjang dan diperlakukan seperti private key.
- Seluruh `akari-state` dikecualikan dari Git.
- Lokasi diturunkan dari `AKARI_HOME`, bukan path Windows yang ditulis langsung di kode.
- Migrasi ke Termux dilakukan dengan kode yang sama dan pemulihan dari snapshot yang konsisten, bukan menyalin database aktif.

## Penyimpanan dan sesi WhatsApp

Untuk vertical slice pertama, `useMultiFileAuthState` Baileys dapat dipakai hanya sebagai mekanisme pairing pilot satu akun/satu proses. Dokumentasi Baileys menyatakan penyimpanan ini tidak direkomendasikan untuk produksi. Sebelum pemakaian harian di tablet, auth state perlu dipindahkan ke adapter SQLite atau dibuktikan cukup andal melalui uji restart dan backup.

SQLite menjadi sumber kebenaran untuk data Akari. Skema awal minimal hanya memerlukan:

- `messages`: ID WhatsApp unik, arah pesan, pengirim, waktu, teks, dan status pemrosesan;
- `outbox`: balasan yang menunggu dikirim dan hasil pengiriman;
- `schema_migrations`: versi skema.

Tabel memori, catatan, pengingat, dan sapaan ditambahkan setelah vertical slice chat lulus. Pemisahan tabel dan service mencegah riwayat percakapan dianggap otomatis sebagai memori personal.

## Scheduler sesuai arah PRD

Scheduler tidak dibutuhkan untuk uji satu pesan, tetapi desainnya ditetapkan sejak awal:

- satu loop ringan memeriksa SQLite secara berkala;
- semua waktu disimpan sebagai timestamp UTC dan ditampilkan/dikonfirmasi dalam WIB;
- pengingat berulang disimpan sebagai aturan dan `next_run_at`, bukan satu proses timer per pengingat;
- setelah restart, query mencari item terlewat dan membuat satu rangkuman sesuai PRD;
- pengiriman memakai outbox agar kegagalan dan retry terbatas dapat diaudit;
- sapaan memakai state tersendiri dan tidak dihitung sebagai pengingat;
- ketika PC tidur atau mati, scheduler tidak berjalan dan tidak dapat mengirim apa pun.

Tidak diperlukan `node-cron` untuk desain ini. Polling SQLite lebih mudah menangani restart dan pengingat terlewat.

## Dependensi sebelum implementasi

### Perangkat dan akun

- PC Windows dengan koneksi internet dan kemampuan mencegah sleep selama sesi uji.
- Nomor WhatsApp khusus Akari yang aktif pada perangkat utama dan dapat menautkan perangkat melalui QR/pairing.
- API key dari Google AI Studio pada tier gratis tanpa billing otomatis.

### Runtime

- Node.js 24 LTS pada PC, termasuk npm.
- Git untuk version control.

Hasil pemeriksaan read-only PC pada 17 Oktober 2026:

| Komponen | Hasil |
|---|---|
| Arsitektur OS | Windows x64 |
| PowerShell | 5.1.19041.6456 |
| Node.js | 24.21.0 |
| npm | 11.19.0 melalui `npm.cmd` |
| Git | 2.55.0.windows.5 |
| `node:sqlite` | Berfungsi; SQLite 3.53.4 |

PowerShell menolak wrapper `npm.ps1` karena execution policy yang aktif. Pengembangan dapat memakai `npm.cmd` tanpa mengubah atau melonggarkan kebijakan keamanan sistem. Versi Node.js harus diperiksa lagi terhadap rilis keamanan terbaru tepat sebelum dependensi dipasang.

### Paket aplikasi yang diusulkan

- `baileys`, dipin ke versi persis yang diuji dan dikunci melalui `package-lock.json`;
- `@google/genai`, SDK JavaScript resmi Google, juga dipin dan dikunci;
- `pino` sebagai logger yang kompatibel dengan Baileys.

Tidak diperlukan pada vertical slice:

- Hermes Agent;
- Python;
- 9Router;
- Docker, WSL, service Windows, atau database server;
- `dotenv`, karena Node mendukung `--env-file`;
- library cron;
- addon SQLite native;
- Obsidian;
- Termux:Boot.

Versi yang dikunci untuk pilot pada 17 Oktober 2026 adalah `baileys@7.0.0-rc14`, `@google/genai@2.30.0`, dan `pino@10.4.0`. Baileys 7 masih release candidate dan membawa perubahan besar. Versi tidak boleh dibiarkan memakai rentang longgar atau Git branch `main`; pembaruan dilakukan sengaja setelah uji regresi.

## Alur vertical slice terkecil

Tujuan: satu pesan teks dari nomor pemilik menghasilkan satu balasan teks.

1. Proses memvalidasi konfigurasi dan memastikan `AKARI_HOME` dapat ditulis.
2. Buka SQLite, jalankan migrasi minimal, lalu buka auth state Baileys.
3. Tampilkan pairing dan tautkan nomor khusus Akari.
4. Setelah koneksi terbuka, dengarkan `messages.upsert`.
5. Hanya proses event `notify`, semua item dalam array, pesan bukan `fromMe`, chat individual, dan JID yang cocok dengan allowlist.
6. Simpan ID pesan dengan batas unik sebelum memanggil Gemini.
7. Kirim teks pesan dan prompt karakter minimum ke model yang dikonfigurasi.
8. Kirim satu balasan melalui `sendMessage` dan catat hasilnya.
9. Nomor lain, grup, history backfill, pesan sendiri, status/broadcast, media, dan pesan tanpa teks diabaikan tanpa memanggil Gemini.

## Uji penerimaan vertical slice

- Proses gagal start bila API key, allowlist, model, atau `AKARI_HOME` hilang.
- QR/pairing berhasil dan sesi dapat dipakai setelah restart.
- Pesan teks baru dari nomor yang diizinkan mendapat tepat satu balasan.
- Pesan yang sama dikirim ulang oleh Baileys tidak menghasilkan panggilan model/balasan kedua.
- Pesan dari nomor lain dan grup tidak mendapat balasan dan tidak dikirim ke Gemini.
- API Gemini gagal atau kuota habis menghasilkan log kegagalan yang jelas tanpa fallback berbayar.
- Mematikan atau menidurkan PC menghentikan layanan; setelah dinyalakan tidak ada klaim bahwa pesan/pengingat berjalan selama masa mati.
- Tidak ada API key, auth WhatsApp, database, atau isi percakapan di Git.

## Batas vertical slice

- Belum ada memori personal, catatan, pengingat, sapaan, backup otomatis, atau restore.
- Belum ada jaminan retry balasan tepat sekali pada crash di antara pengiriman WhatsApp dan commit status; outbox penuh ditambahkan pada tahap berikutnya.
- `useMultiFileAuthState` hanya untuk pilot awal, bukan keputusan penyimpanan auth produksi.
- Tier gratis Gemini dapat membatasi atau menolak permintaan dan data pada tier gratis dapat digunakan Google untuk peningkatan produk sesuai kebijakan tier tersebut.
- Baileys tetap integrasi WhatsApp tidak resmi dengan risiko logout, perubahan protokol, dan pembatasan akun.

## Urutan setelah persetujuan dependensi

1. Periksa versi Node.js, npm, dan Git yang sudah ada di PC tanpa memasang apa pun.
2. Tentukan versi paket persis berdasarkan registry dan release resmi pada hari instalasi.
3. Buat skeleton repositori, pemisahan `AKARI_HOME`, `.gitignore`, dan konfigurasi contoh.
4. Uji `node:sqlite` serta migrasi minimal tanpa WhatsApp/Gemini.
5. Uji Gemini dengan satu prompt lokal tanpa WhatsApp.
6. Uji pairing Baileys tanpa memanggil Gemini.
7. Gabungkan menjadi alur satu pesan masuk → satu balasan.
8. Uji allowlist, grup, history backfill, pesan duplikat, kegagalan API, restart, dan sleep PC.
9. Baru setelah vertical slice lulus, tambahkan outbox kuat, catatan, memori, scheduler, pengingat, sapaan, dan backup secara bertahap.

## Referensi resmi yang diperiksa

- Baileys quickstart dan event handling: https://baileys.wiki/docs/
- Baileys session management: https://github.com/WhiskeySockets/docs/blob/main/authentication/session-management.mdx
- Baileys package metadata: https://github.com/WhiskeySockets/Baileys/blob/master/package.json
- Google Gen AI SDK: https://ai.google.dev/gemini-api/docs/libraries
- Gemini API quickstart: https://ai.google.dev/gemini-api/docs/get-started
- Gemini pricing/data tier: https://ai.google.dev/gemini-api/docs/pricing
- Node.js releases: https://nodejs.org/en/about/previous-releases
- Node.js SQLite: https://nodejs.org/download/release/latest-v24.x/docs/api/sqlite.html
