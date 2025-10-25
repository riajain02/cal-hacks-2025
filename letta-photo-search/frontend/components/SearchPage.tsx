'use client';

import { useState, useEffect, useRef } from 'react';
import { Mic, Send, ArrowLeft } from 'lucide-react';

interface SearchPageProps {
  onShowMemory: (photo: any) => void;
}

interface Photo {
  id: number;
  url: string;
  title: string;
  description: string;
  tags: string[];
  similarity_score?: number;
}

interface AgentStep {
  name: string;
  icon: string;
  status: string;
  result?: any;
}

export function SearchPage({ onShowMemory }: SearchPageProps) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [query, setQuery] = useState('');
  const [currentView, setCurrentView] = useState<'voice' | 'processing'>('voice');
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [searchResults, setSearchResults] = useState<Photo[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join('');
        setTranscript(transcript);

        if (event.results[0].isFinal) {
          setQuery(transcript);
          handleSearch(transcript);
        }
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const toggleVoiceInput = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      setTranscript('');
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;

    setIsProcessing(true);
    setCurrentView('processing');
    setAgentSteps([]);
    setSearchResults([]);

    try {
      // Voice Processing Agent
      await showAgentStep({
        name: 'Voice Processing Agent',
        icon: '🎤',
        status: 'Processing natural language...',
        action: async () => {
          const response = await fetch('/api/voice/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: searchQuery })
          });
          return await response.json();
        }
      });

      // Embedding Search Agent
      const searchResult = await showAgentStep({
        name: 'Embedding Search Agent',
        icon: '🔍',
        status: 'Computing vector embeddings...',
        action: async () => {
          const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              query: searchQuery,
              use_voice_processing: true
            })
          });
          return await response.json();
        }
      });

      if (searchResult.success && searchResult.photos) {
        setSearchResults(searchResult.photos);
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const showAgentStep = async ({ name, icon, status, action }: {
    name: string;
    icon: string;
    status: string;
    action: () => Promise<any>;
  }) => {
    const step: AgentStep = { name, icon, status: 'thinking' };
    setAgentSteps(prev => [...prev, step]);

    await new Promise(resolve => setTimeout(resolve, 800));

    const result = await action();

    setAgentSteps(prev => prev.map(s =>
      s.name === name ? { ...s, status: 'complete', result } : s
    ));

    await new Promise(resolve => setTimeout(resolve, 300));

    return result;
  };

  const handleBackClick = () => {
    setCurrentView('voice');
    setQuery('');
    setTranscript('');
    setSearchResults([]);
    setAgentSteps([]);
  };

  return (
    <div className="min-h-screen p-8">
      {currentView === 'voice' ? (
        <div className="max-w-2xl mx-auto">
          {/* Voice Page */}
          <div className="text-center mb-12">
            <div className="mb-8">
              <div className="text-6xl mb-4">🧠</div>
              <h1 className="text-4xl font-bold text-white mb-2">AI Agent Search</h1>
              <p className="text-gray-300">Search memories using natural language</p>
            </div>

            {/* Mic Button */}
            <button
              onClick={toggleVoiceInput}
              className={`relative w-20 h-20 rounded-full mx-auto mb-8 transition-all duration-300 ${
                isListening
                  ? 'bg-white shadow-2xl shadow-white/50 animate-glow-pulse ring-4 ring-white/30 scale-110'
                  : 'bg-gray-800 hover:bg-gray-700 hover:scale-105 hover:shadow-2xl hover:shadow-white/20 border border-gray-600'
              }`}
            >
              <Mic className={`w-8 h-8 mx-auto transition-colors duration-300 ${
                isListening ? 'text-black' : 'text-white'
              }`} />
            </button>

            {/* Status Text */}
            <p className={`text-lg mb-4 ${isListening ? 'text-white animate-pulse' : 'text-gray-400'}`}>
              {isListening ? 'Listening... Speak now' : 'Click to speak or type your query'}
            </p>

            {/* Transcript */}
            {transcript && (
              <p className="text-white text-xl mb-4 min-h-[2rem]">
                {transcript}
              </p>
            )}

            {/* Text Input */}
            <div className="flex gap-4 max-w-lg mx-auto">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch(query)}
                placeholder="Type your search query..."
                className="flex-1 bg-gray-800/50 backdrop-blur-md border border-gray-600 rounded-full px-6 py-4 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-white focus:border-white transition-all duration-300"
              />
              <button
                onClick={() => handleSearch(query)}
                className="bg-white text-black rounded-full p-4 hover:scale-110 transition-all duration-300 hover:shadow-lg hover:shadow-white/20"
              >
                <Send className="w-6 h-6" />
              </button>
            </div>

            {/* Suggestion Buttons */}
            <div className="mt-8 flex flex-wrap gap-3 justify-center">
              {['Happy dog', 'Peaceful sunset', 'City lights', 'Ocean waves'].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setQuery(suggestion);
                    handleSearch(suggestion);
                  }}
                  className="px-6 py-2 bg-gray-800/50 backdrop-blur-md border border-gray-600 rounded-full text-gray-300 hover:bg-gray-700 hover:text-white hover:border-white transition-all duration-300 hover:shadow-lg hover:shadow-white/10 hover:scale-105"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="max-w-6xl mx-auto">
          {/* Processing Page */}
          <button
            onClick={handleBackClick}
            className="flex items-center gap-2 text-gray-300 mb-8 hover:text-white transition-all duration-300 hover:scale-105"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Search
          </button>

          <h2 className="text-3xl font-bold text-white mb-4">
            Searching for: <span className="text-white font-light">{query}</span>
          </h2>

          {/* Agent Timeline */}
          <div className="space-y-4 mb-8">
            {agentSteps.map((step, index) => (
              <div
                key={index}
                className="bg-gray-800/50 backdrop-blur-md border border-gray-600 rounded-2xl p-6 animate-fade-in hover:bg-gray-700/50 transition-all duration-300"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex items-start gap-4">
                  <div className="text-4xl">{step.icon}</div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-white mb-2">{step.name}</h3>
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`w-3 h-3 rounded-full ${
                        step.status === 'complete' ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'
                      }`} />
                      <span className="text-gray-300">
                        {step.status === 'complete' ? 'Complete' : step.status}
                      </span>
                    </div>
                    {step.result && step.name.includes('Voice') && step.result.success && (
                      <div className="mt-3 text-sm text-gray-300 bg-black/20 rounded-lg p-3">
                        <strong>Intent:</strong> {step.result.data?.intent}<br />
                        <strong>Query:</strong> {step.result.data?.search_query}
                      </div>
                    )}
                    {step.result && step.name.includes('Embedding') && step.result.success && (
                      <div className="mt-3 text-sm text-gray-300 bg-black/20 rounded-lg p-3">
                        Found {step.result.photos?.length || 0} matching images
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div>
              <h3 className="text-2xl font-bold text-white mb-6">
                Search Results ({searchResults.length} photos)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {searchResults.map((photo) => (
                  <div
                    key={photo.id}
                    className="bg-gray-800/50 backdrop-blur-md border border-gray-600 rounded-2xl overflow-hidden hover:scale-105 hover:bg-gray-700/50 transition-all duration-300 cursor-pointer animate-slide-in-scale hover:shadow-2xl hover:shadow-white/10"
                    style={{ animationDelay: `${(searchResults.indexOf(photo) * 0.1)}s` }}
                  >
                    <img
                      src={photo.url}
                      alt={photo.description}
                      className="w-full h-48 object-cover"
                    />
                    <div className="p-4">
                      <h4 className="text-lg font-semibold text-white mb-2">{photo.title}</h4>
                      <p className="text-gray-300 text-sm mb-3">{photo.description}</p>
                      <div className="flex flex-wrap gap-2 mb-3">
                        {photo.tags?.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-1 bg-gray-700 rounded-full text-xs text-gray-300 border border-gray-600"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                      {photo.similarity_score && (
                        <div className="mb-3">
                          <div className="flex items-center justify-between text-sm text-gray-300 mb-1">
                            <span>Relevance:</span>
                            <span>{(photo.similarity_score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-white h-2 rounded-full shadow-lg shadow-white/30"
                              style={{ width: `${photo.similarity_score * 100}%` }}
                            />
                          </div>
                        </div>
                      )}
                      <button
                        onClick={() => onShowMemory(photo)}
                        className="w-full bg-white text-black py-2 rounded-lg hover:shadow-2xl hover:shadow-white/30 transition-all duration-300 flex items-center justify-center gap-2 hover:scale-105"
                      >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polygon points="5 3 19 12 5 21 5 3"/>
                        </svg>
                        Generate Memory Story
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
