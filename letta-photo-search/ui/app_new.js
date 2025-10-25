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
        this.voicePage.classList.add('hidden');
        this.processingPage.classList.remove('hidden');
        this.queryDisplay.textContent = `"${query}"`;
        this.agentsTimeline.innerHTML = '';
        this.resultsSection.innerHTML = '';
    }

    showVoicePage() {
        this.processingPage.classList.add('hidden');
        this.memoryPage.classList.add('hidden');
        this.voicePage.classList.remove('hidden');
        this.textInput.value = '';
        this.transcript.textContent = '';
    }

    showMemoryPage(photo) {
        this.processingPage.classList.add('hidden');
        this.voicePage.classList.add('hidden');
        this.memoryPage.classList.remove('hidden');

        // Set photo and query
        this.memoryQueryDisplay.textContent = photo.title;
        this.memoryPhoto.src = photo.url;
        this.memoryPhoto.alt = photo.description;

        // Clear previous content
        this.memoryAgentsTimeline.innerHTML = '';
        this.narrationSection.classList.add('hidden');
        document.getElementById('memory-loading').classList.remove('hidden');

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
        stepDiv.className = 'glass-effect rounded-2xl p-6 animate-fade-in';
        stepDiv.style.animationDelay = `${this.agentsTimeline.children.length * 0.1}s`;

        stepDiv.innerHTML = `
            <div class="flex items-start gap-4">
                <div class="text-4xl">${icon}</div>
                <div class="flex-1">
                    <h3 class="text-xl font-semibold mb-2">${name}</h3>
                    <div class="flex items-center gap-2 mb-2">
                        <div class="w-3 h-3 rounded-full bg-yellow-500 animate-pulse status-indicator"></div>
                        <span class="text-gray-300 status-text">${status}</span>
                    </div>
                    <div class="agent-result-container mt-3"></div>
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
        const statusText = stepDiv.querySelector('.status-text');
        const resultContainer = stepDiv.querySelector('.agent-result-container');

        statusIndicator.classList.remove('bg-yellow-500', 'animate-pulse');
        statusIndicator.classList.add('bg-green-500');
        statusText.textContent = 'Complete';

        // Show result based on agent type
        if (name === 'Voice Processing Agent' && result.success) {
            const data = result.data;
            resultContainer.innerHTML = `
                <div class="bg-black/20 rounded-xl p-4 text-sm">
                    <div class="text-gray-300 mb-2">
                        <strong>Intent:</strong> ${data.intent}<br>
                        <strong>Search Query:</strong> "${data.search_query}"
                    </div>
                    <div class="flex flex-wrap gap-2 mt-2">
                        ${data.entities.map(e => `<span class="bg-purple-500/30 px-3 py-1 rounded-full text-xs">${e}</span>`).join('')}
                    </div>
                </div>
            `;
        } else if (name === 'Embedding Search Agent' && result.success) {
            resultContainer.innerHTML = `
                <div class="bg-black/20 rounded-xl p-4 text-sm">
                    <div class="text-gray-300 mb-2">
                        Found ${result.photos.length} matching images using 384-dimensional embeddings
                    </div>
                    <div class="flex flex-wrap gap-2 mt-2">
                        ${result.photos.slice(0, 3).map(p =>
                            `<span class="bg-pink-500/30 px-3 py-1 rounded-full text-xs">${p.title}: ${(p.similarity_score * 100).toFixed(1)}%</span>`
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
                <div class="glass-effect rounded-2xl p-8 text-center">
                    <div class="text-5xl mb-4">🔍</div>
                    <h3 class="text-2xl font-semibold mb-2">No Results</h3>
                    <p class="text-gray-300">
                        No photos found matching your query. Try a different search term.
                    </p>
                </div>
            `;
            return;
        }

        const photos = searchResult.photos;
        this.searchResults = photos; // Store for later use

        this.resultsSection.innerHTML = `
            <div class="mb-8">
                <h3 class="text-3xl font-bold mb-2">Search Results</h3>
                <p class="text-gray-300 text-lg">${photos.length} photos found</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="results-grid"></div>
        `;

        const grid = document.getElementById('results-grid');

        photos.forEach((photo, index) => {
            const card = document.createElement('div');
            card.className = 'glass-effect rounded-2xl overflow-hidden hover:scale-105 transition-transform animate-fade-in';
            card.style.animationDelay = `${(index * 0.15) + 0.5}s`;

            const similarityScore = (photo.similarity_score || photo.relevance_score / 100 || 0.5) * 100;

            card.innerHTML = `
                <img src="${photo.url}" alt="${photo.description}" class="w-full h-48 object-cover" />
                <div class="p-4">
                    <h4 class="text-lg font-semibold mb-2">${photo.title}</h4>
                    <p class="text-gray-300 text-sm mb-3">${photo.description}</p>
                    <div class="flex flex-wrap gap-2 mb-3">
                        ${photo.tags.map(tag => `<span class="bg-purple-500/30 px-2 py-1 rounded-full text-xs">${tag}</span>`).join('')}
                    </div>
                    <div class="mb-3">
                        <div class="flex items-center justify-between text-sm text-gray-300 mb-1">
                            <span>Relevance:</span>
                            <span>${similarityScore.toFixed(1)}%</span>
                        </div>
                        <div class="w-full bg-gray-700 rounded-full h-2">
                            <div class="bg-gradient-to-r from-pink-500 to-purple-600 h-2 rounded-full" style="width: ${similarityScore}%"></div>
                        </div>
                    </div>
                    <button class="play-memory-button w-full bg-gradient-to-r from-pink-500 to-purple-600 py-3 rounded-xl hover:shadow-lg hover:shadow-pink-500/50 transition-all font-semibold flex items-center justify-center gap-2" data-photo-index="${index}">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="5 3 19 12 5 21 5 3"/>
                        </svg>
                        Generate Memory Story
                    </button>
                </div>
            `;

            // Click on image/title speaks description
            const img = card.querySelector('img');
            const title = card.querySelector('h4');
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
        stepDiv.className = 'glass-effect rounded-xl p-4 animate-fade-in';
        stepDiv.style.animationDelay = `${timeline.children.length * 0.1}s`;

        stepDiv.innerHTML = `
            <div class="flex items-center gap-4">
                <div class="text-3xl">${icon}</div>
                <div class="flex-1">
                    <h4 class="text-lg font-semibold">${name}</h4>
                    <div class="flex items-center gap-2 mt-1">
                        <div class="w-2 h-2 rounded-full bg-yellow-500 animate-pulse status-indicator"></div>
                        <span class="text-sm text-gray-300 status-text">${status}</span>
                    </div>
                </div>
            </div>
        `;

        timeline.appendChild(stepDiv);

        // Simulate processing time
        await this.sleep(1500);

        // Update to complete
        const statusIndicator = stepDiv.querySelector('.status-indicator');
        const statusText = stepDiv.querySelector('.status-text');

        statusIndicator.classList.remove('bg-yellow-500', 'animate-pulse');
        statusIndicator.classList.add('bg-green-500');
        statusText.textContent = 'Complete';

        await this.sleep(300);
    }

    displayNarration(narrationData) {
        // Hide loading state
        document.getElementById('memory-loading').classList.add('hidden');

        let html = `<p class="text-gray-200">${narrationData.main_narration}</p>`;

        // Add person dialogues if any
        if (narrationData.person_dialogues && narrationData.person_dialogues.length > 0) {
            narrationData.person_dialogues.forEach(dialogue => {
                html += `
                    <div class="mt-4 pl-4 border-l-4 border-purple-500 italic">
                        <p class="text-gray-200">"${dialogue.dialogue}"</p>
                        ${dialogue.emotion ? `<span class="text-pink-400 text-sm">- ${dialogue.emotion}</span>` : ''}
                    </div>
                `;
            });
        }

        // Add ambient descriptions
        if (narrationData.ambient_descriptions && narrationData.ambient_descriptions.length > 0) {
            html += `
                <p class="mt-6 italic text-gray-400 text-sm">
                    Ambient atmosphere: ${narrationData.ambient_descriptions.join(', ')}
                </p>
            `;
        }

        this.narrationText.innerHTML = html;
        this.narrationSection.classList.remove('hidden');
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
