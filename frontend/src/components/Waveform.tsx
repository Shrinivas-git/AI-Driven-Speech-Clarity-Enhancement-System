import React, { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";

interface WaveformProps {
  audioUrl: string | null;
}

export const Waveform: React.FC<WaveformProps> = ({ audioUrl }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Skip waveform for blob URLs (recordings) - they can cause issues
    if (!audioUrl || audioUrl.startsWith("blob:")) {
      if (wavesurferRef.current) {
        try {
          wavesurferRef.current.destroy();
        } catch (e) {
          // Ignore errors during cleanup
        }
        wavesurferRef.current = null;
      }
      return;
    }

    if (!containerRef.current) {
      return;
    }

    // Clean up previous instance
    if (wavesurferRef.current) {
      try {
        wavesurferRef.current.destroy();
      } catch (e) {
        // Ignore errors during cleanup
      }
      wavesurferRef.current = null;
    }

    setIsLoading(true);
    setError(null);

    let ws: WaveSurfer | null = null;
    let isMounted = true;

    try {
      ws = WaveSurfer.create({
        container: containerRef.current,
        waveColor: "#64748b",
        progressColor: "#0ea5e9",
        cursorColor: "#e5e7eb",
        barWidth: 2,
        height: 80,
        responsive: true,
        normalize: true,
      });

      // Handle loading errors
      ws.on("error", (err) => {
        if (isMounted) {
          console.error("WaveSurfer error:", err);
          setError("Failed to load audio waveform");
          setIsLoading(false);
        }
      });

      // Handle successful load
      ws.on("ready", () => {
        if (isMounted) {
          setIsLoading(false);
          setError(null);
        }
      });

      // Load the audio
      ws.load(audioUrl).catch((err) => {
        if (isMounted) {
          console.error("Failed to load audio:", err);
          setError("Failed to load audio");
          setIsLoading(false);
        }
      });

      wavesurferRef.current = ws;
    } catch (err) {
      if (isMounted) {
        console.error("Failed to create WaveSurfer:", err);
        setError("Failed to initialize waveform");
        setIsLoading(false);
      }
    }

    return () => {
      isMounted = false;
      // Cleanup on unmount or audioUrl change
      if (wavesurferRef.current) {
        try {
          wavesurferRef.current.destroy();
        } catch (e) {
          // Ignore errors during cleanup
        }
        wavesurferRef.current = null;
      }
    };
  }, [audioUrl]);

  if (error) {
    return <div style={{ color: "#ef4444", fontSize: "0.875rem" }}>{error}</div>;
  }

  if (isLoading) {
    return <div style={{ color: "#64748b", fontSize: "0.875rem" }}>Loading waveform...</div>;
  }

  return <div ref={containerRef} />;
};






