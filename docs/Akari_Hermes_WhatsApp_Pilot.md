# Pilot WhatsApp Akari melalui Hermes

Tanggal pengujian: 17 Oktober 2026  
Status akhir: pairing dan alur dasar berfungsi; mitigasi lokal replay sudah diterapkan dan lolos uji tiruan, sedangkan uji WhatsApp nyata setelah perbaikan belum dilakukan

## Konfigurasi aktif

- Integrasi: bridge Baileys bawaan Hermes, mode nomor bot terpisah.
- Akses DM: `allowlist`, berisi tepat satu nomor pemilik.
- Akses semua pengguna: nonaktif.
- Grup: `disabled`.
- Pesan yang dikirim dari akun Akari sendiri: tidak diteruskan ke agent.
- Pesan broadcast, status, dan newsletter: disaring oleh adapter.
- Perilaku DM tidak sah: `ignore`.
- Toolset WhatsApp: kosong; persona dan batas kemampuan di `hermes/SOUL.md` dipertahankan.
- Gateway: manual/foreground; tidak ada service atau auto-start.
- Sapaan spontan, scheduler, catatan, dan memori personal: belum aktif.

Nomor telepon berada hanya di `%LOCALAPPDATA%\hermes\.env`. Kredensial Baileys berada hanya di direktori sesi lokal Hermes. Keduanya tidak dicatat di repositori atau dokumen ini.

## Hasil uji minimum

1. Pairing akun nomor khusus Akari selesai dan sesi tersimpan lokal.
2. Validasi lokal memastikan akun tertaut berbeda dari nomor pemilik dan allowlist bukan wildcard.
3. Satu pesan teks dari nomor pemilik menghasilkan tepat satu balasan Akari.
4. Pesan keluar Akari tidak memicu echo-loop langsung pada uji awal.
5. Gateway dihentikan lalu dijalankan kembali tanpa QR; Hermes memakai sesi yang sudah ada.
6. Satu pesan setelah restart gateway kembali mendapat balasan Akari.
7. Pesan dari nomor yang tidak diizinkan ditolak dengan alasan `allowlist_mismatch`.
8. Pesan grup ditolak dengan alasan `group_policy_rejected`.

## Temuan replay pesan

Setelah uji restart dan pembatasan akses, teks pesan pertama diterima kembali oleh gateway sebagai event inbound baru dan menghasilkan balasan kedua. Log menunjukkan pemrosesan awal pada 21:36 dan event dengan teks sama pada 21:56. Ini bukan echo langsung dari pesan keluar; bridge menyerahkan ulang pesan masuk lama sehingga model dipanggil kembali.

Source bridge Hermes v0.22.2 menerima event Baileys `notify` maupun `append`, tetapi tidak terlihat memiliki deduplikasi persisten untuk ID pesan teks masuk. Event `append` dibutuhkan oleh mode self-chat, namun pada mode bot dapat membuat pesan lama yang disinkronkan ulang tampak seperti pesan baru. Ini adalah diagnosis berdasarkan source lokal dan urutan log; tipe event replay tidak tercatat karena debug bridge tidak diaktifkan.

## Mitigasi lokal v0.22.2

Perbaikan lokal diterapkan pada bridge Hermes tanpa mengubah sesi maupun riwayat:

- Mode bot menolak event `append` karena event tersebut mewakili history/pesan lama; mode self-chat tetap kompatibel dengan `append`.
- Event inbound yang lolos pembatasan dicatat dalam ledger terbatas berkapasitas 4.096 ID.
- Ledger menyimpan fingerprint SHA-256, bukan nomor, JID, isi pesan, atau ID pesan mentah.
- Ledger berada di direktori sesi sehingga deduplikasi tetap bekerja setelah restart bridge.
- Duplikat dihentikan sebelum diteruskan ke antrean gateway/model.

Uji lokal Node dengan event tiruan mencakup pesan baru, history lama, pesan sendiri, duplikat dalam proses yang sama, dan duplikat setelah simulasi restart. Seluruh 28 tes bridge lulus. Pengujian ini tidak menyalakan gateway dan tidak memanggil Gemini.

Perubahan menyentuh instalasi Hermes dan dapat tertimpa pembaruan. Patch yang dapat diterapkan ulang serta petunjuknya disimpan di `patches/hermes-whatsapp-replay-v0.22.2/`. Setelah pembaruan, periksa dahulu apakah upstream sudah menyediakan mitigasi sejenis; jangan menerapkan patch secara buta.

## Belum teruji

- Satu pesan WhatsApp nyata setelah perbaikan menghasilkan tepat satu balasan.
- Reconnect/restart nyata tidak memutar ulang pesan lama dan sesi tetap dapat dipakai tanpa pairing ulang.
- Filter pesan sendiri, nomor lain, grup, dan status tetap berlaku pada koneksi WhatsApp nyata setelah patch.
- Restart penuh Windows, tidur/hibernasi, pemulihan jaringan lama, dan kestabilan jangka panjang.
- Perubahan protokol WhatsApp/Baileys serta risiko pembatasan akun.
- Operasi 24 jam. Saat PC mati, tidur, atau gateway berhenti, Akari tidak membalas.
- Sapaan spontan, scheduler, pengingat, memori personal, dan pemulihan sesi dari backup.

Gemini tetap memakai kuota gratis, sehingga balasan dapat melambat atau gagal ketika terkena rate-limit. Tidak ada billing atau fallback berbayar yang diaktifkan.

## Menjalankan secara manual

```powershell
hermes gateway
```

Tekan `Ctrl+C` untuk menghentikan gateway. Jangan menjalankan `hermes gateway install` sebelum keputusan auto-start dibuat.
