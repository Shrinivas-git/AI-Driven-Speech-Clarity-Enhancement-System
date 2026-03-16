import React, { useState, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiUtils } from '../utils/api';
import { Waveform } from '../components/Waveform';
import {
  CloudArrowUpIcon,
  MicrophoneIcon,
  StopIcon,
  PlayIcon,
  ArrowDownTrayIcon,
  DocumentTextIcon,
  SpeakerWaveIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

// Helper function to convert AudioBuffer to WAV Blob
function audioBufferToWav(buffer: AudioBuffer): Blob {
  const length = buffer.length;
  const numberOfChannels = buffer.numberOfChannels;
  const sampleRate = buffer.sampleRate;
  const arrayBuffer = new ArrayBuffer(44 + length * numberOfChannels * 2);
  const view = new DataView(arrayBuffer);
  
  // WAV header
  const writeString = (offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };
  
  writeString(0, 'RIFF');
  view.setUint32(4, 36 + length * numberOfChannels * 2, true);
  writeString(8, 'WAVE');
  writeString(12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
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
  
  return new Blob([arrayBuffer], { type: 'audio/wav' });
}

type OutputMode = "audio" | "text" | "both";
type FluencyMetrics = {
  before: {
    repetitions: number;
    fillers: number;
    pauses: number;
    grammar_errors?: number;
    total_words: number;
    fluency_score: number;
  };
  after: {
    repetitions: number;
    fillers: number;
    pauses: number;
    grammar_errors?: number;
    total_words: number;
    fluency_score: number;
  };
  improvement: {
    repetitions_reduced: number;
    fillers_reduced: number;
    grammar_errors_fixed?: number;
    score_improvement: number;
  };
};

export const ProcessAudioPage: React.FC = () => {
  const { usageInfo, refreshUsage } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [originalUrl, setOriginalUrl] = useState<string | null>(null);
  const [enhancedUrl, setEnhancedUrl] = useState<string | null>(null);
  const [cleanedText, setCleanedText] = useState<string>("");
  const [rawText, setRawText] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [outputMode, setOutputMode] = useState<OutputMode>("both");
  const [realtimeMode, setRealtimeMode] = useState<boolean>(false);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [metrics, setMetrics] = useState<FluencyMetrics | null>(null);
  const [showMetrics, setShowMetrics] = useState<boolean>(true);
  const [grammarCorrection, setGrammarCorrection] = useState<boolean>(true);
  const [processingProgress, setProcessingProgress] = useState<string>("");
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setEnhancedUrl(null);
      setCleanedText("");
      setRawText("");
      setMetrics(null);
      setError(null);
      const url = URL.createObjectURL(f);
      setOriginalUrl(url);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const f = files[0];
      if (f.type.startsWith('audio/')) {
        setFile(f);
        setEnhancedUrl(null);
        setCleanedText("");
        setRawText("");
        setMetrics(null);
        setError(null);
        const url = URL.createObjectURL(f);
        setOriginalUrl(url);
      } else {
        toast.error('Please upload an audio file');
      }
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        // Convert WebM to WAV for better compatibility
        try {
          const audioContext = new AudioContext();
          const arrayBuffer = await audioBlob.arrayBuffer();
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
          const wavBlob = audioBufferToWav(audioBuffer);
          
          const file = new File([wavBlob], 'recording.wav', { type: 'audio/wav' });
          setFile(file);
          const url = URL.createObjectURL(wavBlob);
          setOriginalUrl(url);
          
          // Auto-process if realtime mode is enabled
          if (realtimeMode) {
            processAudio(file);
          }
        } catch (error) {
          console.error('Audio conversion failed:', error);
          toast.error('Failed to process recording');
        }
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      
      // Auto-stop after 10 seconds for realtime mode
      if (realtimeMode) {
        setTimeout(() => {
          if (mediaRecorderRef.current && isRecording) {
            stopRecording();
          }
        }, 10000);
      }
    } catch (error) {
      console.error('Recording failed:', error);
      toast.error('Failed to start recording. Please check microphone permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async (audioFile?: File) => {
    const fileToProcess = audioFile || file;
    if (!fileToProcess) {
      toast.error('Please select an audio file first');
      return;
    }

    // Check usage limits
    if (usageInfo && !usageInfo.is_premium && usageInfo.remaining_uses <= 0) {
      toast.error('Usage limit exceeded. Please upgrade to premium for unlimited access.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setProcessingProgress("Uploading file...");

    try {
      const formData = new FormData();
      formData.append('file', fileToProcess);
      formData.append('output_mode', outputMode);
      formData.append('calculate_metrics', showMetrics.toString());
      formData.append('grammar_correction', grammarCorrection.toString());
      formData.append('realtime', realtimeMode.toString());

      setProcessingProgress("Processing audio...");
      
      const response = await apiUtils.enhanceSpeech(formData);
      const result = response.data;

      // Update results
      if (result.cleaned_text) {
        setCleanedText(result.cleaned_text);
      }
      if (result.raw_text) {
        setRawText(result.raw_text);
      }
      if (result.enhanced_audio_filename) {
        setEnhancedUrl(`http://localhost:8000/download/${result.enhanced_audio_filename}`);
      }
      if (result.fluency_metrics) {
        setMetrics(result.fluency_metrics);
      }

      // Refresh usage info
      await refreshUsage();

      toast.success(result.message || 'Audio processed successfully!');
      
    } catch (error: any) {
      console.error('Processing failed:', error);
      
      if (error.response?.status === 402) {
        const detail = error.response.data?.detail;
        if (typeof detail === 'object' && detail.upgrade_required) {
          setError(detail.message || 'Usage limit exceeded. Please upgrade to premium.');
        } else {
          setError('Usage limit exceeded. Please upgrade to premium.');
        }
      } else {
        const message = error.response?.data?.detail || 'Processing failed. Please try again.';
        setError(message);
        toast.error(message);
      }
    } finally {
      setIsLoading(false);
      setProcessingProgress("");
    }
  };

  const downloadAudio = async () => {
    if (!enhancedUrl) return;
    
    try {
      const filename = enhancedUrl.split('/').pop();
      if (!filename) return;
      
      const response = await apiUtils.downloadAudio(filename);
      const blob = response.data;
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Audio downloaded successfully');
    } catch (error) {
      console.error('Download failed:', error);
      toast.error('Failed to download audio');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Process Audio</h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Upload an audio file or record directly to enhance speech clarity
          </p>
          
          {/* Usage indicator */}
          {usageInfo && !usageInfo.is_premium && (
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md">
              <p className="text-sm text-blue-700 dark:text-blue-300">
                <span className="font-medium">{usageInfo.remaining_uses}</span> free uses remaining.
                {usageInfo.remaining_uses <= 3 && (
                  <span className="ml-2 text-blue-600 dark:text-blue-400">
                    Consider upgrading to premium for unlimited usage.
                  </span>
                )}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Settings */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Processing Options</h3>
          
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {/* Output Mode */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Output Mode
              </label>
              <select
                value={outputMode}
                onChange={(e) => setOutputMode(e.target.value as OutputMode)}
                className="form-input dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="both">Audio + Text</option>
                <option value="audio">Audio Only</option>
                <option value="text">Text Only</option>
              </select>
            </div>

            {/* Realtime Mode */}
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={realtimeMode}
                  onChange={(e) => setRealtimeMode(e.target.checked)}
                  className="rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Real-time Mode</span>
              </label>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Auto-process 10-second recordings
              </p>
            </div>

            {/* Show Metrics */}
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={showMetrics}
                  onChange={(e) => setShowMetrics(e.target.checked)}
                  className="rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Calculate Metrics</span>
              </label>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Show fluency improvement scores
              </p>
            </div>

            {/* Grammar Correction */}
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={grammarCorrection}
                  onChange={(e) => setGrammarCorrection(e.target.checked)}
                  className="rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Grammar Correction</span>
              </label>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Fix grammar errors in transcript
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* File Upload / Recording */}
      <div className="bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* File Upload */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 text-center">Upload Audio File</h3>
              <div
                className="cursor-pointer transition-transform hover:scale-105 flex items-center justify-center py-8"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => fileInputRef.current?.click()}
              >
                <img 
                  src="/pic4.png" 
                  alt="Upload Audio" 
                  className="h-64 w-64 object-contain"
                />
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="audio/*"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>
              
              {file && (
                <div className="mt-4 p-3 bg-white dark:bg-gray-700 rounded-md shadow-sm">
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    <span className="font-medium">Selected:</span> {file.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Size: {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              )}
            </div>

            {/* Recording */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 text-center">Record Audio</h3>
              <div className="text-center">
                <div 
                  className="cursor-pointer transition-transform hover:scale-105 flex items-center justify-center py-8 relative"
                  onClick={() => {
                    if (!isRecording) {
                      startRecording();
                    } else {
                      stopRecording();
                    }
                  }}
                >
                  <img 
                    src="/pic3.png" 
                    alt="Record Audio" 
                    className="h-64 w-64 object-contain"
                  />
                  {isRecording && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="flex flex-col items-center">
                        <div className="w-6 h-6 bg-red-500 rounded-full animate-pulse mb-2"></div>
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 px-3 py-1 rounded-full shadow-lg">
                          Recording...
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Process Button */}
          {file && (
            <div className="mt-6 text-center">
              <button
                onClick={() => processAudio()}
                disabled={isLoading}
                className="btn-primary"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {processingProgress || 'Processing...'}
                  </>
                ) : (
                  <>
                    <SpeakerWaveIcon className="h-4 w-4 mr-2" />
                    Process Audio
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Processing Error</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {(cleanedText || enhancedUrl || metrics) && (
        <div className="space-y-6">
          {/* Audio Results */}
          {(originalUrl || enhancedUrl) && (
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Audio Results</h3>
                
                <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                  {originalUrl && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Original Audio</h4>
                      <audio controls className="w-full">
                        <source src={originalUrl} type="audio/wav" />
                        Your browser does not support the audio element.
                      </audio>
                      <Waveform audioUrl={originalUrl} />
                    </div>
                  )}
                  
                  {enhancedUrl && (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Enhanced Audio</h4>
                        <button
                          onClick={downloadAudio}
                          className="inline-flex items-center px-2 py-1 text-xs font-medium text-primary-600 dark:text-primary-400 hover:text-primary-500"
                        >
                          <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                          Download
                        </button>
                      </div>
                      <audio controls className="w-full">
                        <source src={enhancedUrl} type="audio/wav" />
                        Your browser does not support the audio element.
                      </audio>
                      <Waveform audioUrl={enhancedUrl} />
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Text Results */}
          {(rawText || cleanedText) && (
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Text Results</h3>
                
                <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                  {rawText && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Original Transcript</h4>
                      <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-md border dark:border-gray-600">
                        <p className="text-sm text-gray-700 dark:text-gray-300">{rawText}</p>
                      </div>
                    </div>
                  )}
                  
                  {cleanedText && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Cleaned Transcript</h4>
                      <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-md border border-green-200 dark:border-green-800">
                        <p className="text-sm text-gray-700 dark:text-gray-300">{cleanedText}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Fluency Metrics */}
          {metrics && (
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Fluency Metrics</h3>
                
                <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                  {/* Before Metrics */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Before Enhancement</h4>
                    <div className="metrics-grid">
                      <div className="metric-card">
                        <div className="metric-value text-red-600">{metrics.before.repetitions}</div>
                        <div className="metric-label">Repetitions</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-value text-red-600">{metrics.before.fillers}</div>
                        <div className="metric-label">Fillers</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-value text-red-600">{metrics.before.pauses}</div>
                        <div className="metric-label">Pauses</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-value text-red-600">{metrics.before.grammar_errors || 0}</div>
                        <div className="metric-label">Grammar Errors</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-value text-blue-600">{metrics.before.fluency_score.toFixed(1)}%</div>
                        <div className="metric-label">Fluency Score</div>
                      </div>
                    </div>
                  </div>

                  {/* After Metrics */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">After Enhancement</h4>
                    <div className="metrics-grid">
                      <div className="metric-card">
                        <div className="metric-value text-green-600">{metrics.after.repetitions}</div>
                        <div className="metric-label">Repetitions</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-value text-green-600">{metrics.after.fillers}</div>
                        <div className="metric-label">Fillers</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-value text-green-600">{metrics.after.pauses}</div>
                        <div className="metric-label">Pauses</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-value text-green-600">{metrics.after.grammar_errors || 0}</div>
                        <div className="metric-label">Grammar Errors</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-value text-green-600">{metrics.after.fluency_score.toFixed(1)}%</div>
                        <div className="metric-label">Fluency Score</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Improvement Summary */}
                <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md">
                  <div className="flex items-center">
                    <ChartBarIcon className="h-5 w-5 text-green-600 dark:text-green-400 mr-2" />
                    <h4 className="text-sm font-medium text-green-800 dark:text-green-300">Improvement Summary</h4>
                  </div>
                  <div className="mt-2 text-sm text-green-700 dark:text-green-400">
                    <p>
                      Fluency improved by <span className="font-medium">+{metrics.improvement.score_improvement.toFixed(1)}%</span>
                    </p>
                    <p>
                      Reduced {metrics.improvement.repetitions_reduced} repetitions and {metrics.improvement.fillers_reduced} filler words
                      {metrics.improvement.grammar_errors_fixed !== undefined && metrics.improvement.grammar_errors_fixed > 0 && (
                        <>, fixed {metrics.improvement.grammar_errors_fixed} grammar errors</>
                      )}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};