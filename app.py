import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import (
    init_db,
    get_all_products,
    get_product_by_id,
    get_all_orders,
    get_order_by_id,
    update_order_status,
    get_admin_stats
)
from bot_logic import process_bot_message
from wppconnect import send_whatsapp_message, check_wpp_status, WPP_HOST, WPP_SESSION

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dimsum-mentai-oishi-secret-2026'

# Inisialisasi database SQLite saat startup
init_db()

@app.route('/')
def index():
    products = get_all_products()
    return render_template('index.html', products=products)

@app.route('/chat')
def chat():
    products = get_all_products()
    return render_template('chat.html', products=products)

@app.route('/presentation')
def presentation():
    return render_template('presentation.html')

@app.route('/admin')
def admin():
    orders = get_all_orders()
    stats = get_admin_stats()
    products = get_all_products()
    wpp_status = check_wpp_status()
    return render_template(
        'admin.html',
        orders=orders,
        stats=stats,
        products=products,
        wpp_status=wpp_status,
        wpp_host=WPP_HOST,
        wpp_session=WPP_SESSION
    )

# =============================================================================
# WEBHOOK WPPCONNECT (Menerima Pesan Real dari WhatsApp)
# =============================================================================
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return jsonify({
            'status': 'active',
            'service': 'WA Chatbot Dimsum Mentai Oishi Gateway',
            'wpp_session': WPP_SESSION
        })

    payload = request.get_json(silent=True) or {}
    print(f"\n📩 [Webhook Received]: {payload}")

    # Ekstraksi data pesan dari WPPConnect (Mendukung beragam format payload WPPConnect)
    data = payload.get('data', payload)
    
    # Abaikan jika pesan dikirim oleh bot sendiri
    from_me = data.get('fromMe', False)
    if from_me:
        return jsonify({'status': 'ignored', 'reason': 'Message from bot itself'}), 200

    # Dapatkan pengirim dan isi pesan
    sender = data.get('from') or data.get('author') or data.get('phone') or ''
    message_body = data.get('body') or data.get('content') or data.get('message') or ''
    sender_name = data.get('sender', {}).get('pushname') or data.get('notifyName') or 'Customer'

    # Abaikan pesan grup (hanya respon pesan personal customer)
    is_group = data.get('isGroupMsg', False) or '@g.us' in sender
    if is_group:
        return jsonify({'status': 'ignored', 'reason': 'Group message'}), 200

    if not sender or not message_body:
        return jsonify({'status': 'ignored', 'reason': 'Empty sender or body'}), 200

    print(f"👤 Pesan dari {sender} ({sender_name}): {message_body}")

    # Proses pesan melalui bot conversation engine
    bot_result = process_bot_message(
        wa_number=sender,
        message_text=message_body,
        sender_name=sender_name
    )

    reply_text = bot_result.get('reply', '')
    print(f"🤖 Balasan Bot:\n{reply_text}\n")

    # Kirim balasan otomatis langsung ke WhatsApp customer via WPPConnect Server
    send_result = send_whatsapp_message(sender, reply_text)

    return jsonify({
        'status': 'success',
        'processed_for': sender,
        'reply': reply_text,
        'wpp_dispatch': send_result
    }), 200

# =============================================================================
# API SIMULATOR CHAT (Untuk Demo di Browser tanpa WPPConnect)
# =============================================================================
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json(silent=True) or {}
    user_msg = data.get('message', '').strip()
    phone = data.get('phone', '628123456789')
    name = data.get('name', 'Customer Demo')

    bot_result = process_bot_message(
        wa_number=phone,
        message_text=user_msg,
        sender_name=name
    )

    return jsonify(bot_result)

# =============================================================================
# API ADMIN (Ubah Status Pesanan & Cek WPPConnect)
# =============================================================================
@app.route('/api/admin/order-status', methods=['POST'])
def api_update_status():
    data = request.get_json(silent=True) or {}
    order_id = data.get('order_id')
    new_status = data.get('status')
    
    if not order_id or not new_status:
        return jsonify({'status': 'error', 'message': 'Parameter tidak lengkap'}), 400

    update_order_status(order_id, new_status)
    stats = get_admin_stats()
    return jsonify({
        'status': 'success',
        'message': f'Status pesanan #ORD-{order_id} berhasil diubah ke {new_status}',
        'stats': stats
    })

@app.route('/api/admin/test-whatsapp', methods=['POST'])
def api_test_whatsapp():
    data = request.get_json(silent=True) or {}
    phone = data.get('phone')
    message = data.get('message', 'Halo! Ini pesan tes dari Dimsum Mentai Oishi WhatsApp Bot.')

    if not phone:
        return jsonify({'status': 'error', 'message': 'Nomor WhatsApp wajib diisi'}), 400

    res = send_whatsapp_message(phone, message)
    return jsonify(res)

@app.route('/api/admin/wpp-live-status', methods=['GET'])
def api_wpp_live_status():
    status = check_wpp_status()
    return jsonify(status)

if __name__ == '__main__':
    print("=" * 60)
    print("   WA Chatbot Penjualan Dimsum Mentai Oishi")
    print("   Server berjalan di:    http://127.0.0.1:5000")
    print("   Halaman Chatbot Demo:  http://127.0.0.1:5000/chat")
    print("   Halaman Admin:        http://127.0.0.1:5000/admin")
    print("   Endpoint Webhook:     http://127.0.0.1:5000/webhook")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
