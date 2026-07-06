const express = require('express');
const app = express();

// =====================================================
// INTERNAL GUDANG MAKANAN NASIONAL SERVICE
// Service ini HANYA bisa diakses dari jaringan internal
// =====================================================

// Case-insensitive routing (default Express behavior)
app.set('case sensitive routing', false);

// Middleware
app.use((req, res, next) => {
  res.setHeader('X-Internal-Service', 'gudang-warehouse-v1');
  res.setHeader('X-Network', 'internal-only');
  next();
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'Gudang Makanan Nasional - Internal API',
    version: '1.0.0',
    access: 'RESTRICTED - Internal Network Only',
    endpoints: ['/internal/status', '/internal/storage']
  });
});

// ---- Internal Endpoints ----

// Status endpoint
app.get('/internal/status', (req, res) => {
  res.json({
    service: 'Gudang Makanan Nasional - Internal Monitoring',
    status: 'OPERATIONAL',
    uptime: Math.floor(process.uptime()),
    region: 'ID-JKT',
    gudang: {
      total: 34,
      aktif: 31,
      maintenance: 3,
      kapasitas_total: '2.450.000 kg'
    },
    distribusi: {
      hari_ini: 15420,
      minggu_ini: 98750,
      bulan_ini: 412300
    },
    lastSync: new Date().toISOString(),
    alert: 'Gudang GDG-017 Makassar kapasitas hampir penuh (97%)'
  });
});

// Storage endpoint
app.get('/internal/storage', (req, res) => {
  res.json({
    storage: [
      { id: 'GDG-001', nama: 'Gudang Pusat Jakarta', kapasitas: '85%', items: 15000, suhu: '18°C', status: 'aktif' },
      { id: 'GDG-002', nama: 'Gudang Regional Surabaya', kapasitas: '72%', items: 12000, suhu: '19°C', status: 'aktif' },
      { id: 'GDG-003', nama: 'Gudang Regional Medan', kapasitas: '91%', items: 18000, suhu: '20°C', status: 'aktif' },
      { id: 'GDG-004', nama: 'Gudang Regional Makassar', kapasitas: '97%', items: 22000, suhu: '21°C', status: 'warning' },
      { id: 'GDG-005', nama: 'Gudang Regional Bandung', kapasitas: '79%', items: 11000, suhu: '17°C', status: 'aktif' },
      { id: 'GDG-006', nama: 'Gudang Regional Semarang', kapasitas: '65%', items: 8500, suhu: '19°C', status: 'aktif' },
      { id: 'GDG-007', nama: 'Gudang Regional Palembang', kapasitas: '58%', items: 7200, suhu: '22°C', status: 'aktif' },
      { id: 'GDG-008', nama: 'Gudang Regional Denpasar', kapasitas: '43%', items: 5100, suhu: '23°C', status: 'aktif' }
    ],
    totalItems: 98800,
    totalKapasitas: '2.450.000 kg',
    terpakai: '1.876.500 kg',
    lastUpdate: new Date().toISOString()
  });
});

// ========== FLAG ENDPOINT ==========
// Menerima /internal/flag, /internal/flag.png, /internal/flag.jpg, dll.
// Regex case-insensitive agar bisa diakses dengan variasi huruf besar/kecil
app.get(/^\/internal\/flag(\.[a-zA-Z0-9]+)?$/i, (req, res) => {
  res.json({
    '🚩': 'CAPTURED',
    message: '=== SELAMAT! Anda berhasil mengakses data rahasia gudang! ===',
    flag: 'flagtxt',
    severity: 'CRITICAL',
    description: 'Data sensitif gudang makanan nasional berhasil diakses dari luar jaringan.',
    recommendation: 'Segera perbaiki validasi URL pada endpoint validasi gambar. Implementasikan allowlist domain dan validasi DNS resolution.',
    accessed_at: new Date().toISOString()
  });
});

// Catch-all for other /internal routes
app.get('/internal/*', (req, res) => {
  res.status(404).json({
    error: 'Endpoint tidak ditemukan',
    path: req.path
  });
});

// Catch-all
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Not Found', path: req.originalUrl });
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`[INTERNAL] Gudang service running on port ${PORT}`);
  console.log(`[INTERNAL] Network: internal-only`);
});
