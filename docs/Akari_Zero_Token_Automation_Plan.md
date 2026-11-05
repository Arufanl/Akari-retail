# Rencana Fitur Otomatisasi Tanpa AI (Zero-Token / Offline-Capable) — Akari

**Tanggal Pencatatan:** 5 November 2026  
**Status:** Direncanakan (Belum Diimplementasikan)  
**Tujuan:** Memungkinkan fungsi-fungsi utama asisten pribadi Akari tetap berjalan instan (< 0,2 detik), memakai **0 token LLM**, dan tetap berfungsi 100% meskipun kuota API model habis atau koneksi ke provider AI sedang gangguan.

---

## 1. Konsep Arsitektur (Hybrid: Tanpa-AI + AI)

Pesan masuk dari WhatsApp pemilik diproses melalui dua jalur di Hermes Gateway tablet:

1. **Jalur Tanpa AI (0 Token — via Plugin Command & Inbound Hook)**:
   - Menangani pengiriman tautan cepat, perintah garis miring (`/ide`, `/tugas`, `/ingat`, `/jajan`, `/tidur`, `/status`), serta tampilan daftar/rekap.
   - Diproses langsung oleh Python + SQLite di tablet dan membalas dengan kalimat bertema Akari (variasi template hangat/manis).
2. **Jalur AI (Percakapan Natural)**:
   - Jika pesan merupakan obrolan biasa atau instruksi bahasa bebas yang kompleks, pesan diteruskan ke model AI (`hermes-fallback`) seperti biasa.

---

## 2. Daftar Fitur Tanpa AI yang Direncanakan

### A. Auto-Save Link / URL Instan (Tanpa Perintah)
- **Pemicu**: Pesan masuk yang diawali dengan `http://` atau `https://` (baik hanya URL maupun `URL + keterangan singkat`).
- **Tindakan**:
  - Otomatis disimpan ke tabel `notes` (`kind = 'link'`, `status = 'open'`) di `akari_notes.db`.
  - Otomatis memperbarui berkas `Akari_Notes.md` untuk sinkronisasi Obsidian.
  - Membalas langsung tanpa memanggil AI (contoh: *"🔗 Tautan udah kusimpan di catatan (#14), Bos~ ✨"*).
- **Pengecualian**: Jika URL berada di tengah kalimat percakapan panjang, tetap diteruskan ke AI agar konteks diskusi tidak terputus.

### B. Tangkap Cepat Catatan, Ide, & Tugas (`/ide`, `/catat`, `/tugas`, `/list`, `/selesai`)
- `/ide <isi>` → Simpan ke kategori `idea` (0 token).
- `/catat <isi>` → Simpan ke kategori `note` (0 token).
- `/tugas <isi>` → Simpan ke kategori `task` dengan status `open` (0 token).
- `/list [ide|tugas|link|catat]` → Tampilkan daftar item aktif langsung dari SQLite (0 token).
- `/selesai <id>` atau `/hapus <id>` → Tandai tugas selesai (`done`) atau hapus item berdasarkan nomor ID (0 token).

### C. Pengingat Cepat Tanpa AI (`/ingat`, `/jadwal`, `/batal`)
- `/ingat <waktu> <pesan>` (contoh: `/ingat 15m angkat jemuran` atau `/ingat 20:00 makan malam`):
  - Membuat jadwal di *Cron Scheduler* dengan mode **`no_agent: true`**.
  - Saat waktu pengingat tiba, sistem mengirim pesan pengingat langsung ke WhatsApp **tanpa memanggil LLM** (0 token saat membuat & 0 token saat alarm berbunyi).
- `/jadwal` → Menampilkan daftar pengingat aktif beserta waktu berbunyi berikutnya (0 token).
- `/batal <id>` → Membatalkan pengingat terjadwal (0 token).

### D. Pencatatan Keuangan Deterministik (`/jajan`, `/keluar`, `/masuk`, `/rekap`)
- Sesuai spesifikasi PRD Bagian 11.A (periode gajian tanggal **28 – 27 bulan berikutnya**).
- Input cepat 0 token:
  - `/keluar <nominal> <kategori> <keterangan>` (contoh: `/keluar 15rb jajan kopi` atau pintasan `/jajan 15rb kopi`, `/bensin 25k`).
  - `/masuk <nominal> <keterangan>`.
- `/rekap` → Menghitung total pengeluaran hari ini, total per kategori, dan sisa anggaran periode 28–27 secara deterministik dengan Python + SQLite (100% akurat tanpa risiko halusinasi angka AI, 0 token).

### E. Kontrol Sapaan & Diagnostik Tablet (`/tidur`, `/bangun`, `/status`)
- `/tidur [jam]` → Menjeda sapaan spontan selama 8 jam (atau sesuai angka jam yang diberikan) di tabel `greeting_state` dan membalas ucapan selamat istirahat khas Akari (0 token).
- `/bangun` → Mengaktifkan kembali sapaan spontan lebih awal (0 token).
- `/status` → Menampilkan kondisi langsung server tablet: sisa RAM, ruang penyimpanan, *uptime*, status masa jeda sapaan, serta jumlah tugas & pengingat aktif (0 token).
