# Status dan handoff proyek Akari

Tanggal pencatatan: 17 Oktober 2026  
Tahap: pilot Hermes di PC Windows; integrasi 9Router/OpenRouter belum selesai  
Dokumen kebutuhan aktif: `docs/Akari_PRD_v0.1.md`

## Ringkasan keadaan saat berhenti

- Hermes Agent `v0.22.2` channel `stable` terpasang native Windows di `%LOCALAPPDATA%\hermes`.
- Persona Akari aktif: kawaii dan ekspresif, memanggil pengguna “Bos”, tidak romantis, dapat mengoreksi dengan lembut, serta diarahkan membalas singkat dan alami. Tool terminal/web dan kemampuan tambahan tetap tidak tersedia untuk Akari.
- Provider Hermes yang masih tersimpan sebagai konfigurasi aktif/pemulihan adalah Gemini dengan model `gemini-3.8-flash`. API key tetap hanya berada di `.env` lokal dan tidak dicatat di dokumen/repo.
- WhatsApp melalui Baileys sudah pernah berhasil: pairing nomor khusus, allowlist pemilik, satu pesan memperoleh satu balasan, dan sesi dapat dipakai lagi setelah restart gateway.
- Gateway WhatsApp tidak dijadikan service dan tidak diaktifkan otomatis. Saat PC mati, tidur, atau gateway berhenti, Akari tidak membalas.
- Sapaan spontan, scheduler, pengingat, memori personal, dan auto-start belum diaktifkan.

## Bug replay WhatsApp

- Pernah terjadi pesan pertama diproses ulang setelah reconnect/restart.
- Diagnosis lokal menemukan event history `append` dan tidak adanya deduplikasi persisten pada bridge Hermes.
- Patch lokal untuk mode bot dan ledger deduplikasi persisten sudah diterapkan pada Hermes `v0.22.2`.
- Sebanyak 28 tes bridge dengan event tiruan lulus tanpa memanggil model: pesan baru, history lama, pesan sendiri, duplikat, dan restart.
- Uji WhatsApp nyata setelah patch belum dilakukan.
- Patch dan petunjuk penerapan ulang tersedia di `patches/hermes-whatsapp-replay-v0.22.2/`; pembaruan Hermes dapat menimpanya.

Rincian lengkap berada di `docs/Akari_Hermes_WhatsApp_Pilot.md`.

## Pekerjaan 9Router hari ini

- Jalur Kiro Free tidak dipakai. Dokumentasi resmi Kiro hanya menjelaskan autentikasi aplikasi/CLI Kiro; API key otomasi tersedia untuk paket berbayar dan tidak ada dukungan resmi yang jelas untuk penggunaan kredensial Free melalui router pihak ketiga.
- `9router@0.5.104` dipasang dari npm dengan versi persis terkunci.
- Server diuji berjalan hanya pada `127.0.0.1:20128`, bukan `0.0.0.0`.
- Password dashboard bawaan sudah diganti. Password tidak pernah dicetak dan disimpan sebagai blob DPAPI lokal di `%APPDATA%\9router\dashboard-password.dpapi`, yang hanya dapat dibuka oleh profil Windows ini.
- Data 9Router berada di `%APPDATA%\9router`; tidak berada di workspace/repo.
- Pengaturan 9Router terverifikasi:
  - Caveman: mati.
  - RTK/token saver: mati.
  - Strategi combo: `fallback`.
  - Strategi koneksi: `fill-first`, bukan round-robin.
- Belum ada akun/provider OpenRouter yang dihubungkan.
- Belum ada API key lokal 9Router yang dibuat untuk Hermes.
- Belum ada panggilan model melalui 9Router.

## Perubahan aman pada Hermes

Sebelum perubahan, `config.yaml` dan `.env` dicadangkan ke:

`%LOCALAPPDATA%\hermes\backups\pre-9router-20261017-231732`

Nilai yang sekarang diterapkan:

```yaml
agent:
  api_max_retries: 1
  auto_recovery_cycles: 0

auxiliary:
  title_generation:
    enabled: false
```

Pada source Hermes yang terpasang, `api_max_retries` dipaksa minimum `1`; konfigurasi ini mencegah loop retry Hermes bertumpuk dengan backoff router. Title generation dimatikan agar percakapan pertama tidak menimbulkan panggilan model tambahan.

Konfigurasi Gemini dan `GEMINI_API_KEY` tidak dihapus. Tidak ada fallback Hermes aktif menuju provider lain; Gemini tetap dapat dipulihkan manual dari backup.

## Model uji yang dipilih, tetapi belum digunakan

- Provider: OpenRouter Free.
- Model tunggal: `nvidia/nemotron-3-ultra-550b-a55b:free`.
- Model dipilih karena slug-nya eksplisit `:free`; `openrouter/free` tidak dipakai karena dapat mengganti model di belakang layar.
- Batas paket gratis OpenRouter dan ketersediaan model dapat berubah.
- Endpoint gratis tersebut menyatakan input/output dapat dicatat dan digunakan untuk peningkatan layanan NVIDIA. Jangan kirim data pribadi atau rahasia pada tahap uji.

## Langkah berikutnya

1. Pengguna membuat satu API key OpenRouter gratis tanpa mengaktifkan billing.
2. Key ditempel melalui prompt `SecureString` lokal dan disimpan sebagai blob DPAPI di `%APPDATA%\9router\openrouter-api-key.dpapi`; key tidak dikirim ke chat atau log.
3. Hubungkan tepat satu koneksi OpenRouter di 9Router dan batasi model ke `nvidia/nemotron-3-ultra-550b-a55b:free`.
4. Buat satu key lokal 9Router khusus Hermes dengan allowlist hanya model tersebut.
5. Cadangkan konfigurasi Hermes lagi, lalu arahkan provider sementara ke endpoint `http://127.0.0.1:20128/v1`.
6. Jalankan satu percakapan terminal singkat saja dan verifikasi dari log 9Router bahwa provider/model yang benar-benar dipakai adalah OpenRouter dan slug `:free` di atas.
7. Jangan jalankan gateway WhatsApp sampai uji terminal dinyatakan berhasil.

## Batas yang tetap berlaku

- Tidak ada rotasi akun untuk melewati kuota.
- Tidak ada provider atau fallback berbayar otomatis.
- Tidak ada WhatsApp gateway, scheduler, sapaan spontan, memori personal, maupun auto-start pada langkah berikutnya.
- 9Router harus selalu dijalankan eksplisit dengan `--host 127.0.0.1`; default CLI `0.0.0.0` tidak boleh dipakai.
- Operasi 24 jam belum dijanjikan selama server masih berada di PC.

