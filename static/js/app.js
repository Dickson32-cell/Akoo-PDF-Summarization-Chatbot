/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║     AKOO AI - Main Application JavaScript                                   ║
 * ║     Created by: Abdul Rashid Dickson                                        ║
 * ║     © 2025 All Rights Reserved                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

(function () {
    'use strict';

    // ========================================================================
    // Global State
    // ========================================================================

    window.AKOO = {
        creator: 'Abdul Rashid Dickson',
        version: '2.0.0',
        initialized: false
    };

    // ========================================================================
    // Theme Management
    // ========================================================================

    const ThemeManager = {
        currentTheme: 'dark',

        init() {
            const savedTheme = localStorage.getItem('akoo-theme') || 'dark';
            this.setTheme(savedTheme);
            this.bindEvents();
        },

        setTheme(theme) {
            this.currentTheme = theme;
            document.documentElement.setAttribute('data-theme', theme);
            document.body.classList.remove('light-theme', 'dark-theme');
            document.body.classList.add(`${theme}-theme`);
            localStorage.setItem('akoo-theme', theme);

            // Update theme toggle icon
            const themeToggle = document.getElementById('theme-toggle');
            if (themeToggle) {
                const icon = themeToggle.querySelector('i');
                if (icon) {
                    icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
                }
            }
        },

        toggle() {
            const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
            this.setTheme(newTheme);
        },

        bindEvents() {
            const themeToggle = document.getElementById('theme-toggle');
            if (themeToggle) {
                themeToggle.addEventListener('click', () => this.toggle());
            }
        }
    };

    // ========================================================================
    // Particle Background
    // ========================================================================

    const ParticleBackground = {
        canvas: null,
        ctx: null,
        particles: [],
        animationId: null,

        init() {
            const container = document.getElementById('particles');
            if (!container) return;

            this.canvas = document.createElement('canvas');
            this.canvas.style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;';
            container.appendChild(this.canvas);

            this.ctx = this.canvas.getContext('2d');
            this.resize();
            this.createParticles();
            this.animate();

            window.addEventListener('resize', () => this.resize());
        },

        resize() {
            if (!this.canvas) return;
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        },

        createParticles() {
            this.particles = [];
            const count = Math.floor((window.innerWidth * window.innerHeight) / 15000);

            for (let i = 0; i < count; i++) {
                this.particles.push({
                    x: Math.random() * this.canvas.width,
                    y: Math.random() * this.canvas.height,
                    size: Math.random() * 2 + 1,
                    speedX: (Math.random() - 0.5) * 0.5,
                    speedY: (Math.random() - 0.5) * 0.5,
                    opacity: Math.random() * 0.5 + 0.2
                });
            }
        },

        animate() {
            if (!this.ctx) return;

            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

            this.particles.forEach(particle => {
                // Update position
                particle.x += particle.speedX;
                particle.y += particle.speedY;

                // Wrap around edges
                if (particle.x < 0) particle.x = this.canvas.width;
                if (particle.x > this.canvas.width) particle.x = 0;
                if (particle.y < 0) particle.y = this.canvas.height;
                if (particle.y > this.canvas.height) particle.y = 0;

                // Draw particle
                this.ctx.beginPath();
                this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                this.ctx.fillStyle = `rgba(102, 126, 234, ${particle.opacity})`;
                this.ctx.fill();
            });

            this.animationId = requestAnimationFrame(() => this.animate());
        },

        destroy() {
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
            }
        }
    };

    // ========================================================================
    // Modal Management
    // ========================================================================

    const ModalManager = {
        modals: {},

        init() {
            // Find all modals
            document.querySelectorAll('.modal').forEach(modal => {
                this.modals[modal.id] = modal;
            });

            // Bind close events
            document.querySelectorAll('.modal-close, .modal-backdrop').forEach(el => {
                el.addEventListener('click', (e) => {
                    const modal = e.target.closest('.modal');
                    if (modal) this.close(modal.id);
                });
            });

            // ESC key to close
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    Object.keys(this.modals).forEach(id => this.close(id));
                }
            });
        },

        open(modalId) {
            const modal = this.modals[modalId];
            if (modal) {
                modal.classList.add('active');
                modal.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }
        },

        close(modalId) {
            const modal = this.modals[modalId];
            if (modal) {
                modal.classList.remove('active');
                modal.style.display = 'none';
                document.body.style.overflow = '';
            }
        }
    };

    // ========================================================================
    // Smooth Scroll
    // ========================================================================

    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // ========================================================================
    // Animation on Scroll
    // ========================================================================

    function initScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        document.querySelectorAll('.feature-card, .step-item, .section-header').forEach(el => {
            el.classList.add('animate-on-scroll');
            observer.observe(el);
        });
    }

    // ========================================================================
    // Upload Zone Handling
    // ========================================================================

    function initUploadZone() {
        const uploadZone = document.getElementById('upload-zone');
        const fileInput = document.getElementById('file-input');
        const uploadHeroBtn = document.getElementById('upload-hero-btn');

        if (!uploadZone || !fileInput) return;

        // Open modal on hero button click
        if (uploadHeroBtn) {
            uploadHeroBtn.addEventListener('click', () => {
                ModalManager.open('upload-modal');
            });
        }

        // Close modal button
        const closeBtn = document.getElementById('close-upload-modal');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                ModalManager.close('upload-modal');
            });
        }

        // Click to upload
        uploadZone.addEventListener('click', () => {
            fileInput.click();
        });

        // Drag and drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }

    function handleFileUpload(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showNotification('Please upload a PDF file', 'error');
            return;
        }

        const uploadZone = document.getElementById('upload-zone');
        const uploadProgress = document.getElementById('upload-progress');

        if (uploadZone) uploadZone.style.display = 'none';
        if (uploadProgress) uploadProgress.style.display = 'flex';

        const formData = new FormData();
        formData.append('file', file);

        // Get summary settings
        const summaryLength = document.getElementById('summary-length');
        const summaryFormat = document.getElementById('summary-format');
        const summaryType = document.getElementById('summary-type');

        if (summaryLength) formData.append('summary_length', summaryLength.value);
        if (summaryFormat) formData.append('summary_format', summaryFormat.value);
        if (summaryType) formData.append('summary_type', summaryType.value);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showNotification(data.error, 'error');
                    resetUploadModal();
                } else if (data.job_id) {
                    // Poll for job completion
                    pollJobStatus(data.job_id);
                } else if (data.summary) {
                    // Direct result
                    showNotification('Summary generated successfully!', 'success');
                    window.location.href = '/chat?summary=' + encodeURIComponent(data.summary);
                }
            })
            .catch(error => {
                console.error('Upload error:', error);
                showNotification('Upload failed. Please try again.', 'error');
                resetUploadModal();
            });
    }

    function pollJobStatus(jobId) {
        const progressCircle = document.getElementById('progress-circle');
        const progressText = document.getElementById('progress-text');
        const progressStatus = document.getElementById('progress-status');

        const poll = () => {
            fetch(`/status/${jobId}`)
                .then(response => response.json())
                .then(data => {
                    // Update progress
                    if (progressText) progressText.textContent = `${data.progress}%`;
                    if (progressStatus) progressStatus.textContent = data.message;
                    if (progressCircle) {
                        const offset = 283 - (283 * data.progress / 100);
                        progressCircle.style.strokeDashoffset = offset;
                    }

                    if (data.status === 'completed') {
                        showNotification('Summary generated successfully!', 'success');
                        ModalManager.close('upload-modal');
                        resetUploadModal();

                        // Redirect to chat with summary
                        if (data.result && data.result.summary) {
                            sessionStorage.setItem('akoo-summary', data.result.summary);
                            window.location.href = '/chat';
                        }
                    } else if (data.status === 'error') {
                        showNotification(data.message || 'Processing failed', 'error');
                        resetUploadModal();
                    } else {
                        // Continue polling
                        setTimeout(poll, 1000);
                    }
                })
                .catch(error => {
                    console.error('Status check error:', error);
                    setTimeout(poll, 2000);
                });
        };

        poll();
    }

    function resetUploadModal() {
        const uploadZone = document.getElementById('upload-zone');
        const uploadProgress = document.getElementById('upload-progress');

        if (uploadZone) uploadZone.style.display = 'flex';
        if (uploadProgress) uploadProgress.style.display = 'none';

        // Reset progress
        const progressCircle = document.getElementById('progress-circle');
        const progressText = document.getElementById('progress-text');

        if (progressCircle) progressCircle.style.strokeDashoffset = 283;
        if (progressText) progressText.textContent = '0%';
    }

    // ========================================================================
    // Notifications
    // ========================================================================

    function showNotification(message, type = 'info') {
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            max-width: 400px;
            padding: 16px 20px;
            background: rgba(18, 18, 26, 0.95);
            border-left: 4px solid ${colors[type]};
            border-radius: 8px;
            color: white;
            font-size: 14px;
            z-index: 10000;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            animation: notificationSlideIn 0.3s ease;
            display: flex;
            align-items: center;
            gap: 12px;
        `;

        notification.innerHTML = `
            <span style="font-size: 18px; color: ${colors[type]};">${icons[type]}</span>
            <span>${message}</span>
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'notificationSlideOut 0.3s ease forwards';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    // Add notification animations
    const notificationStyles = document.createElement('style');
    notificationStyles.textContent = `
        @keyframes notificationSlideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes notificationSlideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        .animate-on-scroll {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease;
        }
        .animate-on-scroll.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
    `;
    document.head.appendChild(notificationStyles);

    // Expose globally
    window.showNotification = showNotification;

    // ========================================================================
    // Initialization
    // ========================================================================

    function init() {
        if (window.AKOO.initialized) return;

        ThemeManager.init();
        ParticleBackground.init();
        ModalManager.init();
        initSmoothScroll();
        initScrollAnimations();
        initUploadZone();

        window.AKOO.initialized = true;

        console.log('%c AKOO AI Application Initialized ', 'background: #667eea; color: white; padding: 5px 10px; border-radius: 5px;');
        console.log('%c Created by: Abdul Rashid Dickson ', 'color: #667eea; font-weight: bold;');
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose managers globally
    window.ThemeManager = ThemeManager;
    window.ModalManager = ModalManager;

})();
