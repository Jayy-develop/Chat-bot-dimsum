# 🚀 Panduan Setup & Menjalankan Project Dimsum Mentai Oishi

Halo! Ini adalah panduan langkah demi langkah untuk menjalankan project chatbot **Dimsum Mentai Oishi** di komputermu.

---

## 🛠️ Tahap 1: Persiapan Aplikasi (Pre-requisites)
Sebelum menjalankan program, pastikan kamu sudah menginstal aplikasi berikut di komputermu. Jika belum punya, klik link download di bawah ini:

1. **Python (versi 3.8 - 3.12)**
   - 🔗 Download: [python.org/downloads](https://www.python.org/downloads/)
   - ⚠️ **PENTING SAAT INSTALL:** Pastikan kamu **MENCENTANG KOTAK** bertuliskan `"Add python.exe to PATH"` di bagian paling bawah installer sebelum menekan tombol "Install Now".

2. **Node.js (Versi LTS terbaru)**
   - 🔗 Download: [nodejs.org](https://nodejs.org/en/)
   - Install dengan opsi next-next biasa.

3. **Google Chrome**
   - 🔗 Download: [google.com/chrome](https://www.google.com/chrome/)
   - Wajib ada karena bot WhatsApp butuh browser Chrome untuk proses scan QR Code.

---

## 💻 Tahap 2: Instalasi Dependencies
Langkah ini hanya perlu dilakukan **SATU KALI** saja saat pertama kali mendapatkan file ini.

1. **Ekstrak/Unzip** folder project ini ke lokasi yang kamu inginkan (misal di Documents atau Desktop).
2. Buka folder tersebut (pastikan kamu melihat file seperti `app.py`, `start.bat`, dll).
3. Klik pada *address bar* (jalur folder) di bagian atas File Explorer, lalu ketik `cmd` dan tekan **Enter**. Ini akan membuka jendela terminal (Command Prompt) hitam.
4. Di jendela hitam tersebut, ketik/copy-paste perintah berikut dan tekan **Enter**:
   ```cmd
   pip install -r requirements.txt
   ```
5. Tunggu proses download selesai. Jika sudah, kamu bisa menutup jendela Command Prompt tersebut.

---

## 🏃 Tahap 3: Menjalankan Program (Setiap Hari)
Ini adalah cara yang harus kamu lakukan setiap kali ingin menyalakan bot:

1. Buka folder project.
2. Cari dan klik dua kali (`double-click`) file bernama **`start.bat`**.
3. Akan muncul jendela hitam baru yang akan menjalankan 2 proses:
   - Server Website Admin & Presentasi
   - Server Bot WhatsApp (otomatis menginstal sesuatu saat pertama kali dijalankan, tunggu saja sampai selesai)
4. Tunggu beberapa detik sampai muncul tulisan `Sistem Berhasil Dijalankan!`. (Sebuah jendela terminal baru "WhatsApp Bot Gateway" juga akan terbuka).
5. **JANGAN TUTUP** jendela hitam tersebut selama kamu ingin bot tetap hidup.

---

## 📱 Tahap 4: Menghubungkan ke WhatsApp

1. Buka browser Google Chrome (bisa juga browser lain).
2. Kunjungi link ini untuk melihat QR Code (bisa juga akses via Dashboard Admin):
   👉 **[http://localhost:3000/qr](http://localhost:3000/qr)**
3. Buka aplikasi WhatsApp di HP kamu.
4. Pergi ke **Settings** (Pengaturan) > **Linked Devices** (Perangkat Tertaut) > **Link a Device** (Tautkan Perangkat).
5. Scan QR Code yang muncul di layar laptop/komputermu.
6. Jika berhasil, di terminal hitam "WhatsApp Bot Gateway" akan muncul pesan `"✅ Client is ready!"`. Artinya bot sudah siap membalas pesan!

---

## 🌐 Link Penting

- **Dashboard Admin:** [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin) (Untuk pantau pesanan)
- **Slide Presentasi:** [http://127.0.0.1:5000/presentation](http://127.0.0.1:5000/presentation) (Untuk presentasi ke kelas)
- **Chatbot Web Simulator:** [http://127.0.0.1:5000/chat](http://127.0.0.1:5000/chat) (Kalau malas scan QR dan hanya ingin tes bot lewat web)

> 💡 **Tips jika Bot Error / Hang:** 
> Tutup semua jendela Command Prompt/Terminal hitam (close semuanya), lalu jalankan ulang file `start.bat`.
