# 🍱 WA Chatbot Penjualan Dimsum Mentai Oishi

Aplikasi chatbot otomatis berbasis WhatsApp untuk mengelola pemesanan produk "Dimsum Mentai Oishi". Sistem ini dibangun menggunakan arsitektur modern yang menggabungkan kemudahan backend Python dengan kestabilan gateway Node.js, memberikan pengalaman pemesanan yang cepat dan interaktif bagi pelanggan.

---

## 🚀 Fitur Utama

1. **🤖 WhatsApp Bot Otomatis (Real-Time):**
   - Integrasi WhatsApp asli menggunakan `whatsapp-web.js`.
   - Proses login mudah dengan QR Code via Web Gateway.
   - Menyapa pelanggan saat mengirim `"Halo"`.

2. **📋 Katalog Produk Dinamis:**
   - Terhubung langsung dengan database SQLite (`products`).
   - Bot selalu menampilkan harga dan daftar menu yang paling *up-to-date*.

3. **💬 Alur Pemesanan Interaktif (State-Based):**
   - Customer memilih menu ➔ Masukkan porsi ➔ Masukkan nama ➔ Masukkan alamat ➔ Konfirmasi.
   - Sistem akan membuat Nomor Order unik (contoh: `#ORD-X`).

4. **📊 Dashboard Admin Interaktif (`/admin`):**
   - Visualisasi pendapatan dan jumlah pesanan secara langsung.
   - Manajemen pesanan masuk (Ubah status ke *Diproses*, *Selesai*, atau *Batal*).
   - Menu pintasan untuk membuka layar Presentasi Interaktif dan Scanner QR Code.

5. **🎓 Mode Presentasi Kelas (`/presentation`):**
   - Terintegrasi dengan presentasi interaktif berbasis HTML/CSS/JS.
   - *Generator PPTX* bawaan untuk membuat file presentasi Microsoft PowerPoint secara instan.

---

## 🛠️ Arsitektur Teknologi

Sistem ini dipecah menjadi dua layanan (Microservices) yang saling berkomunikasi secara mulus via HTTP Webhook:

- **Backend Logic (Python/Flask):** Menangani logika database, dashboard web, state pesanan, dan UI presentasi.
- **WhatsApp Gateway (Node.js/Puppeteer):** Menangani koneksi ke server WhatsApp secara *headless*, menangkap pesan masuk, dan merespons pelanggan.
- **Database (SQLite):** Menyimpan histori pelanggan, produk, dan transaksi dengan aman.

---

## 🏃 Cara Menjalankan Project (Untuk Demo / Presentasi)

Sistem ini sudah didesain agar sangat mudah dijalankan tanpa perlu pengaturan *environment* yang rumit.

1. **Jalankan Aplikasi:**
   - Cukup klik dua kali (double-click) pada file **`start.bat`**.
   - Skrip ini akan secara otomatis menyalakan *Server Flask Python* dan *WhatsApp Gateway Node.js* bersamaan.

2. **Akses Dashboard Utama:**
   Buka browser dan kunjungi: **[http://localhost:5000/admin](http://localhost:5000/admin)**

3. **Hubungkan WhatsApp Bot:**
   - Dari dashboard admin, klik tombol **"Scan QR (Bot WA)"** (atau buka [http://localhost:3000/qr](http://localhost:3000/qr)).
   - Scan QR tersebut menggunakan aplikasi WhatsApp dari HP Anda (Linked Devices).
   - Jika terminal Node.js memunculkan `✅ Client is ready!`, maka bot siap melayani pelanggan.

---

## 🎬 Simulasi Demo Pemesanan (Tanpa WhatsApp)

Jika Anda ingin mendemonstrasikan logika bot tanpa harus menghubungkan perangkat WhatsApp, gunakan **Web Chatbot Simulator**:

1. Buka browser ke: **[http://127.0.0.1:5000/chat](http://127.0.0.1:5000/chat)**
2. Ketik `Halo` ➔ Bot menyapa dan memberikan opsi.
3. Ketik `2` (Pesan) ➔ Bot menampilkan varian dimsum.
4. Selesaikan simulasi dengan mengetik jumlah porsi, nama lengkap, dan alamat.
5. Konfirmasi dengan mengetik `YA` untuk melihat order masuk di Dashboard Admin!

---
*Dibuat untuk Project Akhir/Presentasi Sistem Informasi.*
