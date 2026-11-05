# Desain Memori Persisten & Profil Bos (Tahap 2.1)

Tanggal: 5 November 2026  
Status: Aktif di Tablet Android Termux

## 1. Arsitektur Memori Hermes

Hermes Agent menggunakan sistem kurasi memori dua arah yang disimpan dalam format Markdown persisten di folder `~/.hermes/memories/`:

1. **`USER.md` (Profil Bos / `target: "user"`)**:
   - Berisi fakta tentang Bos: nama/panggilan, preferensi, sifat, kebiasaan, makanan/hal favorit, batasan pribadi.
   - Karakter limit: 1.375 karakter (padat dan relevan).
   - Dimuat otomatis ke dalam system prompt saat percakapan dimulai.

2. **`MEMORY.md` (Catatan Fakta / `target: "memory"`)**:
   - Berisi konteks penting lintas sesi: keputusan proyek, fakta yang disepakati, hal-hal yang dititipkan Bos untuk diingat.
   - Karakter limit: 2.200 karakter.
   - Dimuat otomatis ke dalam system prompt sebagai snapshot statis (menjaga cache prefix token model).

## 2. Penggunaan Tool `memory`

Akari diberikan tepat satu tool bawaan: `memory`.
- **Action**:
  - `add`: Menyimpan fakta baru.
  - `patch`: Memperbarui atau merevisi fakta lama.
  - `remove`: Menghapus fakta yang diminta Bos untuk dilupakan.
  - `view`: Memeriksa isi memori saat ini.
- **Target**:
  - `user`: Hal-hal mengenai diri Bos.
  - `memory`: Konteks obrolan atau fakta umum lainnya.

## 3. Batasan Privasi & Keamanan

1. Dilarang keras menyimpan password, PIN, OTP, nomor rekening, token autentikasi, atau rahasia sensitif lainnya.
2. Tool lain (terminal, eksekusi kode, browser, file system) **tetap dinonaktifkan** demi keamanan sistem dan penghematan token kuota.
3. Scheduler waktu/alarm/pengingat jam otomatis belum aktif (akan diintegrasikan pada Tahap 2.3).
