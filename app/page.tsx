'use client'

import { useState, useRef, useEffect } from 'react'

export default function WisprInterface() {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [transcriptions, setTranscriptions] = useState<Array<{
    id: string
    timestamp: string
    rawText: string
    cleanedText: string
    source?: string
  }>>([
    {
      id: '1',
      timestamp: '2:47 PM',
      rawText: 'Click the microphone to start real transcription with Whisper',
      cleanedText: 'Click the microphone to start real transcription with Whisper.',
      source: 'demo'
    }
  ])

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      setError(null)
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 8000,  // Lower sample rate for faster processing
          channelCount: 1,   // Mono audio
          autoGainControl: true
        } 
      })
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        await sendAudioToBackend(audioBlob)
        
        // Clean up stream
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorder.start()
      setIsRecording(true)
      
    } catch (err) {
      console.error('Error starting recording:', err)
      setError('Microphone access denied. Please allow microphone permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsProcessing(true)
    }
  }

  const sendAudioToBackend = async (audioBlob: Blob) => {
    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')
      
      const response = await fetch('http://localhost:5001/transcribe', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        // Transcription is now automatically stored in backend and will be fetched by polling
        console.log('Transcription successful:', result.cleaned_text)
        // Immediately fetch updated transcriptions
        setTimeout(fetchTranscriptions, 500)
      } else {
        setError(result.error || 'Transcription failed')
      }
    } catch (err) {
      console.error('Error sending audio to backend:', err)
      setError('Failed to connect to transcription service. Make sure the backend is running.')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleMicClick = async () => {
    if (isRecording) {
      stopRecording()
    } else {
      await startRecording()
    }
  }

  const fetchTranscriptions = async () => {
    try {
      const response = await fetch('http://localhost:5001/transcriptions')
      if (response.ok) {
        const result = await response.json()
        if (result.success && result.transcriptions) {
          // Filter out demo transcription and add it back if no real transcriptions exist
          const realTranscriptions = result.transcriptions
          if (realTranscriptions.length === 0) {
            // Keep the demo transcription if no real ones exist
            setTranscriptions([{
              id: '1',
              timestamp: '2:47 PM',
              rawText: 'Click the microphone to start real transcription with Whisper',
              cleanedText: 'Click the microphone to start real transcription with Whisper.',
              source: 'demo'
            }])
          } else {
            setTranscriptions(realTranscriptions)
          }
        }
      }
    } catch (err) {
      console.error('Error fetching transcriptions:', err)
    }
  }

  const clearHistory = async () => {
    try {
      const response = await fetch('http://localhost:5001/clear-history', {
        method: 'POST',
      })
      
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          console.log('History cleared successfully')
          // Refresh the transcriptions list
          fetchTranscriptions()
        }
      } else {
        console.error('Failed to clear history')
      }
    } catch (err) {
      console.error('Error clearing history:', err)
    }
  }

  // Poll for new transcriptions every 2 seconds
  useEffect(() => {
    fetchTranscriptions() // Initial fetch
    const interval = setInterval(fetchTranscriptions, 2000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center justify-center min-h-screen font-light bg-[url(https://images.unsplash.com/photo-1635151227785-429f420c6b9d?w=2160&q=80)] bg-cover">
      {/* Main Container */}
      <div className="relative flex flex-col overflow-hidden cursor-default beautiful-shadow transition-custom max-w-4xl w-full font-semibold text-white rounded-3xl mx-4">
        <div className="absolute z-0 inset-0 backdrop-blur-md glass-filter overflow-hidden isolate"></div>
        <div className="z-10 absolute inset-0 bg-white bg-opacity-15"></div>
        <div 
          className="absolute inset-0 z-20 overflow-hidden shadow-inner rounded-3xl"
          style={{
            boxShadow: 'inset 2px 2px 1px 0 rgba(255, 255, 255, 0.5), inset -1px -1px 1px 1px rgba(255, 255, 255, 0.5)'
          }}
        ></div>
        
        {/* Top Section - Header & Controls */}
        <div className="z-30 flex flex-col relative text-center bg-black/10 pt-8 pr-8 pb-8 pl-8 items-center justify-center">
          {/* Logo & Brand */}
          <div className="mb-6">
            <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 overflow-hidden">
              <div className="absolute z-0 inset-0 backdrop-blur-sm glass-filter"></div>
              <div className="z-10 absolute inset-0 bg-gradient-to-br from-white/30 to-white/10"></div>
              <div 
                className="absolute inset-0 z-20 rounded-2xl"
                style={{
                  boxShadow: 'inset 3px 3px 2px 0 rgba(255, 255, 255, 0.6), inset -2px -2px 2px 2px rgba(255, 255, 255, 0.4)'
                }}
              ></div>
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="z-30 text-white">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
              </svg>
            </div>
            <h1 className="leading-tight text-5xl font-normal text-white tracking-tighter mb-2">Voice Transcription</h1>
            <p className="leading-relaxed text-sm font-light text-white/80">Powered by OpenAI Whisper + DeepSeek V3 for perfect speech-to-text</p>
          </div>

          {/* Microphone Button */}
          <div className="mb-6">
            <button
              onClick={handleMicClick}
              disabled={isProcessing}
              className={`relative overflow-hidden rounded-full cursor-pointer transition-custom hover:shadow-lg w-24 h-24 ${isRecording ? 'pulse-animation mic-glow' : ''}`}
            >
              <div className="absolute z-0 inset-0 backdrop-blur-sm glass-filter"></div>
              <div className={`z-10 absolute inset-0 ${
                isRecording 
                  ? 'bg-gradient-to-r from-red-400/40 to-red-500/30' 
                  : isProcessing 
                    ? 'bg-gradient-to-r from-gray-400/30 to-gray-500/20' 
                    : 'bg-gradient-to-r from-blue-400/40 to-blue-500/30'
              }`}></div>
              <div 
                className="absolute inset-0 z-20 rounded-full"
                style={{
                  boxShadow: 'inset 2px 2px 1px 0 rgba(255, 255, 255, 0.5), inset -1px -1px 1px 1px rgba(255, 255, 255, 0.3)'
                }}
              ></div>
              <div className="z-30 relative w-full h-full flex items-center justify-center text-3xl text-white">
                {isProcessing ? (
                  <div className="w-8 h-8 border-3 border-white/30 border-t-white rounded-full spinning" />
                ) : isRecording ? (
                  '⏹️'
                ) : (
                  '🎤'
                )}
              </div>
            </button>
          </div>

          {/* Status */}
          <div className="text-center mb-4">
            {error && (
              <div className="relative overflow-hidden rounded-xl mb-3 max-w-md">
                <div className="absolute z-0 inset-0 backdrop-blur-sm glass-filter"></div>
                <div className="z-10 absolute inset-0 bg-red-500/20"></div>
                <div 
                  className="absolute inset-0 z-20 rounded-xl"
                  style={{
                    boxShadow: 'inset 1px 1px 1px 0 rgba(255, 255, 255, 0.3), inset -1px -1px 1px 1px rgba(255, 255, 255, 0.1)'
                  }}
                ></div>
                <p className="z-30 relative px-4 py-3 text-sm font-medium text-white">{error}</p>
              </div>
            )}
            {isRecording && (
              <p className="text-red-300 font-medium text-lg">🔴 Recording... Click to stop</p>
            )}
            {isProcessing && (
              <p className="text-blue-300 font-medium text-lg">🔄 Processing with Whisper + DeepSeek...</p>
            )}
            {!isRecording && !isProcessing && !error && (
              <p className="text-white/70 text-lg">Ready to record • Click microphone or press Cmd+Shift+V</p>
            )}
          </div>
        </div>

        {/* Bottom Section - Transcriptions */}
        <div className="z-30 flex flex-col p-8 justify-start overflow-y-auto max-h-96">
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-2xl font-medium text-white">Recent Transcriptions</h2>
              {transcriptions.length > 0 && transcriptions[0].source !== 'demo' && (
                <button
                  onClick={clearHistory}
                  className="relative overflow-hidden rounded-lg cursor-pointer transition-custom hover:shadow-lg"
                >
                  <div className="absolute z-0 inset-0 backdrop-blur-sm glass-filter"></div>
                  <div className="z-10 absolute inset-0 bg-red-400/20 hover:bg-red-400/30"></div>
                  <div 
                    className="absolute inset-0 z-20 rounded-lg"
                    style={{
                      boxShadow: 'inset 1px 1px 1px 0 rgba(255, 255, 255, 0.4), inset -1px -1px 1px 1px rgba(255, 255, 255, 0.2)'
                    }}
                  ></div>
                  <span className="z-30 relative text-xs font-semibold text-red-100 px-3 py-2 flex items-center gap-1">
                    🗑️ Clear All
                  </span>
                </button>
              )}
            </div>
            <p className="text-sm font-normal text-white/70">Live updates from web interface and system-wide hotkey</p>
          </div>

          {/* Transcriptions List */}
          <div className="space-y-4">
            {transcriptions.map((entry) => (
              <div key={entry.id} className="relative overflow-hidden rounded-xl">
                <div className="absolute z-0 inset-0 backdrop-blur-lg glass-filter"></div>
                <div className="z-10 absolute inset-0 bg-white/10"></div>
                <div 
                  className="absolute inset-0 z-20 rounded-xl"
                  style={{
                    boxShadow: 'inset 1px 1px 1px 0 rgba(255, 255, 255, 0.3), inset -1px -1px 1px 1px rgba(255, 255, 255, 0.1)'
                  }}
                ></div>
                <div className="z-30 relative p-6">
                  {/* Timestamp and Source */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="text-sm font-mono text-white/60">{entry.timestamp}</div>
                    <div className="flex gap-2">
                      {entry.source === 'voice_assistant' && (
                        <div className="relative overflow-hidden rounded-lg">
                          <div className="absolute z-0 inset-0 backdrop-blur-sm glass-filter"></div>
                          <div className="z-10 absolute inset-0 bg-green-400/20"></div>
                          <div 
                            className="absolute inset-0 z-20 rounded-lg"
                            style={{
                              boxShadow: 'inset 1px 1px 1px 0 rgba(255, 255, 255, 0.4), inset -1px -1px 1px 1px rgba(255, 255, 255, 0.2)'
                            }}
                          ></div>
                          <span className="z-30 relative text-xs font-semibold text-green-100 px-3 py-1">Cmd+Shift+V</span>
                        </div>
                      )}
                      {entry.source === 'web' && (
                        <div className="relative overflow-hidden rounded-lg">
                          <div className="absolute z-0 inset-0 backdrop-blur-sm glass-filter"></div>
                          <div className="z-10 absolute inset-0 bg-blue-400/20"></div>
                          <div 
                            className="absolute inset-0 z-20 rounded-lg"
                            style={{
                              boxShadow: 'inset 1px 1px 1px 0 rgba(255, 255, 255, 0.4), inset -1px -1px 1px 1px rgba(255, 255, 255, 0.2)'
                            }}
                          ></div>
                          <span className="z-30 relative text-xs font-semibold text-blue-100 px-3 py-1">Web</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Raw Whisper */}
                  <div className="mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-semibold text-red-300 uppercase tracking-wide">🎤 Raw Whisper</span>
                    </div>
                    <p className="text-sm text-white/70 italic leading-relaxed">{entry.rawText}</p>
                  </div>

                  {/* Cleaned DeepSeek */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-semibold text-blue-300 uppercase tracking-wide">✨ DeepSeek Cleaned</span>
                    </div>
                    <p className="text-base text-white font-medium leading-relaxed">{entry.cleanedText}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="text-center mt-8">
            <p className="text-sm font-normal text-white/50">
              System automatically syncs transcriptions from web and global hotkey
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 