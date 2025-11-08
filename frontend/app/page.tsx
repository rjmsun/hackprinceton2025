'use client'

import { useState } from 'react'
import Dashboard from '@/components/Dashboard'
import RecordingPanel from '@/components/RecordingPanel'
import TasksPanel from '@/components/TasksPanel'
import SummaryPanel from '@/components/SummaryPanel'

export default function Home() {
  const [transcript, setTranscript] = useState('')
  const [tasks, setTasks] = useState([])
  const [summary, setSummary] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex justify-center items-center mb-4">
            <img 
              src="/logo.svg" 
              alt="EVE Logo" 
              className="h-20 w-20 object-contain"
              onError={(e) => {
                // Try alternative formats if SVG doesn't exist
                const formats = ['png', 'jpg', 'jpeg', 'webp'];
                const currentSrc = e.currentTarget.src;
                const basePath = currentSrc.substring(0, currentSrc.lastIndexOf('.'));
                let formatIndex = 0;
                
                const tryNextFormat = () => {
                  if (formatIndex < formats.length) {
                    e.currentTarget.src = `${basePath}.${formats[formatIndex]}`;
                    formatIndex++;
                  }
                };
                
                e.currentTarget.onerror = tryNextFormat;
                tryNextFormat();
              }}
            />
          </div>
          <p className="text-xl text-gray-600">
            Your Everyday Virtual Executive
          </p>
          <div className="mt-4 flex justify-center gap-2 flex-wrap">
            <span className="px-3 py-1 bg-white rounded-full text-sm text-gray-700 shadow-sm">
              🎙️ OpenAI Whisper
            </span>
            <span className="px-3 py-1 bg-white rounded-full text-sm text-gray-700 shadow-sm">
              🧠 Claude 3.5
            </span>
            <span className="px-3 py-1 bg-white rounded-full text-sm text-gray-700 shadow-sm">
              📅 Google Calendar
            </span>
            <span className="px-3 py-1 bg-white rounded-full text-sm text-gray-700 shadow-sm">
              🗣️ ElevenLabs
            </span>
          </div>
        </header>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <RecordingPanel 
            onTranscriptUpdate={setTranscript}
            onProcessingChange={setIsProcessing}
            onTasksExtracted={setTasks}
            onSummaryGenerated={setSummary}
          />
          
          <SummaryPanel 
            summary={summary}
            isProcessing={isProcessing}
          />
        </div>

        <div className="grid grid-cols-1 gap-6 mb-6">
          <TasksPanel 
            tasks={tasks}
            onTasksUpdate={setTasks}
          />
        </div>

        <Dashboard 
          tasksCount={tasks.length}
          transcript={transcript}
        />
      </div>
    </main>
  )
}

