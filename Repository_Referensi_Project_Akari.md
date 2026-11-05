# Referensi Repository — Project Akari

**Tanggal rangkuman:** 20 Oktober 2026  
**Status:** Catatan eksplorasi; belum ada instalasi, integrasi, atau perubahan proyek.

## 1. Tujuan Project Akari

Akari adalah rencana asisten AI pribadi dengan percakapan melalui WhatsApp dan pendamping desktop PC, memori yang digunakan bersama, pengingat dan pesan proaktif, pencatatan ide/tautan/pengeluaran, serta penggunaan model AI dengan opsi gratis atau biaya rendah. Tablet diharapkan menjadi host utama agar fungsi penting tidak bergantung pada PC yang selalu menyala. Kompatibilitas perangkat, background operation, dan integrasi WhatsApp perlu diuji sebelum memilih fondasi.

## 2. Repository inti AI agent

### 2.1 OpenClaw
- **Website:** https://openclaw.ai/
- **GitHub:** https://github.com/openclaw/openclaw
- **Fungsi:** AI agent self-hosted dengan gateway untuk saluran pesan, tools, memori, penjadwalan, dan otomasi.
- **Relevansi:** Kandidat fondasi komunikasi WhatsApp, reminder, tugas proaktif, dan tools untuk Akari.
- **Catatan:** Menjalankan gateway 24/7 langsung di tablet HarmonyOS/Termux belum terbukti cocok; perlu menilai keamanan akses dan konsumsi daya. Biaya model AI terpisah.

### 2.2 OpenHuman
- **GitHub:** https://github.com/tinyhumansai/openhuman
- **Fungsi:** Framework/runtime AI agent serbaguna dengan tools, memory, dan otomatisasi.
- **Relevansi:** Alternatif fondasi Akari, menarik untuk membandingkan efisiensi runtime dan integrasi.
- **Catatan:** Jangan menyamakan fitur yang didokumentasikan dengan kompatibilitas siap pakai di perangkat tablet atau WhatsApp.

### 2.3 Oh My Hermes
- **GitHub:** https://github.com/rlaope/oh-my-hermes
- **Fungsi:** Lapisan orkestrasi untuk Hermes Agent, mencakup routing model, skill, memori, pembagian tugas, dan pemeriksaan hasil.
- **Relevansi:** Kandidat pelengkap jika Akari tetap memakai Hermes sebagai agent utama dan memanfaatkan provider gratis/9Router.
- **Catatan:** Bukan pengganti Hermes atau sumber model AI gratis; biaya dan kuota ditentukan provider. Periksa apakah kompleksitasnya sepadan.

## 3. Antarmuka dan komunikasi

### 3.1 Vercel Chatbot
- **GitHub:** https://github.com/vercel/chatbot
- **Fungsi:** Template aplikasi chat berbasis Next.js, React, TypeScript, Vercel AI SDK, login, dan penyimpanan percakapan.
- **Relevansi:** Referensi UI chat berbasis web dan arsitektur multi-provider; bisa dijadikan lapisan antarmuka Akari.
- **Catatan:** Bukan engine memori personal, bot WhatsApp, atau sistem pesan proaktif yang lengkap. Infrastruktur database, hosting, dan API model perlu disiapkan.

## 4. Infrastruktur AI coding dan pengetahuan (pendukung pengembangan Akari)

### 4.1 Codebase Memory MCP
- **GitHub:** https://github.com/DeusData/codebase-memory-mcp
- **Fungsi:** Mengindeks source code dan hubungan fungsi/dependensi agar agent coding dapat mencari bagian kode relevan.
- **Relevansi:** Membantu Codex/OpenCode memahami backend Akari ketika ukurannya bertambah.
- **Catatan:** Berbeda dari memori percakapan Akari; indeks harus diperbarui dan kode sumber tetap perlu diverifikasi.

### 4.2 Graphify
- **GitHub:** https://github.com/Graphify-Labs/graphify
- **Fungsi:** Menyusun knowledge graph dari source code dan dokumentasi proyek.
- **Relevansi:** Memetakan relasi antara rancangan Akari, catatan teknis, dan implementasi ketika proyek berkembang.
- **Catatan:** Merupakan alat bantu pengembang, bukan penyimpanan memori personal Akari.

## 5. Hubungan dengan sistem yang sudah dipertimbangkan

- **Hermes Agent:** kandidat AI agent utama; Oh My Hermes adalah tambahan opsional.
- **9Router:** routing/fallback provider/model; tidak menggantikan agent atau sistem memori.
- **Obsidian:** tempat keputusan, pelajaran, dan dokumentasi proyek; tidak sama dengan memori percakapan agent maupun indeks source code.
- **OpenClaw dan OpenHuman:** alternatif yang perlu dibandingkan dengan Hermes, bukan langsung digabung semuanya.

## 6. Hal yang harus dibandingkan sebelum memilih

1. **Operasional 24/7:** Apakah gateway dapat hidup stabil di tablet HarmonyOS/Termux, restart otomatis, dan pulih sesudah koneksi putus?
2. **WhatsApp:** Metode koneksi, keamanan sesi, risiko pembatasan akun, dan apakah ada kebutuhan layanan tambahan.
3. **Memory lintas perangkat:** Format data, backup, pencarian, dan privasi.
4. **Pesan proaktif:** Scheduler, notifikasi ketika offline, dan batas penggunaan model gratis.
5. **Kompatibilitas provider:** Hermes/9Router/Gemini/OpenRouter, tool calling, streaming, fallback.
6. **Beban perangkat:** RAM, CPU, daya, koneksi, serta perawatan.
7. **Keamanan:** Izin shell/browser/file, allowlist pengirim, pengelolaan kredensial dan backup.

## 7. Pemetaan prioritas (bukan keputusan implementasi)

| Prioritas evaluasi | Proyek | Tujuan pengujian |
|---|---|---|
| Tinggi | OpenClaw vs Hermes + Oh My Hermes | WhatsApp, otomasi, dan kesesuaian 24/7 |
| Menengah | OpenHuman | Alternatif runtime dan efisiensi |
| Menengah | Vercel Chatbot | UI chat web, tidak mendesak untuk backend |
| Nanti ketika codebase membesar | Codebase Memory MCP / Graphify | Navigasi proyek dan efisiensi coding |

## 8. Prinsip pengembangan

- Saat ini **eksplorasi saja**, belum ada instalasi atau keputusan migrasi.
- Utamakan opsi gratis tetapi jangan mengasumsikan API dan layanan pihak ketiga selalu gratis.
- Jangan mencampurkan seluruh platform agent menjadi satu tanpa alasan fungsional.
- Konfirmasi kebutuhan yang berpengaruh besar sebelum perubahan implementasi.

---
**Daftar tautan Akari:**
1. https://openclaw.ai/ — https://github.com/openclaw/openclaw
2. https://github.com/tinyhumansai/openhuman
3. https://github.com/rlaope/oh-my-hermes
4. https://github.com/vercel/chatbot
5. https://github.com/DeusData/codebase-memory-mcp
6. https://github.com/Graphify-Labs/graphify
