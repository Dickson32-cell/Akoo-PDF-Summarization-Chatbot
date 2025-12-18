/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║     AKOO AI - Visualization Module                                          ║
 * ║     Created by: Abdul Rashid Dickson                                        ║
 * ║     © 2025 All Rights Reserved                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

(function () {
    'use strict';

    const AKOO_VIZ = {
        CREATOR: 'Abdul Rashid Dickson',

        /**
         * Render a knowledge graph
         */
        renderGraph(container, graphData) {
            if (!container) return;

            const nodes = graphData.nodes || [];
            const edges = graphData.edges || [];

            // Create SVG container
            const width = container.clientWidth || 600;
            const height = 400;

            let html = `<svg width="${width}" height="${height}" style="background: rgba(0,0,0,0.2); border-radius: 8px;">`;

            // Simple force-directed layout simulation
            const positions = this._calculatePositions(nodes, width, height);

            // Draw edges
            edges.forEach(edge => {
                const source = positions[edge.source];
                const target = positions[edge.target];
                if (source && target) {
                    html += `<line x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" 
                            stroke="rgba(102, 126, 234, 0.5)" stroke-width="2"/>`;

                    // Edge label
                    const midX = (source.x + target.x) / 2;
                    const midY = (source.y + target.y) / 2;
                    html += `<text x="${midX}" y="${midY}" fill="rgba(255,255,255,0.5)" 
                            font-size="10" text-anchor="middle">${edge.label || ''}</text>`;
                }
            });

            // Draw nodes
            nodes.forEach((node, i) => {
                const pos = positions[i];
                if (pos) {
                    const color = this._getNodeColor(node.type);
                    const size = node.size || 10;

                    html += `<circle cx="${pos.x}" cy="${pos.y}" r="${size}" 
                            fill="${color}" stroke="white" stroke-width="2" class="graph-node"/>`;
                    html += `<text x="${pos.x}" y="${pos.y + size + 15}" 
                            fill="white" font-size="11" text-anchor="middle">${this._truncate(node.label, 15)}</text>`;
                }
            });

            html += '</svg>';

            // Add stats
            const metadata = graphData.metadata || {};
            html += `<div class="viz-stats" style="padding: 16px; color: var(--text-secondary);">
                <div><strong>Entities:</strong> ${metadata.entity_count || nodes.length}</div>
                <div><strong>Relationships:</strong> ${metadata.relationship_count || edges.length}</div>
                <div style="margin-top: 8px; font-size: 12px; color: var(--text-tertiary);">
                    Created by ${this.CREATOR}
                </div>
            </div>`;

            container.innerHTML = html;
        },

        /**
         * Render a mind map
         */
        renderMindMap(container, mindmapData) {
            if (!container) return;

            const data = mindmapData.mindmap || mindmapData;

            let html = '<div class="mindmap-container" style="padding: 20px; overflow: auto;">';
            html += this._renderMindMapNode(data, 0);
            html += '</div>';

            // Add metadata
            const metadata = mindmapData.metadata || {};
            html += `<div class="viz-stats" style="padding: 16px; color: var(--text-secondary);">
                <div><strong>Sections:</strong> ${metadata.sections || 0}</div>
                <div><strong>Key Concepts:</strong> ${metadata.concepts || 0}</div>
                <div style="margin-top: 8px; font-size: 12px; color: var(--text-tertiary);">
                    Created by ${this.CREATOR}
                </div>
            </div>`;

            container.innerHTML = html;
        },

        _renderMindMapNode(node, level) {
            const indent = level * 24;
            const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'];
            const color = colors[level % colors.length];
            const fontSize = Math.max(11, 16 - level * 2);

            let html = `<div class="mindmap-node" style="margin-left: ${indent}px; margin-bottom: 8px;">`;
            html += `<div class="node-title" style="font-size: ${fontSize}px; font-weight: ${level === 0 ? '700' : '500'}; 
                    color: ${color}; display: flex; align-items: center; gap: 8px;">`;

            if (level > 0) {
                html += `<span style="width: 8px; height: 8px; background: ${color}; border-radius: 50%;"></span>`;
            }
            html += `${node.title || 'Untitled'}</div>`;

            if (node.content && level > 0) {
                html += `<div class="node-content" style="font-size: 12px; color: var(--text-tertiary); 
                        margin-left: 16px; margin-top: 4px; max-width: 500px;">
                        ${this._truncate(node.content, 150)}
                        </div>`;
            }

            if (node.children && node.children.length > 0) {
                html += '<div class="node-children" style="margin-top: 8px;">';
                node.children.forEach(child => {
                    html += this._renderMindMapNode(child, level + 1);
                });
                html += '</div>';
            }

            html += '</div>';
            return html;
        },

        _calculatePositions(nodes, width, height) {
            const positions = {};
            const count = nodes.length;
            const centerX = width / 2;
            const centerY = height / 2;
            const radius = Math.min(width, height) * 0.35;

            nodes.forEach((node, i) => {
                const angle = (2 * Math.PI * i) / count;
                positions[i] = {
                    x: centerX + radius * Math.cos(angle),
                    y: centerY + radius * Math.sin(angle)
                };
            });

            return positions;
        },

        _getNodeColor(type) {
            const colors = {
                'person': '#667eea',
                'organization': '#764ba2',
                'concept': '#f093fb',
                'date': '#4facfe',
                'default': '#00f2fe'
            };
            return colors[type] || colors.default;
        },

        _truncate(text, maxLength) {
            if (!text) return '';
            return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
        },

        /**
         * Render quiz
         */
        renderQuiz(container, quizData) {
            if (!container) return;

            const questions = quizData.quiz || [];

            let html = '<div class="quiz-container" style="padding: 20px;">';
            html += `<h3 style="color: var(--accent-primary); margin-bottom: 16px;">
                    📝 Quiz (${questions.length} questions)</h3>`;

            questions.forEach((q, i) => {
                html += `<div class="quiz-question" style="margin-bottom: 16px; padding: 16px; 
                        background: var(--surface-1); border-radius: 8px;">
                    <div style="font-weight: 500; margin-bottom: 8px;">Q${i + 1}: ${q.question}</div>
                    <input type="text" class="quiz-answer" data-answer="${q.answer}" 
                        placeholder="Your answer..." 
                        style="width: 100%; padding: 8px; border-radius: 4px; 
                        background: var(--surface-2); border: 1px solid var(--glass-border); color: white;">
                </div>`;
            });

            html += `<button onclick="AKOO_VIZ.checkQuizAnswers()" class="btn btn-primary" 
                    style="margin-top: 16px;">Check Answers</button>`;
            html += '</div>';

            container.innerHTML = html;
        },

        checkQuizAnswers() {
            const inputs = document.querySelectorAll('.quiz-answer');
            let correct = 0;

            inputs.forEach(input => {
                const answer = input.dataset.answer.toLowerCase();
                const userAnswer = input.value.toLowerCase().trim();

                if (userAnswer === answer || answer.includes(userAnswer)) {
                    input.style.borderColor = '#10b981';
                    correct++;
                } else {
                    input.style.borderColor = '#ef4444';
                }
            });

            window.showNotification?.(`You got ${correct}/${inputs.length} correct!`,
                correct === inputs.length ? 'success' : 'info');
        },

        /**
         * Render sentiment analysis
         */
        renderSentiment(container, sentimentData) {
            if (!container) return;

            const score = sentimentData.positivity_score || 50;
            const sentiment = sentimentData.sentiment || 'neutral';
            const colors = { positive: '#10b981', neutral: '#f59e0b', negative: '#ef4444' };
            const color = colors[sentiment] || colors.neutral;

            let html = `<div style="padding: 20px; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 16px;">
                    ${sentiment === 'positive' ? '😊' : sentiment === 'negative' ? '😔' : '😐'}
                </div>
                <div style="font-size: 24px; font-weight: 700; color: ${color}; text-transform: capitalize;">
                    ${sentiment}
                </div>
                <div style="margin: 20px 0;">
                    <div style="width: 100%; height: 12px; background: var(--surface-2); border-radius: 6px; overflow: hidden;">
                        <div style="width: ${score}%; height: 100%; background: ${color}; transition: width 0.5s;"></div>
                    </div>
                    <div style="margin-top: 8px; color: var(--text-secondary);">Positivity: ${score}%</div>
                </div>
                <div style="color: var(--text-tertiary); font-size: 14px;">
                    ${sentimentData.description || ''}
                </div>
                <div style="margin-top: 16px; font-size: 12px; color: var(--text-muted);">
                    Analysis by AKOO AI - Created by ${this.CREATOR}
                </div>
            </div>`;

            container.innerHTML = html;
        }
    };

    // Expose globally
    window.AKOO_VIZ = AKOO_VIZ;

    console.log('%c AKOO Visualization Module Loaded ',
        'background: #764ba2; color: white; padding: 5px 10px; border-radius: 5px;');
    console.log('%c Created by: Abdul Rashid Dickson ', 'color: #764ba2; font-weight: bold;');

})();
