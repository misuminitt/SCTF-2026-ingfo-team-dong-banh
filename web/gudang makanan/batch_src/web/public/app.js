// =====================================================
// GUDANG MAKANAN NASIONAL - Frontend Application
// Version 2.3.1
// =====================================================

(function () {
  'use strict';

  // ---- DOM Elements ----
  const sidebar = document.getElementById('sidebar');
  const menuToggle = document.getElementById('menu-toggle');
  const navItems = document.querySelectorAll('.nav-item');
  const pages = document.querySelectorAll('.page');
  const pageTitle = document.getElementById('page-title');
  const pageSubtitle = document.getElementById('page-subtitle');

  const checkForm = document.getElementById('check-form');
  const imageUrlInput = document.getElementById('image-url');
  const btnValidate = document.getElementById('btn-validate');
  const resultPanel = document.getElementById('result-panel');
  const errorPanel = document.getElementById('error-panel');
  const resultContent = document.getElementById('result-content');
  const errorContent = document.getElementById('error-content');

  // ---- Page Config ----
  const pageConfig = {
    dashboard: {
      title: 'Dashboard',
      subtitle: 'Monitoring Distribusi Makanan Bergizi Nasional'
    },
    'check-image': {
      title: 'Cek Gambar Menu',
      subtitle: 'Validasi Gambar Makanan dari Supplier'
    },
    stok: {
      title: 'Stok Makanan',
      subtitle: 'Monitoring Stok per Gudang Regional'
    },
    statistik: {
      title: 'Statistik',
      subtitle: 'Data Distribusi dan Nutrisi Nasional'
    },
    gudang: {
      title: 'Data Gudang',
      subtitle: 'Informasi Gudang Regional Seluruh Indonesia'
    },
  };

  // ---- Sidebar Navigation ----
  function navigateTo(pageName) {
    // Update nav active state
    navItems.forEach(item => item.classList.remove('active'));
    const activeNav = document.querySelector(`[data-page="${pageName}"]`);
    if (activeNav) activeNav.classList.add('active');

    // Show page
    pages.forEach(page => page.classList.remove('active'));
    const activePage = document.getElementById(`page-${pageName}`);
    if (activePage) {
      activePage.classList.remove('active');
      // Force reflow for animation
      void activePage.offsetWidth;
      activePage.classList.add('active');
    }

    // Update header
    const config = pageConfig[pageName];
    if (config) {
      pageTitle.textContent = config.title;
      pageSubtitle.textContent = config.subtitle;
    }

    // Close sidebar on mobile
    sidebar.classList.remove('open');
  }

  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const page = item.getAttribute('data-page');
      if (page) navigateTo(page);
    });
  });

  // Mobile menu toggle
  if (menuToggle) {
    menuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }

  // Close sidebar on outside click (mobile)
  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 1024 &&
      sidebar.classList.contains('open') &&
      !sidebar.contains(e.target) &&
      e.target !== menuToggle) {
      sidebar.classList.remove('open');
    }
  });

  // ---- Animated Counters ----
  function animateCounters() {
    const counters = document.querySelectorAll('.stat-value[data-count]');
    counters.forEach(counter => {
      const target = parseInt(counter.getAttribute('data-count'));
      const duration = 1500;
      const start = performance.now();

      function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 4); // easeOutQuart
        const current = Math.floor(eased * target);
        counter.textContent = current.toLocaleString('id-ID');

        if (progress < 1) {
          requestAnimationFrame(update);
        }
      }

      requestAnimationFrame(update);
    });
  }

  // ---- Check Image Form ----
  if (checkForm) {
    checkForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const url = imageUrlInput.value.trim();
      if (!url) {
        showError('Masukkan URL gambar yang ingin divalidasi.');
        return;
      }

      // UI: Loading state
      setLoading(true);
      hideResults();

      try {
        const response = await fetch('/api/check-image', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
          showError(data.error || 'Terjadi kesalahan saat memvalidasi URL.');
          return;
        }

        showResult(data.data);
      } catch (err) {
        showError('Gagal menghubungi server. Pastikan koneksi internet Anda aktif.');
      } finally {
        setLoading(false);
      }
    });
  }

  function setLoading(loading) {
    if (!btnValidate) return;
    const btnText = btnValidate.querySelector('.btn-text');
    const btnIcon = btnValidate.querySelector('.btn-icon');
    const btnLoading = btnValidate.querySelector('.btn-loading');

    if (loading) {
      btnValidate.disabled = true;
      if (btnText) btnText.style.display = 'none';
      if (btnIcon) btnIcon.style.display = 'none';
      if (btnLoading) btnLoading.style.display = 'inline-flex';
    } else {
      btnValidate.disabled = false;
      if (btnText) btnText.style.display = 'inline';
      if (btnIcon) btnIcon.style.display = 'inline';
      if (btnLoading) btnLoading.style.display = 'none';
    }
  }

  function hideResults() {
    if (resultPanel) resultPanel.style.display = 'none';
    if (errorPanel) errorPanel.style.display = 'none';
  }

  function showError(message) {
    if (errorPanel) errorPanel.style.display = 'block';
    if (resultPanel) resultPanel.style.display = 'none';
    if (errorContent) {
      errorContent.innerHTML = `
        <div class="error-message">
          <span class="error-icon">❌</span>
          <span class="error-text">${escapeHtml(message)}</span>
        </div>
      `;
    }
  }

  function showResult(data) {
    if (resultPanel) resultPanel.style.display = 'block';
    if (errorPanel) errorPanel.style.display = 'none';

    if (!resultContent) return;

    const isImage = data.contentType && data.contentType.startsWith('image/');
    const isJSON = data.contentType && data.contentType.includes('application/json');

    // Check if the response contains a flag
    let rawText = '';
    let hasFlag = false;

    if (!isImage) {
      try {
        rawText = atob(data.preview.split(',')[1]);
        if (rawText.includes('SCTF26{')) {
          hasFlag = true;
        }
      } catch {
        rawText = '[Binary data - unable to decode]';
      }
    }

    let html = '';

    // Flag celebration
    if (hasFlag) {
      try {
        const flagData = JSON.parse(rawText);
        html += `
          <div class="flag-found">
            <h3>🚩 FLAG CAPTURED! 🚩</h3>
            <p style="margin-bottom: 1rem; color: var(--text-secondary); font-size: 0.85rem;">
              ${escapeHtml(flagData.message || 'Flag ditemukan!')}
            </p>
            <div class="flag-value">${escapeHtml(flagData.flag || '')}</div>
          </div>
        `;
      } catch {
        html += `<div class="flag-found"><h3>🚩 FLAG FOUND!</h3></div>`;
      }
    }

    // Image preview
    if (isImage) {
      html += `
        <div class="result-preview">
          <img src="${data.preview}" alt="Menu preview" loading="lazy">
        </div>
      `;
    }

    // Metadata
    html += `
      <div class="result-meta">
        <div class="meta-item">
          <span class="meta-label">Status</span>
          <span class="meta-value">${data.status} ${escapeHtml(data.statusText || '')}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Content-Type</span>
          <span class="meta-value">${escapeHtml(data.contentType)}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Ukuran</span>
          <span class="meta-value">${escapeHtml(data.sizeFormatted)}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Waktu Fetch</span>
          <span class="meta-value">${new Date(data.metadata.fetchedAt).toLocaleString('id-ID')}</span>
        </div>
      </div>
    `;

    // Raw response (non-image)
    if (!isImage && rawText) {
      html += `
        <div style="margin-top: 1rem;">
          <span class="meta-label">Raw Response</span>
          <div class="result-raw">${escapeHtml(rawText)}</div>
        </div>
      `;
    }

    resultContent.innerHTML = html;
  }

  // Close buttons
  const btnCloseResult = document.getElementById('btn-close-result');
  const btnCloseError = document.getElementById('btn-close-error');

  if (btnCloseResult) {
    btnCloseResult.addEventListener('click', () => {
      if (resultPanel) resultPanel.style.display = 'none';
    });
  }

  if (btnCloseError) {
    btnCloseError.addEventListener('click', () => {
      if (errorPanel) errorPanel.style.display = 'none';
    });
  }



  // ---- Test URL Buttons (Dashboard) ----
  const testUrlBtns = document.querySelectorAll('.test-url-btn');
  testUrlBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const urlToTest = btn.getAttribute('data-url');
      if (urlToTest) {
        // Pindah ke halaman cek gambar
        navigateTo('check-image');
        
        // Isi form dan submit
        if (imageUrlInput && checkForm) {
          imageUrlInput.value = urlToTest;
          // Trigger event submit pada form
          checkForm.dispatchEvent(new Event('submit'));
        }
      }
    });
  });

  // ---- Utilities ----
  function escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
  }

  // ---- Initialize ----
  document.addEventListener('DOMContentLoaded', () => {
    animateCounters();
  });

  // Run counters immediately if DOM is already ready
  if (document.readyState !== 'loading') {
    animateCounters();
  }

})();
