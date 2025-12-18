/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║     AKOO AI - Voice Input/Output Module                                     ║
 * ║     Created by: Abdul Rashid Dickson                                        ║
 * ║     © 2025 All Rights Reserved                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

(function () {
    'use strict';

    const AKOO_VOICE = {
        CREATOR: 'Abdul Rashid Dickson',
        recognition: null,
        synthesis: window.speechSynthesis,
        isRecording: false,

        /**
         * Initialize speech recognition
         */
        init() {
            if ('webkitSpeechRecognition' in window) {
                this.recognition = new webkitSpeechRecognition();
                this.recognition.continuous = false;
                this.recognition.interimResults = true;
                this.recognition.lang = 'en-US';

                console.log('%c AKOO Voice Module Ready ',
                    'background: #10b981; color: white; padding: 5px 10px; border-radius: 5px;');
            } else if ('SpeechRecognition' in window) {
                this.recognition = new SpeechRecognition();
                this.recognition.continuous = false;
                this.recognition.interimResults = true;
                this.recognition.lang = 'en-US';
            } else {
                console.warn('Speech recognition not supported in this browser');
            }
        },

        /**
         * Start voice recording
         */
        startRecording(onResult) {
            if (!this.recognition) {
                window.showNotification?.('Voice input not supported in this browser', 'error');
                return;
            }

            if (this.isRecording) {
                this.stopRecording();
                return;
            }

            this.isRecording = true;

            // Show voice modal
            const modal = document.getElementById('voice-modal');
            if (modal) modal.style.display = 'flex';

            const status = document.getElementById('voice-status');

            this.recognition.onstart = () => {
                if (status) status.textContent = 'Listening...';
                console.log('Voice recording started');
            };

            this.recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }

                if (status) {
                    status.textContent = finalTranscript || interimTranscript || 'Listening...';
                }

                if (finalTranscript && onResult) {
                    onResult(finalTranscript);
                }
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                if (status) status.textContent = 'Error: ' + event.error;
                this.stopRecording();
            };

            this.recognition.onend = () => {
                this.stopRecording();
            };

            try {
                this.recognition.start();
            } catch (e) {
                console.error('Error starting recognition:', e);
                this.stopRecording();
            }
        },

        /**
         * Stop voice recording
         */
        stopRecording() {
            this.isRecording = false;

            if (this.recognition) {
                try {
                    this.recognition.stop();
                } catch (e) {
                    // Already stopped
                }
            }

            // Hide voice modal
            const modal = document.getElementById('voice-modal');
            if (modal) modal.style.display = 'none';
        },

        /**
         * Speak text using text-to-speech
         */
        speak(text, options = {}) {
            if (!this.synthesis) {
                console.warn('Speech synthesis not supported');
                return;
            }

            // Cancel any ongoing speech
            this.synthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = options.rate || 1;
            utterance.pitch = options.pitch || 1;
            utterance.volume = options.volume || 1;
            utterance.lang = options.lang || 'en-US';

            // Choose a nice voice if available
            const voices = this.synthesis.getVoices();
            const preferredVoice = voices.find(v =>
                v.name.includes('Google') || v.name.includes('Microsoft') || v.lang.startsWith('en')
            );
            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }

            utterance.onend = () => {
                console.log('Finished speaking');
            };

            utterance.onerror = (event) => {
                console.error('Speech error:', event);
            };

            this.synthesis.speak(utterance);
        },

        /**
         * Stop speaking
         */
        stopSpeaking() {
            if (this.synthesis) {
                this.synthesis.cancel();
            }
        },

        /**
         * Check if currently speaking
         */
        isSpeaking() {
            return this.synthesis && this.synthesis.speaking;
        }
    };

    // Initialize on load
    AKOO_VOICE.init();

    // Bind stop recording button
    document.addEventListener('DOMContentLoaded', () => {
        const stopBtn = document.getElementById('stop-recording');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => AKOO_VOICE.stopRecording());
        }

        // Click backdrop to close
        const backdrop = document.querySelector('#voice-modal .modal-backdrop');
        if (backdrop) {
            backdrop.addEventListener('click', () => AKOO_VOICE.stopRecording());
        }
    });

    // Expose globally
    window.AKOO_VOICE = AKOO_VOICE;

    console.log('%c Created by: Abdul Rashid Dickson ', 'color: #10b981; font-weight: bold;');

})();
