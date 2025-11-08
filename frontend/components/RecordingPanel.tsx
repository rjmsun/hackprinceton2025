'use client'

import { useState, useRef } from 'react'
import { Mic, Upload, Loader2, Play, Square } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function RecordingPanel({ 
  onTranscriptUpdate, 
  onProcessingChange,
  onTasksExtracted,
  onSummaryGenerated 
}: any) {
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        await transcribeAudio(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
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

      const response = await axios.post(`${API_URL}/transcribe/file`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      const transcriptText = response.data.transcript
      setTranscript(transcriptText)
      onTranscriptUpdate(transcriptText)

      // Auto-process
      await processTranscript(transcriptText)
    } catch (error) {
      console.error('Transcription error:', error)
      alert('Transcription failed. Check that your backend is running and API keys are set.')
    } finally {
      setIsProcessing(false)
      onProcessingChange(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsProcessing(true)
    onProcessingChange(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(`${API_URL}/transcribe/file`, formData)
      const transcriptText = response.data.transcript
      setTranscript(transcriptText)
      onTranscriptUpdate(transcriptText)

      await processTranscript(transcriptText)
    } catch (error) {
      console.error('Upload error:', error)
      alert('File upload failed. Check backend connection.')
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
      onSummaryGenerated(response.data.summary || null)
    } catch (error) {
      console.error('Processing error:', error)
    }
  }

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Recording</h2>
      
      <div className="flex gap-4 mb-6">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          className={`flex-1 flex items-center justify-center gap-2 py-4 rounded-lg font-semibold transition-all ${
            isRecording 
              ? 'bg-red-500 hover:bg-red-600 text-white' 
              : 'bg-primary hover:bg-indigo-700 text-white'
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
            <span className="text-red-700 font-medium">Recording in progress...</span>
          </div>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-4 min-h-[200px] max-h-[400px] overflow-y-auto">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">Live Transcript</h3>
        {transcript ? (
          <p className="text-gray-800 whitespace-pre-wrap">{transcript}</p>
        ) : (
          <p className="text-gray-400 italic">
            Start recording or upload an audio file to see the transcript here...
          </p>
        )}
      </div>
    </div>
  )
}

