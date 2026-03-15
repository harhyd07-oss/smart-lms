// main.js
// Client-side interactivity for Smart LMS
// Runs in the browser after every page loads

document.addEventListener('DOMContentLoaded', function () {
    // ── Restore scroll position after download redirect ──
    const scrollPos = sessionStorage.getItem('scrollPos');
    if (scrollPos) {
        window.scrollTo(0, parseInt(scrollPos));
        sessionStorage.removeItem('scrollPos');
    }
   // ── THEME TOGGLE ──
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon   = document.getElementById('theme-icon');

    // Load saved theme — update icon only (html class already
    // applied in <head> before page painted — no flash)
    const savedTheme = localStorage.getItem('lms-theme');
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        if (themeIcon) themeIcon.textContent = '🌙';
    } else {
        document.documentElement.classList.remove('dark-mode');
        if (themeIcon) themeIcon.textContent = '☀️';
    }

    // Toggle on button click
    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            document.documentElement.classList.toggle('dark-mode');

            if (document.documentElement.classList.contains('dark-mode')) {
                localStorage.setItem('lms-theme', 'dark');
                if (themeIcon) themeIcon.textContent = '🌙';
            } else {
                localStorage.setItem('lms-theme', 'light');
                if (themeIcon) themeIcon.textContent = '☀️';
            }
        });
    }

    // ── 1. Auto-dismiss alerts after 4 seconds ──
    // Flash messages disappear automatically
    // so the user doesn't have to manually close them
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            // Bootstrap's fade out
            alert.classList.remove('show');
            alert.classList.add('fade');
            setTimeout(function () {
                alert.remove();
            }, 300);
        }, 4000);
    });


    // ── 2. Highlight active sidebar link ──
    // Compares current URL to each nav link
    // and adds active-link class automatically
    const currentPath = window.location.pathname;
    const navLinks    = document.querySelectorAll('.sidebar .nav-link');

    navLinks.forEach(function (link) {
        // Remove any existing active state first
        link.classList.remove('active-link');
        link.style.color = '';

        const linkPath = link.getAttribute('href');

        if (linkPath && currentPath === linkPath) {
            link.classList.add('active-link');
        }

        // Special case: mark library as active for similar page too
        if (linkPath === '/library' && currentPath.includes('/similar')) {
            link.classList.add('active-link');
        }
    });


    // ── 3. Animate progress bars on page load ──
    // Progress bars start at 0 and animate to their value
    // giving a smooth visual effect when the page loads
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function (bar) {
        const targetWidth = bar.style.width;
        bar.style.width   = '0%';

        setTimeout(function () {
            bar.style.transition = 'width 0.8s ease';
            bar.style.width      = targetWidth;
        }, 300);
    });


    // ── 4. Search bar keyboard shortcut ──
    // Press '/' anywhere on the page to focus the search bar
    // Same shortcut used by GitHub, Notion, Linear
    document.addEventListener('keydown', function (e) {
        const searchInput = document.getElementById('dashboard-search')
                         || document.querySelector('input[name="search"]');

        // '/' key and not already typing in an input
        if (e.key === '/' &&
            document.activeElement.tagName !== 'INPUT' &&
            document.activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }

        // Escape key to blur search
        if (e.key === 'Escape') {
            if (searchInput) {
                searchInput.blur();
            }
        }
    });


    // ── 5. Add loading state to buttons on form submit ──
    // When a form is submitted, the submit button shows
    // "Loading..." so the user knows something is happening
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled    = true;
                submitBtn.innerHTML   = '⏳ Loading...';
            }
        });
    });


    // ── 6. Smooth scroll to top on logo click ──
    const brand = document.querySelector('.navbar-brand');
    if (brand) {
        brand.style.cursor = 'pointer';
    }


    // ── 7. Card click ripple effect ──
    // Adds a subtle visual feedback when cards are clicked
    const cards = document.querySelectorAll('.card');
    cards.forEach(function (card) {
        card.addEventListener('click', function (e) {
            // Only trigger if not clicking a button or link
            if (e.target.tagName === 'A' ||
                e.target.tagName === 'BUTTON' ||
                e.target.closest('a') ||
                e.target.closest('button')) {
                return;
            }
            card.style.transform = 'scale(0.99)';
            setTimeout(function () {
                card.style.transform = '';
            }, 100);
        });
    });


    // ── 8. Show character count on description textarea ──
    const textarea = document.querySelector('textarea[name="description"]');
    if (textarea) {
        const counter    = document.createElement('small');
        counter.className = 'text-muted';
        counter.textContent = '0 / 200 characters';
        textarea.parentNode.appendChild(counter);

        textarea.addEventListener('input', function () {
            const len            = textarea.value.length;
            counter.textContent  = len + ' / 200 characters';
            counter.style.color  = len > 180 ? '#dc2626' : '#64748b';
        });
    }


    console.log('Smart LMS loaded ✅');
});
// ── Handle resource download without page jump ──
function handleDownload(resourceId, btn) {
    const originalText = btn.innerHTML;

    btn.disabled  = true;
    btn.innerHTML = '⏳ Downloading...';

    fetch('/download/' + resourceId)
        .then(response => {
            if (response.ok) {
                const contentType = response.headers.get('content-type');

                if (contentType && contentType.includes('application/json')) {
                    // No real file — do NOT update count
                    return response.json().then(data => {
                        if (data.no_file) {
                            showToast('⚠️ ' + data.title + ' has no file attached.');
                        }
                    });
                } else {
                    // Real file exists — update count AND trigger download
                    return response.blob().then(blob => {
                        const disposition = response.headers.get('content-disposition');
                        let filename = 'download';
                        if (disposition) {
                            const match = disposition.match(/filename="?([^"]+)"?/);
                            if (match) filename = match[1];
                        }

                        // Trigger browser download
                        const url  = window.URL.createObjectURL(blob);
                        const a    = document.createElement('a');
                        a.href     = url;
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        a.remove();

                        // Update ONLY the count span closest to the button
                        // This fixes the double count issue
                        const card    = btn.closest('.card');
                        const countEl = card
                            ? card.querySelector('[id^="downloads-"]')
                            : document.getElementById('downloads-' + resourceId);

                        if (countEl) {
                            countEl.textContent = parseInt(countEl.textContent) + 1;
                        }

                        showToast('✅ Download started!');
                    });
                }
            }
        })
        .catch(error => {
            console.error('Download error:', error);
            showToast('❌ Download failed. Please try again.');
        })
        .finally(() => {
            btn.disabled  = false;
            btn.innerHTML = originalText;
        });
}

// ── Simple toast notification ──
function showToast(message) {
    const existing = document.getElementById('lms-toast');
    if (existing) existing.remove();

    const toast       = document.createElement('div');
    toast.id          = 'lms-toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: #1e293b;
        color: #fff;
        padding: 12px 20px;
        border-radius: 10px;
        font-size: 14px;
        font-weight: 500;
        z-index: 9999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: opacity 0.3s ease;
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}