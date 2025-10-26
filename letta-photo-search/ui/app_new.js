/**
 * Synesthesia - AI Memory Assistant
 * Clean, minimal black & white design
 */

class SynesthesiaApp {
    constructor() {
        // DOM Elements
        this.splashScreen = document.getElementById('splash-screen');
        this.appContainer = document.getElementById('app-container');
        this.particlesContainer = document.getElementById('particles-container');
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
        this.showSplashScreen();
        setTimeout(() => {
            this.hideSplashScreen();
            this.initApp();
        }, 2500);
    }

    showSplashScreen() {
        // Create minimal particles
        for (let i = 0; i < 15; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.bottom = '0';
            particle.style.animationDelay = `${Math.random() * 12}s`;
            this.particlesContainer.appendChild(particle);
        }
    }

    hideSplashScreen() {
        this.splashScreen.style.opacity = '0';
        this.splashScreen.style.transition = 'opacity 0.8s ease';
        setTimeout(() => {
            this.splashScreen.style.display = 'none';
            this.appContainer.classList.remove('hidden');
        }, 800);
    }

    initApp() {
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
                this.textInput.value = e.target.dataset.query || e.target.closest('.suggestion').dataset.query;
                this.processQuery();
            });
        });

        this.speak('Welcome to Synesthesia, your memory companion. Use your voice or keyboard to rediscover your cherished moments.');
        this.textInput.focus();
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
                    this.speak(`Searching for ${transcript}`);
                    this.processQuery();
                }
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopListening();
                this.speak('Could not understand. Please try again.');
                this.updateStatus('Error - try again');
            };

            this.recognition.onend = () => {
                this.stopListening();
            };
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
        this.micButton.classList.add('recording-active');
        this.micButton.setAttribute('aria-pressed', 'true');
        this.statusText.textContent = 'Listening...';
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
        this.micButton.classList.remove('recording-active');
        this.micButton.setAttribute('aria-pressed', 'false');
        this.statusText.textContent = 'Click to speak or type below';
    }

    updateStatus(message) {
        this.statusText.textContent = message;
    }

    async processQuery() {
        const query = this.textInput.value.trim();
        if (!query) {
            this.speak('Please enter a search query');
            return;
        }

        this.currentQuery = query;
        this.showProcessingPage(query);
        await this.runAgentWorkflow(query);
    }

    showProcessingPage(query) {
        this.voicePage.classList.add('hidden');
        this.memoryPage.classList.add('hidden');
        this.processingPage.classList.remove('hidden');

        if (query) {
            this.queryDisplay.textContent = `"${query}"`;
        }

        this.agentsTimeline.innerHTML = '';
        this.resultsSection.innerHTML = '';
        window.scrollTo(0, 0);
    }

    showVoicePage() {
        this.processingPage.classList.add('hidden');
        this.memoryPage.classList.add('hidden');
        this.voicePage.classList.remove('hidden');
        this.textInput.value = '';
        this.transcript.textContent = '';
        this.textInput.focus();
        this.speak('Back to search');
    }

    showMemoryPage(photo) {
        this.processingPage.classList.add('hidden');
        this.voicePage.classList.add('hidden');
        this.memoryPage.classList.remove('hidden');

        this.memoryQueryDisplay.textContent = photo.title;
        this.memoryPhoto.src = photo.image_url || photo.url;
        this.memoryPhoto.alt = photo.description;

        this.memoryAgentsTimeline.innerHTML = '';
        this.narrationSection.classList.add('hidden');
        document.getElementById('memory-loading').classList.remove('hidden');

        this.speak(`Generating story for ${photo.title}`);
        this.generateMemoryStory(photo);
        window.scrollTo(0, 0);
    }

    async runAgentWorkflow(query) {
        try {
            // Step 1: Voice Processing
            const voiceResult = await this.showAgentStep({
                name: 'Voice Processing',
                icon: '🎤',
                status: 'Analyzing language...',
                action: async () => {
                    const response = await fetch('/api/voice/process', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: query })
                    });
                    return await response.json();
                }
            });

            // Step 2: Vector Search
            const searchResult = await this.showAgentStep({
                name: 'Vector Search',
                icon: '🔍',
                status: 'Searching memories...',
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

            // Display Results
            await this.displayResults(searchResult);

            if (searchResult.success && searchResult.photos.length > 0) {
                const count = searchResult.photos.length;
                const topResult = searchResult.photos[0];
                this.speak(`Found ${count} precious ${count === 1 ? 'memory' : 'memories'}. The first one is: ${topResult.title}. ${topResult.description}`);
            } else {
                this.speak('No memories found for that search. Try describing it differently or use different keywords.');
            }

        } catch (error) {
            console.error('Workflow error:', error);
            this.speak('An error occurred. Please try again.');
        }
    }

    async showAgentStep({ name, icon, status, action }) {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'glass rounded-2xl p-5 animate-fade-in';

        stepDiv.innerHTML = `
            <div class="flex items-center gap-4">
                <div class="text-3xl">${icon}</div>
                <div class="flex-1">
                    <h3 class="text-lg font-semibold text-gray-900 mb-1">${name}</h3>
                    <div class="flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full bg-gray-800 animate-pulse status-indicator"></div>
                        <span class="text-sm text-gray-600 status-text">${status}</span>
                    </div>
                </div>
            </div>
        `;

        this.agentsTimeline.appendChild(stepDiv);
        await this.sleep(400);

        const result = await action();

        const statusIndicator = stepDiv.querySelector('.status-indicator');
        const statusText = stepDiv.querySelector('.status-text');

        statusIndicator.classList.remove('bg-gray-800', 'animate-pulse');
        statusIndicator.classList.add('bg-gray-600');
        statusText.textContent = '✓ Complete';

        await this.sleep(200);
        return result;
    }

    async displayResults(searchResult) {
        if (!searchResult.success || !searchResult.photos.length) {
            this.resultsSection.innerHTML = `
                <div class="glass-strong rounded-2xl p-16 text-center">
                    <div class="text-5xl mb-4 opacity-30">🔍</div>
                    <h3 class="text-2xl font-bold mb-2 text-gray-900">No Results</h3>
                    <p class="text-gray-600">Try a different search query</p>
                </div>
            `;
            return;
        }

        const photos = searchResult.photos;
        this.searchResults = photos;

        this.resultsSection.innerHTML = `
            <div class="mb-8 animate-fade-in">
                <h3 class="text-3xl font-bold mb-2 text-gray-900">📸 Your Memories</h3>
                <p class="text-gray-600">${photos.length} precious ${photos.length === 1 ? 'moment' : 'moments'} rediscovered</p>
            </div>
            <div class="space-y-3" id="results-list"></div>
        `;

        const list = document.getElementById('results-list');

        photos.forEach((photo, index) => {
            const confidence = (photo.similarity_score || 0.5) * 100;

            const item = document.createElement('div');
            item.className = 'experience-item glass-strong rounded-xl p-6 border-l-4 border-transparent animate-slide-in';
            item.style.animationDelay = `${index * 0.1}s`;

            item.innerHTML = `
                <div class="flex items-center justify-between gap-6">
                    <div class="flex-1 min-w-0">
                        <h4 class="text-xl font-bold text-gray-900 mb-2 truncate">${photo.title}</h4>
                        <p class="text-gray-600 text-sm mb-3 line-clamp-2">${photo.description}</p>

                        <div class="flex items-center gap-3">
                            <span class="text-xs text-gray-500 uppercase tracking-wide">Match</span>
                            <div class="flex-1 bg-gray-200 rounded-full h-2 max-w-xs overflow-hidden">
                                <div class="h-2 rounded-full bg-gradient-to-r from-gray-800 to-gray-600 progress-fill" style="--progress-width: ${confidence}%; width: ${confidence}%"></div>
                            </div>
                            <span class="text-sm font-bold text-gray-900">${confidence.toFixed(0)}%</span>
                        </div>
                    </div>

                    <button
                        class="generate-btn flex-shrink-0 bg-gradient-to-r from-gray-800 to-gray-600 text-white px-6 py-3 rounded-xl font-semibold transition-all hover:scale-105 hover-lift whitespace-nowrap"
                        data-photo-index="${index}"
                        aria-label="Generate story for ${photo.title}"
                    >
                        Generate Story
                    </button>
                </div>
            `;

            // Click title/description to hear it
            const titleEl = item.querySelector('h4');
            const descEl = item.querySelector('p');
            [titleEl, descEl].forEach(el => {
                el.addEventListener('click', () => {
                    this.speak(`${photo.title}. ${photo.description}`);
                });
                el.style.cursor = 'pointer';
            });

            // Generate button
            const btn = item.querySelector('.generate-btn');
            btn.addEventListener('click', () => {
                this.showMemoryPage(photo);
            });

            list.appendChild(item);
        });
    }

    async generateMemoryStory(photo) {
        try {
            // Show agent steps
            await this.showMemoryAgentStep({
                name: 'Perception',
                icon: '👁️',
                status: 'Analyzing image...',
                timeline: this.memoryAgentsTimeline
            });

            await this.showMemoryAgentStep({
                name: 'Emotion',
                icon: '💭',
                status: 'Detecting mood...',
                timeline: this.memoryAgentsTimeline
            });

            await this.showMemoryAgentStep({
                name: 'Narration',
                icon: '📖',
                status: 'Writing story...',
                timeline: this.memoryAgentsTimeline
            });

            // Call API
            const response = await fetch('/api/story/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ photo_url: photo.image_url || photo.url })
            });

            const result = await response.json();

            if (result.success) {
                this.speak('Story complete');
                this.displayNarration(result.narration, result.person_dialogues);

                // Store audio URLs for playback
                this.storyAudioUrls = [];

                // Add dialogue audios if available
                if (result.person_dialogues && result.person_dialogues.length > 0) {
                    result.person_dialogues.forEach(dialogue => {
                        if (dialogue.audio_url) {
                            this.storyAudioUrls.push({
                                type: 'dialogue',
                                url: dialogue.audio_url,
                                text: dialogue.text
                            });
                        }
                    });
                }

                // Add main narration audio
                if (result.narration && result.narration.audio_url) {
                    this.storyAudioUrls.push({
                        type: 'narration',
                        url: result.narration.audio_url,
                        text: result.narration.main_narration
                    });
                }

                this.currentAudioUrl = result.narration?.audio_url || null;
            } else {
                throw new Error(result.message || 'Story generation failed');
            }

        } catch (error) {
            console.error('Story error:', error);
            this.speak('Unable to generate story. Please try again.');
            this.narrationText.innerHTML = `<p class="text-red-600">Error: ${error.message}</p>`;
            document.getElementById('memory-loading').classList.add('hidden');
            this.narrationSection.classList.remove('hidden');
        }
    }

    async showMemoryAgentStep({ name, icon, status, timeline }) {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'glass rounded-xl p-4 animate-fade-in';

        stepDiv.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="text-2xl">${icon}</div>
                <div class="flex-1">
                    <h4 class="text-sm font-semibold text-gray-900 mb-1">${name}</h4>
                    <div class="flex items-center gap-2">
                        <div class="w-1.5 h-1.5 rounded-full bg-gray-800 animate-pulse status-indicator"></div>
                        <span class="text-xs text-gray-600 status-text">${status}</span>
                    </div>
                </div>
            </div>
        `;

        timeline.appendChild(stepDiv);
        await this.sleep(1000);

        const statusIndicator = stepDiv.querySelector('.status-indicator');
        const statusText = stepDiv.querySelector('.status-text');

        statusIndicator.classList.remove('bg-gray-800', 'animate-pulse');
        statusIndicator.classList.add('bg-gray-600');
        statusText.textContent = '✓ Done';

        await this.sleep(150);
    }

    displayNarration(narrationData, personDialogues = []) {
        document.getElementById('memory-loading').classList.add('hidden');

        let html = '';

        // Display person dialogues first if available
        if (personDialogues && personDialogues.length > 0) {
            html += `<div class="mb-6 space-y-3">`;
            personDialogues.forEach((dialogue, idx) => {
                const voiceLabel = idx === 0 ? 'Voice 1' : 'Voice 2';
                html += `
                    <div class="pl-4 border-l-4 border-gray-800 italic">
                        <p class="text-gray-900 font-medium">"${dialogue.text}"</p>
                        <span class="text-gray-500 text-xs">— ${voiceLabel}</span>
                    </div>
                `;
            });
            html += `</div>`;
        }

        // Then display main narration
        html += `<p class="text-gray-900 leading-relaxed">${narrationData.main_narration}</p>`;

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
            }
        } catch (error) {
            console.error('TTS error:', error);
        }
    }

    async playNarrationAudio() {
        // Play all story audios in sequence (dialogues first, then main narration)
        if (this.storyAudioUrls && this.storyAudioUrls.length > 0) {
            // Play directly without announcement
            for (const audioInfo of this.storyAudioUrls) {
                await this.playAudio(audioInfo.url);
            }

            return;
        }

        // Fallback to current audio URL
        if (!this.currentAudioUrl) {
            this.speak('Audio not available yet');
            return;
        }

        if (this.ttsAudio.paused) {
            this.ttsAudio.src = this.currentAudioUrl;
            this.ttsAudio.play();

            this.playAudioButton.innerHTML = `
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                    <rect x="6" y="4" width="4" height="16"/>
                    <rect x="14" y="4" width="4" height="16"/>
                </svg>
                ⏸ Pause Story
            `;

            this.ttsAudio.onended = () => {
                this.resetAudioButton();
            };
        } else {
            this.ttsAudio.pause();
            this.resetAudioButton();
        }
    }

    resetAudioButton() {
        this.playAudioButton.innerHTML = `
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            🎧 Play Full Memory Story
        `;
    }

    playAudio(audioUrl) {
        return new Promise((resolve, reject) => {
            const audio = new Audio(audioUrl);

            audio.onended = () => {
                console.log('Audio finished:', audioUrl);
                resolve();
            };

            audio.onerror = (error) => {
                console.error('Audio playback error:', error);
                reject(error);
            };

            audio.play().catch(err => {
                console.error('Failed to play audio:', err);
                reject(err);
            });
        });
    }

    speak(text) {
        if (!this.synthesis) return;

        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.95;
        utterance.pitch = 1;
        utterance.volume = 0.9;

        this.synthesis.speak(utterance);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    new SynesthesiaApp();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const backBtn = document.getElementById('back-button');
        const memoryBackBtn = document.getElementById('memory-back-button');

        if (!backBtn.parentElement.classList.contains('hidden')) {
            backBtn.click();
        } else if (!memoryBackBtn.parentElement.classList.contains('hidden')) {
            memoryBackBtn.click();
        }
    }

    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const input = document.getElementById('text-input');
        if (input && !input.closest('.hidden')) {
            input.focus();
        }
    }
});
