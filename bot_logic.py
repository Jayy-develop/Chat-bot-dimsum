import json
from database import (
    get_all_products,
    get_product_by_id,
    update_product_stock,
    get_or_create_customer,
    update_customer_session,
    create_order,
    get_orders_by_customer_wa
)

def format_rupiah(amount):
    return f"Rp{amount:,.0f}".replace(',', '.')

def normalize_wa_number(raw_number):
    """
    Normalisasi nomor WhatsApp ke format internasional: 628xxxxxxxxx
    Menangani format:
    - 6285xxxxxxxx@c.us         -> 6285xxxxxxxx
    - 6285xxxxxxxx@s.whatsapp.net -> 6285xxxxxxxx
    - 085xxxxxxxx               -> 6285xxxxxxxx
    - 85xxxxxxxx                -> 6285xxxxxxxx
    - WA Lid format panjang (>13 digit tanpa 62) -> gunakan sender_name fallback
    """
    # Hapus suffix WhatsApp
    clean = str(raw_number)
    clean = clean.replace('@c.us', '').replace('@s.whatsapp.net', '').replace('@lid', '').strip()
    # Ambil digit saja
    digits = ''.join(filter(str.isdigit, clean))
    if not digits:
        return '628000000000'
    # Normalisasi ke format 62xxx
    if digits.startswith('62') and len(digits) >= 10:
        return digits  # sudah benar
    elif digits.startswith('08') and len(digits) >= 10:
        return '62' + digits[1:]  # 085xxx -> 6285xxx
    elif digits.startswith('8') and len(digits) >= 9:
        return '62' + digits      # 85xxx -> 6285xxx
    elif len(digits) > 13:
        # Format WA lid internal (sangat panjang) - gunakan apa adanya
        return digits
    return digits

def process_bot_message(wa_number, message_text, sender_name=None):
    """
    Memproses pesan masuk dari WhatsApp dan mengembalikan pesan balasan bot
    berdasarkan alur Customer -> Produk -> Jumlah -> Nama -> Alamat -> Checkout
    """
    clean_wa = normalize_wa_number(wa_number)
    
    text = (message_text or '').strip()
    text_lower = text.lower()

    # Dapatkan data customer dan sesi percakapan
    customer = get_or_create_customer(clean_wa, default_name=sender_name)
    current_state = customer.get('state', 'IDLE') or 'IDLE'
    
    try:
        session_data = json.loads(customer.get('session_data') or '{}')
    except Exception:
        session_data = {}

    # OPSI PEMBATALAN GLOBAL (Kapan saja customer ketik batal)
    if text_lower in ['batal', 'cancel', 'reset', 'ulang']:
        update_customer_session(clean_wa, state='IDLE', session_data={})
        reply = (
            "❌ Pemesanan telah dibatalkan.\n\n"
            "Ketik *Halo* untuk kembali ke menu utama Dimsum Mentai Oishi 🍱"
        )
        return {
            'reply': reply,
            'state': 'IDLE',
            'quick_replies': ['Halo', '1. Lihat Produk', '2. Pesan']
        }

    # =========================================================================
    # STATE: IDLE (Menu Utama & Informasi)
    # =========================================================================
    if current_state == 'IDLE':
        # Trigger Halo / Sapaan
        if any(greet in text_lower for greet in ['halo', 'hai', 'hi', 'start', 'mulai', 'pagi', 'siang', 'sore', 'malam', 'assalamualaikum']) or not text:
            reply = (
                "Halo Kak 👋\n"
                "Selamat datang di Dimsum Mentai Oishi 🍱\n\n"
                "Menu:\n"
                "1. Lihat Produk\n"
                "2. Pesan\n"
                "3. Cek Pesanan"
            )
            return {
                'reply': reply,
                'state': 'IDLE',
                'quick_replies': ['1. Lihat Produk', '2. Pesan', '3. Cek Pesanan']
            }

        # Opsi 1: Lihat Produk
        if text_lower in ['1', 'lihat produk', '1. lihat produk', 'produk', 'menu', 'katalog'] or 'lihat produk' in text_lower or text_lower.startswith('1.'):
            products = get_all_products()
            reply = "🍱 *KATALOG PRODUK DIMSUM MENTAI OISHI* 🍱\n\n"
            for idx, p in enumerate(products, 1):
                reply += (
                    f"{idx}. *{p['nama']}*\n"
                    f"   💰 {format_rupiah(p['harga'])} (Stok: {p['stok']})\n\n"
                )
            reply += "Silakan ketik *2* atau *Pesan* untuk mulai melakukan pemesanan! 🥢"
            return {
                'reply': reply,
                'state': 'IDLE',
                'quick_replies': ['2. Pesan', '3. Cek Pesanan', 'Halo']
            }

        # Opsi 2: Pesan (Masuk ke alur pemesanan)
        if text_lower in ['2', 'pesan', 'order', 'beli', 'mau pesan', '2. pesan'] or 'pesan' in text_lower or text_lower.startswith('2.'):
            products = get_all_products()
            reply = (
                "🥢 *PILIH VARIAN DIMSUM:*\n"
                "Silakan ketik nomor produk yang ingin dipesan:\n\n"
            )
            for idx, p in enumerate(products, 1):
                reply += f"{idx}. {p['nama']} - {format_rupiah(p['harga'])}\n"
            
            reply += "\n_Contoh: ketik angka *1* untuk Dimsum Mentai Original_\n"
            reply += "(Ketik *Batal* kapan saja untuk membatalkan)"
            
            update_customer_session(clean_wa, state='AWAIT_PRODUCT', session_data={})
            quick_replies = [f"{idx}. {p['nama']}" for idx, p in enumerate(products, 1)]
            quick_replies.append('Batal')
            return {
                'reply': reply,
                'state': 'AWAIT_PRODUCT',
                'quick_replies': quick_replies
            }

        # Opsi 3: Cek Pesanan
        if text_lower in ['3', 'cek pesanan', 'cek order', 'status', 'lacak', '3. cek pesanan'] or 'cek pesanan' in text_lower or text_lower.startswith('3.'):
            orders = get_orders_by_customer_wa(clean_wa)
            if orders:
                reply = f"📋 *DAFTAR PESANAN KAKAK:* ({len(orders)} pesanan)\n\n"
                for o in orders:
                    status_icon = "👨‍🍳" if o['status'] == 'Diproses' else ("✅" if o['status'] == 'Selesai' else "❌")
                    reply += (
                        f"🆔 *Order #ORD-{o['id']}*\n"
                        f"🍱 {o['produk']}\n"
                        f"💰 Total: {format_rupiah(o['total'])}\n"
                        f"⚡ Status: *{o['status']}* {status_icon}\n"
                        f"📅 Waktu: {o['created_at']}\n"
                        f"-----------------------------\n"
                    )
                reply += "Ketik *Halo* untuk kembali ke menu utama."
            else:
                reply = (
                    "Belum ada pesanan aktif dengan nomor WhatsApp ini ya Kak.\n\n"
                    "Ketik *2* atau *Pesan* untuk membuat pesanan baru! 🍱"
                )
            return {
                'reply': reply,
                'state': 'IDLE',
                'quick_replies': ['1. Lihat Produk', '2. Pesan', 'Halo']
            }

        # Fallback default untuk IDLE
        reply = (
            "Halo Kak 👋\n"
            "Selamat datang di Dimsum Mentai Oishi 🍱\n\n"
            "Menu:\n"
            "1. Lihat Produk\n"
            "2. Pesan\n"
            "3. Cek Pesanan"
        )
        return {
            'reply': reply,
            'state': 'IDLE',
            'quick_replies': ['1. Lihat Produk', '2. Pesan', '3. Cek Pesanan']
        }

    # =========================================================================
    # STATE: AWAIT_PRODUCT (Pilih Produk)
    # =========================================================================
    if current_state == 'AWAIT_PRODUCT':
        products = get_all_products()
        selected_product = None

        # Cek berdasarkan nomor urut (1, 2, 3...)
        clean_input = text.replace('.', '').strip()
        if clean_input.isdigit():
            idx = int(clean_input) - 1
            if 0 <= idx < len(products):
                selected_product = products[idx]

        # Cek berdasarkan nama produk
        if not selected_product:
            for p in products:
                if p['nama'].lower() in text_lower or text_lower in p['nama'].lower():
                    selected_product = p
                    break

        if not selected_product:
            return {
                'reply': "⚠️ Pilihan produk tidak dikenali Kak. Mohon ketik nomor produk yang valid (contoh: *1*, *2*, atau *3*).\n\n(Ketik *Batal* untuk berhenti)",
                'state': 'AWAIT_PRODUCT',
                'quick_replies': ['1. Original', '2. Spicy', '3. Cheese', 'Batal']
            }

        session_data['product_id'] = selected_product['id']
        session_data['product_name'] = selected_product['nama']
        session_data['harga'] = selected_product['harga']

        update_customer_session(clean_wa, state='AWAIT_QTY', session_data=session_data)

        reply = (
            f"✅ Pilihan: *{selected_product['nama']}*\n"
            f"Harga: {format_rupiah(selected_product['harga'])} / porsi\n\n"
            "Berapa *jumlah porsi* yang ingin dipesan?\n"
            "_(Ketik angka saja, contoh: 2)_"
        )
        return {
            'reply': reply,
            'state': 'AWAIT_QTY',
            'quick_replies': ['1', '2', '3', '5', 'Batal']
        }

    # =========================================================================
    # STATE: AWAIT_QTY (Masukkan Jumlah)
    # =========================================================================
    if current_state == 'AWAIT_QTY':
        # Validasi input jumlah
        clean_num = ''.join(filter(str.isdigit, text))
        if not clean_num or int(clean_num) <= 0:
            return {
                'reply': "⚠️ Mohon masukkan jumlah porsi dalam bentuk angka minimal 1 ya Kak (contoh: *2*).\n\n(Ketik *Batal* untuk berhenti)",
                'state': 'AWAIT_QTY',
                'quick_replies': ['1', '2', '3', '5', 'Batal']
            }

        qty = int(clean_num)
        total_harga = session_data.get('harga', 25000) * qty
        session_data['qty'] = qty
        session_data['total'] = total_harga

        update_customer_session(clean_wa, state='AWAIT_NAME', session_data=session_data)

        reply = (
            f"📦 Jumlah: *{qty} porsi*\n"
            f"💰 Subtotal: *{format_rupiah(total_harga)}*\n\n"
            "Atas nama siapa pesanan ini Kak?\n"
            "_(Ketik *Nama Lengkap* Kakak)_"
        )
        return {
            'reply': reply,
            'state': 'AWAIT_NAME',
            'quick_replies': [customer.get('nama') or 'Kak Pembeli', 'Batal']
        }

    # =========================================================================
    # STATE: AWAIT_NAME (Masukkan Nama)
    # =========================================================================
    if current_state == 'AWAIT_NAME':
        nama = text.strip()
        if len(nama) < 2:
            return {
                'reply': "⚠️ Mohon masukkan nama yang valid ya Kak 🙏",
                'state': 'AWAIT_NAME'
            }

        session_data['nama'] = nama
        update_customer_session(clean_wa, state='AWAIT_ADDRESS', session_data=session_data, nama=nama)

        reply = (
            f"Senang melayani Kak *{nama}* 😊\n\n"
            "Sekarang, mohon kirimkan *Alamat Lengkap Pengiriman* Kakak:\n"
            "_(Contoh: Jl. Mawar No. 12, RT 02/05, Kebayoran Baru, Jakarta)_"
        )
        return {
            'reply': reply,
            'state': 'AWAIT_ADDRESS',
            'quick_replies': ['Batal']
        }

    # =========================================================================
    # STATE: AWAIT_ADDRESS (Masukkan Alamat)
    # =========================================================================
    if current_state == 'AWAIT_ADDRESS':
        alamat = text.strip()
        if len(alamat) < 4:
            return {
                'reply': "⚠️ Mohon masukkan alamat pengiriman yang lebih jelas ya Kak 🙏",
                'state': 'AWAIT_ADDRESS'
            }

        session_data['alamat'] = alamat
        update_customer_session(clean_wa, state='AWAIT_CHECKOUT', session_data=session_data, alamat=alamat)

        p_name = session_data.get('product_name', 'Dimsum Mentai')
        qty = session_data.get('qty', 1)
        total = session_data.get('total', 25000)
        nama = session_data.get('nama', 'Customer')

        reply = (
            "📋 *RINGKASAN PESANAN KAKAK:*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🍱 Produk: *{p_name}*\n"
            f"🔢 Jumlah: *{qty} porsi*\n"
            f"💰 Total: *{format_rupiah(total)}*\n"
            f"👤 Nama: *{nama}*\n"
            f"📱 WhatsApp: *{clean_wa}*\n"
            f"📍 Alamat: *{alamat}*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Ketik *YA* untuk checkout & proses pesanan sekarang.\n"
            "(Atau ketik *Batal* jika ingin membatalkan)"
        )
        return {
            'reply': reply,
            'state': 'AWAIT_CHECKOUT',
            'quick_replies': ['YA', 'Batal']
        }

    # =========================================================================
    # STATE: AWAIT_CHECKOUT (Konfirmasi Checkout)
    # =========================================================================
    if current_state == 'AWAIT_CHECKOUT':
        if text_lower in ['ya', 'yes', 'oke', 'ok', 'checkout', 'pesan sekarang', 'setuju', '1']:
            p_id = session_data.get('product_id', 1)
            p_name = session_data.get('product_name', 'Dimsum Mentai Original')
            qty = session_data.get('qty', 1)
            total = session_data.get('total', 25000)
            nama = session_data.get('nama', customer.get('nama') or 'Customer')
            alamat = session_data.get('alamat', customer.get('alamat') or '-')
            produk_deskripsi = f"{p_name} ({qty} porsi)"

            # Simpan order ke database SQLite
            order_id = create_order(
                customer_id=customer.get('id'),
                nama_customer=nama,
                no_wa=clean_wa,
                alamat=alamat,
                produk=produk_deskripsi,
                total=total,
                status='Diproses'
            )

            # Kurangi stok produk
            update_product_stock(p_id, qty)

            # Reset status customer ke IDLE
            update_customer_session(clean_wa, state='IDLE', session_data={})

            reply = (
                "Pesanan berhasil dibuat. 🎉\n"
                "Terima kasih sudah memesan Dimsum Mentai Oishi 🍱🙏\n\n"
                f"📋 *Rincian Pesanan:*\n"
                f"🆔 Nomor Order: *#ORD-{order_id}*\n"
                f"👤 Nama: {nama}\n"
                f"🍱 Produk: {produk_deskripsi}\n"
                f"💰 Total: {format_rupiah(total)}\n"
                f"📍 Alamat: {alamat}\n"
                f"⚡ Status: *Diproses* 👨‍🍳\n\n"
                "Pesanan Kakak sedang disiapkan di dapur dan akan segera dikirimkan!\n"
                "Ketik *3* atau *Cek Pesanan* kapan saja untuk memeriksa status pesanan."
            )
            return {
                'reply': reply,
                'state': 'IDLE',
                'order_id': order_id,
                'quick_replies': ['3. Cek Pesanan', '1. Lihat Produk', 'Halo']
            }
        else:
            return {
                'reply': "Mohon ketik *YA* untuk mengonfirmasi pesanan, atau *Batal* untuk membatalkan pesanan Kakak 😊",
                'state': 'AWAIT_CHECKOUT',
                'quick_replies': ['YA', 'Batal']
            }

    # Reset jika state tidak dikenal
    update_customer_session(clean_wa, state='IDLE', session_data={})
    return {
        'reply': (
            "Halo Kak 👋\n"
            "Selamat datang di Dimsum Mentai Oishi 🍱\n\n"
            "Menu:\n"
            "1. Lihat Produk\n"
            "2. Pesan\n"
            "3. Cek Pesanan"
        ),
        'state': 'IDLE',
        'quick_replies': ['1. Lihat Produk', '2. Pesan', '3. Cek Pesanan']
    }
