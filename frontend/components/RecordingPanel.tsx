'use client'

import { useState, useRef, useEffect } from 'react'
import { Mic, Upload, Loader2, Square } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function RecordingPanel({ 
  onTranscriptUpdate, 
  onProcessingChange,
  onTasksExtracted,
  onSummaryGenerated,
  onTranscriptFinalized,
  mediaType = 'audio'
}: any) {
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const videoPreviewRef = useRef<HTMLVideoElement>(null)

  // This effect reliably attaches the stream to the video element
  useEffect(() => {
    if (videoPreviewRef.current && stream) {
      console.log('✅ Stream ready, attaching to video element.')
      videoPreviewRef.current.srcObject = stream
      videoPreviewRef.current.play().catch(e => {
        console.error('❌ Video play failed:', e)
        setCameraError('Could not start video preview.')
      })
    } else {
      console.log('🧹 Stream cleared, cleaning up video element.')
      if (videoPreviewRef.current) {
        videoPreviewRef.current.srcObject = null
      }
    }
  }, [stream])

  const startRecording = async () => {
    try {
      setCameraError(null)
      const constraints = mediaType === 'video' 
        ? { 
            audio: { echoCancellation: true, noiseSuppression: true, sampleRate: 16000 },
            video: { facingMode: 'user', width: 1280, height: 720 }
          }
        : { 
            audio: { echoCancellation: true, noiseSuppression: true, sampleRate: 16000 } 
          }
      
      const newStream = await navigator.mediaDevices.getUserMedia(constraints)
      setStream(newStream)
      setIsRecording(true)

      const mimeType = mediaType === 'video' ? 'video/webm;codecs=vp8,opus' : 'audio/webm;codecs=opus'
      const mediaRecorder = new MediaRecorder(newStream, { mimeType })
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: mimeType })
        if (mediaType === 'video') {
          await transcribeVideo(blob)
        } else {
          await transcribeAudio(blob)
        }
      }

      mediaRecorder.start()
      setTranscript('')

    } catch (error: any) {
      console.error('❌ Error starting recording:', error)
      let errorMessage = `Could not access ${mediaType === 'video' ? 'camera/microphone' : 'microphone'}.`
      
      if (error.name === 'NotAllowedError') {
        errorMessage = '🚫 Permission denied. Please allow camera/microphone access in your browser.'
        setCameraError('Permission denied')
      } else if (error.name === 'NotFoundError') {
        errorMessage = '📹 No camera/microphone found. Please check your device.'
        setCameraError('No camera found')
      } else {
        errorMessage += ` Error: ${error.message}`
        setCameraError('An unknown error occurred')
      }
      alert(errorMessage)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
    }
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
    }
    setIsRecording(false)
    setStream(null)
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
      onTranscriptFinalized(transcriptText, response.data)

    } catch (error: any) {
      console.error('Transcription error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error'
      alert(`Transcription failed: ${errorMessage}`)
    } finally {
      setIsProcessing(false)
      onProcessingChange(false)
    }
  }

  const transcribeVideo = async (videoBlob: Blob) => {
    setIsProcessing(true)
    onProcessingChange(true)

    try {
      const formData = new FormData()
      formData.append('file', videoBlob, 'recording.webm')

      const response = await axios.post(`${API_URL}/transcribe/file?validate=true&analyze_video=true&vision_mode=detailed`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 600000 // 10 minute timeout for video
      })

      const transcriptText = response.data.transcript
      setTranscript(transcriptText)
      onTranscriptUpdate(transcriptText)
      onTranscriptFinalized(transcriptText, response.data)

    } catch (error: any) {
      console.error('Video transcription error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error'
      alert(`Video processing failed: ${errorMessage}`)
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

      // Only analyze video if mediaType is video AND file is actually a video
      const isVideoFile = (mediaType === 'video') && (file.type.startsWith('video/') || file.name.toLowerCase().includes('.mp4'))
      const queryParams = new URLSearchParams({
        validate: mediaType === 'audio' ? 'true' : 'false',  // Validate audio, skip for video (speed)
        analyze_video: isVideoFile ? 'true' : 'false',
        vision_mode: 'detailed'  // Use detailed mode for quality
      })

      const response = await axios.post(`${API_URL}/transcribe/file?${queryParams}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 600000, // 10 minute timeout for video files
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
      onTranscriptFinalized(transcriptText, response.data) // Notify parent with full response data
    } catch (error: any) {
      console.error('Upload error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error'
      const isVideoFile = file?.type.startsWith('video/') || file?.name.toLowerCase().includes('.mp4')
      
      alert(`File upload failed: ${errorMessage}\n\nCheck:\n1. Backend is running on ${API_URL}\n2. File format is supported ${isVideoFile ? '(mp4, mov, avi for video)' : '(mp3, wav, webm for audio)'}\n3. File size is under ${isVideoFile ? '200MB for video' : '100MB for audio'}\n4. ${isVideoFile ? 'ffmpeg is installed for video processing' : 'Audio codec is supported'}`)
      onTranscriptUpdate(''); // Clear placeholder
    } finally {
      setIsProcessing(false)
      onProcessingChange(false)
    }
  }

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        1. Record or Upload {mediaType === 'video' ? 'Video' : 'Audio'}
      </h2>
      
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
                    {mediaType === 'video' ? 'Start Video Recording' : 'Start Recording'}
                  </>
                )}
        </button>

                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isProcessing || isRecording}
                  className="px-6 py-4 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title={mediaType === 'video' ? 'Upload video files (mp4) - analysis coming soon' : 'Upload audio files (mp3, wav, webm)'}
                >
          <Upload size={20} />
        </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept={mediaType === 'video' ? 'video/*' : 'audio/*'}
                  onChange={handleFileUpload}
                  className="hidden"
                />
      </div>

      {isProcessing && (
        <div className="flex items-center justify-center gap-2 mb-4 text-indigo-600">
          <Loader2 className="animate-spin" size={20} />
          <span className="font-medium">
            {mediaType === 'video' ? 'Processing video (audio + visual analysis)...' : 'Processing audio...'}
          </span>
        </div>
      )}

      {isRecording && (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-red-700 dark:text-red-400 font-medium">
              {mediaType === 'video' ? '📹 Recording video...' : '🎙️ Recording...'} Click "Stop Recording" when done
            </span>
          </div>
          {mediaType === 'video' && (
            <div className="relative">
              <video 
                ref={videoPreviewRef}
                className="mt-2 w-full h-64 md:h-80 bg-black object-cover rounded-lg border-4 border-red-500 shadow-2xl"
                autoPlay
                playsInline
                muted
                style={{ objectFit: 'cover' }}
              />
              <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold flex items-center gap-2">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                REC
              </div>
              {cameraError && (
                <div className="absolute inset-0 bg-black/80 flex items-center justify-center text-white text-center p-4 rounded-lg">
                  <div>
                    <div className="text-2xl mb-2">📹</div>
                    <div className="font-semibold mb-1">Camera Issue</div>
                    <div className="text-sm">{cameraError}</div>
                    <div className="text-xs mt-2 opacity-75">Check browser permissions</div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-4 min-h-[200px] max-h-[400px] overflow-y-auto">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">Transcript</h3>
        {transcript ? (
          <p className="text-gray-800 whitespace-pre-wrap">{transcript}</p>
        ) : (
          <p className="text-gray-400 italic">
            {isRecording 
              ? `Recording ${mediaType}... (transcript will appear after you stop recording)` 
              : `Start recording or upload ${mediaType === 'video' ? 'a video' : 'an audio'} file to see the transcript here...`}
          </p>
        )}
      </div>
    </div>
  )
}


