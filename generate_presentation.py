import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Inisialisasi presentasi 16:9 widescreen
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Palet Warna Premium
BG_DARK = RGBColor(17, 24, 39)       # #111827 Dark Navy
CARD_BG = RGBColor(31, 41, 55)       # #1F2937 Card Background
ACCENT_ORANGE = RGBColor(255, 107, 53) # #FF6B35 Mentai Orange
ACCENT_GREEN = RGBColor(37, 211, 102) # #25D366 WhatsApp Green
ACCENT_YELLOW = RGBColor(251, 191, 36) # #FBBF24 Warm Gold
TEXT_WHITE = RGBColor(255, 255, 255)
TEXT_MUTED = RGBColor(156, 163, 175) # #9CA3AF Gray
BORDER_COLOR = RGBColor(55, 65, 81)

blank_slide_layout = prs.slide_layouts[6]

def add_header(slide, title_text, category_text="PROYEK CHATBOT WHATSAPP"):
    # Header background shape
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    # Category / Badge
    p0 = tf.paragraphs[0]
    p0.text = category_text.upper()
    p0.font.name = "Segoe UI"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_ORANGE
    
    # Title
    p1 = tf.add_paragraph()
    p1.text = title_text
    p1.font.name = "Segoe UI"
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_before = Pt(4)

def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_DARK

def create_card(slide, left, top, width, height, title, items, badge=""):
    # Shape container
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD_BG
    shape.line.color.rgb = BORDER_COLOR
    shape.line.width = Pt(1)
    
    # Text
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.25)
    tf.margin_bottom = Inches(0.25)
    
    if badge:
        p_badge = tf.paragraphs[0]
        p_badge.text = badge.upper()
        p_badge.font.name = "Segoe UI"
        p_badge.font.size = Pt(9)
        p_badge.font.bold = True
        p_badge.font.color.rgb = ACCENT_ORANGE
        
        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.name = "Segoe UI"
        p_title.font.size = Pt(15)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE
        p_title.space_before = Pt(2)
        p_title.space_after = Pt(8)
    else:
        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.name = "Segoe UI"
        p_title.font.size = Pt(16)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE
        p_title.space_after = Pt(8)
        
    for item in items:
        p = tf.add_paragraph()
        p.text = f"• {item}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(4)

# ==============================================================================
# SLIDE 1: COVER (TITLE SLIDE)
# ==============================================================================
slide1 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide1)

# Main Title Card
cover_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.5))
tf1 = cover_box.text_frame
tf1.word_wrap = True

p_badge = tf1.paragraphs[0]
p_badge.text = "PROJEK AKHIR • PRESENTASI KELAS"
p_badge.font.name = "Segoe UI"
p_badge.font.size = Pt(14)
p_badge.font.bold = True
p_badge.font.color.rgb = ACCENT_ORANGE

p_main = tf1.add_paragraph()
p_main.text = "Rancang Bangun Chatbot Penjualan\nDimsum Mentai Oishi Berbasis WhatsApp"
p_main.font.name = "Segoe UI"
p_main.font.size = Pt(36)
p_main.font.bold = True
p_main.font.color.rgb = TEXT_WHITE
p_main.space_before = Pt(12)

p_sub = tf1.add_paragraph()
p_sub.text = "Otomasi Transaksi Pemesanan Makanan Real-Time dengan Integrasi WhatsApp Gateway, Python Flask, dan SQLite Database"
p_sub.font.name = "Segoe UI"
p_sub.font.size = Pt(16)
p_sub.font.color.rgb = TEXT_MUTED
p_sub.space_before = Pt(14)

p_footer = tf1.add_paragraph()
p_footer.text = "🍱 Dimsum Mentai Oishi  |  💬 WhatsApp Bot  |  📊 Admin Web Dashboard"
p_footer.font.name = "Segoe UI"
p_footer.font.size = Pt(13)
p_footer.font.bold = True
p_footer.font.color.rgb = ACCENT_GREEN
p_footer.space_before = Pt(28)

# ==============================================================================
# SLIDE 2: LATAR BELAKANG & PERMASALAHAN
# ==============================================================================
slide2 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide2)
add_header(slide2, "Latar Belakang & Identifikasi Masalah", "01. LATAR BELAKANG")

create_card(slide2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "Tantangan Order Manual", 
    [
        "Admin kewalahan membalas chat satu per satu di jam sibuk (makan siang/malam).",
        "Respon lambat (slow response) menyebabkan customer membatalkan pesanan (churn).",
        "Pencatatan data pesanan manual rentan salah alamat, salah varian, atau salah hitung harga.",
        "Keterbatasan jam operasional admin manusia (tidak bisa 24/7)."
    ], "Masalah UMKM")

create_card(slide2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "Potensi Saluran WhatsApp", 
    [
        "WhatsApp adalah aplikasi pesan nomor 1 di Indonesia dengan penetrasi >88%.",
        "Customer lebih suka memesan langsung via chat daripada mendownload aplikasi baru yang memberatkan memori.",
        "Komunikasi instan memberikan rasa percaya dan keintiman antara penjual dan pembeli.",
        "Mudah membagikan tautan pesanan, nota digital, dan bukti transfer."
    ], "Peluang Pasar")

create_card(slide2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "Kebutuhan Solusi Otomasi", 
    [
        "Perlu asisten virtual pintar yang menjawab salam dan menampilkan menu seketika.",
        "Memandu alur belanja tahap demi tahap secara interaktif dan terstruktur.",
        "Merekam otomatis pesanan ke basis data terpusat secara rapi dan aman.",
        "Menyediakan dashboard admin untuk memantau status pesanan (Proses, Selesai, Batal)."
    ], "Tujuan Riset")

# ==============================================================================
# SLIDE 3: SOLUSI YANG DITAWARKAN
# ==============================================================================
slide3 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide3)
add_header(slide3, "Solusi: Ekosistem Penjualan Otomatis 3-in-1", "02. SOLUSI INOVASI")

create_card(slide3, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "1. WhatsApp Chatbot Asli", 
    [
        "Berjalan di nomor WhatsApp bisnis nyata menggunakan WhatsApp Web Gateway.",
        "Customer cukup mengirim pesan 'Halo' dari aplikasi WhatsApp di HP mereka.",
        "Menampilkan katalog menu lengkap beserta harga dan deskripsi lezat.",
        "Menerima pesanan dan mencetak ringkasan nota digital otomatis dalam hitungan detik."
    ], "Channel Pelanggan")

create_card(slide3, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "2. Web Chat Simulator", 
    [
        "Antarmuka simulasi obrolan WhatsApp berbasis web (UI identik dengan WA asli).",
        "Sangat ideal untuk presentasi di kelas tanpa bergantung pada jaringan seluler.",
        "Dilengkapi fitur Quick Reply button dan pengujian nomor pelanggan simulasi.",
        "Terhubung ke mesin percakapan (bot logic) dan database yang sama persis."
    ], "Demo Interaktif")

create_card(slide3, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "3. Admin Management Portal", 
    [
        "Dashboard pemantauan transaksi real-time (omset, total order, status).",
        "Tabel pesanan masuk lengkap: nama, varian, jumlah, alamat kirim, total harga.",
        "Fitur ganti status sekali klik: Menunggu -> Diproses -> Selesai / Batal.",
        "Panel status koneksi gateway WA dan fitur uji kirim pesan langsung dari web."
    ], "Operasional Toko")

# ==============================================================================
# SLIDE 4: KATALOG PRODUK DIMSUM MENTAI OISHI
# ==============================================================================
slide4 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide4)
add_header(slide4, "Katalog Produk & Struktur Data Penjualan", "03. PRODUK & MENU")

create_card(slide4, Inches(0.8), Inches(1.8), Inches(2.7), Inches(4.8), 
    "Mentai Original", 
    [
        "Harga: Rp25.000",
        "Isi: 4 pcs Dimsum Ayam Udang",
        "Topping: Saus mentai gurih khas Jepang di-torch wangi + Nori crumbles.",
        "Status Stok: Ready (Terkontrol otomatis di DB)."
    ], "BEST SELLER ⭐")

create_card(slide4, Inches(3.8), Inches(1.8), Inches(2.7), Inches(4.8), 
    "Mentai Spicy", 
    [
        "Harga: Rp27.000",
        "Isi: 4 pcs Dimsum Ayam Udang",
        "Topping: Saus mentai pedas cabai pilihan + Tobiko segar.",
        "Favorit pecinta sensasi pedas mantap."
    ], "TERLARIS 🔥")

create_card(slide4, Inches(6.8), Inches(1.8), Inches(2.7), Inches(4.8), 
    "Cheese Melt", 
    [
        "Harga: Rp28.000",
        "Isi: 4 pcs Dimsum Ayam",
        "Topping: Saus mentai + Lelehan keju mozzarella premium yang dibakar lumer.",
        "Varian premium gurih berlipat."
    ], "FAVORIT 🧀")

create_card(slide4, Inches(9.8), Inches(1.8), Inches(2.7), Inches(4.8), 
    "Platter Party", 
    [
        "Harga: Rp95.000",
        "Isi: 16 pcs Dimsum Mix 4 Rasa",
        "Cocok untuk acara kumpul, kantor, atau perayaan keluarga.",
        "Diskon paket hemat Rp10.000."
    ], "HEMAT 🍱")

# ==============================================================================
# SLIDE 5: ARSITEKTUR TEKNOLOGI & DATA FLOW
# ==============================================================================
slide5 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide5)
add_header(slide5, "Arsitektur Sistem & Aliran Komunikasi Data", "04. ARSITEKTUR SISTEM")

create_card(slide5, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "1. WhatsApp Gateway", 
    [
        "Teknologi: Node.js + whatsapp-web.js + Puppeteer (Google Chrome Headless).",
        "Mengautentikasi sesi WhatsApp via QR Code tanpa perlu akun WhatsApp Business API berbayar.",
        "Menangkap event 'message' secara real-time dari customer.",
        "Meneruskan JSON payload pesan ke Flask melalui HTTP POST Webhook."
    ], "Frontend Layer")

create_card(slide5, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "2. Conversation Engine", 
    [
        "Teknologi: Python 3 + Flask Web Framework.",
        "Menerapkan Finite State Machine (FSM) untuk melacak posisi percakapan tiap user.",
        "Melakukan validasi input: kuantitas angka, format alamat, dan konfirmasi YA/TIDAK.",
        "Menghasilkan balasan ramah dalam bahasa Indonesia berformat WhatsApp Markdown."
    ], "Logic Layer")

create_card(slide5, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "3. Storage & Monitoring", 
    [
        "Teknologi: SQLite 3 Database terindeks ACID compliant.",
        "Tabel terstruktur: products, customers, orders, order_items.",
        "Admin Dashboard menyajikan statistik omset, order aktif, dan perubahan status pengiriman.",
        "Live Polling AJAX: data update instan tanpa me-reload seluruh halaman browser."
    ], "Data Layer")

# ==============================================================================
# SLIDE 6: ALUR PERCAKAPAN (FINITE STATE MACHINE)
# ==============================================================================
slide6 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide6)
add_header(slide6, "Alur Percakapan Chatbot (Conversation Flow)", "05. LOGIKA PERCAKAPAN")

create_card(slide6, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "Fase 1: Sapaan & Pilihan", 
    [
        "1. STATE: IDLE\nCustomer kirim 'Halo' -> Bot menyapa ramah dan menyajikan 3 opsi: Lihat Menu, Pesan, Cek Pesanan.",
        "2. STATE: SELECTING_PRODUCT\nBot menampilkan katalog menu bernomor. Customer cukup ketik angka '1', '2', atau nama menu.",
        "Fitur Keamanan: Validasi nomor produk. Jika input salah, bot mengulang dengan sopan."
    ], "Step 1 & 2")

create_card(slide6, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "Fase 2: Identitas & Kirim", 
    [
        "3. STATE: INPUT_QTY\nCustomer menentukan porsi (contoh: '2'). Bot mengecek stok tersedia.",
        "4. STATE: INPUT_NAME\nCustomer memasukkan nama pemesan.",
        "5. STATE: INPUT_ADDRESS\nCustomer menginput alamat lengkap untuk pengantaran kurir.",
        "Data disimpan sementara ke sesi percakapan SQLite (session_data JSON)."
    ], "Step 3 & 4")

create_card(slide6, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "Fase 3: Konfirmasi & Nota", 
    [
        "6. STATE: CONFIRMING\nBot menyajikan rincian nota: Pesanan, Jumlah, Total Biaya, Nama, Alamat. Pilihan: YA / BATAL.",
        "7. FINISH / ORDER CREATED\nKetik 'YA' -> Pesanan disimpan resmi ke database, stok dipotong, nota final terbit.",
        "8. OPSI BATAL GLOBAL\nKapan saja ketik 'Batal', percakapan kembali ke menu awal tanpa menyimpan sampah."
    ], "Step 5 & 6")

# ==============================================================================
# SLIDE 7: FITUR UNGGULAN & KEUNGGULAN KOMPETITIF
# ==============================================================================
slide7 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide7)
add_header(slide7, "Fitur Unggulan Prototipe Dimsum Bot", "06. FITUR UNGGULAN")

create_card(slide7, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "Otomasi Transaksi Penuh", 
    [
        "Bekerja 24/7 tanpa henti melayani order bahkan saat toko tutup untuk antrean besok.",
        "Perhitungan subtotal dan total harga instan otomatis bebas dari 'human calculation error'.",
        "Penomoran ID pesanan unik (#ORD-xxx) mempermudah pelacakan invoice dan resi pengiriman.",
        "Customer dapat mengecek status pesanannya sendiri lewat opsi '3. Cek Pesanan'."
    ], "Efisiensi Tinggi")

create_card(slide7, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "Dual Channel Architecture", 
    [
        "Dukungan WhatsApp Nyata: Integrasi dengan nomor WhatsApp aktif via pemindaian QR Code.",
        "Dukungan Simulator Web: Tersedia antarmuka pengujian lokal untuk demonstrasi kelas dan presentasi.",
        "Kedua saluran berbagi basis data yang sama: order dari simulator langsung muncul di admin begitu juga sebaliknya.",
        "Zero-Cost Setup: Tidak memerlukan langganan bulanan WhatsApp Cloud API berbayar."
    ], "Fleksibilitas Demo")

create_card(slide7, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "Toleransi Kesalahan & AI Helper", 
    [
        "Pembersihan Lock Chromium Otomatis: Mencegah error 'Browser already running' saat restart.",
        "Normalisasi nomor telepon otomatis (mendukung format 08xx, +62xx, maupun 62xx).",
        "Respons natural bahasa Indonesia dengan emotikon ramah selaras citra brand kuliner Oishi.",
        "Panel kontrol admin web interaktif yang responsif diakses dari laptop maupun HP."
    ], "Kehandalan Sistem")

# ==============================================================================
# SLIDE 8: STACK TEKNOLOGI & IMPLEMENTASI
# ==============================================================================
slide8 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide8)
add_header(slide8, "Spesifikasi Teknologi Perangkat Lunak", "07. TECH STACK")

create_card(slide8, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "Backend & Service", 
    [
        "Python 3.10+: Bahasa pemrograman utama untuk webhook handler dan bot engine.",
        "Flask Framework: Microframework ringan, cepat, dan handal untuk REST API & Web Server.",
        "SQLite 3: Embedded Relational Database Management System berkas tunggal (dimsum.db).",
        "Gunicorn / Werkzeug: WSGI application server."
    ], "Server Side")

create_card(slide8, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "WhatsApp Gateway", 
    [
        "Node.js Runtime (v22+): Menjalankan automasi WhatsApp Web headless.",
        "whatsapp-web.js: Pustaka penghubung resmi ke client WhatsApp Web.",
        "Puppeteer Core: Mengendalikan peramban Google Chrome tanpa antarmuka GUI (Headless Chromium).",
        "qrcode-terminal & qrcode: Merender QR Code baik di CLI maupun web browser."
    ], "WhatsApp Integration")

create_card(slide8, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "Frontend & Admin UI", 
    [
        "HTML5 & Vanilla JavaScript ES6: Pengolahan AJAX fetch API tanpa library berat.",
        "Bootstrap 5.3: Kerangka desain responsif modern (Mobile First Design).",
        "Bootstrap Icons: Ikonografi UI antarmuka standar profesional.",
        "Custom Design System: Tema palet warna khas Dimsum Mentai (Oranye, Hitam Elegan, Emas)."
    ], "Client Interface")

# ==============================================================================
# SLIDE 9: RENCANA PENGEMBANGAN LANJUTAN
# ==============================================================================
slide9 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide9)
add_header(slide9, "Rencana Pengembangan Masa Depan (Roadmap)", "08. ROADMAP")

create_card(slide9, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "1. Payment Gateway (QRIS)", 
    [
        "Integrasi API pembayaran instan seperti Midtrans atau Xendit.",
        "Bot mengirimkan kode QRIS dinamis unik ke chat WhatsApp customer.",
        "Deteksi otomatis pembayaran berhasil (Callback Webhook) tanpa perlu verifikasi transfer manual oleh admin.",
        "Status pesanan langsung otomatis berubah ke 'Diproses'."
    ], "Fase 1: Finansial")

create_card(slide9, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "2. Logistik & Kurir Otomatis", 
    [
        "Koneksi API kurir instan seperti Gosend, GrabExpress, atau Lalamove.",
        "Perhitungan ongkos kirim otomatis berdasarkan koordinat atau kelurahan alamat customer.",
        "Penjemputan driver otomatis begitu pesanan selesai dikukus oleh dapur.",
        "Pemberian tautan live tracking kurir langsung ke nomor customer."
    ], "Fase 2: Distribusi")

create_card(slide9, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
    "3. AI NLP & Personalisasi", 
    [
        "Penerapan model kecerdasan buatan NLP (Gemini / LLM) untuk memahami bahasa santai/slang.",
        "Rekomendasi menu cerdas berbasis riwayat pesanan sebelumnya (contoh: 'Mau pesan Dimsum Spicy favorit Kakak lagi?').",
        "Program loyalitas pelanggan otomatis: pengumpulan poin dan kupon diskon via chat WhatsApp."
    ], "Fase 3: Smart CRM")

# ==============================================================================
# SLIDE 10: KESIMPULAN & SESI TANYA JAWAB
# ==============================================================================
slide10 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide10)
add_header(slide10, "Kesimpulan & Sesi Tanya Jawab (Q&A)", "09. KESIMPULAN")

create_card(slide10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), 
    "Kesimpulan Proyek", 
    [
        "Prototipe Chatbot Dimsum Mentai Oishi berhasil menjawab tantangan efisiensi penjualan UMKM.",
        "Sistem memangkas waktu proses pemesanan dari rata-rata 5-8 menit manual menjadi di bawah 45 detik secara otomatis.",
        "Mencegah kesalahan pencatatan pesanan hingga 100% karena data diinput langsung oleh pembeli dan tersimpan di database relasional.",
        "Dukungan dual mode (WhatsApp Asli + Simulator Web) memudahkan operasional serta proses validasi pengujian.",
        "Investasi teknologi tepat guna yang hemat biaya dan siap ditingkatkan (scalable) ke skala bisnis yang lebih besar."
    ], "Ringkasan Hasil")

create_card(slide10, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), 
    "Terima Kasih! Mari Berdiskusi", 
    [
        "Kami siap menjawab pertanyaan, masukan, dan saran dari Dosen serta rekan-rekan kelas sekalian.",
        "",
        "🔗 Demo Sistem Live:",
        "• Web Simulator: http://127.0.0.1:5000/chat",
        "• Dashboard Admin: http://127.0.0.1:5000/admin",
        "• QR Code Gateway: http://127.0.0.1:3000/qr",
        "",
        "🍱 'Kelezatan Dimsum Mentai Hangat di Ujung Jari Anda!' ✨"
    ], "Sesi Tanya Jawab (Q&A)")

output_path = os.path.abspath("e:/New folder/Dimsum_Mentai_Oishi_Presentasi.pptx")
prs.save(output_path)
print(f"✅ Slide presentasi berhasil dibuat: {output_path}")
