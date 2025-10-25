'use client';

import { useState, useEffect, useRef } from 'react';
import { ArrowLeft, Play, Pause } from 'lucide-react';

interface MemoryPageProps {
  photo: any;
  onBack: () => void;
}

interface AgentStep {
  name: string;
  icon: string;
  status: 'thinking' | 'complete';
}

export function MemoryPage({ photo, onBack }: MemoryPageProps) {
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [narration, setNarration] = useState<any>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (photo) {
      generateMemoryStory();
    }
  }, [photo]);

  const generateMemoryStory = async () => {
    setIsLoading(true);
    setAgentSteps([]);

    try {
      // Step 1: Perception Agent
      await showAgentStep({
        name: 'Perception Agent',
        icon: '👁️',
        status: 'Analyzing visual content...',
      });

      // Step 2: Emotion Agent
      await showAgentStep({
        name: 'Emotion Agent',
        icon: '💭',
        status: 'Detecting emotions and mood...',
      });

      // Step 3: Narration Agent
      await showAgentStep({
        name: 'Narration Agent',
        icon: '📖',
        status: 'Generating story...',
      });

      // Call backend to generate story
      const response = await fetch('/api/story/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photo_url: photo.url })
      });

      const result = await response.json();

      if (result.success) {
        setNarration(result.narration);
        if (result.narration?.audio_url) {
          setAudioUrl(result.narration.audio_url);
        }
      } else {
        console.error('Story generation failed:', result.message);
      }
    } catch (error) {
      console.error('Error generating memory story:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const showAgentStep = async ({ name, icon, status }: {
    name: string;
    icon: string;
    status: string;
  }) => {
    const step: AgentStep = { name, icon, status: 'thinking' };
    setAgentSteps(prev => [...prev, step]);

    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Mark as complete
    setAgentSteps(prev => prev.map(s =>
      s.name === name ? { ...s, status: 'complete' } : s
    ));

    await new Promise(resolve => setTimeout(resolve, 300));
  };

  const toggleAudio = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Back Button */}
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-300 mb-8 hover:text-white transition-all duration-300 hover:scale-105"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Results
        </button>

        <h2 className="text-3xl font-bold text-white mb-8">
          Memory: <span className="text-white font-light">{photo?.title}</span>
        </h2>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Photo Display */}
          <div className="bg-gray-800/50 backdrop-blur-md border border-gray-600 rounded-2xl overflow-hidden hover:bg-gray-700/50 transition-all duration-300">
            <img
              src={photo?.url}
              alt={photo?.description}
              className="w-full h-auto object-cover"
            />
          </div>

          {/* Agent Timeline */}
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">AI Agent Processing</h3>
            <div className="space-y-4 mb-8">
              {agentSteps.map((step, index) => (
                <div
                  key={index}
                  className="bg-gray-800/50 backdrop-blur-md border border-gray-600 rounded-2xl p-4 animate-fade-in hover:bg-gray-700/50 transition-all duration-300"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="flex items-center gap-4">
                    <div className="text-3xl">{step.icon}</div>
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-white">{step.name}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <div className={`w-2 h-2 rounded-full ${
                          step.status === 'complete' ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'
                        }`} />
                        <span className="text-sm text-gray-300">
                          {step.status === 'complete' ? 'Complete' : 'Processing'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Narration Display */}
            {narration && (
              <div className="bg-gray-800/50 backdrop-blur-md border border-gray-600 rounded-2xl p-6 animate-fade-in hover:bg-gray-700/50 transition-all duration-300">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                  <span>📖</span>
                  Story Narration
                </h3>
                <div className="text-gray-200 space-y-4">
                  <p>{narration.main_narration}</p>

                  {narration.person_dialogues && narration.person_dialogues.length > 0 && (
                    <div className="mt-4 space-y-2">
                      {narration.person_dialogues.map((dialogue: any, index: number) => (
                        <div key={index} className="border-l-4 border-white pl-4 italic">
                          <p>&quot;{dialogue.dialogue}&quot;</p>
                          {dialogue.emotion && (
                            <span className="text-sm text-gray-300">- {dialogue.emotion}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {narration.ambient_descriptions && narration.ambient_descriptions.length > 0 && (
                    <p className="text-sm text-gray-400 italic mt-4">
                      Ambient atmosphere: {narration.ambient_descriptions.join(', ')}
                    </p>
                  )}
                </div>

                {/* Audio Player */}
                {audioUrl && (
                  <div className="mt-6">
                    <button
                      onClick={toggleAudio}
                      className="w-full bg-white text-black py-3 rounded-lg hover:shadow-2xl hover:shadow-white/30 transition-all duration-300 flex items-center justify-center gap-2 hover:scale-105"
                    >
                      {isPlaying ? (
                        <>
                          <Pause className="w-5 h-5" />
                          Pause Audio Narration
                        </>
                      ) : (
                        <>
                          <Play className="w-5 h-5" />
                          Play Audio Narration
                        </>
                      )}
                    </button>
                    <audio
                      ref={audioRef}
                      src={audioUrl}
                      onEnded={() => setIsPlaying(false)}
                      onPlay={() => setIsPlaying(true)}
                      onPause={() => setIsPlaying(false)}
                    />
                  </div>
                )}
              </div>
            )}

            {/* Loading State */}
            {isLoading && !narration && (
              <div className="bg-gray-800/50 backdrop-blur-md border border-gray-600 rounded-2xl p-6 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent mx-auto mb-4"></div>
                <p className="text-gray-300">Generating your memory story...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
