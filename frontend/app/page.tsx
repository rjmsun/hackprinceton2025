'use client'

import { useState } from 'react'
import Dashboard from '@/components/Dashboard'
import RecordingPanel from '@/components/RecordingPanel'
import TasksPanel from '@/components/TasksPanel'
import SummaryPanel from '@/components/SummaryPanel'
import axios from 'axios';
import { Loader2 } from 'lucide-react';

export default function Home() {
  const [transcript, setTranscript] = useState('')
  const [tasks, setTasks] = useState([])
  const [summary, setSummary] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isTranscriptReady, setIsTranscriptReady] = useState(false)
  const [isAnalysisRunning, setIsAnalysisRunning] = useState(false)

  const handleSmartAnalysis = async () => {
    if (!transcript) return;
    setIsAnalysisRunning(true);
    setIsProcessing(true); // Use the main processing spinner
    try {
      const response = await axios.post(`http://localhost:8000/process/transcript`, {
        text: transcript,
        user_id: 'demo_user',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      });
      setTasks(response.data.tasks || []);
      const openAiSummary = response.data.summary_openai || response.data.summary || null;
      const geminiSummary = response.data.summary_gemini || null;
      setSummary({ 
        ...openAiSummary, 
        gemini_alternative: geminiSummary 
      });
    } catch (error) {
      console.error('Smart analysis error:', error);
      alert('Failed to generate smart analysis. Please check the console.');
    } finally {
      setIsAnalysisRunning(false);
      setIsProcessing(false);
    }
  };

  const handleTranscriptFinalized = (finalTranscript: string) => {
    setTranscript(finalTranscript);
    setIsTranscriptReady(true);
    setIsProcessing(false); // Stop the initial processing spinner
  };

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
              🧠 GPT-4o
            </span>
            <span className="px-3 py-1 bg-white rounded-full text-sm text-gray-700 shadow-sm">
              🤖 Gemini 2.5
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
            onTranscriptFinalized={handleTranscriptFinalized}
          />
          
          <SummaryPanel 
            summary={summary}
            isProcessing={isProcessing || isAnalysisRunning}
          />
        </div>

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

