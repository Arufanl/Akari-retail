# Integrasi Hermes ke 9Router

Tanggal lokal: 20 Oktober 2026 (Asia/Jakarta).

Hermes memakai provider `custom`, endpoint `http://127.0.0.1:20128/v1`, mode `chat_completions`, dan combo `akari`.

Combo berurutan dengan strategi global `fallback`:

1. `nvidia/nvidia/nemotron-3-ultra-550b-a55b`
2. `oc/mimo-v2.6-flash-free`

Namespace NVIDIA pertama adalah rute provider; namespace kedua bagian ID model upstream. Rute satu namespace menghasilkan model tidak ditemukan pada pengujian ini.

Key lokal khusus bernama `Hermes Akari`, dibatasi pada combo dan kedua rute model. Nilainya hanya disimpan dalam `.env` Hermes di variabel `AKARI_9ROUTER_API_KEY`. Tidak ada nilai rahasia dicatat di workspace.

Backup sebelum perubahan pertama:

- Hermes: `C:\Users\Akari\AppData\Local\hermes\backups\pre-9router-connect-2026-10-19T20-31-49-646Z`
- 9Router: `C:\Users\Akari\AppData\Roaming\9router-backups\pre-hermes-connect-2026-10-19T20-31-49-646Z`

Nama folder menggunakan UTC. Backup 9Router mencakup salinan folder dan `consistent-data.sqlite`, dibuat dengan API backup SQLite dan diperiksa integritasnya.

Verifikasi:

- Permintaan pendek ke combo `akari` berhasil HTTP 200 dengan isi balasan.
- Resolver runtime Hermes terpasang membaca model `akari`, endpoint lokal, mode Chat Completions, dan key khusus yang sesuai; seluruh pemeriksaan lulus.
- Model cadangan mengembalikan HTTP 429 saat diuji langsung sebelumnya; keberhasilan fallback saat model utama gagal belum dibuktikan.
- Provider dan key lama dipertahankan. Konfigurasi Gemini lama tersedia dalam backup; key Gemini tidak dihapus.
- Gateway WhatsApp, scheduler, dan auto-start tidak dijalankan oleh pekerjaan ini.

Untuk percakapan baru, jalankan 9Router pada `127.0.0.1:20128` sebelum Hermes. Sesi Hermes yang sudah berjalan perlu dimulai ulang untuk membaca konfigurasi baru.
