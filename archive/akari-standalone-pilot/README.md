# Akari Pilot

Vertical slice saat ini hanya menangani satu alur: pesan teks baru dari nomor yang berada di allowlist diproses oleh Gemini lalu dibalas satu kali melalui WhatsApp.

## Batas tahap ini

- Belum ada memori personal, catatan, scheduler, pengingat, sapaan, atau backup otomatis.
- Baileys adalah integrasi tidak resmi dan `useMultiFileAuthState` hanya dipakai untuk pilot.
- Proses berhenti ketika PC mati, tidur, hibernasi, kehilangan jaringan, atau terminal ditutup.
- Deduplikasi bersifat _at-most-once_: event dengan ID sama tidak dibalas ulang setelah restart. Crash pada celah setelah pengiriman tetapi sebelum status SQLite diperbarui dapat membuat status lokal belum akurat.

## State runtime

Kode tidak menyimpan kredensial atau data pengguna di repositori. Tentukan `AKARI_HOME` di luar folder proyek dan buat struktur berikut:

```text
AKARI_HOME/
  config/akari.json
  secrets/.env
  auth/baileys/       # dibuat/diisi saat pairing
  data/akari.sqlite   # dibuat saat aplikasi mulai
  backups/
  logs/
```

Salin `config/default.json` menjadi `AKARI_HOME/config/akari.json`, lalu ganti placeholder model dan JID pemilik. JID pemilik menggunakan nomor internasional digit-saja, misalnya `62...@s.whatsapp.net`.

Salin `.env.example` menjadi `AKARI_HOME/secrets/.env`, lalu isi secara lokal:

```dotenv
GEMINI_API_KEY=...
WHATSAPP_PAIRING_NUMBER=...
```

`WHATSAPP_PAIRING_NUMBER` adalah nomor khusus Akari dalam format internasional, digit saja tanpa `+`. Jangan kirim nilai kedua variabel atau isi direktori `auth/baileys` ke chat maupun Git.

## Menjalankan

Setelah konfigurasi lokal selesai, buka terminal pada direktori proyek, set `AKARI_HOME`, lalu jalankan:

```powershell
$env:AKARI_HOME = "$env:LOCALAPPDATA\Akari"
npm.cmd start
```

Pada pairing pertama, terminal menampilkan kode sementara. Di WhatsApp nomor Akari buka **Perangkat tertaut → Tautkan perangkat → Tautkan dengan nomor telepon**, lalu masukkan kode tersebut. Proses berikutnya memakai sesi di `AKARI_HOME/auth/baileys` dan tidak seharusnya meminta pairing ulang selama sesi masih valid.

## Pemeriksaan lokal

```powershell
npm.cmd test
npm.cmd ls --depth=0
```
