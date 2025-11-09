'use client'

import { useState, useRef, useEffect } from 'react'
import { Mic, Square, Volume2, Loader2, MessageCircle, RotateCcw, X } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Message {
  role: 'user' | 'assistant'
  content: string
  audio?: string
}

interface AIPracticePanelProps {
  transcript: string
  context: string
  coachingInsights: any
  onClose?: () => void
}

export default function AIPracticePanel({ 
  transcript, 
  context, 
  coachingInsights,
  onClose
}: AIPracticePanelProps) {
  const [sessionActive, setSessionActive] = useState(false)
  const [sessionData, setSessionData] = useState<any>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isPlayingAudio, setIsPlayingAudio] = useState(false)
  const [currentTranscript, setCurrentTranscript] = useState('')
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  // Removed auto-scrolling to prevent page jumping

  const startSession = async () => {
    setIsProcessing(true)
    try {
      const response = await axios.post(`${API_URL}/conversation/start`, {
        transcript,
        context,
        coaching_insights: coachingInsights
      })

      const session = response.data.session
      setSessionData(session)
      setSessionActive(true)
      
      // Add opening message to chat
      const openingMessage: Message = {
        role: 'assistant',
        content: session.opening_message,
        audio: session.opening_audio
      }
      setMessages([openingMessage])

      // Auto-play the opening message
      if (session.opening_audio) {
        playAudioFromBase64(session.opening_audio)
      }
    } catch (error: any) {
      console.error('Failed to start session:', error)
      alert(`Failed to start practice session: ${error.response?.data?.detail || error.message}`)
    } finally {
      setIsProcessing(false)
    }
  }

  const playAudioFromBase64 = (base64Audio: string) => {
    try {
      // Stop any currently playing audio
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }

      setIsPlayingAudio(true)
      const audioBlob = base64ToBlob(base64Audio, 'audio/mpeg')
      const audioUrl = URL.createObjectURL(audioBlob)
      
      audioRef.current = new Audio(audioUrl)
      audioRef.current.onended = () => {
        setIsPlayingAudio(false)
        URL.revokeObjectURL(audioUrl)
      }
      audioRef.current.onerror = () => {
        setIsPlayingAudio(false)
        console.error('Audio playback failed')
      }
      
      audioRef.current.play()
    } catch (error) {
      console.error('Failed to play audio:', error)
      setIsPlayingAudio(false)
    }
  }

  const base64ToBlob = (base64: string, contentType: string) => {
    const byteCharacters = atob(base64)
    const byteNumbers = new Array(byteCharacters.length)
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i)
    }
    const byteArray = new Uint8Array(byteNumbers)
    return new Blob([byteArray], { type: contentType })
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        } 
      })
      streamRef.current = stream

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
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        await processUserResponse(audioBlob)
        
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
        }
      }

      mediaRecorder.start()
      setIsRecording(true)
      setCurrentTranscript('')
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

  const processUserResponse = async (audioBlob: Blob) => {
    setIsProcessing(true)
    try {
      // Step 1: Transcribe the user's audio
      const formData = new FormData()
      formData.append('file', audioBlob, 'response.webm')
      
      const transcriptResponse = await axios.post(`${API_URL}/transcribe/file?validate=false&analyze_video=false`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000
      })
      
      const userMessage = transcriptResponse.data.transcript
      
      // Add user message to chat
      const userMsg: Message = {
        role: 'user',
        content: userMessage
      }
      setMessages(prev => [...prev, userMsg])

      // Step 2: Get AI response
      const continueResponse = await axios.post(`${API_URL}/conversation/continue`, {
        user_message: userMessage,
        conversation_history: sessionData.conversation_history,
        context_data: sessionData.context_data,
        session_type: sessionData.session_type
      })

      // Update session data with new conversation history
      setSessionData({
        ...sessionData,
        conversation_history: continueResponse.data.conversation_history
      })

      // Add AI response to chat
      const assistantMsg: Message = {
        role: 'assistant',
        content: continueResponse.data.assistant_message,
        audio: continueResponse.data.audio
      }
      setMessages(prev => [...prev, assistantMsg])

      // Auto-play AI response
      if (continueResponse.data.audio) {
        setTimeout(() => {
          playAudioFromBase64(continueResponse.data.audio)
        }, 500)
      }
      
    } catch (error: any) {
      console.error('Failed to process response:', error)
      alert(`Failed to process your response: ${error.response?.data?.detail || error.message}`)
    } finally {
      setIsProcessing(false)
    }
  }

  const replayMessage = (message: Message) => {
    if (message.audio) {
      playAudioFromBase64(message.audio)
    }
  }

  const resetSession = () => {
    setSessionActive(false)
    setSessionData(null)
    setMessages([])
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
    }
  }

  if (!transcript || !['interview', 'lecture', 'coffee_chat'].includes(context)) {
    return (
      <div className="card bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600">
        <div className="text-center py-8">
          <MessageCircle className="mx-auto mb-4 text-purple-400" size={48} />
          <h3 className="text-xl font-bold text-gray-700 mb-2">Practice with AI</h3>
          <p className="text-gray-600">
            Available for <span className="font-semibold">Interview</span>, <span className="font-semibold">Lecture</span>, or <span className="font-semibold">Coffee Chat</span> contexts
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Record a conversation and run Smart Analysis first
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="card bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 relative">
      {/* Close button */}
      {onClose && (
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 bg-gray-200 hover:bg-gray-300 rounded-full transition-colors"
          title="Close"
        >
          <X size={20} />
        </button>
      )}

      <div className="flex items-center gap-3 mb-6">
        <MessageCircle className="text-purple-600" size={32} />
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Practice with AI</h2>
          <p className="text-sm text-gray-600">
            {context === 'interview' && 'Interactive Interview Practice'}
            {context === 'lecture' && '📚 Conversational Study Session'}
            {context === 'coffee_chat' && '☕ Networking Skills Practice'}
          </p>
        </div>
      </div>

      {!sessionActive ? (
        <div className="text-center py-12">
          <div className="bg-white rounded-lg p-6 mb-6 max-w-2xl mx-auto shadow-sm">
            <h3 className="font-semibold text-gray-800 mb-3 text-lg">
              {context === 'interview' && 'Practice Interview Questions'}
              {context === 'lecture' && '💡 Test Your Understanding'}
              {context === 'coffee_chat' && '🗣️ Improve Your Networking'}
            </h3>
            <p className="text-gray-600 mb-4">
              {context === 'interview' && 'Have a natural conversation with AI to practice answering interview questions. Get instant feedback and improve your responses.'}
              {context === 'lecture' && 'Engage in a study session with AI. Answer questions, ask for explanations, and deepen your understanding of the material.'}
              {context === 'coffee_chat' && 'Practice your networking skills in a casual conversation with AI. Learn to ask better questions and make meaningful connections.'}
            </p>
            <ul className="text-left text-sm text-gray-600 space-y-2 mb-6">
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-0.5">✓</span>
                <span>AI speaks to you using natural voice (ElevenLabs)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-0.5">✓</span>
                <span>Record your responses by clicking the mic button</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-0.5">✓</span>
                <span>Get immediate, conversational feedback</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-0.5">✓</span>
                <span>Continue the conversation as long as you want</span>
              </li>
            </ul>
          </div>

          <button
            onClick={startSession}
            disabled={isProcessing}
            className="px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-3"
          >
            {isProcessing ? (
              <>
                <Loader2 className="animate-spin" size={24} />
                Starting Session...
              </>
            ) : (
              <>
                <MessageCircle size={24} />
                Start Practice Session
              </>
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Chat messages */}
          <div className="bg-white rounded-lg shadow-inner p-4 min-h-[400px] max-h-[600px] overflow-y-auto">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-800 border border-gray-200'
                    }`}
                  >
                    <div className="flex items-start gap-2 mb-2">
                      <span className="font-semibold text-sm">
                        {message.role === 'user' ? '👤 You' : '🤖 AI Coach'}
                      </span>
                      {message.role === 'assistant' && message.audio && (
                        <button
                          onClick={() => replayMessage(message)}
                          disabled={isPlayingAudio}
                          className="ml-auto p-1 hover:bg-gray-200 rounded transition-colors disabled:opacity-50"
                          title="Replay audio"
                        >
                          <Volume2 size={16} />
                        </button>
                      )}
                    </div>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              ))}
              
              {isProcessing && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-4 border border-gray-200">
                    <div className="flex items-center gap-2">
                      <Loader2 className="animate-spin text-gray-600" size={20} />
                      <span className="text-gray-600">Processing...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Recording controls */}
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isProcessing || isPlayingAudio}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all shadow-md ${
                  isRecording
                    ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                    : 'bg-green-600 hover:bg-green-700 text-white'
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
                    {messages.length > 1 ? 'Record Response' : 'Start Talking'}
                  </>
                )}
              </button>

              <button
                onClick={resetSession}
                disabled={isProcessing || isRecording}
                className="flex items-center gap-2 px-4 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition-all disabled:opacity-50"
              >
                <RotateCcw size={18} />
                Reset
              </button>
            </div>

            {isRecording && (
              <div className="mt-4 text-center">
                <div className="inline-flex items-center gap-2 bg-red-50 px-4 py-2 rounded-full">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                  <span className="text-red-700 font-medium text-sm">Recording... Speak now</span>
                </div>
              </div>
            )}

            {isPlayingAudio && (
              <div className="mt-4 text-center">
                <div className="inline-flex items-center gap-2 bg-blue-50 px-4 py-2 rounded-full">
                  <Volume2 className="text-blue-600 animate-pulse" size={16} />
                  <span className="text-blue-700 font-medium text-sm">AI is speaking...</span>
                </div>
              </div>
            )}
          </div>

          {/* Session info */}
          <div className="text-center text-sm text-gray-600">
            <p>💬 {messages.length} message{messages.length !== 1 ? 's' : ''} in conversation</p>
          </div>
        </div>
      )}
    </div>
  )
}

