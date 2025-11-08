'use client'

import { useState, useRef, useEffect } from 'react'
import { Mic, Upload, Loader2, Square } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

export default function RecordingPanel({ 
  onTranscriptUpdate, 
  onProcessingChange,
  onTasksExtracted,
  onSummaryGenerated,
  onTranscriptFinalized
}: any) {
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [liveTranscript, setLiveTranscript] = useState('') // Real-time partial transcripts
  const [isProcessing, setIsProcessing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  // Clean up WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000 // Optimize for Whisper
        } 
      })
      streamRef.current = stream

      // Connect to WebSocket for real-time transcription
      const ws = new WebSocket(`${WS_URL}/ws/realtime`)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('[WS] Connected for live transcription')
      }

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data)
        console.log('[WS] Message:', message.type)

        if (message.type === 'partial_transcript') {
          // Update live transcript as chunks come in
          setLiveTranscript(message.full_transcript)
          onTranscriptUpdate(message.full_transcript)
        } else if (message.type === 'final_transcript') {
          setTranscript(message.data)
          setLiveTranscript('')
          onTranscriptFinalized(message.data); // Notify parent that transcript is ready
          setIsProcessing(false) // Stop the recording processing indicator
          onProcessingChange(false)
        } else if (message.type === 'error') {
          console.error('[WS] Error:', message.message)
          alert(`Live recording error: ${message.message}`)
          setIsProcessing(false)
          onProcessingChange(false)
        }
      }

      ws.onerror = (error) => {
        console.error('[WS] Error:', error)
        alert('WebSocket connection failed. Check backend is running.')
      }

      ws.onclose = () => {
        console.log('[WS] Connection closed')
      }

      // Set up MediaRecorder to send chunks via WebSocket
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0 && ws.readyState === WebSocket.OPEN) {
          // Send audio chunk to backend for real-time transcription
          e.data.arrayBuffer().then(buffer => {
            ws.send(buffer)
          })
        }
      }

      // Request data every 100ms for low latency
      mediaRecorder.start(100)
      setIsRecording(true)
      setLiveTranscript('')
      setTranscript('')

    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Could not access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      
      // Stop all tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }

      // Send stop signal to backend to process final audio
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: 'stop' }))
        setIsProcessing(true)
        onProcessingChange(true)
      }
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Immediately show processing state
    setIsProcessing(true)
    onProcessingChange(true)
    onTranscriptUpdate('Transcribing uploaded file...'); // Placeholder text

    // Check file size (100MB limit)
    const maxSize = 100 * 1024 * 1024 // 100MB
    if (file.size > maxSize) {
      alert(`File is too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Maximum size is 100MB.`)
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)

      console.log(`Uploading file: ${file.name}, size: ${(file.size / 1024 / 1024).toFixed(2)}MB, type: ${file.type}`)

      const response = await axios.post(`${API_URL}/transcribe/file?validate=true`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minute timeout for large files
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            console.log(`Upload progress: ${percentCompleted}%`)
          }
        }
      })

      const transcriptText = response.data.transcript
      setTranscript(transcriptText)
      setLiveTranscript('')
      onTranscriptFinalized(transcriptText) // Notify parent that transcript is ready

      await processTranscript(transcriptText)
    } catch (error: any) {
      console.error('Upload error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error'
      alert(`File upload failed: ${errorMessage}\n\nCheck:\n1. Backend is running on ${API_URL}\n2. File format is supported (mp3, wav, webm, etc.)\n3. File size is under 100MB`)
      onTranscriptUpdate(''); // Clear placeholder
    } finally {
      setIsProcessing(false)
      onProcessingChange(false)
    }
  }

  const processTranscript = async (text: string) => {
    try {
      const response = await axios.post(`${API_URL}/process/transcript`, {
        text: text,
        user_id: 'demo_user',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      })

      onTasksExtracted(response.data.tasks || [])
      // Support both new dual summary format and old single summary
      const summary = response.data.summary_openai || response.data.summary || null
      const summaryGemini = response.data.summary_gemini || null
      onSummaryGenerated({ 
        ...summary, 
        gemini_alternative: summaryGemini 
      })
    } catch (error) {
      console.error('Processing error:', error)
      alert(`Processing failed: ${error}. Check console for details.`)
    }
  }

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">1. Record or Upload Audio</h2>
      
      <div className="flex gap-4 mb-6">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          className={`flex-1 flex items-center justify-center gap-2 py-4 rounded-lg font-semibold transition-all ${
            isRecording 
              ? 'bg-red-500 hover:bg-red-600 text-white' 
              : 'bg-indigo-600 hover:bg-indigo-700 text-white'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isRecording ? (
            <>
              <Square size={20} fill="white" />
              Stop Recording
            </>
          ) : (
            <>
              <Mic size={20} />
              Start Recording
            </>
          )}
        </button>

        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isProcessing || isRecording}
          className="px-6 py-4 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Upload size={20} />
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>

      {isProcessing && (
        <div className="flex items-center justify-center gap-2 mb-4 text-indigo-600">
          <Loader2 className="animate-spin" size={20} />
          <span className="font-medium">Processing audio...</span>
        </div>
      )}

      {isRecording && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-red-700 font-medium">🎙️ Recording live - transcription appears in real-time below...</span>
          </div>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-4 min-h-[200px] max-h-[400px] overflow-y-auto">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">
          {isRecording ? '🔴 Live Transcript' : 'Transcript'}
        </h3>
        {transcript || liveTranscript ? (
          <div>
            {liveTranscript && isRecording && (
              <p className="text-gray-800 whitespace-pre-wrap mb-2">
                {liveTranscript}
                <span className="inline-block w-2 h-4 ml-1 bg-gray-800 animate-pulse"></span>
              </p>
            )}
            {!isRecording && transcript && (
              <p className="text-gray-800 whitespace-pre-wrap">{transcript}</p>
            )}
          </div>
        ) : (
          <p className="text-gray-400 italic">
            Start recording for real-time transcription or upload an audio file...
          </p>
        )}
      </div>
    </div>
  )
}

