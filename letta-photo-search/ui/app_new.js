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
        this.memoryPage = document.getElementById('memory-page');
        this.backButton = document.getElementById('back-button');
        this.memoryBackButton = document.getElementById('memory-back-button');
        this.queryDisplay = document.getElementById('query-display');
        this.agentsTimeline = document.getElementById('agents-timeline');
        this.resultsSection = document.getElementById('results-section');

        // Memory page elements
        this.memoryQueryDisplay = document.getElementById('memory-query-display');
        this.memoryPhoto = document.getElementById('memory-photo');
        this.memoryAgentsTimeline = document.getElementById('memory-agents-timeline');
        this.narrationSection = document.getElementById('narration-section');
        this.narrationText = document.getElementById('narration-text');
        this.playAudioButton = document.getElementById('play-audio-button');
        this.ttsAudio = document.getElementById('tts-audio');

        // State
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.currentQuery = '';
        this.searchResults = [];
        this.currentAudioUrl = null;

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
        this.memoryBackButton.addEventListener('click', () => this.showProcessingPage());
        this.playAudioButton.addEventListener('click', () => this.playNarrationAudio());

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
        this.memoryPage.classList.remove('active');
        this.voicePage.classList.add('active');
        this.textInput.value = '';
        this.transcript.textContent = '';
    }

    showMemoryPage(photo) {
        this.processingPage.classList.remove('active');
        this.voicePage.classList.remove('active');
        this.memoryPage.classList.add('active');

        // Set photo and query
        this.memoryQueryDisplay.textContent = `Memory: "${photo.title}"`;
        this.memoryPhoto.src = photo.url;
        this.memoryPhoto.alt = photo.description;

        // Clear previous content
        this.memoryAgentsTimeline.innerHTML = '';
        this.narrationSection.style.display = 'none';

        // Start memory generation
        this.generateMemoryStory(photo);
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
        this.searchResults = photos; // Store for later use

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
                    ${index === 0 ? `
                        <button class="play-memory-button" data-photo-index="${index}">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="5 3 19 12 5 21 5 3"/>
                            </svg>
                            Play this Memory
                        </button>
                    ` : ''}
                </div>
            `;

            // Click on image/title speaks description
            const img = card.querySelector('.result-image');
            const title = card.querySelector('.result-title-text');
            [img, title].forEach(el => {
                el.addEventListener('click', () => {
                    this.speak(`${photo.title}. ${photo.description}`);
                });
            });

            // Play memory button
            const playButton = card.querySelector('.play-memory-button');
            if (playButton) {
                playButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.showMemoryPage(photo);
                });
            }

            grid.appendChild(card);
        });
    }

    async generateMemoryStory(photo) {
        try {
            // Step 1: Perception Agent
            await this.showMemoryAgentStep({
                name: 'Perception Agent',
                icon: '👁️',
                status: 'Analyzing visual content...',
                timeline: this.memoryAgentsTimeline
            });

            // Step 2: Emotion Agent
            await this.showMemoryAgentStep({
                name: 'Emotion Agent',
                icon: '💭',
                status: 'Detecting emotions and mood...',
                timeline: this.memoryAgentsTimeline
            });

            // Step 3: Narration Agent
            await this.showMemoryAgentStep({
                name: 'Narration Agent',
                icon: '📖',
                status: 'Generating story...',
                timeline: this.memoryAgentsTimeline
            });

            // Call backend to generate story
            const response = await fetch('/api/story/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ photo_url: photo.url })
            });

            const result = await response.json();

            if (result.success) {
                // Display narration
                this.displayNarration(result.narration);

                // Generate audio
                await this.generateNarrationAudio(result.narration.main_narration);
            } else {
                throw new Error(result.message || 'Story generation failed');
            }

        } catch (error) {
            console.error('Error generating memory story:', error);
            this.narrationText.textContent = `Unable to generate story: ${error.message}. Please try again.`;
            this.narrationSection.style.display = 'block';
        }
    }

    async showMemoryAgentStep({ name, icon, status, timeline }) {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'agent-step';
        stepDiv.style.animationDelay = `${timeline.children.length * 0.1}s`;

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
                    <span>Processing</span>
                    <div class="thinking-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;

        timeline.appendChild(stepDiv);

        // Simulate processing time
        await this.sleep(1500);

        // Update to complete
        const statusIndicator = stepDiv.querySelector('.status-indicator');
        const statusTextAgent = stepDiv.querySelector('.status-text-agent');

        statusIndicator.classList.remove('thinking');
        statusIndicator.classList.add('complete');
        statusTextAgent.textContent = 'Complete';

        await this.sleep(300);
    }

    displayNarration(narrationData) {
        let html = `<p>${narrationData.main_narration}</p>`;

        // Add person dialogues if any
        if (narrationData.person_dialogues && narrationData.person_dialogues.length > 0) {
            narrationData.person_dialogues.forEach(dialogue => {
                html += `
                    <p style="margin-top: 1rem; padding-left: 1rem; border-left: 3px solid var(--accent-secondary);">
                        <em>"${dialogue.dialogue}"</em>
                        ${dialogue.emotion ? `<span style="color: var(--accent-primary);"> - ${dialogue.emotion}</span>` : ''}
                    </p>
                `;
            });
        }

        // Add ambient descriptions
        if (narrationData.ambient_descriptions && narrationData.ambient_descriptions.length > 0) {
            html += `
                <p style="margin-top: 1.5rem; font-style: italic; color: var(--text-secondary);">
                    Ambient atmosphere: ${narrationData.ambient_descriptions.join(', ')}
                </p>
            `;
        }

        this.narrationText.innerHTML = html;
        this.narrationSection.style.display = 'block';
    }

    async generateNarrationAudio(text) {
        try {
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            const result = await response.json();

            if (result.success) {
                this.currentAudioUrl = result.audio_url;
                console.log('Audio generated:', this.currentAudioUrl);
            } else {
                console.error('TTS error:', result.message);
            }
        } catch (error) {
            console.error('Error generating audio:', error);
        }
    }

    playNarrationAudio() {
        if (!this.currentAudioUrl) {
            console.error('No audio URL available');
            return;
        }

        this.ttsAudio.src = this.currentAudioUrl;
        this.ttsAudio.play();

        this.playAudioButton.classList.add('playing');
        this.playAudioButton.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
            </svg>
            Pause
        `;

        this.ttsAudio.onended = () => {
            this.playAudioButton.classList.remove('playing');
            this.playAudioButton.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                Play Audio Narration
            `;
        };
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
