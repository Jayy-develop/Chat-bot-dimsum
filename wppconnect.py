import os
import requests
import json

# Konfigurasi default Gateway WhatsApp Bot
WPP_HOST = os.getenv('WPP_HOST', 'http://127.0.0.1:3000')
WPP_SESSION = os.getenv('WPP_SESSION', 'dimsum-session')

def format_phone_number(phone):
    """
    Format nomor HP ke standar WhatsApp internasional (contoh: 628123456789)
    """
    clean = str(phone).replace('@c.us', '').replace('@s.whatsapp.net', '').strip()
    clean = ''.join(filter(str.isdigit, clean))
    if clean.startswith('08'):
        clean = '628' + clean[2:]
    elif clean.startswith('8'):
        clean = '62' + clean
    return clean

def send_whatsapp_message(phone, message):
    """
    Mengirim pesan teks ke WhatsApp customer via Gateway API
    """
    clean_phone = format_phone_number(phone)
    url = f"{WPP_HOST}/send-message"
    
    payload = {
        "phone": clean_phone,
        "message": message
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code in [200, 201]:
            print(f"✅ [WA Gateway] Pesan terkirim ke {clean_phone}")
            return {'success': True, 'data': response.json()}
        else:
            data = {}
            try:
                data = response.json()
            except Exception:
                pass
            err_msg = data.get('error') or response.text
            print(f"⚠️ [WA Gateway] Gagal kirim ({response.status_code}): {err_msg}")
            return {'success': False, 'error': err_msg}
    except requests.exceptions.RequestException as e:
        print(f"ℹ️ [WA Gateway Server Offline]: {e}")
        return {'success': False, 'error': 'Server gateway WhatsApp (port 3000) belum berjalan', 'offline': True}

def check_wpp_status():
    """
    Mengecek apakah WhatsApp Gateway aktif dan status session WA
    """
    url = f"{WPP_HOST}/status"
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                'online': True,
                'ready': data.get('ready', False),
                'status': data.get('status', 'unknown'),
                'bot_number': data.get('bot_number'),
                'bot_name': data.get('bot_name'),
                'has_qr': data.get('has_qr', False),
                'qr_image': data.get('qr_image'),
                'data': data
            }
        return {'online': False, 'status_code': response.status_code}
    except requests.exceptions.RequestException:
        return {'online': False, 'ready': False, 'reason': f'Gateway WhatsApp belum aktif di {WPP_HOST}'}
