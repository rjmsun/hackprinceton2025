'use client'

import { useState } from 'react'
import { useTheme } from './layout'
import Dashboard from '@/components/Dashboard'
import RecordingPanel from '@/components/RecordingPanel'
import TasksPanel from '@/components/TasksPanel'
import SummaryPanel from '@/components/SummaryPanel'
import axios from 'axios'
import { Loader2, MessageCircle } from 'lucide-react'
import CoachingPanel from '@/components/CoachingPanel'
import AIPracticePanel from '@/components/AIPracticePanel'
import VideoAnalysisPanel from '@/components/VideoAnalysisPanel'

export default function Home() {
  const [transcript, setTranscript] = useState('')
  const [tasks, setTasks] = useState([])
  const [summary, setSummary] = useState<any>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isTranscriptReady, setIsTranscriptReady] = useState(false)
  const [isAnalysisRunning, setIsAnalysisRunning] = useState(false)
  const [context, setContext] = useState<
    'general' | 'interview' | 'coffee_chat' | 'lecture'
  >('general')
  const [coachingInsights, setCoachingInsights] = useState<any>(null)
  const [vibeAnalysis, setVibeAnalysis] = useState<any>(null)
  const [mediaType, setMediaType] = useState<'audio' | 'video'>('audio')
  const [showAIPractice, setShowAIPractice] = useState(false)
  const [videoAnalysis, setVideoAnalysis] = useState<any>(null)
  const [isVideo, setIsVideo] = useState(false)
  const [previousAnalyses, setPreviousAnalyses] = useState<any[]>([])
  const [showPrevious, setShowPrevious] = useState(false)

  const { theme, toggleTheme } = useTheme()

  const deleteAnalysis = (analysisId: number) => {
    setPreviousAnalyses(prev => prev.filter(analysis => analysis.id !== analysisId))
  }

  const loadAnalysis = (analysis: any) => {
    setTranscript(analysis.transcript)
    setTasks(analysis.tasks)
    setSummary(analysis.summary)
    setCoachingInsights(analysis.coachingInsights)
    setVibeAnalysis(analysis.vibeAnalysis)
    setVideoAnalysis(analysis.videoAnalysis)
    setIsVideo(analysis.isVideo)
    setContext(analysis.context)
    setMediaType(analysis.mediaType)
    setIsTranscriptReady(!!analysis.transcript)
    setShowPrevious(false) // Close drawer after loading
  }

  const startNewAnalysis = () => {
    // Save current analysis to previous analyses
    if (transcript || summary || videoAnalysis) {
      const currentAnalysis = {
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        transcript,
        summary,
        tasks,
        coachingInsights,
        vibeAnalysis,
        videoAnalysis,
        isVideo,
        context,
        mediaType
      }
      setPreviousAnalyses([currentAnalysis, ...previousAnalyses])
    }

    // Reset all state
    setTranscript('')
    setTasks([])
    setSummary(null)
    setCoachingInsights(null)
    setVibeAnalysis(null)
    setVideoAnalysis(null)
    setIsVideo(false)
    setIsTranscriptReady(false)
    setShowAIPractice(false)
  }

  const normalizeGemini = (raw: any) => {
    if (!raw) return null
    if (typeof raw === 'string') {
      const cleaned = raw
        .trim()
        .replace(/^```(?:json)?\s*/i, '')
        .replace(/```\s*$/i, '')
      try {
        return JSON.parse(cleaned)
      } catch {
        return raw
      }
    }
    return raw
  }

  const handleSmartAnalysis = async () => {
    if (!transcript) return
    setIsAnalysisRunning(true)
    setIsProcessing(true)
    try {
      const response = await axios.post(
        `http://localhost:8000/process/transcript`,
        {
          text: transcript,
          user_id: 'demo_user',
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          context: context,
          media_type: mediaType,
        },
      )
      setTasks(response.data.tasks || [])
      const openAiSummary =
        response.data.summary_openai || response.data.summary || null
      const geminiSummary = normalizeGemini(response.data.summary_gemini || null)
      setCoachingInsights(response.data.coaching_insights || null)
      setVibeAnalysis(response.data.vibe_analysis || null)
      setSummary({
        ...openAiSummary,
        gemini_alternative: geminiSummary,
      })
    } catch (error: any) {
      console.error('Smart analysis error:', error)
      const detail =
        error?.response?.data?.detail || error?.message || 'Unknown error'
      alert(`Failed to generate smart analysis. Details: ${detail}`)
    } finally {
      setIsAnalysisRunning(false)
      setIsProcessing(false)
    }
  }

  const handleTranscriptFinalized = (
    finalTranscript: string,
    videoData?: any,
  ) => {
    setTranscript(finalTranscript)
    setIsTranscriptReady(true)
    setIsProcessing(false)

    if (videoData && videoData.is_video) {
      setIsVideo(true)
      setVideoAnalysis(videoData.video_analysis)
    } else {
      setIsVideo(false)
      setVideoAnalysis(null)
    }
  }

  return (
    <main className="min-h-screen bg-white dark:bg-gray-900 transition-colors duration-500">
      {/* Global overlay loader */}
      {isProcessing && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl flex items-center gap-3 shadow-xl">
            <Loader2
              className="animate-spin text-indigo-600 dark:text-indigo-400"
              size={30}
            />
            <span className="text-gray-800 dark:text-gray-100 font-semibold">
              {mediaType === 'video'
                ? 'Processing video (audio + visual analysis)...'
                : 'Processing audio...'}
            </span>
          </div>
        </div>
      )}

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="sticky top-0 z-40 w-full backdrop-blur-md bg-white/40 dark:bg-[#363435] border-b border-white/20 dark:border-gray-700/50 shadow-sm transition-all">
          <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-3">

            {/* Logo */}
            <div className="flex items-center gap-3">
              <img
                src={theme === 'dark' ? '/logo-dark.svg' : '/logo.svg'}
                alt="EVE Logo"
                className="h-10 w-10 md:h-12 md:w-12 object-contain transition-transform duration-300 hover:scale-105"
                onError={(e) => {
                  // Fallback if SVG doesn't exist
                  e.currentTarget.src = '/logo.svg'
                }}
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100 tracking-tight">Eve</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">Your Everyday Virtual Executive</p>
              </div>
            </div>

            {/* Right side: Start New + Theme Toggle */}
            <div className="flex items-center gap-3">
              {(transcript || summary) && (
                <button
                  onClick={startNewAnalysis}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-600 text-white rounded-lg shadow-sm transition-colors text-sm font-medium"
                  title="Start a new analysis"
                >
                  ✨ New Analysis
                </button>
              )}
              
              {previousAnalyses.length > 0 && (
                <button
                  onClick={() => setShowPrevious(!showPrevious)}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 text-white rounded-lg shadow-sm transition-colors text-sm font-medium"
                  title="View previous analyses"
                >
                  📂 History ({previousAnalyses.length})
                </button>
              )}
              
              {/* Theme Toggle Button */}
              <button
                onClick={toggleTheme}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg shadow-sm text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
                title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              >
                {theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode'}
              </button>
            </div>
          </div>
        </header>

        {/* Previous Analyses Drawer */}
        {showPrevious && previousAnalyses.length > 0 && (
          <div className="max-w-7xl mx-auto mt-4 mb-8 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100">Analysis History</h3>
              <button
                onClick={() => setShowPrevious(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2 rounded-full"
              >
                ✕
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[50vh] overflow-y-auto pr-2">
              {previousAnalyses.map((analysis) => (
                <div
                  key={analysis.id}
                  className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 flex flex-col justify-between hover:shadow-md transition-shadow"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-semibold text-gray-800 dark:text-gray-100">
                        {analysis.mediaType === 'video' ? '📹' : '🎤'} {analysis.context.replace('_', ' ')}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500 dark:text-gray-400">{analysis.timestamp.split(',')[0]}</span>
                        <button
                          onClick={() => deleteAnalysis(analysis.id)}
                          className="text-red-500 hover:text-red-700 p-1 rounded transition-colors"
                          title="Delete this analysis"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-3 mb-3">
                      {analysis.transcript?.substring(0, 150) || "No transcript available."}...
                    </p>
                  </div>
                  <button
                    onClick={() => loadAnalysis(analysis)}
                    className="w-full mt-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 text-white rounded-lg shadow-sm text-sm font-semibold transition-colors"
                  >
                    Load Analysis
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Mode Selection - Top Priority */}
        <div className="max-w-7xl mx-auto my-8 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4 text-center">
            Choose Your Mode
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Media Type Selection */}
            <div>
              <label className="block font-semibold text-gray-700 dark:text-gray-200 mb-3">
                Media Type
              </label>
              <select
                value={mediaType}
                onChange={(e) => setMediaType(e.target.value as any)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 font-medium"
              >
                <option value="audio">Audio Only (mp3, webm, wav)</option>
                <option value="video">Video + Audio (mp4) - AI Vision</option>
              </select>
              {mediaType === 'video' && (
                <p className="text-sm text-purple-600 dark:text-purple-400 mt-2">
                  Includes: GPT-4o Vision, scene analysis, OCR, object detection
                </p>
              )}
            </div>

            {/* Context Selection */}
            <div>
              <label className="block font-semibold text-gray-700 dark:text-gray-200 mb-3">
                Context Type
              </label>
              <select
                value={context}
                onChange={(e) => setContext(e.target.value as any)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 font-medium"
                disabled={isAnalysisRunning}
              >
                <option value="general">General Meeting</option>
                <option value="interview">Interview Practice</option>
                <option value="coffee_chat">Coffee Chat</option>
                <option value="lecture">Lecture / Study</option>
              </select>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Analysis will adapt based on your context choice
              </p>
            </div>
          </div>
        </div>

        {/* Panels */}
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="card bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-md transition-all">
              <RecordingPanel
                onTranscriptUpdate={setTranscript}
                onProcessingChange={setIsProcessing}
                onTasksExtracted={setTasks}
                onSummaryGenerated={setSummary}
                onTranscriptFinalized={handleTranscriptFinalized}
                mediaType={mediaType}
              />
            </div>

            <div className="card bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-md transition-all">
              <SummaryPanel
                summary={summary}
                isProcessing={isProcessing || isAnalysisRunning}
              />
            </div>
          </div>

          {/* Video Analysis Panel - Only show for video media type */}
          {mediaType === 'video' && isVideo && (
            <VideoAnalysisPanel
              videoAnalysis={videoAnalysis}
              isProcessing={isProcessing}
            />
          )}

          <CoachingPanel
            insights={coachingInsights}
            vibe={vibeAnalysis}
            context={context}
          />

          {/* AI Practice Mode - Available for both audio and video */}
          {transcript && summary && (
            <div className="my-8">
              {!showAIPractice ? (
                <div className="text-center">
                  <button
                    onClick={() => setShowAIPractice(true)}
                    className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg rounded-lg shadow-lg transition-all inline-flex items-center gap-3"
                  >
                    <MessageCircle size={24} />
                    Practice with AI
                    <span className="text-sm font-normal opacity-90">
                      (Conversational)
                    </span>
                  </button>
                  <p className="text-sm text-gray-600 mt-2">
                    Have a natural back-and-forth conversation with an AI coach
                  </p>
                </div>
              ) : (
                <AIPracticePanel
                  transcript={transcript}
                  context={context}
                  coachingInsights={coachingInsights}
                  onClose={() => setShowAIPractice(false)}
                />
              )}
            </div>
          )}

          {/* Generate Analysis - Dependent on Mode Selection */}
          <div className="text-center my-8 bg-gray-50 dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-2">
                Generate Analysis
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {!isTranscriptReady
                  ? 'Upload or record content first'
                  : `Ready to analyze your ${mediaType} content as a ${context.replace(
                      '_',
                      ' ',
                    )}`}
              </p>
            </div>

            <button
              onClick={handleSmartAnalysis}
              disabled={isAnalysisRunning || !isTranscriptReady}
              className="px-8 py-4 bg-green-600 hover:bg-green-700 text-white font-bold text-lg rounded-xl shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-3"
            >
              {isAnalysisRunning ? (
                <>
                  <Loader2 className="animate-spin" size={24} />
                  Analyzing {context.replace('_', ' ')}...
                </>
              ) : (
                <>
                  Generate Smart Analysis & Tasks
                  <span className="text-sm font-normal opacity-90">
                    ({context.replace('_', ' ')} mode)
                  </span>
                </>
              )}
            </button>
          </div>

          {/* Tasks + Dashboard */}
          <div className="grid grid-cols-1 gap-6 mb-6">
            <div className="card bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-md transition-all">
              <TasksPanel tasks={tasks} onTasksUpdate={setTasks} />
            </div>
          </div>

          <div className="card bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-md transition-all">
            <Dashboard tasksCount={tasks.length} transcript={transcript} />
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 py-6 text-center border-t border-gray-200 dark:border-gray-700">
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            Made with ❤️ for HackPrinceton 2025
          </p>
        </footer>
      </div>
    </main>
  )
}
