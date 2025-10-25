# fetch_models.py
from uagents import Model
from typing import List, Dict, Optional

class VisionAnalysisRequest(Model):
    photo_url: str
    session_id: str

class PerceptionData(Model):
    session_id: str
    objects: List[str]
    people_count: int
    people_details: List[Dict]
    layout: Dict[str, str]
    scene_type: str
    setting: str
    colors: List[str]
    lighting: str
    ambient_sounds: List[str]

class EmotionRequest(Model):
    session_id: str
    photo_url: str

class EmotionData(Model):
    session_id: str
    mood: str
    emotion_tags: List[str]
    tone: str
    intensity: str
    voice_characteristics: Dict
    ambient_mood: str

class NarrationRequest(Model):
    session_id: str
    perception: Dict
    emotion: Dict

class NarrationData(Model):
    session_id: str
    main_narration: str
    person_dialogues: List[Dict]
    ambient_descriptions: List[str]

class VoiceRequest(Model):
    session_id: str
    narration_data: Dict
    emotion_data: Dict

class VoiceData(Model):
    session_id: str
    voice_files: List[Dict]  # List of {type, position, url}

class AudioMixRequest(Model):
    session_id: str
    voice_files: List[Dict]
    ambient_sounds: List[str]

class AudioMixData(Model):
    session_id: str
    final_audio_url: str

class ExperienceComplete(Model):
    session_id: str
    perception: Dict
    emotion: Dict
    narration: Dict
    audio_layers: List[Dict]
    final_audio_url: str

class ErrorMessage(Model):
    session_id: str
    error: str
    step: str
