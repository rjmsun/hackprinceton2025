'use client'

import { FileText, Loader2, Volume2 } from 'lucide-react'
import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function SummaryPanel({ summary, isProcessing }: any) {
  const [isPlayingAudio, setIsPlayingAudio] = useState(false)

  const playVoiceSummary = async () => {
    if (!summary) return

    setIsPlayingAudio(true)
    try {
      // Create a simple actions array from summary
      const actions = [
        { title: 'Meeting Summary', description: summary.short_summary }
      ]

      const response = await axios.post(
        `${API_URL}/voice/summary`,
        actions,
        { responseType: 'blob' }
      )

      const audioBlob = new Blob([response.data], { type: 'audio/mpeg' })
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      
      audio.onended = () => {
        setIsPlayingAudio(false)
        URL.revokeObjectURL(audioUrl)
      }
      
      audio.onerror = () => {
        setIsPlayingAudio(false)
        alert('Audio playback failed. Make sure ElevenLabs API key is configured.')
      }
      
      audio.play()
    } catch (error) {
      console.error('Voice summary error:', error)
      setIsPlayingAudio(false)
      alert('Voice generation failed. Check ElevenLabs API key.')
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Summary</h2>
        {summary && (
          <button
            onClick={playVoiceSummary}
            disabled={isPlayingAudio}
            className="flex items-center gap-2 px-4 py-2 bg-purple-100 hover:bg-purple-200 text-purple-700 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            <Volume2 size={18} />
            {isPlayingAudio ? 'Playing...' : 'Listen'}
          </button>
        )}
      </div>

      {isProcessing ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-primary" size={32} />
        </div>
      ) : summary ? (
        <div className="space-y-4">
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <FileText className="text-indigo-600 mt-1" size={20} />
              <div>
                <h3 className="font-semibold text-indigo-900 mb-1">Quick Summary</h3>
                <p className="text-indigo-800">{summary.short_summary}</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-3">Detailed Summary</h3>
            <ul className="space-y-2">
              {summary.detailed_summary?.map((item: string, index: number) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-primary font-bold mt-0.5">•</span>
                  <span className="text-gray-700">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {summary.insights && summary.insights.length > 0 && (
            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
              <h3 className="font-semibold text-indigo-900 mb-3">💡 Key Insights</h3>
              <ul className="space-y-2">
                {summary.insights.map((insight: string, index: number) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-indigo-600 font-bold mt-0.5">→</span>
                    <span className="text-indigo-800">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {summary.clarifying_questions && summary.clarifying_questions.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="font-semibold text-yellow-900 mb-3">❓ Questions to Consider</h3>
              <ul className="space-y-2">
                {summary.clarifying_questions.map((question: string, index: number) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-yellow-600 font-bold mt-0.5">?</span>
                    <span className="text-yellow-800">{question}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-12">
          <FileText className="mx-auto mb-4 text-gray-400" size={48} />
          <p className="text-gray-500">Process audio to see the summary here...</p>
        </div>
      )}
    </div>
  )
}

