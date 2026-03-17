<<<<<<< HEAD
import React, { useState, useRef } from "react";
import { Waveform } from "./components/Waveform";

// Types
type OutputMode = "audio" | "text" | "both";

interface FluencyMetrics {
  fluency_score: number;
  repetitions: number;
  fillers: number;
  pauses: number;
  total_words: number;
}

interface FluencyComparison {
  before: FluencyMetrics;
  after: FluencyMetrics;
  improvement: {
    score_improvement: number;
    repetitions_reduced: number;
    fillers_reduced: number;
  };
}

// Audio buffer to WAV conversion utility
function audioBufferToWav(buffer: AudioBuffer): Blob {
  const length = buffer.length;
  const arrayBuffer = new ArrayBuffer(44 + length * 2);
  const view = new DataView(arrayBuffer);
  const channels = buffer.numberOfChannels;
  const sampleRate = buffer.sampleRate;

=======
import React, { useState, useEffect, useRef } from "react";
import { Waveform } from "./components/Waveform";

// Helper function to convert AudioBuffer to WAV Blob
function audioBufferToWav(buffer: AudioBuffer): Blob {
  const length = buffer.length;
  const numberOfChannels = buffer.numberOfChannels;
  const sampleRate = buffer.sampleRate;
  const arrayBuffer = new ArrayBuffer(44 + length * numberOfChannels * 2);
  const view = new DataView(arrayBuffer);
  
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
  // WAV header
  const writeString = (offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };
<<<<<<< HEAD

  writeString(0, 'RIFF');
  view.setUint32(4, 36 + length * 2, true);
=======
  
  writeString(0, 'RIFF');
  view.setUint32(4, 36 + length * numberOfChannels * 2, true);
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
  writeString(8, 'WAVE');
  writeString(12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
<<<<<<< HEAD
  view.setUint16(22, channels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(36, 'data');
  view.setUint32(40, length * 2, true);

  // Convert audio data
  const channelData = buffer.getChannelData(0);
  let offset = 44;
  for (let i = 0; i < length; i++) {
    const sample = Math.max(-1, Math.min(1, channelData[i]));
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
    offset += 2;
  }

=======
  view.setUint16(22, numberOfChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * numberOfChannels * 2, true);
  view.setUint16(32, numberOfChannels * 2, true);
  view.setUint16(34, 16, true);
  writeString(36, 'data');
  view.setUint32(40, length * numberOfChannels * 2, true);
  
  // Convert float samples to 16-bit PCM
  let offset = 44;
  for (let i = 0; i < length; i++) {
    for (let channel = 0; channel < numberOfChannels; channel++) {
      const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
      offset += 2;
    }
  }
  
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
  return new Blob([arrayBuffer], { type: 'audio/wav' });
}

const API_BASE = "http://localhost:8000";

<<<<<<< HEAD
=======
type OutputMode = "audio" | "text" | "both";
type FluencyMetrics = {
  before: {
    repetitions: number;
    fillers: number;
    pauses: number;
    total_words: number;
    fluency_score: number;
  };
  after: {
    repetitions: number;
    fillers: number;
    pauses: number;
    total_words: number;
    fluency_score: number;
  };
  improvement: {
    repetitions_reduced: number;
    fillers_reduced: number;
    score_improvement: number;
  };
};

>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
export const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [originalUrl, setOriginalUrl] = useState<string | null>(null);
  const [enhancedUrl, setEnhancedUrl] = useState<string | null>(null);
  const [cleanedText, setCleanedText] = useState<string>("");
  const [rawText, setRawText] = useState<string>("");
<<<<<<< HEAD
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [outputMode, setOutputMode] = useState<OutputMode>("both");
  const [showMetrics, setShowMetrics] = useState<boolean>(true);
  const [metrics, setMetrics] = useState<FluencyComparison | null>(null);
  const [isDark, setIsDark] = useState<boolean>(false);
  const [realtimeMode, setRealtimeMode] = useState<boolean>(false);
  const [isRecording, setIsRecording] = useState<boolean>(false);
=======
  const [isDark, setIsDark] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [outputMode, setOutputMode] = useState<OutputMode>("both");
  const [realtimeMode, setRealtimeMode] = useState<boolean>(false);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [metrics, setMetrics] = useState<FluencyMetrics | null>(null);
  const [showMetrics, setShowMetrics] = useState<boolean>(true);
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
<<<<<<< HEAD
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      const url = URL.createObjectURL(selectedFile);
      setOriginalUrl(url);
      setError(null);
      setEnhancedUrl(null);
      setCleanedText("");
      setRawText("");
      setMetrics(null);
    }
  };
=======
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setEnhancedUrl(null);
      setCleanedText("");
      setError(null);
      const url = URL.createObjectURL(f);
      setOriginalUrl(url);
    }
  };

>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
  const handleEnhance = async (audioFile?: File) => {
    const fileToProcess = audioFile || file;
    if (!fileToProcess) return;
    
    setIsLoading(true);
    setError(null);
    setMetrics(null);
    setCleanedText("");
    setRawText("");
    setEnhancedUrl(null);

    const form = new FormData();
    form.append("file", fileToProcess);
    form.append("output_mode", outputMode);
    form.append("calculate_metrics", showMetrics ? "true" : "false");
    form.append("realtime", realtimeMode ? "true" : "false");

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 150000);

    try {
      const res = await fetch(`${API_BASE}/enhance-speech`, {
        method: "POST",
        body: form,
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const backendDetail =
          (data && (data.detail || data.message)) ||
          `Backend error (${res.status}): ${res.statusText}`;
        throw new Error(String(backendDetail));
      }

      const data = await res.json();
      
      // Handle different output modes
      if (outputMode === "text" || outputMode === "both") {
        if (data.cleaned_text) {
          setCleanedText(data.cleaned_text);
        }
        if (data.raw_text) {
          setRawText(data.raw_text);
        }
      }
      
      if (outputMode === "audio" || outputMode === "both") {
        if (data.enhanced_audio_filename) {
          const audioUrl = `${API_BASE}/download/${data.enhanced_audio_filename}`;
          setEnhancedUrl(audioUrl);
        }
      }
      
      if (data.fluency_metrics) {
        setMetrics(data.fluency_metrics);
      }
    } catch (err: any) {
      clearTimeout(timeoutId);
      
      if (err.name === "AbortError") {
        setError("Request timed out. The audio processing is taking too long. Please try a shorter audio file.");
      } else if (err.message) {
        setError(err.message);
      } else {
        setError("Failed to process audio. Please check if the backend server is running.");
      }
      
      console.error("Enhancement error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        
        // Stop all tracks first
        stream.getTracks().forEach(track => track.stop());
        
        // Check if we have audio data
        if (audioChunksRef.current.length === 0 || audioBlob.size === 0) {
          setError("Recording failed: No audio data captured. Please try again.");
          setIsRecording(false);
          return;
        }
        
        try {
          // Convert WebM to WAV using Web Audio API for better backend compatibility
          const arrayBuffer = await audioBlob.arrayBuffer();
          const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
          
          // Convert AudioBuffer to WAV
          const wavBlob = audioBufferToWav(audioBuffer);
          const audioFile = new File([wavBlob], "recording.wav", { type: "audio/wav" });
          
          setFile(audioFile);
          const url = URL.createObjectURL(wavBlob);
          setOriginalUrl(url);
          
          // Process the recording
          await handleEnhance(audioFile);
        } catch (err) {
          // Fallback: try sending WebM directly
          console.warn("WAV conversion failed, trying WebM:", err);
          try {
            const audioFile = new File([audioBlob], "recording.webm", { type: "audio/webm" });
            setFile(audioFile);
            const url = URL.createObjectURL(audioBlob);
            setOriginalUrl(url);
            await handleEnhance(audioFile);
          } catch (err2) {
            setError("Failed to process recording. Please try uploading a file instead.");
            console.error("Recording processing error:", err2);
            setIsRecording(false);
          }
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      
      // Auto-stop after 10 seconds (near real-time)
      setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
          mediaRecorderRef.current.stop();
          setIsRecording(false);
        }
      }, 10000);
    } catch (err) {
      setError("Could not access microphone. Please check permissions.");
      console.error("Recording error:", err);
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const toggleTheme = () => setIsDark((prev) => !prev);

  const themeClass = isDark ? "theme-dark" : "theme-light";

  return (
    <div className={themeClass}>
      <div className="app-shell">
        <header className="app-header">
          <div>
            <h1>Speech Clarity Enhancement</h1>
            <p className="subtitle">
              ASR → Intelligent Text Cleaning → TTS for stuttered speech
            </p>
          </div>
          <button className="theme-toggle" onClick={toggleTheme}>
            {isDark ? "Light Mode" : "Dark Mode"}
          </button>
        </header>

        <main className="layout">
          <section className="card upload-card" aria-label="Upload audio">
            <h2>1. Input & Settings</h2>
            
            {/* Real-Time Mode Toggle */}
            <div className="setting-group">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={realtimeMode}
                  onChange={(e) => setRealtimeMode(e.target.checked)}
                  disabled={isLoading || isRecording}
                />
                <span>🎙️ Near Real-Time Mode</span>
              </label>
              {realtimeMode && (
                <p className="helper-small">
                  Record 5-10 seconds of audio for quick processing
                </p>
              )}
            </div>

            {/* Real-Time Recording */}
            {realtimeMode ? (
              <div className="realtime-controls">
                {!isRecording ? (
                  <button
                    className="record-btn"
                    onClick={handleStartRecording}
                    disabled={isLoading}
                  >
                    🎤 Start Recording (10s max)
                  </button>
                ) : (
                  <button
                    className="record-btn recording"
                    onClick={handleStopRecording}
                  >
                    ⏹️ Stop Recording
                  </button>
                )}
              </div>
            ) : (
              <>
                <p className="helper">
                  Supported: FLAC, WAV, MP3. Use stuttered or unclear speech samples.
                </p>
                <label className="upload-box">
                  <span>Choose a file or drag &amp; drop</span>
                  <input
                    type="file"
                    accept="audio/flac,audio/wav,audio/x-wav,audio/mpeg"
                    onChange={handleFileChange}
                    disabled={isLoading || isRecording}
                  />
                </label>
              </>
            )}

            {/* Output Mode Selection */}
            <div className="setting-group">
              <label className="setting-label">Output Mode:</label>
              <div className="radio-group">
                <label className="radio-label">
                  <input
                    type="radio"
                    name="outputMode"
                    value="both"
                    checked={outputMode === "both"}
                    onChange={(e) => setOutputMode(e.target.value as OutputMode)}
                    disabled={isLoading}
                  />
                  <span>🎧 + 📝 Both</span>
                </label>
                <label className="radio-label">
                  <input
                    type="radio"
                    name="outputMode"
                    value="audio"
                    checked={outputMode === "audio"}
                    onChange={(e) => setOutputMode(e.target.value as OutputMode)}
                    disabled={isLoading}
                  />
                  <span>🎧 Audio Only</span>
                </label>
                <label className="radio-label">
                  <input
                    type="radio"
                    name="outputMode"
                    value="text"
                    checked={outputMode === "text"}
                    onChange={(e) => setOutputMode(e.target.value as OutputMode)}
                    disabled={isLoading}
                  />
                  <span>📝 Text Only</span>
                </label>
              </div>
            </div>

            {/* Metrics Toggle */}
            <div className="setting-group">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={showMetrics}
                  onChange={(e) => setShowMetrics(e.target.checked)}
                  disabled={isLoading}
                />
                <span>📊 Calculate Fluency Metrics</span>
              </label>
            </div>

            {originalUrl && (
              <div className="section">
                <h3>Original Audio</h3>
                <audio controls src={originalUrl} className="audio-player" />
                {!realtimeMode && !originalUrl.startsWith("blob:") && (
                  <Waveform audioUrl={originalUrl} />
                )}
                {realtimeMode && originalUrl.startsWith("blob:") && (
                  <p className="helper-small">📹 Recording playback (waveform not available for recordings)</p>
                )}
              </div>
            )}

            <button
              className="primary-btn"
              onClick={() => handleEnhance()}
              disabled={(!file && !realtimeMode) || isLoading || isRecording}
            >
              {isLoading ? (
                <>
                  <span className="spinner" aria-label="Processing" />
                  <span>Processing...</span>
                </>
              ) : (
                <span>Enhance Speech</span>
              )}
            </button>

            {error && <p className="error-text">{error}</p>}
          </section>

          <section className="card output-card" aria-label="Enhanced output">
            <h2>2. Results & Comparison</h2>
            
            {/* Fluency Metrics */}
            {metrics && showMetrics && (
              <div className="metrics-section">
                <h3>📊 Fluency Metrics</h3>
                <div className="metrics-grid">
                  <div className="metric-card before">
                    <h4>Before Processing</h4>
                    <div className="metric-score">{metrics.before.fluency_score.toFixed(1)}%</div>
                    <div className="metric-details">
                      <div>Repetitions: {metrics.before.repetitions}</div>
                      <div>Fillers: {metrics.before.fillers}</div>
                      <div>Pauses: {metrics.before.pauses}</div>
                      <div>Words: {metrics.before.total_words}</div>
                    </div>
                  </div>
                  <div className="metric-card after">
                    <h4>After Processing</h4>
                    <div className="metric-score">{metrics.after.fluency_score.toFixed(1)}%</div>
                    <div className="metric-details">
                      <div>Repetitions: {metrics.after.repetitions}</div>
                      <div>Fillers: {metrics.after.fillers}</div>
                      <div>Pauses: {metrics.after.pauses}</div>
                      <div>Words: {metrics.after.total_words}</div>
                    </div>
                  </div>
                </div>
                <div className="improvement-badge">
                  ✨ Improvement: +{metrics.improvement.score_improvement.toFixed(1)}% 
                  ({metrics.improvement.repetitions_reduced} fewer repetitions, 
                  {metrics.improvement.fillers_reduced} fewer fillers)
                </div>
              </div>
            )}

            {/* Before/After Comparison */}
            <div className="comparison-section">
              {/* Original Transcript */}
              {rawText && (
                <div className="comparison-panel">
                  <h3>📝 Original Transcript</h3>
                  <div className="transcript-box original">
                    <p>{rawText}</p>
                  </div>
                </div>
              )}

              {/* Enhanced Audio */}
              {(outputMode === "audio" || outputMode === "both") && (
                <div className="comparison-panel">
                  <h3>🎧 Enhanced Audio</h3>
                  {enhancedUrl ? (
                    <>
                      <audio controls src={enhancedUrl} className="audio-player" />
                      <a
                        className="secondary-btn"
                        href={enhancedUrl}
                        download="enhanced_speech.wav"
                      >
                        Download Enhanced Audio
                      </a>
                    </>
                  ) : (
                    <p className="placeholder">
                      Enhanced audio will appear here after processing.
                    </p>
                  )}
                </div>
              )}

              {/* Cleaned Transcript */}
              {(outputMode === "text" || outputMode === "both") && (
                <div className="comparison-panel">
                  <h3>✨ Cleaned Transcript</h3>
                  {cleanedText ? (
                    <div className="transcript-box cleaned">
                      <p>{cleanedText}</p>
                    </div>
                  ) : (
                    <p className="placeholder">
                      Clean, fluent text will appear here after processing.
                    </p>
                  )}
                </div>
              )}
            </div>
          </section>
        </main>

        <footer className="app-footer">
          <p>
            Designed for academic evaluation: compare original vs. enhanced
            speech and transcripts easily.
          </p>
        </footer>
      </div>
    </div>
  );
<<<<<<< HEAD
};
=======
};



>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
