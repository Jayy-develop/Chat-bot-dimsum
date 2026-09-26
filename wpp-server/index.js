/**
 * whatsapp-web.js Gateway + HTTP API
 * Dimsum Mentai Oishi WhatsApp Bot
 *
 * Fitur:
 * 1. Tampilkan QR Code di terminal (qrcode-terminal)
 * 2. Tampilkan QR Code di browser: http://127.0.0.1:3000/qr
 * 3. Tampilkan QR Code & status real-time di Admin Dashboard: http://127.0.0.1:5000/admin
 * 4. Otomatis forward pesan customer ke Flask (http://127.0.0.1:5000/webhook)
 * 5. Otomatis balas pesan ke customer via WhatsApp
 * 6. Pembersihan lock Chromium otomatis agar lancar tanpa crash
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcodeTerminal = require('qrcode-terminal');
const QRCode = require('qrcode');
const axios = require('axios');
const http = require('http');
const fs = require('fs');
const path = require('path');

// ── KONFIGURASI ───────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3000;
const FLASK_WEBHOOK_URL = process.env.FLASK_WEBHOOK_URL || 'http://127.0.0.1:5000/webhook';
const AUTH_DIR = path.join(__dirname, '.wwebjs_auth', 'session-dimsum-bot');

// Bersihkan file lock lama jika ada
function cleanChromiumLocks(dir) {
  if (!fs.existsSync(dir)) return;
  try {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      if (file.toLowerCase().includes('singleton') || file.toLowerCase().includes('lock')) {
        const fullPath = path.join(dir, file);
        try {
          fs.unlinkSync(fullPath);
          console.log(`🧹 Membersihkan lock lama: ${file}`);
        } catch (_) {}
      }
    }
  } catch (_) {}
}

cleanChromiumLocks(AUTH_DIR);

// Cari browser yang terpasang (Google Chrome / Edge)
const chromePath = fs.existsSync('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
  ? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
  : (fs.existsSync('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe')
    ? 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
    : undefined);

// ── STATE GATEWAY ─────────────────────────────────────────────────────────────
let botState = {
  status: 'initializing', // initializing | qr_ready | authenticated | ready | disconnected
  qrCode: null,
  qrDataUrl: null,
  botNumber: null,
  botName: null,
  lastError: null
};

// ── BUAT CLIENT WHATSAPP ──────────────────────────────────────────────────────
const client = new Client({
  authStrategy: new LocalAuth({ clientId: 'dimsum-bot' }),
  qrMaxRetries: 0, // 0 = Tanpa batas (akan terus menunggu sampai user berhasil scan)
  puppeteer: {
    headless: true,
    executablePath: chromePath,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu'
    ]
  }
});

// ── EVENT: QR CODE MUNCUL ────────────────────────────────────────────────────
client.on('qr', async (qr) => {
  botState.status = 'qr_ready';
  botState.qrCode = qr;
  try {
    botState.qrDataUrl = await QRCode.toDataURL(qr, { width: 360, margin: 2 });
  } catch (err) {
    console.error('Error generate QR Data URL:', err.message);
  }

  console.log('\n');
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║        🍱  DIMSUM MENTAI OISHI - WHATSAPP BOT  🍱             ║');
  console.log('╚══════════════════════════════════════════════════════════════╝');
  console.log('\n   👉 SCAN QR CODE DI BAWAH INI DENGAN WHATSAPP:');
  console.log('   Buka WhatsApp di HP → ⋮ → Perangkat Tertaut → Tautkan Perangkat\n');

  qrcodeTerminal.generate(qr, { small: true });

  console.log('\n   💡 Atau buka QR di browser jika di terminal kurang jelas:');
  console.log(`      🔗 http://127.0.0.1:${PORT}/qr`);
  console.log(`      🔗 http://127.0.0.1:5000/admin (Dashboard Admin)`);
  console.log('\n   ⏳ Menunggu scan WhatsApp dari HP...');
  console.log('══════════════════════════════════════════════════════════════\n');
});

// ── EVENT: CLIENT SIAP ───────────────────────────────────────────────────────
client.on('ready', () => {
  const info = client.info;
  botState.status = 'ready';
  botState.qrCode = null;
  botState.qrDataUrl = null;
  botState.botNumber = info.wid ? info.wid.user : 'Unknown';
  botState.botName = info.pushname || 'Dimsum Mentai Oishi';

  console.log('\n' + '═'.repeat(60));
  console.log('✅ WHATSAPP BERHASIL TERHUBUNG!');
  console.log(`📱 Nomor Akun Bot : ${botState.botNumber}`);
  console.log(`👤 Nama WhatsApp  : ${botState.botName}`);
  console.log(`🌐 Dashboard Admin: http://127.0.0.1:5000/admin`);
  console.log(`🤖 Status         : Siap menerima dan membalas pesanan customer!`);
  console.log('═'.repeat(60) + '\n');
});

client.on('loading_screen', (percent, message) => {
  console.log(`⏳ Memuat WhatsApp Web: ${percent}% (${message})`);
});

client.on('authenticated', () => {
  botState.status = 'authenticated';
  console.log('🔐 Autentikasi berhasil! Menginisialisasi sesi...');
});

client.on('auth_failure', (msg) => {
  botState.status = 'auth_failure';
  botState.lastError = msg;
  console.error('❌ Autentikasi gagal:', msg);
});

client.on('disconnected', (reason) => {
  botState.status = 'disconnected';
  console.log('⚠️ WhatsApp terputus:', reason);
  console.log('   Menghubungkan ulang...');
  setTimeout(() => client.initialize(), 5000);
});

// ── EVENT: PESAN MASUK ──────────────────────────────────────────────────────
client.on('message', async (message) => {
  // Abaikan pesan dari grup, status, atau dari bot sendiri
  if (message.from.endsWith('@g.us') || message.from === 'status@broadcast' || message.fromMe) {
    return;
  }

  const from = message.from;
  const body = (message.body || '').trim();
  
  let senderName = 'Customer';
  try {
    const contact = await message.getContact();
    senderName = contact.pushname || contact.name || 'Customer';
  } catch (_) {}

  console.log(`\n📩 [${new Date().toLocaleTimeString('id-ID')}] Pesan masuk dari ${from} (${senderName}):`);
  console.log(`   "${body}"`);

  // Forward ke Flask
  try {
    const response = await axios.post(FLASK_WEBHOOK_URL, {
      event: 'onmessage',
      session: 'dimsum-session',
      data: {
        from: from,
        body: body,
        isGroupMsg: false,
        fromMe: false,
        sender: {
          pushname: senderName,
          id: from
        },
        notifyName: senderName
      }
    }, { timeout: 15000 });

    const botReply = response.data?.reply || '';
    if (botReply) {
      await client.sendMessage(from, botReply);
      console.log(`🤖 Balasan terkirim ke ${from}:`);
      console.log(`   ${botReply.split('\n')[0]}...`);
    }
  } catch (err) {
    console.error(`❌ Gagal forward ke Flask: ${err.message}`);
    try {
      await client.sendMessage(from,
        'Halo Kak! Maaf sistem kami sedang sinkronisasi sebentar 🙏\n' +
        'Silakan ketik *Halo* lagi ya kak.'
      );
    } catch (_) {}
  }
});

// ── HTTP API SERVER (PORT 3000) ──────────────────────────────────────────────
const server = http.createServer((req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // GET /status
  if (req.url === '/status' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      online: true,
      ready: botState.status === 'ready',
      status: botState.status,
      bot_number: botState.botNumber,
      bot_name: botState.botName,
      has_qr: !!botState.qrCode,
      qr_image: botState.qrDataUrl,
      last_error: botState.lastError
    }));
    return;
  }

  // GET /qr (Tampilan visual QR Code di Browser)
  if (req.url === '/qr' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(`
      <!DOCTYPE html>
      <html lang="id">
      <head>
        <title>Scan QR WhatsApp Bot - Dimsum Mentai Oishi</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #111b21; color: #e9edef; text-align: center; padding: 25px; margin: 0; }
          .card { background: #202c33; max-width: 440px; margin: 20px auto; padding: 24px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
          .qr-box { background: #fff; padding: 16px; border-radius: 14px; display: inline-block; margin: 15px 0; }
          .qr-box img { display: block; width: 280px; height: 280px; border-radius: 6px; }
          .title { font-size: 1.3rem; font-weight: bold; margin-bottom: 6px; color: #ff7a00; }
          .steps { text-align: left; background: #111b21; padding: 12px 16px; border-radius: 10px; font-size: 0.85rem; color: #8696a0; margin-top: 15px; }
          .steps ol { margin: 6px 0 0 18px; padding: 0; }
          .steps li { margin-bottom: 4px; }
          .badge { display: inline-block; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; margin-bottom: 12px; }
          .badge-wait { background: #ffaa0022; color: #ffaa00; border: 1px solid #ffaa0055; }
          .badge-ok { background: #25d36622; color: #25d366; border: 1px solid #25d36655; }
        </style>
      </head>
      <body>
        <div class="card">
          <div class="title">🍱 WhatsApp Bot Dimsum Mentai</div>
          <div id="statusBadge" class="badge badge-wait">⏳ Menunggu Scan WhatsApp...</div>
          
          <div class="qr-box">
            <img id="qrImg" src="${botState.qrDataUrl || ''}" alt="QR Code WhatsApp">
          </div>

          <div class="steps">
            <b style="color:#25d366;">📱 Langkah di HP kamu:</b>
            <ol>
              <li>Buka WhatsApp &rarr; Titik tiga (<b>⋮</b>) di pojok kanan</li>
              <li>Pilih <b>Perangkat Tertaut</b> &rarr; <b>Tautkan Perangkat</b></li>
              <li>Arahkan kamera ke QR Code di atas</li>
            </ol>
          </div>
          <p style="font-size: 12px; color: #8696a0; margin-top: 12px;">Halaman ini tidak perlu di-refresh manual. Status otomatis update.</p>
        </div>

        <script>
          async function checkStatus() {
            try {
              const res = await fetch('/status');
              const data = await res.json();
              if (data.ready) {
                document.getElementById('statusBadge').className = 'badge badge-ok';
                document.getElementById('statusBadge').innerText = '✅ Terhubung: +' + data.bot_number;
                document.querySelector('.card').innerHTML = '<h2 style="color:#25d366;">✅ WhatsApp Berhasil Terhubung!</h2><p>Nomor Bot: <b>+' + data.bot_number + '</b> (' + data.bot_name + ')</p><p><a href="http://127.0.0.1:5000/admin" style="color:#ff7a00;text-decoration:none;font-weight:bold;">&larr; Buka Admin Dashboard</a></p>';
              } else if (data.qr_image) {
                const img = document.getElementById('qrImg');
                if (img.src !== data.qr_image) {
                  img.src = data.qr_image;
                }
              }
            } catch (_) {}
          }
          setInterval(checkStatus, 2000);
        </script>
      </body>
      </html>
    `);
    return;
  }

  // POST /send-message (Kirim pesan keluar dari Admin/Sistem)
  if (req.url === '/send-message' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', async () => {
      try {
        const data = JSON.parse(body || '{}');
        const phone = data.phone;
        const msg = data.message;

        if (!phone || !msg) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'Parameter phone dan message wajib diisi' }));
          return;
        }

        if (botState.status !== 'ready') {
          res.writeHead(503, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'WhatsApp bot belum terhubung / belum scan QR' }));
          return;
        }

        let clean = phone.replace(/[^0-9]/g, '');
        if (clean.startsWith('08')) clean = '628' + clean.slice(2);
        else if (clean.startsWith('8')) clean = '62' + clean;
        const chatId = clean + '@c.us';

        await client.sendMessage(chatId, msg);
        console.log(`📤 [Admin API] Pesan berhasil dikirim ke ${chatId}`);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, message: `Pesan terkirim ke ${clean}` }));
      } catch (err) {
        console.error('Error send-message:', err.message);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: err.message }));
      }
    });
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Endpoint not found' }));
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🌐 HTTP Gateway API aktif di: http://127.0.0.1:${PORT}`);
});

// ── MULAI INITIALIZE CLIENT ──────────────────────────────────────────────────
console.log('\n══════════════════════════════════════════════════════════════');
console.log('   🍱  Dimsum Mentai Oishi - WhatsApp Bot Gateway');
console.log('══════════════════════════════════════════════════════════════');
console.log('   Memulai WhatsApp Web dengan Google Chrome...');
console.log('   Menunggu QR code (~5-15 detik)...\n');

client.initialize();
