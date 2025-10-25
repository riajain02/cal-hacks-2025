/**
 * Photo Story Generator - Frontend JavaScript
 * Handles photo upload, camera capture, and story generation
 */

// Global state
let selectedFile = null;
let photoUrl = null;

// DOM elements
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const photoPreview = document.getElementById('photo-preview');
const storyDisplay = document.getElementById('story-display');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // Upload area click
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    

    
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
// Validate file type
if (!file.type.startsWith('image/')) {
alert('Please select an image file');
return;
}

selectedFile = file;

// Show preview
const reader = new FileReader();
reader.onload = (e) => {
photoPreview.src = e.target.result;
photoPreview.classList.add('visible');
// Automatically generate story
    generateStory();
};
    reader.readAsDataURL(file);

    console.log('File selected:', file.name);
}



async function generateStory() {
if (!selectedFile) {
alert('Please select a photo first');
return;
}

try {
// Upload photo
const formData = new FormData();
formData.append('photo', selectedFile);

const uploadResponse = await fetch('/api/photos/upload', {
    method: 'POST',
    body: formData
        });

if (!uploadResponse.ok) {
throw new Error('Failed to upload photo');
}

const uploadData = await uploadResponse.json();
console.log('Upload response:', uploadData);

        if (!uploadData.success) {
    throw new Error(uploadData.message || 'Upload failed');
}

photoUrl = uploadData.photo_url;
const photoPath = uploadData.filepath;

        // Generate story
const storyResponse = await fetch('/api/story/generate', {
    method: 'POST',
            headers: {
        'Content-Type': 'application/json'
    },
            body: JSON.stringify({
        photo_url: photoUrl,
        photo_path: photoPath
})
});

if (!storyResponse.ok) {
throw new Error('Failed to generate story');
}

const storyData = await storyResponse.json();
console.log('Story response:', storyData);

if (!storyData.success) {
throw new Error(storyData.message || 'Story generation failed');
}

// Display story
displayStory(storyData);

} catch (error) {
console.error('Error generating story:', error);
alert(`Error: ${error.message}`);
    }
}

function displayStory(data) {
    // Hide progress

    // Display perception data
    const perceptionData = data.emotion?.perception_data || {};
    displayPerceptionData(perceptionData);

    // Display emotion data
    const emotionData = data.emotion || {};
    displayEmotionData(emotionData);

    // Display narration
    const narrationData = data.narration || {};
    displayNarration(narrationData);

    // Show story display
    storyDisplay.classList.add('visible');

    // Scroll to story
    storyDisplay.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayPerceptionData(data) {
    const container = document.getElementById('perception-data');
    container.innerHTML = '';

    // Objects
    if (data.objects && data.objects.length > 0) {
        const objectsDiv = document.createElement('div');
        objectsDiv.className = 'data-item';
        objectsDiv.innerHTML = `
            <div class="data-item-label">Objects Detected</div>
            <div class="tag-list">
                ${data.objects.map(obj => `<span class="tag">${obj}</span>`).join('')}
            </div>
        `;
        container.appendChild(objectsDiv);
    }

    // Scene type
    if (data.scene_type) {
        const sceneDiv = document.createElement('div');
        sceneDiv.className = 'data-item';
        sceneDiv.innerHTML = `
            <div class="data-item-label">Scene Type</div>
            <div class="data-item-value">${data.scene_type}</div>
        `;
        container.appendChild(sceneDiv);
    }

    // Setting
    if (data.setting) {
        const settingDiv = document.createElement('div');
        settingDiv.className = 'data-item';
        settingDiv.innerHTML = `
            <div class="data-item-label">Setting</div>
            <div class="data-item-value">${data.setting}</div>
        `;
        container.appendChild(settingDiv);
    }

    // People count
    if (data.people_count !== undefined) {
        const peopleDiv = document.createElement('div');
        peopleDiv.className = 'data-item';
        peopleDiv.innerHTML = `
            <div class="data-item-label">People</div>
            <div class="data-item-value">${data.people_count} detected</div>
        `;
        container.appendChild(peopleDiv);
    }

    // Colors
    if (data.colors && data.colors.length > 0) {
        const colorsDiv = document.createElement('div');
        colorsDiv.className = 'data-item';
        colorsDiv.innerHTML = `
            <div class="data-item-label">Colors</div>
            <div class="tag-list">
                ${data.colors.map(color => `<span class="tag">${color}</span>`).join('')}
            </div>
        `;
        container.appendChild(colorsDiv);
    }

    // Lighting
    if (data.lighting) {
        const lightingDiv = document.createElement('div');
        lightingDiv.className = 'data-item';
        lightingDiv.innerHTML = `
            <div class="data-item-label">Lighting</div>
            <div class="data-item-value">${data.lighting}</div>
        `;
        container.appendChild(lightingDiv);
    }

    // Ambient sounds
    if (data.ambient_sounds && data.ambient_sounds.length > 0) {
        const soundsDiv = document.createElement('div');
        soundsDiv.className = 'data-item';
        soundsDiv.innerHTML = `
            <div class="data-item-label">Ambient Sounds</div>
            <div class="tag-list">
                ${data.ambient_sounds.map(sound => `<span class="tag">${sound}</span>`).join('')}
            </div>
        `;
        container.appendChild(soundsDiv);
    }
}

function displayEmotionData(data) {
    const container = document.getElementById('emotion-data');
    container.innerHTML = '';

    // Mood
    if (data.mood) {
        const moodDiv = document.createElement('div');
        moodDiv.className = 'data-item';
        moodDiv.innerHTML = `
            <div class="data-item-label">Overall Mood</div>
            <div class="data-item-value">${data.mood}</div>
        `;
        container.appendChild(moodDiv);
    }

    // Tone
    if (data.tone) {
        const toneDiv = document.createElement('div');
        toneDiv.className = 'data-item';
        toneDiv.innerHTML = `
            <div class="data-item-label">Tone</div>
            <div class="data-item-value">${data.tone}</div>
        `;
        container.appendChild(toneDiv);
    }

    // Intensity
    if (data.intensity) {
        const intensityDiv = document.createElement('div');
        intensityDiv.className = 'data-item';
        intensityDiv.innerHTML = `
            <div class="data-item-label">Intensity</div>
            <div class="data-item-value">${data.intensity}</div>
        `;
        container.appendChild(intensityDiv);
    }

    // Ambient mood
    if (data.ambient_mood) {
        const ambientDiv = document.createElement('div');
        ambientDiv.className = 'data-item';
        ambientDiv.innerHTML = `
            <div class="data-item-label">Ambient Mood</div>
            <div class="data-item-value">${data.ambient_mood}</div>
        `;
        container.appendChild(ambientDiv);
    }

    // Emotion tags
    if (data.emotion_tags && data.emotion_tags.length > 0) {
        const tagsDiv = document.createElement('div');
        tagsDiv.className = 'data-item';
        tagsDiv.innerHTML = `
            <div class="data-item-label">Emotion Tags</div>
            <div class="tag-list">
                ${data.emotion_tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
        `;
        container.appendChild(tagsDiv);
    }
}

function displayNarration(data) {
const container = document.getElementById('narration-text');
    const audioPlayer = document.getElementById('audio-player');
const audioSource = document.getElementById('audio-source');

// Main narration
if (data.main_narration) {
        container.innerHTML = `<p>${data.main_narration}</p>`;
}

// Person dialogues
if (data.person_dialogues && data.person_dialogues.length > 0) {
const dialoguesHTML = data.person_dialogues.map(dialogue => `
<p style="margin-top: 1rem; padding-left: 1rem; border-left: 3px solid #c084fc;">
    <em>"${dialogue.dialogue}"</em>
        ${dialogue.emotion ? `<span style="color: #ff6b9d;"> - ${dialogue.emotion}</span>` : ''}
    </p>
    `).join('');
container.innerHTML += dialoguesHTML;
}

// Ambient descriptions
if (data.ambient_descriptions && data.ambient_descriptions.length > 0) {
const ambienceHTML = `
<p style="margin-top: 1.5rem; font-style: italic; color: rgba(255, 255, 255, 0.7);">
        Ambient atmosphere: ${data.ambient_descriptions.join(', ')}
    </p>
    `;
container.innerHTML += ambienceHTML;
}

    // Audio narration
    if (data.audio_url) {
        audioSource.src = data.audio_url;
        audioPlayer.style.display = 'block';
        // Force reload of audio element
        audioPlayer.load();
    } else {
        audioPlayer.style.display = 'none';
    }
}

console.log('Photo Story Generator loaded');
