/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║     AKOO AI - Chat Interface JavaScript                                     ║
 * ║     Created by: Abdul Rashid Dickson                                        ║
 * ║     © 2025 All Rights Reserved                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

(function () {
    'use strict';

    // ========================================================================
    // Chat State
    // ========================================================================

    const ChatState = {
        messages: [],
        currentDocument: null,
        isProcessing: false,
        sessionId: null,
        currentTool: null
    };

    // ========================================================================
    // DOM Elements
    // ========================================================================

    const elements = {
        messagesContainer: null,
        messageInput: null,
        sendBtn: null,
        typingIndicator: null,
        fileInput: null,
        vizPanel: null
    };

    // ========================================================================
    // Initialization
    // ========================================================================

    function init() {
        // Get DOM elements
        elements.messagesContainer = document.getElementById('messages-container');
        elements.messageInput = document.getElementById('message-input');
        elements.sendBtn = document.getElementById('send-btn');
        elements.typingIndicator = document.getElementById('typing-indicator');
        elements.fileInput = document.getElementById('file-input');
        elements.vizPanel = document.getElementById('viz-panel');

        // Generate session ID
        ChatState.sessionId = localStorage.getItem('akoo-session') || generateSessionId();
        localStorage.setItem('akoo-session', ChatState.sessionId);

        // Bind events
        bindEvents();

        // Check for stored summary
        const storedSummary = sessionStorage.getItem('akoo-summary');
        if (storedSummary) {
            sessionStorage.removeItem('akoo-summary');
            addBotMessage(storedSummary, 'summary');
        }

        // Auto-resize textarea
        setupAutoResize();

        console.log('%c AKOO Chat Initialized ', 'background: #667eea; color: white; padding: 5px 10px; border-radius: 5px;');
    }

    function generateSessionId() {
        return 'akoo-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    // ========================================================================
    // Event Bindings
    // ========================================================================

    function bindEvents() {
        // Send message
        if (elements.sendBtn) {
            elements.sendBtn.addEventListener('click', sendMessage);
        }

        // Enter to send (Shift+Enter for new line)
        if (elements.messageInput) {
            elements.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
        }

        // File upload
        const uploadBtn = document.getElementById('btn-upload-pdf');
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => {
                elements.fileInput?.click();
            });
        }

        const attachBtn = document.getElementById('btn-attach');
        if (attachBtn) {
            attachBtn.addEventListener('click', () => {
                elements.fileInput?.click();
            });
        }

        if (elements.fileInput) {
            elements.fileInput.addEventListener('change', handleFileUpload);
        }

        // Tool buttons
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tool = btn.dataset.tool;
                selectTool(tool, btn);
            });
        });

        // Summary length slider
        const summaryLengthSlider = document.getElementById('summary-length');
        const summaryLengthValue = document.getElementById('summary-length-value');
        if (summaryLengthSlider && summaryLengthValue) {
            summaryLengthSlider.addEventListener('input', (e) => {
                summaryLengthValue.textContent = `${e.target.value} sentences`;
            });
        }

        // New chat button
        const newChatBtn = document.getElementById('btn-new-chat');
        if (newChatBtn) {
            newChatBtn.addEventListener('click', startNewChat);
        }

        // Visualization panel close
        const vizClose = document.getElementById('viz-close');
        if (vizClose) {
            vizClose.addEventListener('click', closeVisualization);
        }

        // Voice input
        const voiceBtn = document.getElementById('btn-voice-input');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', startVoiceInput);
        }

        // Export chat
        const exportBtn = document.getElementById('btn-export');
        if (exportBtn) {
            exportBtn.addEventListener('click', exportChat);
        }
    }

    function setupAutoResize() {
        if (!elements.messageInput) return;

        elements.messageInput.addEventListener('input', () => {
            elements.messageInput.style.height = 'auto';
            elements.messageInput.style.height = Math.min(elements.messageInput.scrollHeight, 200) + 'px';
        });
    }

    // ========================================================================
    // Message Handling
    // ========================================================================

    function sendMessage() {
        const message = elements.messageInput?.value.trim();
        if (!message || ChatState.isProcessing) return;

        // Check integrity before processing
        if (window.AKOO_INTEGRITY_FAILED) {
            addBotMessage('⚠️ Application integrity compromised. Created by Abdul Rashid Dickson.', 'error');
            return;
        }

        // Add user message to UI
        addUserMessage(message);

        // Clear input
        elements.messageInput.value = '';
        elements.messageInput.style.height = 'auto';

        // Show typing indicator
        showTypingIndicator();
        ChatState.isProcessing = true;

        // Send to backend
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input: message })
        })
            .then(response => response.json())
            .then(data => {
                hideTypingIndicator();
                ChatState.isProcessing = false;

                if (data.error) {
                    addBotMessage('Sorry, I encountered an error: ' + data.error, 'error');
                } else {
                    addBotMessage(data.response);
                }
            })
            .catch(error => {
                console.error('Chat error:', error);
                hideTypingIndicator();
                ChatState.isProcessing = false;
                addBotMessage('Sorry, I encountered a connection error. Please try again.', 'error');
            });
    }

    function addUserMessage(content) {
        const message = createMessageElement('user', content);
        elements.messagesContainer?.appendChild(message);
        scrollToBottom();
        ChatState.messages.push({ role: 'user', content, timestamp: new Date() });
    }

    function addBotMessage(content, type = 'text') {
        const message = createMessageElement('bot', content, type);
        elements.messagesContainer?.appendChild(message);
        scrollToBottom();
        ChatState.messages.push({ role: 'bot', content, timestamp: new Date() });
    }

    function createMessageElement(role, content, type = 'text') {
        const isBot = role === 'bot';
        const div = document.createElement('div');
        div.className = `message ${role}-message`;

        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Format content based on type
        let formattedContent = content;
        if (type === 'summary' && typeof marked !== 'undefined') {
            formattedContent = `<div class="summary-content">${marked.parse(content)}</div>`;
        } else if (type === 'error') {
            formattedContent = `<div class="error-content" style="color: #ef4444;">${escapeHtml(content)}</div>`;
        } else {
            // Check if content looks like markdown
            if (content.includes('#') || content.includes('*') || content.includes('•')) {
                if (typeof marked !== 'undefined') {
                    formattedContent = marked.parse(content);
                }
            } else {
                formattedContent = escapeHtml(content).replace(/\n/g, '<br>');
            }
        }

        div.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${isBot ? 'robot' : 'user'}"></i>
            </div>
            <div class="message-content glass-panel">
                <div class="message-header">
                    <span class="message-sender">${isBot ? 'AKOO AI' : 'You'}</span>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-body">${formattedContent}</div>
            </div>
        `;

        return div;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function showTypingIndicator() {
        if (elements.typingIndicator) {
            elements.typingIndicator.style.display = 'flex';
            scrollToBottom();
        }
    }

    function hideTypingIndicator() {
        if (elements.typingIndicator) {
            elements.typingIndicator.style.display = 'none';
        }
    }

    function scrollToBottom() {
        if (elements.messagesContainer) {
            elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
        }
    }

    // ========================================================================
    // File Upload
    // ========================================================================

    function handleFileUpload(e) {
        const file = e.target.files?.[0];
        if (!file) return;

        if (!file.name.toLowerCase().endsWith('.pdf')) {
            window.showNotification?.('Please upload a PDF file', 'error');
            return;
        }

        // Show processing message
        addBotMessage('📄 Processing your document: ' + file.name + '...', 'text');
        showTypingIndicator();
        ChatState.isProcessing = true;

        // Update current document display
        updateCurrentDocument(file.name);

        const formData = new FormData();
        formData.append('file', file);

        // Get settings
        const summaryLength = document.getElementById('summary-length')?.value || 30;
        const summaryFormat = document.getElementById('summary-format')?.value || 'paragraph';
        const summaryType = document.getElementById('summary-type')?.value || 'academic';

        formData.append('summary_length', summaryLength);
        formData.append('summary_format', summaryFormat);
        formData.append('summary_type', summaryType);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    hideTypingIndicator();
                    ChatState.isProcessing = false;
                    addBotMessage('❌ Error: ' + data.error, 'error');
                } else if (data.job_id) {
                    pollJobStatus(data.job_id);
                } else if (data.summary) {
                    hideTypingIndicator();
                    ChatState.isProcessing = false;
                    addBotMessage(data.summary, 'summary');
                }
            })
            .catch(error => {
                console.error('Upload error:', error);
                hideTypingIndicator();
                ChatState.isProcessing = false;
                addBotMessage('❌ Upload failed. Please try again.', 'error');
            });

        // Reset file input
        e.target.value = '';
    }

    function pollJobStatus(jobId) {
        const poll = () => {
            fetch(`/status/${jobId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'completed') {
                        hideTypingIndicator();
                        ChatState.isProcessing = false;

                        if (data.result?.summary) {
                            addBotMessage(data.result.summary, 'summary');
                        }
                    } else if (data.status === 'error') {
                        hideTypingIndicator();
                        ChatState.isProcessing = false;
                        addBotMessage('❌ ' + (data.message || 'Processing failed'), 'error');
                    } else {
                        // Still processing
                        setTimeout(poll, 1000);
                    }
                })
                .catch(() => {
                    setTimeout(poll, 2000);
                });
        };

        poll();
    }

    function updateCurrentDocument(filename) {
        const section = document.getElementById('current-doc-section');
        const nameEl = document.getElementById('current-doc-name');

        if (section) section.style.display = 'block';
        if (nameEl) nameEl.textContent = filename;

        ChatState.currentDocument = filename;
    }

    // ========================================================================
    // Tool Selection
    // ========================================================================

    function selectTool(tool, btn) {
        // Remove active from all buttons
        document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        ChatState.currentTool = tool;

        // Handle tool-specific actions
        switch (tool) {
            case 'knowledge-graph':
                if (ChatState.currentDocument) {
                    requestKnowledgeGraph();
                } else {
                    window.showNotification?.('Please upload a document first', 'warning');
                }
                break;
            case 'mind-map':
                if (ChatState.currentDocument) {
                    requestMindMap();
                } else {
                    window.showNotification?.('Please upload a document first', 'warning');
                }
                break;
            case 'compare':
                window.showNotification?.('Document comparison coming soon!', 'info');
                break;
            case 'translate':
                window.showNotification?.('Translation coming soon!', 'info');
                break;
            case 'citations':
                window.showNotification?.('Citation extraction coming soon!', 'info');
                break;
            case 'sentiment':
                window.showNotification?.('Sentiment analysis coming soon!', 'info');
                break;
            case 'quiz':
                window.showNotification?.('Quiz generation coming soon!', 'info');
                break;
            default:
                break;
        }
    }

    function requestKnowledgeGraph() {
        showTypingIndicator();
        addBotMessage('🔄 Generating knowledge graph...', 'text');

        fetch('/api/knowledge-graph', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ document: ChatState.currentDocument })
        })
            .then(response => response.json())
            .then(data => {
                hideTypingIndicator();
                if (data.graph) {
                    showVisualization('Knowledge Graph', data.graph, 'graph');
                } else {
                    addBotMessage('❌ Could not generate knowledge graph', 'error');
                }
            })
            .catch(() => {
                hideTypingIndicator();
                addBotMessage('❌ Knowledge graph generation failed', 'error');
            });
    }

    function requestMindMap() {
        showTypingIndicator();
        addBotMessage('🔄 Generating mind map...', 'text');

        fetch('/api/mind-map', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ document: ChatState.currentDocument })
        })
            .then(response => response.json())
            .then(data => {
                hideTypingIndicator();
                if (data.mindmap) {
                    showVisualization('Mind Map', data.mindmap, 'mindmap');
                } else {
                    addBotMessage('❌ Could not generate mind map', 'error');
                }
            })
            .catch(() => {
                hideTypingIndicator();
                addBotMessage('❌ Mind map generation failed', 'error');
            });
    }

    // ========================================================================
    // Visualization
    // ========================================================================

    function showVisualization(title, data, type) {
        if (!elements.vizPanel) return;

        const titleEl = document.getElementById('viz-title');
        const contentEl = document.getElementById('viz-content');

        if (titleEl) titleEl.textContent = title;

        elements.vizPanel.style.display = 'flex';
        document.querySelector('.chat-container')?.classList.add('with-viz');

        // Render based on type
        if (window.AKOO_VIZ) {
            switch (type) {
                case 'graph':
                    window.AKOO_VIZ.renderGraph(contentEl, data);
                    break;
                case 'mindmap':
                    window.AKOO_VIZ.renderMindMap(contentEl, data);
                    break;
            }
        } else {
            if (contentEl) {
                contentEl.innerHTML = '<p style="color: var(--text-tertiary);">Visualization module not loaded</p>';
            }
        }
    }

    function closeVisualization() {
        if (elements.vizPanel) {
            elements.vizPanel.style.display = 'none';
        }
        document.querySelector('.chat-container')?.classList.remove('with-viz');
    }

    // ========================================================================
    // Voice Input
    // ========================================================================

    function startVoiceInput() {
        if (window.AKOO_VOICE) {
            window.AKOO_VOICE.startRecording((transcript) => {
                if (elements.messageInput) {
                    elements.messageInput.value = transcript;
                    elements.messageInput.dispatchEvent(new Event('input'));
                }
            });
        } else {
            window.showNotification?.('Voice input not available', 'warning');
        }
    }

    // ========================================================================
    // Utility Functions
    // ========================================================================

    function startNewChat() {
        if (elements.messagesContainer) {
            // Keep welcome message, remove others
            const messages = elements.messagesContainer.querySelectorAll('.message:not(.welcome-message)');
            messages.forEach(msg => msg.remove());
        }

        ChatState.messages = [];
        ChatState.currentDocument = null;
        ChatState.currentTool = null;

        // Hide current document section
        const docSection = document.getElementById('current-doc-section');
        if (docSection) docSection.style.display = 'none';

        // Close visualization
        closeVisualization();

        window.showNotification?.('Started a new chat', 'success');
    }

    function exportChat() {
        if (ChatState.messages.length === 0) {
            window.showNotification?.('No messages to export', 'warning');
            return;
        }

        let content = '# AKOO AI Chat Export\n';
        content += `# Created by: Abdul Rashid Dickson\n`;
        content += `# Date: ${new Date().toLocaleString()}\n\n`;

        ChatState.messages.forEach(msg => {
            const time = msg.timestamp.toLocaleTimeString();
            content += `## ${msg.role === 'bot' ? 'AKOO AI' : 'You'} (${time})\n\n`;
            content += msg.content + '\n\n---\n\n';
        });

        content += '\n\n---\n*Exported from AKOO AI - Created by Abdul Rashid Dickson*\n';

        const blob = new Blob([content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `akoo-chat-${Date.now()}.md`;
        a.click();
        URL.revokeObjectURL(url);

        window.showNotification?.('Chat exported successfully', 'success');
    }

    // ========================================================================
    // Initialize
    // ========================================================================

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose for external access
    window.AKOO_CHAT = {
        addBotMessage,
        addUserMessage,
        state: ChatState
    };

})();
