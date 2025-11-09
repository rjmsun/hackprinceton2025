'use client'

import { useState } from 'react'
import Dashboard from '@/components/Dashboard'
import RecordingPanel from '@/components/RecordingPanel'
import TasksPanel from '@/components/TasksPanel'
import SummaryPanel from '@/components/SummaryPanel'
import axios from 'axios'
import { Loader2 } from 'lucide-react'
import { useTheme } from '@/app/layout'

export default function Home() {
  const [transcript, setTranscript] = useState('')
  const [tasks, setTasks] = useState([])
  const [summary, setSummary] = useState<any>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isTranscriptReady, setIsTranscriptReady] = useState(false)
  const [isAnalysisRunning, setIsAnalysisRunning] = useState(false)

  const { theme, toggleTheme } = useTheme()

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
    <main className="min-h-screen bg-gray-50 dark:bg-darkbg transition-colors duration-500">
      {/* Global overlay loader */}
      {isProcessing && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-carddark p-5 rounded-2xl flex items-center gap-3 shadow-xl">
            <Loader2 className="animate-spin text-indigo-600 dark:text-primary" size={30} />
            <span className="text-gray-800 dark:text-textdark font-semibold">Processing...</span>
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
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-800 dark:text-textdark tracking-tight">EVE</h1>
                <p className="text-sm text-gray-600 dark:text-textmuted">Your Everyday Virtual Executive</p>
              </div>
            </div>

            {/* Right: Integrations + Dark Mode Toggle */}
            <div className="flex items-center gap-2">
              <div className="hidden md:flex gap-2 flex-wrap justify-end">
                {['🎙️ Whisper', '🧠 GPT-4o', '🤖 Gemini 2.5', '📅 Calendar', '🗣️ ElevenLabs'].map((tech) => (
                  <span
                    key={tech}
                    className="px-3 py-1 bg-white/70 dark:bg-buttondark rounded-full text-xs text-gray-700 dark:text-textdark shadow-sm"
                  >
                    {tech}
                  </span>
                ))}
              </div>

              <button
                onClick={toggleTheme}
                className="ml-4 px-3 py-1 w-[150px] bg-gray-200 dark:bg-buttondark rounded-lg shadow-sm text-gray-800 dark:text-textdark hover:bg-gray-300 dark:hover:bg-buttondarkHover transition-colors text-sm flex items-center justify-center"
              >
                {theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}
              </button>
            </div>
          </div>
        </header>

        {/* Spacer */}
        <div className="h-6 md:h-8 bg-transparent"></div>

        {/* Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="card bg-white dark:bg-carddark text-gray-900 dark:text-textdark shadow-md transition-colors">
            <RecordingPanel
              onTranscriptUpdate={setTranscript}
              onProcessingChange={setIsProcessing}
              onTasksExtracted={setTasks}
              onSummaryGenerated={setSummary}
              onTranscriptFinalized={handleTranscriptFinalized}
            />
          </div>

          <div className="card bg-white dark:bg-carddark text-gray-900 dark:text-textdark shadow-md transition-colors">
            <SummaryPanel summary={summary} isProcessing={isProcessing || isAnalysisRunning} />
          </div>
        </div>

        {/* Smart Analysis Button */}
        {isTranscriptReady && !summary && (
          <div className="text-center my-6">
            <button
              onClick={handleSmartAnalysis}
              disabled={isAnalysisRunning}
              className="px-6 py-3 bg-primary hover:bg-indigo-700 text-white font-semibold rounded-lg shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 mx-auto"
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
          <div className="card bg-white dark:bg-carddark text-gray-900 dark:text-textdark shadow-md transition-colors">
            <TasksPanel tasks={tasks} onTasksUpdate={setTasks} />
          </div>
        </div>

        <div className="card bg-white dark:bg-carddark text-gray-900 dark:text-textdark shadow-md transition-colors">
          <Dashboard tasksCount={tasks.length} transcript={transcript} />
        </div>
      </div>
    </main>
  )
}
