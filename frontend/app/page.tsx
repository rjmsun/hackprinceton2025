'use client'

import { useState } from 'react'
import Dashboard from '@/components/Dashboard'
import RecordingPanel from '@/components/RecordingPanel'
import TasksPanel from '@/components/TasksPanel'
import SummaryPanel from '@/components/SummaryPanel'
import axios from 'axios'
import { Loader2 } from 'lucide-react'

export default function Home() {
  const [transcript, setTranscript] = useState('')
  const [tasks, setTasks] = useState([])
  const [summary, setSummary] = useState<any>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isTranscriptReady, setIsTranscriptReady] = useState(false)
  const [isAnalysisRunning, setIsAnalysisRunning] = useState(false)

  // normalize Gemini responses (in case they come as markdown JSON)
  const normalizeGemini = (raw: any) => {
    if (!raw) return null
    if (typeof raw === 'string') {
      const cleaned = raw.trim().replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/i, '')
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
      const response = await axios.post(`http://localhost:8000/process/transcript`, {
        text: transcript,
        user_id: 'demo_user',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      })
      setTasks(response.data.tasks || [])
      const openAiSummary = response.data.summary_openai || response.data.summary || null
      const geminiSummary = normalizeGemini(response.data.summary_gemini || null)
      setSummary({
        ...openAiSummary,
        gemini_alternative: geminiSummary,
      })
    } catch (error: any) {
      console.error('Smart analysis error:', error)
      const detail = error?.response?.data?.detail || error?.message || 'Unknown error'
      alert(`Failed to generate smart analysis. Details: ${detail}`)
    } finally {
      setIsAnalysisRunning(false)
      setIsProcessing(false)
    }
  }

  const handleTranscriptFinalized = (finalTranscript: string) => {
    setTranscript(finalTranscript)
    setIsTranscriptReady(true)
    setIsProcessing(false)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-500">

      {/* Global overlay loader */}
      {isProcessing && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl flex items-center gap-3 shadow-xl">
            <Loader2 className="animate-spin text-indigo-600 dark:text-indigo-400" size={30} />
            <span className="text-gray-800 dark:text-gray-100 font-semibold">Processing...</span>
          </div>
        </div>
      )}

      <div className="container mx-auto px-4 py-8">
        <header className="sticky top-0 z-40 w-full backdrop-blur-md bg-white/40 dark:bg-gray-800/40 border-b border-white/20 dark:border-gray-700/50 shadow-sm transition-all">
          <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-3">
            {/* Left side: Logo + Name */}
            <div className="flex items-center gap-3">
              <img
                src="/logo.svg"
                alt="EVE Logo"
                className="h-10 w-10 md:h-12 md:w-12 object-contain transition-transform duration-300 hover:scale-105 dark:drop-shadow-[0_0_0.5rem_#6366f1]"
                onError={(e) => {
                  const formats = ['png', 'jpg', 'jpeg', 'webp']
                  const currentSrc = e.currentTarget.src
                  const basePath = currentSrc.substring(0, currentSrc.lastIndexOf('.'))
                  let formatIndex = 0
                  const tryNextFormat = () => {
                    if (formatIndex < formats.length) {
                      e.currentTarget.src = `${basePath}.${formats[formatIndex]}`
                      formatIndex++
                    }
                  }
                  e.currentTarget.onerror = tryNextFormat
                  tryNextFormat()
                }}
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100 tracking-tight">
                  EVE
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Your Everyday Virtual Executive
                </p>
              </div>
            </div>

            {/* Right side: Integrations */}
            <div className="hidden md:flex gap-2 flex-wrap justify-end">
              {[
                '🎙️ Whisper',
                '🧠 GPT-4o',
                '🤖 Gemini 2.5',
                '📅 Calendar',
                '🗣️ ElevenLabs',
              ].map((tech) => (
                <span
                  key={tech}
                  className="px-3 py-1 bg-white/70 dark:bg-gray-700/50 rounded-full text-xs text-gray-700 dark:text-gray-200 shadow-sm"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </header>

        {/* Blank lip section */}
        <div className="h-6 md:h-8 bg-transparent"></div>

        {/* Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="card bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-md transition-all">
            <RecordingPanel
              onTranscriptUpdate={setTranscript}
              onProcessingChange={setIsProcessing}
              onTasksExtracted={setTasks}
              onSummaryGenerated={setSummary}
              onTranscriptFinalized={handleTranscriptFinalized}
            />
          </div>

          <div className="card bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-md transition-all">
            <SummaryPanel summary={summary} isProcessing={isProcessing || isAnalysisRunning} />
          </div>
        </div>

        {/* Smart Analysis Button */}
        {isTranscriptReady && !summary && (
          <div className="text-center my-6">
            <button
              onClick={handleSmartAnalysis}
              disabled={isAnalysisRunning}
              className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 mx-auto"
            >
              {isAnalysisRunning ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Analyzing...
                </>
              ) : (
                '✨ Generate Smart Analysis & Tasks'
              )}
            </button>
          </div>
        )}

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
    </main>
  )
}
