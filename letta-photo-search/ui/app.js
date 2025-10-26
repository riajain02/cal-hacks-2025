/**
 * Accessible Photo Search - Frontend Application
 * Features: Voice input/output, screen reader support, keyboard navigation
 */

class PhotoSearchApp {
    constructor() {
        this.searchInput = document.getElementById('search-input');
        this.searchBtn = document.getElementById('search-btn');
        this.voiceBtn = document.getElementById('voice-btn');
        this.statusDiv = document.getElementById('status');
        this.resultsDiv = document.getElementById('results');

        // Voice recognition setup
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;

        this.init();
    }

    init() {
        // Initialize speech recognition
        this.initSpeechRecognition();

        // Event listeners
        this.searchBtn.addEventListener('click', () => this.performSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.performSearch();
        });
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceInput());

        // Welcome message
        this.speak('Welcome to Accessible Photo Search. You can type or use voice to search for photos.');
        this.showStatus('Ready to search. Type your query or click the microphone.', 'success');
    }

    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.searchInput.value = transcript;
                this.speak(`You said: ${transcript}. Searching now.`);
                this.performSearch();
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.speak('Sorry, I could not understand. Please try again.');
                this.stopListening();
            };

            this.recognition.onend = () => {
                this.stopListening();
            };
        } else {
            console.warn('Speech recognition not supported');
            this.voiceBtn.disabled = true;
            this.voiceBtn.title = 'Voice input not supported in this browser';
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
        if (!this.recognition) {
            this.speak('Voice input is not supported in your browser.');
            return;
        }

        this.isListening = true;
        this.voiceBtn.classList.add('listening');
        this.voiceBtn.setAttribute('aria-label', 'Listening... Click to stop');
        this.speak('Listening. Please say your search query.');
        this.showStatus('Listening... Speak your search query now.', 'loading');

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
        this.voiceBtn.classList.remove('listening');
        this.voiceBtn.setAttribute('aria-label', 'Use voice input');
    }

    async performSearch() {
        const query = this.searchInput.value.trim();

        if (!query) {
            this.speak('Please enter a search query.');
            this.showStatus('Please enter a search query.', 'error');
            this.searchInput.focus();
            return;
        }

        this.showStatus(`Searching for "${query}"...`, 'loading');
        this.searchBtn.disabled = true;
        this.resultsDiv.innerHTML = '';

        try {
            // Call backend API
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();

            if (data.success && data.photos.length > 0) {
                this.displayResults(data.photos, query);
                const count = data.photos.length;
                const message = `Found ${count} photo${count > 1 ? 's' : ''} matching "${query}"`;
                this.showStatus(message, 'success');
                this.speak(message + '. Use tab to navigate through the results.');
            } else {
                const message = `No photos found for "${query}". Try a different search term.`;
                this.showStatus(message, 'error');
                this.speak(message);
                this.resultsDiv.innerHTML = `<p class="no-results">${message}</p>`;
            }
        } catch (error) {
            console.error('Search error:', error);
            const message = 'An error occurred while searching. Please try again.';
            this.showStatus(message, 'error');
            this.speak(message);
        } finally {
            this.searchBtn.disabled = false;
        }
    }

    displayResults(photos, query) {
        this.resultsDiv.innerHTML = '';

        photos.forEach((photo, index) => {
            const card = this.createPhotoCard(photo, index);
            this.resultsDiv.appendChild(card);
        });

        // Announce results to screen reader
        this.resultsDiv.setAttribute('aria-label', `${photos.length} photo results for ${query}`);
    }

    createPhotoCard(photo, index) {
        const card = document.createElement('article');
        card.className = 'photo-card';
        card.setAttribute('role', 'article');
        card.setAttribute('tabindex', '0');
        card.setAttribute('aria-label', `Photo ${index + 1}: ${photo.title}`);

        // Create image
        const img = document.createElement('img');
        img.src = photo.image_url || `/api/photo/${photo.id}`;
        img.alt = photo.description;
        img.loading = 'lazy';

        // Create info section
        const info = document.createElement('div');
        info.className = 'photo-info';

        const title = document.createElement('h3');
        title.className = 'photo-title';
        title.textContent = photo.title;

        const description = document.createElement('p');
        description.className = 'photo-description';
        description.textContent = photo.description;

        const tagsContainer = document.createElement('div');
        tagsContainer.className = 'photo-tags';
        tagsContainer.setAttribute('aria-label', 'Photo tags');

        photo.tags.forEach(tag => {
            const tagSpan = document.createElement('span');
            tagSpan.className = 'tag';
            tagSpan.textContent = tag;
            tagsContainer.appendChild(tagSpan);
        });

        // Create speak button
        const speakBtn = document.createElement('button');
        speakBtn.className = 'speak-btn';
        speakBtn.textContent = '🔊 Hear Description';
        speakBtn.setAttribute('aria-label', `Hear description of ${photo.title}`);
        speakBtn.onclick = (e) => {
            e.stopPropagation();
            this.speakPhotoDescription(photo);
        };

        // Assemble card
        info.appendChild(title);
        info.appendChild(description);
        info.appendChild(tagsContainer);
        info.appendChild(speakBtn);

        card.appendChild(img);
        card.appendChild(info);

        // Add click handler to card
        card.onclick = () => {
            this.speakPhotoDescription(photo);
        };

        // Add keyboard support
        card.onkeypress = (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.speakPhotoDescription(photo);
            }
        };

        return card;
    }

    speakPhotoDescription(photo) {
        const description = `${photo.title}. ${photo.description}. Tags: ${photo.tags.join(', ')}.`;
        this.speak(description);
    }

    speak(text) {
        if (!this.synthesis) {
            console.warn('Speech synthesis not available');
            return;
        }

        // Cancel any ongoing speech
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;

        this.synthesis.speak(utterance);
    }

    showStatus(message, type) {
        this.statusDiv.textContent = message;
        this.statusDiv.className = `status show ${type}`;

        // Auto-hide success/error messages after 5 seconds
        if (type !== 'loading') {
            setTimeout(() => {
                this.statusDiv.classList.remove('show');
            }, 5000);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new PhotoSearchApp();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('search-input').focus();
    }

    // Ctrl/Cmd + / for voice input
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        document.getElementById('voice-btn').click();
    }
});
