# Balasan WhatsApp adaptif Akari

Patch lokal pada adapter WhatsApp Hermes; pembaruan Hermes dapat menimpanya.

Konfigurasi: `platforms.whatsapp.extra.reply_quote_mode: adaptive`.

- Satu pesan DM yang belum dijawab: pesan balasan biasa.
- Beberapa pesan DM belum dijawab: kutip target balasan untuk membedakan konteks.
- Pesan lebih baru yang datang selama pengiriman tetap tercatat sebagai belum dijawab.
- Pengiriman gagal dan pesan interim tidak menghabiskan catatan pesan tertunda.
- Grup dan target yang tidak diketahui mempertahankan perilaku kutipan semula.
- Kebijakan ini berlaku pada balasan teks; jalur media tetap seperti sebelumnya.

Delapan pemeriksaan offline pada helper dan metode send adapter dengan transport tiruan lulus. Loader konfigurasi gateway dan impor adapter terpasang juga lulus. Tidak ada pesan WhatsApp atau permintaan model yang dikirim oleh pengujian.

Backup adapter dan konfigurasi: `C:\Users\Akari\AppData\Local\hermes\backups\pre-adaptive-reply-20261019T205633Z`.

Gateway berhasil dijalankan kembali secara manual, status WhatsApp `connected`. Tidak ada service atau auto-start baru. Tampilan pada WhatsApp nyata masih perlu diperiksa pengguna dengan satu pesan dan beberapa pesan berurutan.

File `adapter.py` adalah salinan versi lokal yang ditambal, bukan patch universal untuk semua versi. Periksa perubahan upstream sebelum menerapkannya lagi; jangan menimpa versi Hermes baru secara buta.
