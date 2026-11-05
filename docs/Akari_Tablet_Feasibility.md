# Rencana Pemeriksaan Kelayakan Tablet Akari

Tanggal: 17 Oktober 2026  
Status: rencana pemeriksaan bertahap; bukan instruksi instalasi penuh

## Tujuan

Menentukan apakah Huawei MatePad SE 11 RAM 4 GB dapat menjalankan gateway Akari melalui Termux dengan cukup stabil untuk pilot pribadi. Keberhasilan menjalankan program sekali belum dianggap membuktikan kelayakan operasi jangka panjang.

## Keputusan yang sudah berlaku

- Pilot memakai Baileys dengan nomor WhatsApp khusus Akari.
- Risiko integrasi WhatsApp tidak resmi diterima untuk pilot.
- WhatsApp Agents tidak dikejar pada tahap ini.
- Model dimulai dari API gratis dan tidak boleh berpindah otomatis ke layanan berbayar.
- Riwayat percakapan tidak dihapus otomatis pada tahap awal; penghapusan manual dan opsi retensi harus tersedia.
- Riwayat percakapan, memori personal, dan catatan dikelola sebagai data terpisah.
- Target sapaan tetap 3–5 per hari dan boleh lebih secara adaptif. Jeda serta batas maksimum adaptif harus dapat dikonfigurasi; nilai awal belum diputuskan.
- Backup lokal dan pemulihan dasar masuk sejak awal. Cloud terenkripsi tetap opsi tahap berikutnya dan penyedianya belum dipilih.

## Gerbang pemeriksaan

### T0 — Inventaris perangkat, tanpa instalasi

Kumpulkan:

- nama/model perangkat dan nomor model;
- versi HarmonyOS dan nomor build;
- versi patch keamanan bila ditampilkan;
- total RAM yang dilaporkan perangkat;
- kapasitas penyimpanan total dan ruang kosong;
- apakah pemasangan APK dari sumber luar AppGallery diizinkan;
- pilihan pengelolaan baterai/aplikasi untuk menjalankan aplikasi secara manual di latar belakang.

Lulus bila identitas perangkat dan kemampuan dasar memasang serta mengizinkan aplikasi latar belakang dapat dipastikan. Tahap ini tidak mengubah pengaturan dan tidak memasang aplikasi.

#### Hasil sementara T0 — 17 Oktober 2026

| Item | Hasil |
|---|---|
| Model | HUAWEI AGS6-W09 |
| Sistem | HarmonyOS 2.0.0 |
| Nomor pembuatan | 2.0.0.115(C301E1R1P1) GPU Turbo |
| Prosesor | HUAWEI Kirin 710A |
| RAM | 4,0 GB |
| Penyimpanan | 128 GB total; 88,1 GB bebas |
| Resolusi | 1920 × 1200 |
| Kernel | 4.14.116; build kernel 19 Februari 2025 |
| Patch keamanan | 1 Februari 2025 |
| Versi kustom | CUST 2.0.0.1(C301) |

Status T0: **lulus pada 17 Oktober 2026**. Kapasitas penyimpanan mencukupi untuk spike. RAM 4 GB belum dinyatakan cukup untuk operasi harian sampai pemakaian proses aktual diuji. Arsitektur userspace belum diasumsikan hanya dari nama prosesor dan akan diperiksa dari Termux pada T1.

Hasil pemeriksaan pengaturan:

- tersedia pengelolaan peluncuran aplikasi secara manual;
- tersedia pilihan **Peluncuran otomatis**, **Peluncuran sekunder**, dan **Jalankan di latar belakang**;
- tersedia menu **Pasang aplikasi dari sumber eksternal**;
- F-Droid sudah terpasang, sehingga Termux dan add-on berikutnya dapat dipertahankan dari sumber/tanda tangan yang sama;
- pengaturan khusus Termux belum dilakukan karena aplikasinya belum dipasang.

### T1 — Termux dasar saja

Setelah T0 ditinjau, pasang Termux dari sumber resmi yang dipilih. Termux dan add-on seperti Termux:Boot harus berasal dari sumber dengan tanda tangan yang sama. Pada tahap ini belum memasang Hermes, Baileys, 9Router, atau kode Akari.

Uji yang direncanakan:

- Termux dapat dibuka dan melaporkan arsitektur serta Android API level;
- ruang penyimpanan dan memori tersedia dapat diperiksa;
- sesi dasar tetap hidup ketika layar dimatikan untuk periode pendek.

#### Hasil sementara T1 — 17 Oktober 2026

| Item | Hasil |
|---|---|
| Sumber instalasi | F-Droid |
| Arsitektur userspace | aarch64 |
| ABI utama | arm64-v8a |
| ABI 64-bit yang didukung | arm64-v8a |
| ABI 32-bit yang didukung | armeabi-v7a, armeabi |
| Android yang dilaporkan Termux | Android 10 |
| Android API/SDK | 29 |
| Kernel | Linux 4.14.116 aarch64 |
| MemTotal saat pemeriksaan | 3.941.584 kB, sekitar 3,76 GiB |
| MemAvailable saat pemeriksaan | 1.418.372 kB, sekitar 1,35 GiB |
| Ruang filesystem Termux | Filesystem `/data`: sekitar 107 GiB total, 25 GiB terpakai, dan 82 GiB tersedia |

Status T1: **lulus pada 17 Oktober 2026**. Arsitektur, API level, dan ruang filesystem memenuhi prasyarat dasar untuk melanjutkan spike Termux. Proses shell dasar menghasilkan heartbeat berurutan sedikitnya dari 19:20 sampai 19:40 saat layar tablet dimatikan, tanpa pengaturan khusus Termux. Nilai memori masih perlu diamati di bawah beban; hasil ini belum membuktikan Hermes dan bridge WhatsApp dapat berjalan stabil bersamaan. Paket dasar melaporkan pembaruan tersedia, tetapi pembaruan belum dilakukan pada tahap pengukuran ini.

### T2 — Ketahanan proses latar belakang

Jalankan proses uji ringan tanpa Hermes. Uji layar mati, perpindahan aplikasi, pengisian daya, Wi-Fi putus-sambung, dan reboot. Konfigurasikan pengecualian baterai/wake lock hanya setelah pilihan pengaturan perangkat sudah dipahami.

Lulus bila proses dapat dijaga atau dipulihkan secara konsisten dan hasil kegagalan dapat didiagnosis.

#### Hasil sementara T2 — 17 Oktober 2026

- Pengelolaan peluncuran otomatis untuk Termux telah dimatikan berdasarkan konfirmasi pemilik.
- **Peluncuran otomatis**, **Peluncuran sekunder**, dan **Jalankan di latar belakang** telah diaktifkan untuk Termux.
- Uji layar mati satu jam ditunda sampai waktu istirahat pemilik; tahap ini belum dinilai lulus atau gagal.
- Uji ketahanan lebih panjang, putus-sambung jaringan, dan reboot belum dilakukan.

### T3 — Runtime minimum

Pasang hanya runtime yang benar-benar dibutuhkan oleh jalur Hermes/WhatsApp terpilih. Catat pemakaian RAM, penyimpanan, suhu, dan proses. Jangan memasang 9Router pada tahap ini.

#### Hasil sementara T3 — 17 Oktober 2026

| Komponen | Hasil setelah pembaruan paket dasar |
|---|---|
| Node.js | v26.4.0 |
| npm | 11.21.1 |
| Git | 2.56.0 |
| SQLite CLI | Belum terpasang |
| Python | 3.14.6, aarch64 |
| pip | 26.2.1 |
| SQLite modul Python | 3.54.0; berfungsi tanpa memasang CLI SQLite |
| RAM setelah Python | 3,8 GiB total; sekitar 1,3 GiB tersedia saat pemeriksaan |
| Swap setelah Python | 2,5 GiB total; sekitar 1,8 GiB sedang digunakan |

Status T3: **parsial**. Node.js memenuhi persyaratan versi minimum bridge, tetapi kompatibilitas aktual Node.js 26 dengan bridge belum diuji. Python 3.14 adalah versi runtime yang dipakai Hermes saat ini dan modul SQLite bawaan berfungsi. Ketersediaan RAM cukup untuk melanjutkan spike secara bertahap, tetapi margin sempit dan penggunaan swap perlu diamati. 9Router dan CLI SQLite tetap tidak dipasang.

### T4 — Hermes tanpa WhatsApp

Uji instalasi minimum Hermes, pemeriksaan kesehatan, dan satu percakapan dengan provider gratis. Tool web, browser, shell otonom, dan kemampuan lain di luar lingkup Akari tetap dinonaktifkan.

Catatan jalur instalasi terbaru: dokumentasi Hermes saat ini mengarahkan pengguna Termux ke paket APT Termux (`pkg install hermes-agent`). Installer sumber/pip lama tidak digunakan untuk perangkat ini. Ketersediaan dan metadata paket harus diperiksa terlebih dahulu tanpa memasangnya.

#### Status T4 — terblokir upstream pada 17 Oktober 2026

- `pkg show hermes-agent` dan `apt-cache policy hermes-agent` tidak menemukan paket karena repositori Hermes belum ditambahkan; paket tersebut bukan bagian repositori default Termux.
- Hermes menyediakan repositori APT bertanda tangan terpisah untuk kanal stable/canary.
- Dokumentasi resmi Hermes saat pemeriksaan menampilkan peringatan bahwa paket Termux sedang rusak dan perbaikan masih dalam proses.
- Repositori Hermes tidak ditambahkan dan paket tidak dipasang.
- Installer desktop/server, instalasi pip dari source, kanal canary, serta skrip pihak ketiga tidak digunakan sebagai jalan pintas.
- Atas persetujuan pemilik, jalur stable resmi dicoba secara terbatas sampai tahap pengambilan kunci repositori. URL resmi `https://hermes-assets.nousresearch.com/releases/termux/stable/key.asc` mengembalikan HTTP 404 sebanyak dua kali, sehingga fingerprint tidak dapat diverifikasi dan proses dihentikan sebelum menambahkan source APT atau memasang paket.

Kesimpulan sementara: **T4 ditunda karena kondisi distribusi Hermes, bukan karena ketidakcocokan arsitektur tablet**. Pengujian dapat dilanjutkan setelah dokumentasi resmi mencabut peringatan dan paket stable dapat diverifikasi, atau setelah pemilik menyetujui evaluasi fondasi non-Hermes sebagai alternatif.

### T5 — Baileys dan allowlist

Pasangkan nomor khusus Akari, aktifkan allowlist hanya untuk nomor pemilik, nonaktifkan grup, dan pastikan nomor tidak dikenal tidak mendapat respons. Uji reconnect dan kredensial sesi setelah restart.

### T6 — Soak test sebelum implementasi penuh

Uji bertahap 24 jam, kemudian 72 jam bila tahap sebelumnya lulus. Cakup layar mati, reboot, koneksi terputus, API kehabisan kuota, pesan ganda, dan pengiriman proaktif. Lama uji final serta ambang kelulusan belum menjadi keputusan proyek.

## Keputusan yang masih terbuka

- Hermes sebagai fondasi final atau hanya bahan pembanding setelah spike.
- SQLite atau penyimpanan utama lain.
- Model Gemini gratis yang digunakan dan perilaku saat kuota/rate limit habis.
- Nilai retry, timeout, dan circuit breaker.
- Nilai awal jeda serta batas maksimum adaptif sapaan.
- Aturan pengingat berulang yang beberapa kali terlewat dan pengingat saat jeda.
- Retensi opsional riwayat dan log; arti penghapusan pada backup lama.
- Jadwal, retensi, format, dan enkripsi backup lokal.
- Penyedia serta jadwal backup cloud terenkripsi.
- Pemantauan eksternal dan saluran pemberitahuannya.
- Target latensi, toleransi keterlambatan pengingat, durasi soak test final, dan waktu pemulihan.

## Langkah pertama untuk pemilik

Tanpa memasang atau mengubah pengaturan apa pun, buka **Pengaturan → Tentang tablet** dan **Pengaturan → Penyimpanan**, lalu catat atau kirim tangkapan layar yang memperlihatkan:

1. nama perangkat dan nomor model;
2. versi HarmonyOS;
3. nomor build;
4. RAM;
5. kapasitas penyimpanan total dan ruang kosong;
6. versi patch keamanan, jika tersedia.

Selain itu, buka pengaturan **Aplikasi** atau **Baterai** dan beri tahu apakah terdapat pilihan bernama kurang lebih **App launch/Peluncuran aplikasi**, **Battery optimization/Optimasi baterai**, atau izin menjalankan aplikasi di latar belakang. Jangan ubah pilihan tersebut dulu.
