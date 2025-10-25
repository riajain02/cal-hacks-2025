/**
 * AI Agent Photo Search - Futuristic UI
 * Shows multi-agent workflow step-by-step
 */

class AgentSearchApp {
    constructor() {
        // DOM Elements
        this.micButton = document.getElementById('mic-button');
        this.statusText = document.getElementById('status-text');
        this.transcript = document.getElementById('transcript');
        this.textInput = document.getElementById('text-input');
        this.sendButton = document.getElementById('send-button');
        this.voicePage = document.getElementById('voice-page');
        this.processingPage = document.getElementById('processing-page');
        this.backButton = document.getElementById('back-button');
        this.queryDisplay = document.getElementById('query-display');
        this.agentsTimeline = document.getElementById('agents-timeline');
        this.resultsSection = document.getElementById('results-section');

        // State
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.currentQuery = '';

        this.init();
    }

    init() {
        // Initialize speech recognition
        this.initSpeechRecognition();

        // Event listeners
        this.micButton.addEventListener('click', () => this.toggleVoiceInput());
        this.sendButton.addEventListener('click', () => this.processQuery());
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.processQuery();
        });
        this.backButton.addEventListener('click', () => this.showVoicePage());

        // Suggestion buttons
        document.querySelectorAll('.suggestion').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.textInput.value = e.target.dataset.query;
                this.processQuery();
            });
        });

        // Welcome audio
        this.speak('Welcome to AI Agent Search. Click the microphone or type to begin.');
    }

    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event) => {
                const transcript = Array.from(event.results)
                    .map(result => result[0].transcript)
                    .join('');

                this.transcript.textContent = transcript;

                if (event.results[0].isFinal) {
                    this.textInput.value = transcript;
                    this.processQuery();
                }
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopListening();
                this.updateStatus('Sorry, could not understand. Please try again.');
            };

            this.recognition.onend = () => {
                this.stopListening();
            };
        } else {
            console.warn('Speech recognition not supported');
            this.micButton.style.opacity = '0.5';
        }
    }

    toggleVoiceInput() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        if (!this.recognition) return;

        this.isListening = true;
        this.micButton.classList.add('listening');
        this.statusText.textContent = 'Listening... Speak now';
        this.statusText.classList.add('active');
        this.transcript.textContent = '';

        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.stopListening();
        }
    }

    stopListening() {
        if (this.recognition) {
            this.recognition.stop();
        }
        this.isListening = false;
        this.micButton.classList.remove('listening');
        this.statusText.textContent = 'Click to speak or type your query';
        this.statusText.classList.remove('active');
    }

    updateStatus(message) {
        this.statusText.textContent = message;
    }

    async processQuery() {
        const query = this.textInput.value.trim();
        if (!query) return;

        this.currentQuery = query;

        // Transition to processing page
        this.showProcessingPage(query);

        // Process through agents
        await this.runAgentWorkflow(query);
    }

    showProcessingPage(query) {
        this.voicePage.classList.remove('active');
        this.processingPage.classList.add('active');
        this.queryDisplay.textContent = `"${query}"`;
        this.agentsTimeline.innerHTML = '';
        this.resultsSection.innerHTML = '';
    }

    showVoicePage() {
        this.processingPage.classList.remove('active');
        this.voicePage.classList.add('active');
        this.textInput.value = '';
        this.transcript.textContent = '';
    }

    async runAgentWorkflow(query) {
        // Step 1: Voice Processing Agent
        const voiceResult = await this.showAgentStep({
            name: 'Voice Processing Agent',
            icon: '🎤',
            status: 'Processing natural language...',
            action: async () => {
                const response = await fetch('/api/voice/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: query })
                });
                return await response.json();
            }
        });

        // Step 2: Embedding Search Agent
        const searchResult = await this.showAgentStep({
            name: 'Embedding Search Agent',
            icon: '🔍',
            status: 'Computing vector embeddings...',
            action: async () => {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: voiceResult.data?.search_query || query,
                        use_voice_processing: true
                    })
                });
                return await response.json();
            }
        });

        // Step 3: Display Results
        await this.displayResults(searchResult, voiceResult);

        // Speak results
        if (searchResult.success && searchResult.photos.length > 0) {
            const count = searchResult.photos.length;
            const ttsText = `I found ${count} photo${count > 1 ? 's' : ''} matching your search. ${searchResult.photos[0].title} is the top result.`;
            this.speak(ttsText);
        }
    }

    async showAgentStep({ name, icon, status, action }) {
        // Create agent step card
        const stepDiv = document.createElement('div');
        stepDiv.className = 'agent-step';
        stepDiv.style.animationDelay = `${this.agentsTimeline.children.length * 0.1}s`;

        stepDiv.innerHTML = `
            <div class="agent-header">
                <div class="agent-icon">${icon}</div>
                <div class="agent-info">
                    <div class="agent-name">${name}</div>
                    <div class="agent-status">
                        <span class="status-indicator thinking"></span>
                        <span class="status-text-agent">${status}</span>
                    </div>
                </div>
            </div>
            <div class="agent-content">
                <div class="thinking-animation">
                    <span>Analyzing</span>
                    <div class="thinking-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;

        this.agentsTimeline.appendChild(stepDiv);

        // Simulate processing time for visual effect
        await this.sleep(800);

        // Execute agent action
        const result = await action();

        // Update to complete state
        const statusIndicator = stepDiv.querySelector('.status-indicator');
        const statusTextAgent = stepDiv.querySelector('.status-text-agent');
        const contentDiv = stepDiv.querySelector('.agent-content');

        statusIndicator.classList.remove('thinking');
        statusIndicator.classList.add('complete');
        statusTextAgent.textContent = 'Complete';

        // Show result based on agent type
        if (name === 'Voice Processing Agent' && result.success) {
            const data = result.data;
            contentDiv.innerHTML = `
                <div class="agent-result">
                    <div class="result-label">Extracted Information</div>
                    <div class="result-content">
                        <strong>Intent:</strong> ${data.intent}<br>
                        <strong>Search Query:</strong> "${data.search_query}"
                    </div>
                    <div class="result-badges">
                        ${data.entities.map(e => `<span class="badge">${e}</span>`).join('')}
                    </div>
                </div>
            `;
        } else if (name === 'Embedding Search Agent' && result.success) {
            contentDiv.innerHTML = `
                <div class="agent-result">
                    <div class="result-label">Vector Similarity Search</div>
                    <div class="result-content">
                        Found ${result.photos.length} matching images using 384-dimensional embeddings
                    </div>
                    <div class="result-badges">
                        ${result.photos.slice(0, 3).map(p =>
                            `<span class="badge">${p.title}: ${(p.similarity_score * 100).toFixed(1)}%</span>`
                        ).join('')}
                    </div>
                </div>
            `;
        }

        await this.sleep(300);
        return result;
    }

    async displayResults(searchResult, voiceResult) {
        if (!searchResult.success || !searchResult.photos.length) {
            this.resultsSection.innerHTML = `
                <div class="agent-step">
                    <div class="agent-result">
                        <div class="result-label">No Results</div>
                        <div class="result-content">
                            No photos found matching your query. Try a different search term.
                        </div>
                    </div>
                </div>
            `;
            return;
        }

        const photos = searchResult.photos;

        this.resultsSection.innerHTML = `
            <div class="results-header">
                <div class="results-title">Search Results</div>
                <div class="results-count">${photos.length} photos found</div>
            </div>
            <div class="results-grid" id="results-grid"></div>
        `;

        const grid = document.getElementById('results-grid');

        photos.forEach((photo, index) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            card.style.animationDelay = `${(index * 0.15) + 0.5}s`;

            const similarityScore = (photo.similarity_score || photo.relevance_score / 100 || 0.5) * 100;

            card.innerHTML = `
                <img src="${photo.url}" alt="${photo.description}" class="result-image" />
                <div class="result-info">
                    <div class="result-title-text">${photo.title}</div>
                    <div class="result-description">${photo.description}</div>
                    <div class="result-tags">
                        ${photo.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                    <div class="result-score">
                        <span class="score-label">Relevance:</span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${similarityScore}%"></div>
                        </div>
                        <span class="score-value">${similarityScore.toFixed(1)}%</span>
                    </div>
                </div>
            `;

            card.addEventListener('click', () => {
                this.speak(`${photo.title}. ${photo.description}`);
            });

            grid.appendChild(card);
        });
    }

    speak(text) {
        if (!this.synthesis) return;

        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;

        this.synthesis.speak(utterance);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AgentSearchApp();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Escape to go back
    if (e.key === 'Escape') {
        document.getElementById('back-button')?.click();
    }
});
