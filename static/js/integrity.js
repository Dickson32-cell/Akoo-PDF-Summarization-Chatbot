/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║     AKOO AI - Client-Side Integrity Protection                              ║
 * ║     Created by: Abdul Rashid Dickson                                        ║
 * ║     © 2025 All Rights Reserved                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * DO NOT MODIFY THIS FILE - Integrity checks will detect tampering
 */

(function () {
    'use strict';

    // ========================================================================
    // Creator Attribution Constants (Multiple Encodings)
    // ========================================================================

    const CREATOR_NAME = 'Abdul Rashid Dickson';
    const CREATOR_B64 = 'QWJkdWwgUmFzaGlkIERpY2tzb24=';
    const CREATOR_HEX = '4162' + '64756c' + '20526173' + '68696420' + '4469636b' + '736f6e';
    const CREATOR_REVERSED = 'noskciD dihsaR ludbA';

    // Split across variables
    const _c = ['Abd', 'ul ', 'Ras', 'hid', ' Di', 'cks', 'on'];

    // ========================================================================
    // Integrity Verification Functions
    // ========================================================================

    function assembleCreator() {
        return _c.join('');
    }

    function decodeBase64(str) {
        try {
            return atob(str);
        } catch (e) {
            return null;
        }
    }

    function decodeHex(hex) {
        try {
            let result = '';
            for (let i = 0; i < hex.length; i += 2) {
                result += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
            }
            return result;
        } catch (e) {
            return null;
        }
    }

    function reverseString(str) {
        return str.split('').reverse().join('');
    }

    function verifyCreatorName() {
        const assembled = assembleCreator();
        const fromB64 = decodeBase64(CREATOR_B64);
        const fromHex = decodeHex(CREATOR_HEX);
        const fromReverse = reverseString(CREATOR_REVERSED);

        return (
            assembled === CREATOR_NAME &&
            fromB64 === CREATOR_NAME &&
            fromHex === CREATOR_NAME &&
            fromReverse === CREATOR_NAME
        );
    }

    // ========================================================================
    // DOM Integrity Checks
    // ========================================================================

    function verifyDOMElements() {
        // Check footer exists
        const footer = document.getElementById('creator-attribution');
        if (!footer) return false;

        // Check creator name display
        const creatorDisplay = document.getElementById('creator-name-display') ||
            document.querySelector('.creator-name');
        if (!creatorDisplay) return false;

        // Verify the displayed name
        const displayedName = creatorDisplay.textContent.trim();
        if (displayedName !== CREATOR_NAME) return false;

        // Check hidden integrity marker
        const marker = document.getElementById('integrity-marker');
        if (marker) {
            const markerCreator = marker.getAttribute('data-c');
            if (markerCreator !== CREATOR_NAME) return false;
        }

        return true;
    }

    function verifyMetaTags() {
        const authorMeta = document.querySelector('meta[name="author"]');
        const creatorMeta = document.querySelector('meta[name="creator"]');

        if (authorMeta && authorMeta.content !== CREATOR_NAME) return false;
        if (creatorMeta && creatorMeta.content !== CREATOR_NAME) return false;

        return true;
    }

    // ========================================================================
    // Protection Actions
    // ========================================================================

    function triggerProtection(reason) {
        console.error('⚠️ INTEGRITY VIOLATION: ' + reason);
        console.error('This application was created by: Abdul Rashid Dickson');
        console.error('Unauthorized modification detected. Some features have been disabled.');

        // Display warning overlay
        showIntegrityWarning();

        // Disable certain functionality
        window.AKOO_INTEGRITY_FAILED = true;
    }

    function showIntegrityWarning() {
        const warning = document.createElement('div');
        warning.id = 'integrity-warning';
        warning.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            max-width: 400px;
            padding: 20px;
            background: rgba(239, 68, 68, 0.95);
            color: white;
            border-radius: 12px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            z-index: 10000;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
        `;

        warning.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <span style="font-size: 24px;">⚠️</span>
                <strong style="font-size: 16px;">Integrity Warning</strong>
            </div>
            <p style="margin: 0; font-size: 14px; line-height: 1.5;">
                This application's creator attribution has been modified.
                <br><br>
                <strong>Original Creator: Abdul Rashid Dickson</strong>
                <br><br>
                Some features may be disabled until the original code is restored.
            </p>
        `;

        // Add animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);

        document.body.appendChild(warning);
    }

    // ========================================================================
    // Continuous Monitoring
    // ========================================================================

    function runIntegrityCheck() {
        // Verify encoded signatures
        if (!verifyCreatorName()) {
            triggerProtection('Creator name encoding verification failed');
            return false;
        }

        // Verify DOM (after DOM is loaded)
        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            if (!verifyDOMElements()) {
                triggerProtection('DOM creator attribution modified');
                return false;
            }

            if (!verifyMetaTags()) {
                triggerProtection('Meta tag creator attribution modified');
                return false;
            }
        }

        return true;
    }

    // MutationObserver to watch for DOM changes to creator elements
    function setupDOMMonitoring() {
        const observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                // Check if creator elements were modified
                const target = mutation.target;
                if (target.id === 'creator-name-display' ||
                    target.classList.contains('creator-name') ||
                    target.id === 'creator-attribution') {
                    if (!verifyDOMElements()) {
                        triggerProtection('Runtime DOM modification detected');
                    }
                }
            });
        });

        // Observe the entire document
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true,
            attributes: true
        });
    }

    // ========================================================================
    // Initialization
    // ========================================================================

    // Run initial check
    if (!runIntegrityCheck()) {
        console.error('Initial integrity check failed');
    }

    // Run check when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            runIntegrityCheck();
            setupDOMMonitoring();
        });
    } else {
        runIntegrityCheck();
        setupDOMMonitoring();
    }

    // Periodic checks
    setInterval(runIntegrityCheck, 30000); // Every 30 seconds

    // Expose verification function globally
    window.AKOO_VERIFY_INTEGRITY = runIntegrityCheck;
    window.AKOO_CREATOR = CREATOR_NAME;

    // Console signature
    console.log('%c AKOO AI - Integrity System Active ', 'background: #10b981; color: white; padding: 5px 10px; border-radius: 5px;');
    console.log('%c Created by: Abdul Rashid Dickson ', 'color: #667eea; font-weight: bold;');

})();
