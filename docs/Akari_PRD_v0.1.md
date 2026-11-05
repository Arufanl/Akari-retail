# PRD Akari — Asisten dan Companion Pribadi
Versi: 0.1 — Draf untuk ditinjau
Tanggal: 16 Oktober 2026
Pembaruan keputusan: 17 Oktober 2026
Status: kebutuhan produk; belum merupakan persetujuan implementasi atau pilihan teknologi final.

## 1. Tujuan dan masalah
Akari adalah teman mengobrol sekaligus asisten pribadi untuk satu pengguna. Pengguna ingin percakapan yang hangat dan konsisten, tempat menitipkan catatan tanpa format rumit, serta pengingat yang dapat dikelola melalui chat. Pengguna sering lupa atau malas mencatat ide dan pengeluaran; keuangan lengkap dikembangkan setelah versi pertama.

Prioritas pertama: pengalaman teman mengobrol. Catatan, memori, sapaan, dan pengingat mendukung pengalaman tersebut.

## 2. Pengguna dan akses
- Hanya untuk pemilik; bukan bot publik.
- Menggunakan nomor WhatsApp khusus Akari. Pemilik memiliki dua nomor.
- Hanya nomor pemilik yang diizinkan dapat menggunakan Akari.
- Tidak melayani nomor lain atau grup dan tidak membuka akses memori kepada mereka.
- Nomor lengkap dan kredensial tidak dicantumkan dalam PRD.

## 3. Lingkup versi pertama
1. Chat teks melalui WhatsApp dengan kepribadian Akari.
2. Memori persisten dan personalisasi bertahap dari percakapan.
3. Sapaan spontan adaptif.
4. Menyimpan, mencari, dan merangkum catatan, ide, link, dan calon tugas.
5. Pengingat sekali, berulang, tunda, selesai, dan batalkan.
6. Kendali privasi, koreksi, penghapusan memori, ketahanan gangguan, serta cadangan/pemulihan.

Companion PC ditunda. PC tetap digunakan untuk pengembangan dan pengujian. Target operasional: server di tablet tetap aktif ketika PC mati; target 24 jam memerlukan uji keandalan, bukan jaminan ketersediaan tanpa gangguan.

## 4. Karakter
| Atribut | Keputusan |
|---|---|
| Panggilan & Nama Lengkap | **Akari Kyoko** (dipanggil **Akari**) |
| Gender dan ras | Perempuan, elf |
| Usia & Tanggal Lahir | Tampak setara 21 tahun manusia; usia elf sebenarnya **231 tahun** (lahir **10 Oktober 1795** kalender manusia) |
| Rambut & Mata | Rambut pirang, mata **biru muda** |
| Gaya pakaian harian | *Casual sweet lolita / soft cottagecore pastel* (gaun terusan berenda krem/putih gading dengan pita, kardigan rajut longgar pink pastel, kaus kaki renda putih, sepatu *mary jane* berpita) |
| Latar fiksi | Jepang dalam dunia fantasi modern |
| Peran | Asisten pribadi yang menyayangi dan perhatian kepada atasannya |
| Panggilan pemilik | Bos |
| Sifat | Hangat, setia, manis/kawaii, punya sisi **PON (*Ponkotsu*)** yang canggung/ceroboh manis saat ngobrol (namun tetap akurat 100% saat mencatat/mengingatkan), manja, suka mencari perhatian dan menggoda |
| Bahasa | Indonesia santai, ekspresif, menggunakan emoji dan sesekali tanda ~ |
| Batas Hubungan | Diizinkan **romantis manis (*wholesome*)** sampai batas wajar (bisa manja/bucin manis sekaligus gampang tersipu/salting saat digoda), **tanpa rayuan seksual/NSFW** |
| Koreksi | Berani mengoreksi dengan lembut; tidak selalu mengiyakan |
| Penyesuaian suasana | Lebih tenang dan serius jika topik membutuhkan |

Panduan karakter, batas perilaku, dan contoh dialog akan dibuat dalam Markdown pada tahap berikutnya. Latar fiksi karakter dibedakan dari kejadian nyata. Penampilan, pakaian, warna mata, dan kesukaan belum diputuskan.

Contoh arah gaya, bukan skrip yang wajib diulang:
> Booos~ 🌸 Gimana harinya? Ada cerita seru atau malah bikin capek? Aku siap dengerin! ✨

## 5. Bahasa dan pemahaman pesan
- Tidak mewajibkan bahasa baku, perintah khusus, atau format terstruktur.
- Mendukung typo, singkatan, dan pesan berantakan.
- Jika maksud jelas, proses lalu konfirmasi singkat.
- Jika informasi penting ambigu, tanya hanya bagian yang diperlukan.
- Jangan diam-diam menebak waktu, nominal, atau objek pengingat.
- Gunakan WIB untuk jadwal; konfirmasi dengan tanggal dan jam eksplisit.
- Koreksi seperti “eh bukan besok, lusa” memperbarui item terkait; jika rujukannya ambigu, klarifikasi.

## 6. Memori dan pembelajaran terkendali
Akari semakin mengenal pemilik melalui informasi relevan dan koreksi. Ini bukan pelatihan otomatis kemampuan dasar model dan tidak membutuhkan fine-tuning pada tahap awal.

### Perilaku
- Tidak perlu formulir biodata pemilik di awal; bertanya secara natural seiring percakapan.
- Mengingat preferensi, rutinitas, cerita, proyek, dan keputusan yang relevan.
- Memperbarui memori ketika informasi berubah.
- Membedakan fakta yang dinyatakan pemilik dan dugaan; mengonfirmasi dugaan yang penting.
- Menyimpan sumber/waktu informasi untuk membantu koreksi.
- Merangkum dan menggabungkan memori berulang secara berkala tanpa menghapus catatan penting sembarangan.
- Pembaruan dilakukan ketika ada informasi relevan, bukan terus menulis ulang semua memori.
- Mendukung “apa yang kamu ingat tentangku?”, “tunjukkan apa yang baru kamu ingat”, koreksi, “lupakan itu”, dan “jangan simpan ini”.

### Privasi dan batas
- Preferensi, ide, rutinitas, dan cerita biasa boleh masuk memori otomatis.
- Informasi sensitif seperti rincian kesehatan atau identitas resmi meminta izin sebelum menjadi memori jangka panjang.
- Kata sandi, OTP, dan kunci API tidak dijadikan memori personal.
- Tidak mencari informasi pribadi pemilik di internet, membaca akun/file di luar izin, mengubah aturan karakter, atau menambah akses/kemampuan sendiri.
- Riset internet mandiri ditunda.
- Riwayat percakapan, memori personal, dan catatan adalah jenis data terpisah dan harus dapat dikelola secara terpisah.
- Riwayat percakapan tidak dihapus otomatis pada tahap awal. Sistem harus menyediakan pengaturan retensi untuk tahap berikutnya dan penghapusan manual.
- Cakupan penghapusan terhadap riwayat mentah, log, dan cadangan masih harus diperjelas sebelum implementasi. Jangan menjanjikan “tidak tersimpan sama sekali” hanya karena tidak masuk memori personal.

## 7. Sapaan spontan adaptif
- Target awal 3–5 sapaan per hari, boleh lebih mengikuti pemilik secara adaptif.
- Tidak ada jam tenang tetap karena jadwal kerja dua shift berubah setiap hari.
- Sapaan dapat menanyakan kabar, membuka topik, melanjutkan cerita, atau mengangkat catatan/link/ide lama.
- Jangan mengarang kenangan atau menganggap tugas/link sudah selesai/dibuka.
- Bila sapaan pertama tidak dibalas, boleh satu sapaan tambahan lalu berhenti menumpuk sapaan sampai ada respons.
- Target 3–5 bukan batas maksimum yang kaku; Akari boleh menyapa lebih sering secara adaptif.
- Jeda antarsapaan dan batas maksimum adaptif harus dapat dikonfigurasi. Nilai awalnya belum diputuskan.
- Pemilik dapat mengurangi, menghentikan, dan melanjutkan sapaan lewat chat.
- “Aku mau tidur/lagi sibuk” memicu jeda. Ikuti durasi jika diberikan; jika tidak, tanyakan kapan boleh menyapa lagi.
- Selama jeda, Akari tetap membalas pesan masuk.
- Sapaan spontan dibedakan dari pengingat eksplisit; angka 3–5 tidak membatasi pengingat yang diminta.

## 8. Catatan, ide, link, tugas, dan rangkuman
- Menerima catatan bebas tanpa format khusus.
- Menyimpan isi asli dan ringkasan bila berguna.
- Mengelompokkan catatan sebagai ide, link, catatan umum, atau calon tugas sesuai konteks.
- Membalas singkat setelah penyimpanan berhasil; tidak otomatis memulai diskusi panjang.
- Klarifikasi jika maksud penting belum jelas.
- “Ingin melakukan nanti” tidak otomatis menjadi pengingat bertanggal tanpa waktu yang disepakati.
- Link disimpan bersama keterangan pengguna; pengambilan isi halaman/pencarian web ditunda.
- Mendukung pencarian berdasarkan waktu/topik dan rangkuman sesuai permintaan.
- Boleh mengangkat catatan lama melalui sapaan, tidak mengulang terus saat belum direspons.
- Cara menandai status selesai/sudah dibuka perlu dirinci.

Contoh:
Pemilik: “simpen ide bikin animasi hujan pixel buat nanti”
Akari setelah berhasil: “Udah kusimpan di ide proyek, Bos~ 📝✨”

## 9. Pengingat
### Kemampuan yang disepakati
- Sekali: “besok jam 8 malam ingatkan bayar listrik”.
- Berulang: “setiap tanggal 28 ingatkan catat gaji”.
- Tunda: “ingatkan lagi 30 menit”.
- Tandai selesai atau batalkan melalui chat.
- Ubah jadwal melalui koreksi percakapan.
- Konfirmasi tanggal/jam WIB yang eksplisit setelah berhasil disimpan.
- Jadwal dijalankan penjadwal sistem, bukan mengandalkan model mengecek waktu terus-menerus.

### Gangguan
- Setelah kembali tersambung, kirim satu rangkuman pengingat terlewat dengan jadwal aslinya.
- Tawarkan jadwalkan ulang atau tandai selesai.
- Jangan mengirim semua pengingat lama satu per satu.
- Aturan pengulangan yang beberapa kali terlewat dan pengiriman saat mode jeda perlu dirinci.
- Pengingat eksplisit boleh berjalan pada waktu yang diminta walau tanpa jam tenang.

Pesan sapaan yang dijadwalkan khusus pernah dibahas tetapi belum diputuskan terpisah; jangan menganggap semua otomasi percakapan sudah masuk versi pertama.

## 10. Operasional dan ketahanan
- Program dibuat/diperbarui di PC; server direncanakan berjalan di tablet.
- Pilot awal dikembangkan dan dijalankan di PC Windows. Selama server masih berada di PC, Akari berhenti ketika PC dimatikan, tidur, hibernasi, kehilangan jaringan, atau proses dihentikan; operasi 24 jam belum dijanjikan pada tahap ini.
- PC mati tidak menghentikan WhatsApp selama server tablet dan koneksinya bekerja.
- Memori yang berhasil disimpan harus bertahan setelah restart.
- Konfirmasi “sudah disimpan” hanya setelah penulisan berhasil; kegagalan diberitahukan.
- Pesan masuk terkirim ulang tidak membuat item/efek ganda.
- Percobaan ulang API dibatasi; ketika memungkinkan beri status gangguan yang jelas.
- Cadangan lokal dan pemulihan dasar disiapkan sejak awal dan harus diuji.
- Opsi cadangan cloud terenkripsi disediakan pada tahap yang sesuai. Penyedia, frekuensi, retensi, dan metode enkripsinya belum dipilih.
- Pemberitahuan setelah tersambung kembali dan penanganan pengingat terlewat masuk rancangan.
- Pemantau independen diperlukan bila ingin notifikasi saat server benar-benar mati; server mati tidak bisa mengirim sendiri. Pilihan pemantau/saluran dan tahap implementasinya belum diputuskan.
- Jangan menjanjikan balasan gangguan melalui WhatsApp bila koneksi WhatsApp/server sendiri sedang tidak tersedia.

## 11. Tahap pengembangan berikutnya
Urutan rinci belum ditetapkan.

### A. Keuangan
- Acuan: tabel pengeluaran pemilik yang diberikan dalam percakapan.
- Periode disepakati mengikuti gajian: tanggal 28–27 bulan berikutnya.
- Mencatat pemasukan, pengeluaran, kategori, tanggal, keterangan, anggaran, total harian/per kategori/per periode, dan sisa.
- Kategori awal: Jajan, Bensin, Servis Motor, Listrik + Wi-Fi, Kuota + Pulsa, Kebutuhan Rumah, Subscribe, Investasi, Wishlist, Minus, Other, Tagihan, Sedekah.
- Definisi kategori (khususnya Minus), perlakuan investasi, tanggal default, dan aturan anggaran dibahas saat pengembangan fitur ini.
- Dukung bahasa bebas, koreksi transaksi, serta laporan menyerupai tabel lama.
- Perhitungan dari data transaksi oleh program; bedakan belum mencatat dan benar-benar nol transaksi.
- Aturan langsung menyimpan vs meminta konfirmasi transaksi belum disepakati final.
- Angka historis dalam contoh bukan saldo awal otomatis aplikasi.

### B. Companion PC
- Karakter kecil di desktop; jendela chat dapat dibuka/ditutup tanpa mematikan asisten.
- Gelembung pesan dekat karakter; tidak otomatis membuka jendela.
- Sapaan/pengingat masuk WhatsApp; PC memberi pemberitahuan untuk pesan yang sama.
- Pilihan “Buka WhatsApp” atau “Balas di sini”.
- Balasan PC dilanjutkan di PC; riwayat/konteks bersama.
- Identitas Akari konsisten antarplatform.
- Detail aset visual, animasi, teknologi, perilaku saat offline, dan pencegahan notifikasi ganda belum dirinci.

### C. Kemampuan tambahan
- Menerima pesan suara (STT) dan menghasilkan suara (TTS).
- Membaca gambar/screenshot dan kemungkinan foto struk.
- Pencarian web; riset mandiri hanya setelah batas dan izin dirancang.
- Ringkasan malam/berkala.
- Pengelolaan tugas lebih lengkap.
- Ekspor data untuk pengguna dan fitur urungkan yang lebih lengkap.
- Kontrol memori dan cadangan dasar tetap masuk versi pertama; ekspor lanjutan bukan alasan menundanya.

## 12. Keputusan dan opsi teknis
| Komponen | Status | Peran yang dipertimbangkan atau diputuskan |
|---|---|---|
| Huawei MatePad SE 11 AGS6-W09, Kirin 710A, RAM 4 GB, HarmonyOS 2.0.0 | T0 lulus; kelayakan akhir belum final | Ruang kosong 88,1 GB dari 128 GB, patch keamanan 1 Februari 2025, pemasangan aplikasi eksternal, dan kontrol peluncuran/latar belakang telah diverifikasi; arsitektur userspace dan kestabilan belum diuji |
| Termux | T1 lulus; T2 belum diuji | Berjalan pada userspace aarch64, ABI arm64-v8a, Android 10/API 29; ruang internal memadai dan proses dasar bertahan sedikitnya 20 menit saat layar mati |
| Hermes Agent | Opsi belum final; instalasi Termux sedang terblokir upstream | Calon fondasi agent dan gateway; dokumentasi resmi per 17 Oktober 2026 memperingatkan paket Termux sedang rusak dan menunggu perbaikan |
| Server Node.js tanpa Hermes | Dipilih untuk evaluasi pilot PC | Calon fondasi portable untuk Baileys, Gemini, penyimpanan lokal, dan scheduler; belum merupakan persetujuan implementasi sebelum dependensi ditinjau |
| Baileys dengan nomor khusus Akari | Diputuskan untuk pilot | Integrasi WhatsApp awal; risiko API tidak resmi, pembatasan akun, dan perubahan protokol diterima untuk tahap pilot |
| WhatsApp Agents | Tidak dikejar pada tahap ini | Nomor khusus Akari tetap dipertahankan |
| Gemini API tier gratis | Diputuskan untuk awal | Penyedia model awal; tidak boleh beralih otomatis ke layanan berbayar |
| 9Router | Opsi belum final dan tidak diperlukan untuk langkah awal | Routing/fallback beberapa penyedia bila kelak terbukti perlu |
| Markdown/Obsidian | Opsi belum final | Tampilan atau akses catatan yang bisa dibaca/edit pengguna; bukan mesin memori utama |
| Database lokal, misalnya SQLite | Opsi belum final | Data terstruktur, transaksi, jadwal, riwayat, dan deduplikasi |

- Server lokal dengan API berarti data yang dikirim ke penyedia tetap keluar dari perangkat.
- Router tidak menciptakan kuota gratis tanpa batas.
- Baileys dipakai untuk pilot dengan nomor khusus. Ketentuan pesan proaktif dan kompatibilitas aktual pada tablet tetap harus diuji.
- API gratis adalah titik awal dan kegagalan/kehabisan kuota tidak boleh memicu penggunaan layanan berbayar secara otomatis.
- Obsidian bukan mesin memori dan tidak wajib terpasang di tablet.
- Penyimpanan database utama dan sinkronisasi catatan perlu dipisahkan dengan benar; jangan menjadikan sinkronisasi file sebagai jaminan konsistensi database.
- Tidak ada instalasi atau akses akun yang disetujui hanya dengan dokumen ini.

## 13. Alur dan kriteria penerimaan versi pertama
| Skenario | Hasil yang harus dapat diperiksa |
|---|---|
| Nomor tak diizinkan/grup menghubungi | Tidak dilayani dan tidak mengakses data pribadi |
| Pemilik chat santai/typo | Jawaban relevan dengan gaya Akari; klarifikasi bila penting |
| Pemilik menitipkan ide | Tersimpan, konfirmasi singkat, bisa ditemukan setelah restart |
| Penyimpanan gagal | Tidak mengaku berhasil; memberi tahu kegagalan |
| Pesan sama dikirim ulang oleh platform | Tidak membuat catatan/pengingat duplikat |
| Preferensi dikoreksi | Ingatan diperbarui dan jawaban berikutnya mengikuti koreksi |
| Informasi sensitif muncul | Izin diminta sebelum memori jangka panjang dibuat |
| “Jangan simpan ini” | Tidak membuat memori personal dari pesan yang ditandai; perilaku riwayat/log harus dijelaskan |
| Pengingat ambigu | Klarifikasi sebelum penjadwalan |
| Pengingat sekali/berulang | Dikirim sesuai waktu WIB yang dikonfirmasi ketika sistem tersedia |
| Tunda/selesai/batal | Status dan jadwal berubah dengan benar, tidak mengirim pengingat yang dibatalkan |
| Server offline melewati jadwal | Setelah pulih, satu rangkuman dengan waktu asli dan pilihan tindak lanjut |
| Sapaan tak dibalas | Maksimal satu susulan, kemudian menunggu |
| Pemilik meminta jeda | Sapaan berhenti sesuai kesepakatan; pesan masuk tetap dibalas |
| PC dimatikan | Layanan tablet yang sehat tetap menjalankan WhatsApp |
| Restart dan pemulihan cadangan | Data tersimpan kembali tersedia; pemulihan diuji |
| Semua penyedia model gagal | Percobaan ulang berhenti pada batas, tidak loop tanpa akhir |

Ukuran latensi, toleransi keterlambatan, lama uji operasi 24 jam, dan target waktu pemulihan belum ditetapkan. Uji wajib mencakup layar tablet mati, restart, internet putus, API gagal, dan pemulihan cadangan.

## 14. Keputusan terbuka sebelum implementasi
1. Kelayakan server tablet dan cara menjaga proses/restart otomatis.
2. Apakah Hermes Agent menjadi fondasi final setelah uji perangkat, serta batas tool yang diaktifkan.
3. Model Gemini gratis yang dipakai, perilaku ketika kuota habis, retry, dan kemungkinan fallback gratis yang tidak otomatis.
4. Penyimpanan utama, pembacaan memori, konsistensi data, serta akses catatan.
5. Retensi opsional untuk riwayat dan log, makna penghapusan manual, dan perlakuan cadangan terhadap data yang dihapus.
6. Frekuensi dan retensi cadangan lokal, enkripsi, penyedia cloud, serta pemantauan eksternal.
7. Nilai konfigurasi awal untuk jeda sapaan, batas maksimum adaptif, dan pengaturan jeda yang praktis.
8. Detail pengingat berulang/terlewat, status tugas, dan pengingat saat jeda.
9. Pemisahan chat biasa, catatan titipan, dan memori jika maksud tidak jelas.
10. Target performa dan langkah pengujian sebelum dipakai harian.

## 15. Tata kelola perubahan
- PRD boleh berubah ketika pemilik menemukan kebutuhan baru.
- Bahas dampak, tentukan apakah sekarang atau tahap berikutnya, lalu perbarui dokumen.
- Jangan mengubah opsi menjadi keputusan final tanpa kesepakatan.
- Catat perubahan penting dan alasan agar pengembangan lintas sesi tidak kembali ke aturan lama.
- Dokumen ini merangkum percakapan; tidak mengklaim repo grill-me telah diinstal atau dijalankan sebagai plugin.

## 16. Riwayat versi
- 0.1 / 16 Oktober 2026: draf pertama berdasarkan keputusan percakapan. Menetapkan versi pertama WhatsApp; companion PC dan keuangan lengkap ditunda.
- Pembaruan / 17 Oktober 2026: menetapkan Baileys dengan nomor khusus untuk pilot; API gratis tanpa peralihan otomatis ke layanan berbayar; riwayat tanpa penghapusan otomatis awal tetapi dengan opsi retensi dan penghapusan manual; pemisahan riwayat, memori, dan catatan; aturan sapaan tetap adaptif dan dapat dikonfigurasi; serta backup lokal/pemulihan dasar sejak awal dengan opsi cloud terenkripsi ditunda.

