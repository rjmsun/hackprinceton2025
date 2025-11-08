'use client'

import { useState, useRef } from 'react'
import { Mic, Upload, Loader2, Square } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function RecordingPanel({ 
  onTranscriptUpdate, 
  onProcessingChange,
  onTasksExtracted,
  onSummaryGenerated,
  onTranscriptFinalized
}: any) {
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        } 
      })
      streamRef.current = stream

      // Set up MediaRecorder to record to chunks (no WebSocket)
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = async () => {
        // When recording stops, transcribe the complete audio
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        await transcribeAudio(audioBlob)
        
        // Stop all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
        }
      }

      mediaRecorder.start()
      setIsRecording(true)
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
    }
  }

  const transcribeAudio = async (audioBlob: Blob) => {
    setIsProcessing(true)
    onProcessingChange(true)

    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'recording.webm')

      const response = await axios.post(`${API_URL}/transcribe/file?validate=true`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000
      })

      const transcriptText = response.data.transcript
      setTranscript(transcriptText)
      onTranscriptUpdate(transcriptText)
      onTranscriptFinalized(transcriptText)

    } catch (error: any) {
      console.error('Transcription error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error'
      alert(`Transcription failed: ${errorMessage}`)
    } finally {
      setIsProcessing(false)
      onProcessingChange(false)
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
      onTranscriptUpdate(transcriptText)
      onTranscriptFinalized(transcriptText) // Notify parent that transcript is ready
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
            <span className="text-red-700 font-medium">🎙️ Recording... Click "Stop Recording" when done</span>
          </div>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-4 min-h-[200px] max-h-[400px] overflow-y-auto">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">Transcript</h3>
        {transcript ? (
          <p className="text-gray-800 whitespace-pre-wrap">{transcript}</p>
        ) : (
          <p className="text-gray-400 italic">
            {isRecording 
              ? 'Recording... (transcript will appear after you stop recording)' 
              : 'Start recording or upload an audio file to see the transcript here...'}
          </p>
        )}
      </div>
    </div>
  )
}

