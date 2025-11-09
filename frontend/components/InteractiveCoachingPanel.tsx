'use client'

import { useState, useRef } from 'react'
import { Play, Pause, Mic, RotateCcw, Volume2, Square, Loader2 } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface InteractiveCoachingPanelProps {
  interactiveScenarios: any
  context: string
  onNewResponse?: (response: any) => void
}

export default function InteractiveCoachingPanel({ 
  interactiveScenarios, 
  context, 
  onNewResponse 
}: InteractiveCoachingPanelProps) {
  const [currentScenario, setCurrentScenario] = useState<any>(null)
  const [isPlayingQuestion, setIsPlayingQuestion] = useState(false)
  const [isRecordingResponse, setIsRecordingResponse] = useState(false)
  const [isProcessingResponse, setIsProcessingResponse] = useState(false)
  const [feedback, setFeedback] = useState<any>(null)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])

  if (!interactiveScenarios || Object.keys(interactiveScenarios).length === 0) {
    return null
  }

  const playQuestion = async (questionText: string) => {
    setIsPlayingQuestion(true)
    try {
      // Use TTS to speak the question
      const response = await axios.post(`${API_URL}/voice/summary`, 
        [{ title: "Question", description: questionText }], 
        { responseType: 'blob' }
      )
      
      const audioBlob = new Blob([response.data], { type: 'audio/mpeg' })
      const audioUrl = URL.createObjectURL(audioBlob)
      
      if (audioRef.current) {
        audioRef.current.pause()
      }
      
      audioRef.current = new Audio(audioUrl)
      audioRef.current.onended = () => {
        setIsPlayingQuestion(false)
        URL.revokeObjectURL(audioUrl)
      }
      audioRef.current.onerror = () => {
        setIsPlayingQuestion(false)
        alert('Audio playback failed. Check ElevenLabs API key.')
      }
      
      await audioRef.current.play()
    } catch (error) {
      setIsPlayingQuestion(false)
      alert('Failed to play question. Check TTS service.')
    }
  }

  const startRecordingResponse = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { echoCancellation: true, noiseSuppression: true } 
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
        await processResponse(audioBlob)
        
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
        }
      }

      mediaRecorder.start()
      setIsRecordingResponse(true)
    } catch (error) {
      alert('Could not access microphone. Please check permissions.')
    }
  }

  const stopRecordingResponse = () => {
    if (mediaRecorderRef.current && isRecordingResponse) {
      mediaRecorderRef.current.stop()
      setIsRecordingResponse(false)
    }
  }

  const processResponse = async (audioBlob: Blob) => {
    setIsProcessingResponse(true)
    try {
      // First, transcribe the response
      const formData = new FormData()
      formData.append('file', audioBlob, 'response.webm')
      
      const transcriptResponse = await axios.post(`${API_URL}/transcribe/file`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000
      })
      
      const userResponse = transcriptResponse.data.transcript
      
      // Then get feedback on the response
      const feedbackResponse = await axios.post(`${API_URL}/interactive/feedback`, {
        original_question: currentScenario?.original_question || currentScenario?.question,
        user_response: userResponse,
        context: context,
        coaching_tip: currentScenario?.coaching_tip || "",
        scenario_type: interactiveScenarios.type
      })
      
      setFeedback({
        user_response: userResponse,
        ...feedbackResponse.data
      })
      
      // Speak the voice feedback if available
      if (feedbackResponse.data.voice_feedback) {
        setTimeout(() => {
          playFeedback(feedbackResponse.data.voice_feedback)
        }, 1000)
      }
      
      if (onNewResponse) {
        onNewResponse(feedbackResponse.data)
      }
      
    } catch (error: any) {
      console.error('Response processing error:', error)
      alert(`Failed to process response: ${error.response?.data?.detail || error.message}`)
    } finally {
      setIsProcessingResponse(false)
    }
  }

  const playFeedback = async (feedbackText: string) => {
    try {
      const response = await axios.post(`${API_URL}/voice/summary`, 
        [{ title: "Feedback", description: feedbackText }], 
        { responseType: 'blob' }
      )
      
      const audioBlob = new Blob([response.data], { type: 'audio/mpeg' })
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      
      audio.onended = () => URL.revokeObjectURL(audioUrl)
      audio.play()
    } catch (error) {
      console.error('Feedback TTS failed:', error)
    }
  }

  const renderInterviewReplay = () => {
    const opportunities = interactiveScenarios.coaching_opportunities || []
    
    return (
      <div className="space-y-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
            <RotateCcw size={20} /> Interview Replay Mode
          </h4>
          <p className="text-blue-800 text-sm">
            {interactiveScenarios.replay_instructions}
          </p>
        </div>

        {opportunities.map((opportunity: any, index: number) => (
          <div key={opportunity.moment_id} className="border rounded-lg p-4 bg-white shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  opportunity.severity === 'blunder' 
                    ? 'bg-red-100 text-red-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {opportunity.severity === 'blunder' ? '🚨 Blunder' : '⚠️ Inaccuracy'}
                </span>
                <span className="text-gray-600 text-sm">{opportunity.type}</span>
              </div>
            </div>

            <div className="space-y-3">
              <div className="bg-gray-50 p-3 rounded">
                <p className="font-medium text-gray-800 mb-1">Original Question:</p>
                <p className="text-gray-700 italic">"{opportunity.original_question}"</p>
              </div>

              <div className="bg-red-50 p-3 rounded">
                <p className="font-medium text-red-800 mb-1">Your Previous Response (Issue):</p>
                <p className="text-red-700 italic">"{opportunity.issue}"</p>
              </div>

              <div className="bg-green-50 p-3 rounded">
                <p className="font-medium text-green-800 mb-1">Coaching Tip:</p>
                <p className="text-green-700">{opportunity.coaching_tip}</p>
              </div>

              <div className="flex gap-3 mt-4">
                <button
                  onClick={() => {
                    setCurrentScenario(opportunity)
                    playQuestion(opportunity.original_question)
                  }}
                  disabled={isPlayingQuestion}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50"
                >
                  {isPlayingQuestion ? <Loader2 className="animate-spin" size={16} /> : <Play size={16} />}
                  Replay Question
                </button>

                {currentScenario?.moment_id === opportunity.moment_id && (
                  <button
                    onClick={isRecordingResponse ? stopRecordingResponse : startRecordingResponse}
                    disabled={isProcessingResponse || isPlayingQuestion}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium ${
                      isRecordingResponse 
                        ? 'bg-red-500 hover:bg-red-600 text-white' 
                        : 'bg-green-600 hover:bg-green-700 text-white'
                    } disabled:opacity-50`}
                  >
                    {isRecordingResponse ? (
                      <>
                        <Square size={16} fill="white" />
                        Stop Response
                      </>
                    ) : (
                      <>
                        <Mic size={16} />
                        Record New Response
                      </>
                    )}
                  </button>
                )}

                {isProcessingResponse && (
                  <div className="flex items-center gap-2 text-blue-600">
                    <Loader2 className="animate-spin" size={16} />
                    <span>Processing...</span>
                  </div>
                )}
              </div>

              {feedback && currentScenario?.moment_id === opportunity.moment_id && (
                <div className="mt-4 space-y-3 border-t pt-4">
                  <div className="bg-blue-50 p-3 rounded">
                    <p className="font-medium text-blue-800 mb-1">Your New Response:</p>
                    <p className="text-blue-700">"{feedback.user_response}"</p>
                  </div>

                  <div className={`p-3 rounded ${
                    feedback.overall_rating === 'excellent' || feedback.overall_rating === 'good' 
                      ? 'bg-green-50 border border-green-200' 
                      : 'bg-yellow-50 border border-yellow-200'
                  }`}>
                    <p className="font-medium mb-2">
                      Rating: <span className="capitalize">{feedback.overall_rating}</span> 
                      {feedback.overall_rating === 'excellent' && '🎉'}
                      {feedback.overall_rating === 'good' && '👍'}
                    </p>
                    <p className="text-gray-700 mb-2">{feedback.specific_feedback}</p>
                    
                    {feedback.improvements && feedback.improvements.length > 0 && (
                      <div className="mb-2">
                        <p className="font-medium text-green-800 text-sm">✅ Improvements:</p>
                        <ul className="list-disc list-inside text-sm text-green-700">
                          {feedback.improvements.map((imp: string, i: number) => (
                            <li key={i}>{imp}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {feedback.still_needs_work && feedback.still_needs_work.length > 0 && (
                      <div>
                        <p className="font-medium text-orange-800 text-sm">🔄 Still needs work:</p>
                        <ul className="list-disc list-inside text-sm text-orange-700">
                          {feedback.still_needs_work.map((work: string, i: number) => (
                            <li key={i}>{work}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    )
  }

  const renderLectureQuestions = () => {
    const questions = interactiveScenarios.questions || []
    const currentQuestion = questions[currentQuestionIndex]

    if (!currentQuestion) return null

    return (
      <div className="space-y-6">
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h4 className="font-semibold text-purple-900 mb-2">
            📚 Conceptual Practice ({currentQuestionIndex + 1} of {questions.length})
          </h4>
          <p className="text-purple-800 text-sm">
            {interactiveScenarios.practice_instructions}
          </p>
        </div>

        <div className="border rounded-lg p-4 bg-white shadow-sm">
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                currentQuestion.difficulty === 'basic' ? 'bg-green-100 text-green-800' :
                currentQuestion.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {currentQuestion.difficulty}
              </span>
              <span className="text-gray-600 text-sm">{currentQuestion.topic}</span>
            </div>
            
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-gray-800 font-medium">{currentQuestion.question}</p>
            </div>
          </div>

          <div className="flex gap-3 mb-4">
            <button
              onClick={() => {
                setCurrentScenario(currentQuestion)
                playQuestion(currentQuestion.question)
              }}
              disabled={isPlayingQuestion}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg disabled:opacity-50"
            >
              <Volume2 size={16} />
              Hear Question
            </button>

            <button
              onClick={isRecordingResponse ? stopRecordingResponse : startRecordingResponse}
              disabled={isProcessingResponse || isPlayingQuestion}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium ${
                isRecordingResponse 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'bg-green-600 hover:bg-green-700 text-white'
              } disabled:opacity-50`}
            >
              {isRecordingResponse ? (
                <>
                  <Square size={16} fill="white" />
                  Stop Answer
                </>
              ) : (
                <>
                  <Mic size={16} />
                  Record Answer
                </>
              )}
            </button>
          </div>

          {feedback && (
            <div className="border-t pt-4 space-y-3">
              <div className="bg-blue-50 p-3 rounded">
                <p className="font-medium text-blue-800 mb-1">Your Answer:</p>
                <p className="text-blue-700">"{feedback.user_response}"</p>
              </div>

              <div className="bg-gray-50 p-3 rounded">
                <p className="font-medium mb-2">
                  Understanding: <span className="capitalize">{feedback.understanding_level}</span>
                  {feedback.understanding_level === 'strong' && ''}
                </p>
                
                {feedback.correct_points && feedback.correct_points.length > 0 && (
                  <div className="mb-2">
                    <p className="font-medium text-green-800 text-sm">✅ What you got right:</p>
                    <ul className="list-disc list-inside text-sm text-green-700">
                      {feedback.correct_points.map((point: string, i: number) => (
                        <li key={i}>{point}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {feedback.missing_points && feedback.missing_points.length > 0 && (
                  <div className="mb-2">
                    <p className="font-medium text-orange-800 text-sm">💡 Key points to consider:</p>
                    <ul className="list-disc list-inside text-sm text-orange-700">
                      {feedback.missing_points.map((point: string, i: number) => (
                        <li key={i}>{point}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {feedback.explanation && (
                  <div className="bg-white p-3 rounded border">
                    <p className="font-medium text-gray-800 mb-1">📖 Explanation:</p>
                    <p className="text-gray-700">{feedback.explanation}</p>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                {currentQuestionIndex < questions.length - 1 && (
                  <button
                    onClick={() => {
                      setCurrentQuestionIndex(currentQuestionIndex + 1)
                      setFeedback(null)
                    }}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
                  >
                    Next Question
                  </button>
                )}
                <button
                  onClick={() => setFeedback(null)}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
                >
                  Try Again
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="card my-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800 flex items-center gap-2">
        <RotateCcw size={24} />
        Interactive Practice Mode
      </h2>

      {interactiveScenarios.type === 'interview_replay' && renderInterviewReplay()}
      {interactiveScenarios.type === 'lecture_practice' && renderLectureQuestions()}
      
      {isRecordingResponse && (
        <div className="fixed bottom-6 right-6 bg-red-500 text-white p-4 rounded-lg shadow-lg flex items-center gap-2">
          <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
          <span className="font-medium">Recording your response...</span>
        </div>
      )}
    </div>
  )
}
