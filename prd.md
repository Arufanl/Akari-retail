# Product Requirements Document (PRD)
## Akari Retail: Mobile Scanner Client & Home Tablet Server

**Status:** Approved by User  
**Versi:** 1.0.0  
**Tanggal:** 15 November 2026  
**Penulis:** Antigravity Team & Akari  

---

## 1. Ringkasan Eksekutif & Latar Belakang

Sistem **Akari Retail** dirancang untuk mempermudah operasional toko dan warung ritel dalam mengelola master data produk (PLU toko dan barcode pabrik EAN-13) serta membuat kartu label rak (*shelf label*) secara otomatis dan instan.

Sistem ini menggunakan arsitektur **Client-Server terdistribusi**:
1. **Server (Tablet Android di Rumah):** Berfungsi sebagai backend terpusat di jaringan rumah yang menjalankan REST API, mengelola database lokal SQLite (50.600+ item produk warung), serta memproses render grafis kartu label tajam siap cetak tanpa token AI (**0-Token AI**).
2. **Client (Smartphone Pengguna):** Aplikasi Android native berbasis Flutter yang memanfaatkan kamera HP berkecepatan 60 FPS untuk scanning barcode secara cepat, melakukan pencarian cerdas ke server, menginput nomor PLU toko, dan menampilkan pratinjau kartu label.

---

## 2. Arsitektur Sistem & Topologi Jaringan

```
┌──────────────────────────────────────────────┐
│            SMARTPHONE (HP KLIEN)             │
│  • Aplikasi Native Android (Flutter)         │
│  • Tema: Hatsune Miku Clean Edition (Teal)   │
│  • Google ML Kit / MobileScanner (60 FPS)    │
│  • UI Form Cerdas & Preview Label            │
└──────────────────────┬───────────────────────┘
                       │
                       │ HTTP/REST (JSON & PNG)
                       │ Jalur 1: WiFi Lokal Rumah (192.168.1.x:5000)
                       │ Jalur 2: Tailscale Mesh VPN (Remote/Luar Rumah)
                       │
┌──────────────────────┴───────────────────────┐
│            TABLET ANDROID (SERVER)           │
│  • Termux Environment                        │
│  • REST API: Python FastAPI + Uvicorn        │
│  • Database: SQLite (retail_products.db)     │
│    50.604 item terindeks (plu, barcode, name)│
│  • Generator: Pillow + FreeType Vector       │
│  • CDN Cache: KlikIndomaret Product Images   │
└──────────────────────────────────────────────┘
```

### 2.1. Spesifikasi Jaringan (Hybrid Connectivity)
* **Koneksi Utama (WiFi Lokal):** Digunakan saat HP dan Tablet berada di jaringan rumah yang sama. Latensi super rendah (< 50 ms).
* **Koneksi Cadangan (Tailscale VPN):** Digunakan saat pengguna berada di luar rumah/toko tanpa perlu port forwarding atau IP publik terbuka.
* **Autentikasi:** API Key statis sederhana yang dikonfigurasi sekali lewat pemindaian kode QR Server pada aplikasi HP.

---

## 3. Matriks Skenario & Kebutuhan Fungsional

Sistem dirancang untuk menangani seluruh kemungkinan input data secara fleksibel tanpa alur buntu (*no dead-end*).

### 3.1. Skenario 1: Scan Barcode Kemasan Pabrik (EAN-13 / UPC)
* **Kasus 1A: Barcode terdaftar di DB 50.600, tetapi BELUM punya PLU toko**
  * *Tindakan Server:* Mengembalikan nama barang, nama pendek varian, dan ukuran/gramatur.
  * *Tindakan HP:* Menampilkan nama barang secara otomatis; kursor langsung fokus ke kolom input PLU toko.
  * *Alur Selesai:* Pengguna mengetik 8 digit PLU $\rightarrow$ Klik **"Simpan & Buat Label"** $\rightarrow$ Server mengaitkan PLU ke barcode, mengunduh foto CDN, merender kartu label, dan mengirimkan gambar PNG kembali ke HP.
* **Kasus 1B: Barcode SUDAH terdaftar dan SUDAH memiliki PLU toko**
  * *Tindakan HP:* Menampilkan status *"Barang Sudah Terdaftar"*, rincian nomor PLU, nama barang, dan langsung memuat pratinjau kartu label.
  * *Opsi:* Tombol *"Simpan Gambar"* atau *"Ubah PLU/Data"*.
* **Kasus 1C: Barcode BENAR-BENAR BARU (Belum ada di database)**
  * *Tindakan HP:* Memberi notifikasi *"Barang Baru Belum Terdaftar"*.
  * *Formulir:* Kolom barcode otomatis terisi dari hasil scan; kolom Nama Barang, Ukuran, dan PLU siap diisi manual $\rightarrow$ Simpan.

### 3.2. Skenario 2: Input Manual / Scan Nomor PLU Saja
* **Kasus 2A: PLU SUDAH pernah didaftarkan**
  * *Tindakan HP:* Langsung menampilkan data barang lengkap beserta barcode EAN-13 terkait dan gambar kartu label siap unduh.
* **Kasus 2B: PLU BARU (Belum terdaftar)**
  * *Tindakan HP:* Menampilkan notifikasi *"PLU Baru Belum Terhubung Barcode"*.
  * *Pilihan Cepat:*
    1. Tombol *"📷 Scan Barcode Kemasan"* (kamera langsung menyala).
    2. Tombol *"🔍 Cari di DB 50.600"* (buka pencarian nama barang untuk memilih barcode).
    3. Input barcode manual.

### 3.3. Skenario 3: Pencarian Cerdas Produk (Smart Search)
* Pengguna mengetik kata kunci nama barang (misal: `"indomie goreng"` atau `"le minerale"`).
* Server melakukan pencarian cepat menggunakan query `LIKE` pada index database SQLite 50.600.
* HP menampilkan daftar hingga 20 produk yang cocok (Nama + Gramatur + Barcode EAN-13).
* Pengguna memilih salah satu produk $\rightarrow$ Form otomatis terisi $\rightarrow$ Pengguna tinggal memasukkan PLU toko.

### 3.4. Skenario 4: Pratinjau & Penyimpanan Kartu Label
* Server mengembalikan kartu label beresolusi tinggi (595 $\times$ 848 px) dengan desain resmi:
  * Warna latar: Warm Beige (`#F6ECE0`) dengan sudut membulat dan garis tepi gelap.
  * *Pill* PLU periwinkle di pojok kanan atas.
  * Foto produk resmi dari CDN KlikIndomaret di tengah.
  * Nama produk kontras tinggi dan *pill* gramatur.
  * Barcode EAN-13 tajam (vektor Pillow) dengan satu baris digit proporsional.
* Pengguna dapat meninjau kartu langsung di HP dan menekan tombol **"Simpan Gambar"** untuk menyimpan file PNG ke galeri penyimpanan HP.

### 3.5. Skenario 5: Pengaturan Awal Cepat via QR Code
* Endpoint server di tablet menyediakan halaman info web lokal yang menampilkan kode QR berisi konfigurasi:
  ```json
  {
    "server_url": "http://192.168.1.2:5000",
    "tailscale_url": "http://100.x.y.z:5000",
    "api_key": "akari_retail_secret_key"
  }
  ```
* Saat pertama kali membuka aplikasi Flutter di HP, pengguna cukup menekan tombol *"Scan Setup QR"* $\rightarrow$ Koneksi langsung siap tanpa mengetik IP secara manual.

---

## 4. Spesifikasi Database & REST API (Tablet Server)

### 4.1. Skema Database SQLite (`retail_products.db`)
```sql
CREATE TABLE IF NOT EXISTS products (
    plu TEXT PRIMARY KEY,
    barcode TEXT NOT NULL,
    name TEXT NOT NULL,
    short_name TEXT,
    size TEXT,
    image_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_barcode ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_name ON products(name);
```

### 4.2. Kontrak REST API (FastAPI)

Semua permintaan API (kecuali `/api/config/qr`) menyertakan header autentikasi:  
`X-API-Key: <secret_key>`

#### 1. `GET /api/product/lookup`
* **Query Parameters:** `code` (string, nomor PLU atau Barcode).
* **Response (200 OK):**
  ```json
  {
    "success": true,
    "found": true,
    "match_type": "plu",
    "product": {
      "plu": "20069208",
      "barcode": "8996001600269",
      "name": "LE MINERALE AIR MINERAL 600ML",
      "short_name": "LE MINERALE AIR MINERAL",
      "size": "600 ML",
      "image_url": "https://cdn-klik.klikindomaret.com/klik-catalog/product/20069208_meta.jpg",
      "label_url": "/api/product/label/20069208"
    }
  }
  ```

#### 2. `GET /api/product/search`
* **Query Parameters:** `q` (kata kunci pencarian), `limit` (default: 20).
* **Response (200 OK):**
  ```json
  {
    "success": true,
    "total": 5,
    "results": [
      {
        "plu": "20069208",
        "barcode": "8996001600269",
        "name": "LE MINERALE AIR MINERAL 600ML",
        "short_name": "LE MINERALE AIR MINERAL",
        "size": "600 ML"
      }
    ]
  }
  ```

#### 3. `POST /api/product/save`
* **Request Body (JSON):**
  ```json
  {
    "plu": "20069208",
    "barcode": "8996001600269",
    "name": "LE MINERALE AIR MINERAL 600ML",
    "short_name": "LE MINERALE",
    "size": "600 ML"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Produk berhasil disimpan!",
    "product": {
      "plu": "20069208",
      "barcode": "8996001600269",
      "name": "LE MINERALE AIR MINERAL 600ML",
      "size": "600 ML",
      "label_url": "/api/product/label/20069208"
    }
  }
  ```

#### 4. `GET /api/product/label/{code}`
* **Response:** File biner `image/png` kartu label rak.

#### 5. `GET /api/config/qr`
* **Response:** Gambar QR Code konfigurasi untuk dipindai oleh aplikasi HP.

---

## 5. Spesifikasi Aplikasi Klien (Flutter Android)

### 5.1. Struktur Modul Aplikasi
* `lib/main.dart`: Titik masuk aplikasi, inisialisasi state, dan routing.
* `lib/services/api_service.dart`: Klien HTTP ke backend FastAPI dengan header API Key dan error handling.
* `lib/services/storage_service.dart`: Penyimpanan preferensi lokal (`server_url`, `api_key`) via `shared_preferences`.
* `lib/screens/scanner_screen.dart`: Viewfinder kamera utama dengan `mobile_scanner` dan overlay bidik.
* `lib/screens/product_form_screen.dart`: Formulir cerdas dengan auto-fill nama barang dan input PLU.
* `lib/screens/label_preview_screen.dart`: Penampil kartu label visual dan tombol simpan ke galeri (`image_gallery_saver`).
* `lib/screens/search_screen.dart`: Pencarian cepat nama produk di database 50.600.
* `lib/screens/settings_screen.dart`: Pengaturan IP server, Tailscale, dan QR scanner setup.

### 5.2. Desain Tema & Estetika (Hatsune Miku Clean Edition)
* **Karakter Visual:** Bersih, segar, dan nyaman di mata (bukan tema gelap *cyberpunk* yang berat).
* **Palet Warna Utama:**
  * **Miku Teal / Aqua (`#39C5BB` / `#2AA89F`):** Warna utama tombol aksi, aksen garis bidik kamera, dan status aktif.
  * **Soft Mint Background (`#EDF7F6` / `#F7FCFB`):** Warna latar belakang layar yang lembut dan adem untuk mata.
  * **Crisp Pure White (`#FFFFFF`):** Warna kartu formulir produk dan modal dialog dengan bayangan lembut (*soft elevation*).
  * **Charcoal Slate (`#2B333E` / `#4A5568`):** Tipografi teks utama yang jelas dan mudah dibaca di bawah pencahayaan toko.
  * **Signature Pink Badge (`#FF5FA2`):** Aksen penanda status penting / wajib diisi.
  * **Signature Badge `01`:** Ikon identitas Miku di pojok status bar aplikasi.

---

## 6. Persyaratan Non-Fungsional (NFR)

1. **Efisiensi Sumber Daya Server (Tablet Android):**
   * Server Termux berjalan dengan konsumsi RAM di bawah 80 MB.
   * CPU *idle* 0% saat tidak ada request scanning.
2. **Kecepatan Respon:**
   * Lookup barcode via WiFi lokal selesai dalam waktu kurang dari 150 milidetik.
   * Render kartu label PNG selesai dalam waktu kurang dari 800 milidetik.
3. **Tanpa Biaya Token AI (0-Token AI):**
   * Semua operasi pencarian, penautan data, dan pembuatan label 100% lokal dan deterministik tanpa melibatkan API LLM berbayar.
4. **Ketahanan Jaringan:**
   * Aplikasi HP memberikan pesan ramah jika tablet server tidak aktif atau koneksi WiFi terputus.

---

## 7. Rencana Tahapan Pelaksanaan

| Fase | Komponen | Target Output |
| :--- | :--- | :--- |
| **Fase 1** | **Server API (Tablet)** | File script `akari_retail_server.py` berbasis FastAPI di Termux, meng-expose endpoint lookup, search, save, label streaming, dan QR setup. |
| **Fase 2** | **Aplikasi Client (HP)** | Proyek Flutter lengkap bertema Hatsune Miku Clean di direktori `mobile_app/`, siap di-build menjadi APK untuk HP Android. |
| **Fase 3** | **Verifikasi & Integrasi** | Uji coba pemindaian barcode langsung dari HP $\rightarrow$ Server tablet menyimpan data $\rightarrow$ Preview kartu label berhasil tampil di HP. |
