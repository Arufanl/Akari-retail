# Status Arsip Pilot Mandiri Akari

Diarsipkan pada 17 Oktober 2026.

Pilot Akari tanpa Hermes dihentikan sementara agar pengembangan dapat beralih ke jalur Hermes tanpa mencampurkan kedua implementasi.

Status terakhir:

- skeleton JavaScript ESM dan dependensi terkunci sudah dibuat;
- 7 pengujian lokal lulus, termasuk deduplikasi SQLite dan persistensi auth state Baileys;
- belum pernah dihubungkan ke Gemini API atau akun WhatsApp nyata;
- tidak ada `AKARI_HOME`, API key, nomor pribadi, database runtime, atau sesi WhatsApp yang dibuat atau dimasukkan ke arsip;
- `node_modules` Windows dipertahankan sebagai bagian dari hasil kerja, tetapi dapat dibuat ulang dari `package-lock.json`.

Dokumen kebutuhan produk aktif tetap berada di `docs/Akari_PRD_v0.1.md` di root workspace.
