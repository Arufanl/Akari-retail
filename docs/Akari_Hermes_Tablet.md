# Arsitektur & Operasional Akari Hermes di Tablet (Termux)

Tanggal: 5 November 2026 (Asia/Jakarta)  
Status: Terkonfigurasi aktif di Tablet Termux (`192.168.1.18`)

---

## 1. Topologi Sistem

- **Server Utama**: Tablet Android (Termux)
  - **Hermes Agent**: Commit `fd267bb3` (3 Nov 2026), berjalan di Termux (`~/.hermes`).
  - **9Router**: `v0.5.112` di port `20128`, melayani combo model `hermes-fallback`.
  - **Karakter (Persona)**: `~/.hermes/SOUL.md` (identik 100% SHA-256 dengan `hermes/SOUL.md` di workspace PC).
  - **WhatsApp Bridge**: Baileys 7.0.0-rc13 dengan patch deduplikasi persisten (SHA-256 ledger di `processed-inbound-ids.jsonl`).
- **PC Windows**: Hanya untuk pengembangan, monitoring, dan penyimpanan berkas backup berkala via SSH. Layanan Hermes & 9Router PC nonaktif.

---

## 2. Model & Routing (9Router)

- **Combo**: `hermes-fallback`
- **Urutan Strategi (Fallback)**:
  1. `ag/gemini-3.7-flash-low`
  2. `ag/claude-opus-4-6-thinking` (terbukti sukses menjawab uji tes saat #1 skip/gagal)
  3. `ag/claude-sonnet-4-6`
  4. 33 model alternatif lainnya (variasi openrouter/oc model free).
- **Endpoint**: `http://127.0.0.1:20128/v1`
- **API Key**: Disimpan di `.env` tablet pada variabel `HERMES_CUSTOM_127_0_0_1_20128_API_KEY`.

---

## 3. WhatsApp Integration & Patch Replay

- **Masalah Replay**: Pada versi Baileys bawaan, event reconnect menghasilkan `messages.upsert` dengan tipe `append` yang memicu bot memproses ulang pesan-pesan lama.
- **Solusi yang Diterapkan**:
  - Filter tipe `append` saat `mode === 'bot'`.
  - Ledger persisten inbound message (`scripts/whatsapp-bridge/inbound_message_gate.js`).
  - Unit test: 32 dari 32 tes lulus 100% (`node --test *.test.mjs`).
  - Berkas patch tersimpan di PC: `patches/hermes-whatsapp-replay-tablet/`.

---

## 4. Panduan Menjalankan & Pairing WhatsApp

Untuk menghubungkan nomor WhatsApp khusus Akari:

1. Buka aplikasi **Termux** di tablet (atau buka sesi SSH dari terminal PC).
2. Jalankan perintah pairing bawaan Hermes:
   ```bash
   hermes whatsapp
   ```
3. Terminal akan meminta konfirmasi konfigurasi (mode `bot`, nomor pemilik yang diizinkan) dan menampilkan **QR Code**.
4. Di smartphone dengan nomor WhatsApp Akari, buka **Linked Devices (Perangkat Tertaut)** -> **Tautkan Perangkat** -> Pindai QR Code di layar.
5. Setelah terhubung, sesi tersimpan permanen di `~/.hermes/whatsapp/session`.

---

## 5. Pengoperasian 24 Jam (Wake-lock & Termux:Boot)

Agar Akari dapat aktif 24 jam di tablet tanpa tertidur oleh manajemen baterai Android:

1. **Wake-lock Termux**:
   Di Termux, jalankan:
   ```bash
   termux-wake-lock
   ```
   *(Pastikan tablet selalu terhubung ke pengisi daya / charger).*

2. **Auto-start via Termux:Boot**:
   Pastikan aplikasi **Termux:Boot** terpasang.
   Buat berkas skrip di `~/.termux/boot/start-akari.sh`:
   ```bash
   mkdir -p ~/.termux/boot
   cat << 'EOF' > ~/.termux/boot/start-akari.sh
   #!/data/data/com.termux/files/usr/bin/sh
   termux-wake-lock
   # Jalankan 9router jika belum aktif
   pgrep -f "9router/cli.js" > /dev/null || nohup 9router --tray > ~/.9router/boot.log 2>&1 &
   # Jalankan gateway Hermes
   sleep 5
   hermes gateway run --quiet &
   EOF
   chmod +x ~/.termux/boot/start-akari.sh
   ```

---

## 6. Prosedur Pemulihan (Disaster Recovery)

Jika tablet rusak atau Termux terinstal ulang:
1. Hubungkan tablet baru ke Wi-Fi yang sama, pasang Termux & OpenSSH.
2. Salin backup konfigurasi dari PC (`C:\Users\Akari\AppData\Local\hermes\backups\tablet\...`) ke `~/.hermes/`.
3. Terapkan ulang patch bridge dari `patches/hermes-whatsapp-replay-tablet/hermes-whatsapp-replay-tablet.patch`.
