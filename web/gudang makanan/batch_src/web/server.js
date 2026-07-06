const express = require('express');
const fetch = require('node-fetch');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// =====================================================
// GUDANG MAKANAN NASIONAL - Web Validation Service
// Version 2.3.1
// =====================================================

// Global response headers
app.use((req, res, next) => {
  res.setHeader('X-Powered-By', 'GudangMakanan/2.3');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  next();
});

// robots.txt
app.get('/robots.txt', (req, res) => {
  res.type('text/plain').send(
`User-agent: *
Disallow: /api/
`
  );
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'gudang-makanan-web',
    version: '2.3.1',
    uptime: Math.floor(process.uptime()),
    environment: process.env.NODE_ENV || 'development'
  });
});

// API info/documentation
app.get('/api/info', (req, res) => {
  res.json({
    name: 'Gudang Makanan Nasional API',
    version: '2.3.1',
    endpoints: {
      'POST /api/check-image': 'Validasi gambar menu dari URL eksternal',
      'GET /api/health': 'Health check service',
      'GET /api/stats': 'Statistik dashboard'
    },
    notes: 'Sistem validasi gambar menu supplier untuk standar gizi nasional'
  });
});

// Dashboard stats endpoint (data dummy)
app.get('/api/stats', (req, res) => {
  res.json({
    menu_aktif: 156,
    gudang_total: 34,
    distribusi_hari_ini: 15420,
    supplier_aktif: 89,
    makanan_terdistribusi_bulan: '412.300 porsi',
    kalori_rata_rata: '2.150 kkal',
    wilayah_terlayani: 514,
    updated_at: new Date().toISOString()
  });
});

// =====================================================
// ENDPOINT UTAMA - Validasi Gambar Menu
// =====================================================
app.post('/api/check-image', async (req, res) => {
  const { url } = req.body;

  if (!url || typeof url !== 'string') {
    return res.status(400).json({
      success: false,
      error: 'URL gambar diperlukan. Masukkan URL yang valid.'
    });
  }

  if (url.length > 2048) {
    return res.status(400).json({
      success: false,
      error: 'URL terlalu panjang (maksimal 2048 karakter)'
    });
  }

  try {
    // ===== LAYER 1: Parse URL =====
    let parsed;
    try {
      parsed = new URL(url);
    } catch {
      return res.status(400).json({
        success: false,
        error: 'Format URL tidak valid. Gunakan format: https://domain.com/gambar.png'
      });
    }

    // ===== LAYER 2: Protocol Check =====
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return res.status(400).json({
        success: false,
        error: 'Hanya protokol HTTP dan HTTPS yang diizinkan'
      });
    }

    // ===== LAYER 3: Hostname Blacklist =====
    const hostname = parsed.hostname.toLowerCase();
    const blockedHosts = [
      'localhost',
      '127.0.0.1',
      '0.0.0.0',
      '::1',
      '[::1]',
      '0177.0.0.1',
      '0x7f000001',
      '0x7f.0x0.0x0.0x1',
      '2130706433',
      '017700000001',
      '0177.0.0.01',
      '127.0.0.0',
      '127.255.255.255',
      'metadata.google.internal',
      '169.254.169.254'
    ];

    if (blockedHosts.some(h => hostname === h)) {
      return res.status(403).json({
        success: false,
        error: 'Akses ke alamat tersebut tidak diizinkan oleh kebijakan keamanan'
      });
    }

    // ===== LAYER 4: Private IP Range Check =====
    const privateIPRegex = /^(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|fc00:|fd[0-9a-f]{2}:)$/i;
    if (privateIPRegex.test(hostname)) {
      return res.status(403).json({
        success: false,
        error: 'Akses ke jaringan privat tidak diizinkan'
      });
    }

    // ===== LAYER 5: Path Keyword Blocking =====
    const urlPath = decodeURIComponent(parsed.pathname);
    const blockedKeywords = ['internal', 'admin', 'flag', 'secret', 'private', '.env', 'config', 'etc/passwd', 'proc/self'];

    if (blockedKeywords.some(keyword => urlPath.includes(keyword))) {
      return res.status(403).json({
        success: false,
        error: 'Path URL mengandung kata kunci yang tidak diizinkan'
      });
    }

    // ===== LAYER 6: Image Extension Check =====
    const pathLower = parsed.pathname.toLowerCase();
    const validExts = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico'];

    if (!validExts.some(ext => pathLower.endsWith(ext))) {
      return res.status(400).json({
        success: false,
        error: 'URL harus mengarah ke file gambar yang valid (.png, .jpg, .jpeg, .gif, .webp, .svg)'
      });
    }

    // ===== FETCH URL =====
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'GudangMakanan-ImageValidator/2.3',
        'Accept': 'image/*,*/*'
      },
      redirect: 'follow',
      follow: 5
    });

    clearTimeout(timeout);

    const contentType = response.headers.get('content-type') || 'unknown';
    const buffer = await response.buffer();
    const sizeBytes = buffer.length;
    const base64Data = buffer.toString('base64');

    // Kirim response ke client
    res.json({
      success: true,
      data: {
        status: response.status,
        statusText: response.statusText,
        contentType: contentType,
        size: sizeBytes,
        sizeFormatted: formatBytes(sizeBytes),
        preview: `data:${contentType};base64,${base64Data}`,
        metadata: {
          url: url,
          fetchedAt: new Date().toISOString(),
          server: response.headers.get('server') || 'unknown',
          headers: {
            'content-type': contentType,
            'content-length': response.headers.get('content-length'),
            'x-internal-service': response.headers.get('x-internal-service') || null
          }
        }
      }
    });

  } catch (err) {
    if (err.name === 'AbortError') {
      return res.status(408).json({
        success: false,
        error: 'Request timeout - server terlalu lama merespon (maks 5 detik)'
      });
    }

    // Error handling
    const errorMap = {
      'ENOTFOUND': 'Hostname tidak dapat ditemukan',
      'ECONNREFUSED': 'Koneksi ditolak oleh server tujuan',
      'ECONNRESET': 'Koneksi direset oleh server tujuan',
      'ETIMEDOUT': 'Koneksi timeout',
      'CERT_HAS_EXPIRED': 'Sertifikat SSL target sudah expired'
    };

    const message = errorMap[err.code] || 'Gagal mengambil gambar dari URL yang diberikan';

    return res.status(500).json({
      success: false,
      error: message
    });
  }
});

// Utility function
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Catch-all: serve index.html for SPA
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`[WEB] Gudang Makanan Nasional - Web Service`);
  console.log(`[WEB] Running on port ${PORT}`);
  console.log(`[WEB] Environment: ${process.env.NODE_ENV || 'development'}`);
});
