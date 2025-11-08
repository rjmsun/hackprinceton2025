'use client'

import { FileText, Loader2, Volume2 } from 'lucide-react'
import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function SummaryPanel({ summary, isProcessing }: any) {
  const [isPlayingAudio, setIsPlayingAudio] = useState(false)
  const [activeTab, setActiveTab] = useState<'openai' | 'gemini'>('openai')

  const playVoiceSummary = async () => {
    if (!summary) return;

    setIsPlayingAudio(true);
    try {
      // Create a motivational recap from summary
      let summaryText = `Great work! Here is what we captured: ${summary.short_summary}. `;
      
      if (summary.knowledge_gaps && summary.knowledge_gaps.length > 0) {
        const gapsText = summary.knowledge_gaps.join(', ');
        summaryText += `I noticed you are working on understanding ${gapsText}. Keep pushing forward!`;
      } else {
        summaryText += 'You are making excellent progress!';
      }

      const actions = [
        { title: 'Summary & Motivation', description: summaryText }
      ];

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
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold text-gray-800">Smart Summaries</h2>
          {summary && (
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('openai')}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'openai' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                OpenAI GPT-4o
              </button>
              <button
                onClick={() => setActiveTab('gemini')}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'gemini' 
                    ? 'bg-blue-100 text-blue-800' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Gemini 2.5 Flash
              </button>
            </div>
          )}
        </div>
        {summary && (
          <button
            onClick={playVoiceSummary}
            disabled={isPlayingAudio}
            className="flex items-center gap-2 px-4 py-2 bg-purple-100 hover:bg-purple-200 text-purple-700 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            <Volume2 size={18} />
            {isPlayingAudio ? '🔊 Speaking...' : '🗣️ Speak Summary'}
          </button>
        )}
      </div>

      {isProcessing ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-indigo-600" size={32} />
          <span className="ml-2">Analyzing...</span>
        </div>
      ) : summary ? (
        <div className="space-y-4">
          {/* Show OpenAI or Gemini summary based on active tab */}
          {activeTab === 'openai' ? (
            <>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <FileText className="text-green-600 mt-1" size={20} />
                  <div>
                    <h3 className="font-semibold text-green-900 mb-1">OpenAI GPT-4o Summary</h3>
                    <p className="text-green-800">{summary.short_summary}</p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-800 mb-3">Detailed Summary</h3>
                <ul className="space-y-2">
                  {summary.detailed_summary?.map((item: string, index: number) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-green-600 font-bold mt-0.5">•</span>
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
            </>
          ) : (
            <>
              {/* Gemini Summary */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <FileText className="text-blue-600 mt-1" size={20} />
                  <div>
                    <h3 className="font-semibold text-blue-900 mb-1">Gemini 2.5 Flash Summary</h3>
                    <p className="text-blue-800">
                      {summary.gemini_alternative?.short_summary || 
                       (typeof summary.gemini_alternative === 'string' 
                         ? summary.gemini_alternative 
                         : 'Processing Gemini summary...')}
                    </p>
                  </div>
                </div>
              </div>

              {summary.gemini_alternative?.detailed_summary && Array.isArray(summary.gemini_alternative.detailed_summary) && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-800 mb-3">Detailed Summary (Gemini)</h3>
                  <ul className="space-y-2">
                    {summary.gemini_alternative.detailed_summary.map((item: string, index: number) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-blue-600 font-bold mt-0.5">•</span>
                        <span className="text-gray-700">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-2 text-center text-sm text-blue-700">
                💡 Comparing multiple AI models helps you get a more comprehensive understanding!
              </div>
            </>
          )}

                  {summary.knowledge_gaps && summary.knowledge_gaps.length > 0 && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <h3 className="font-semibold text-red-900 mb-3">⚠️ Knowledge Gaps Detected</h3>
                      <ul className="space-y-2">
                        {summary.knowledge_gaps.map((gap: string, index: number) => (
                          <li key={index} className="flex items-start gap-2">
                            <span className="text-red-600 font-bold mt-0.5">!</span>
                            <span className="text-red-800">{gap}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {summary.strengths && summary.strengths.length > 0 && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <h3 className="font-semibold text-green-900 mb-3">✅ Strengths Demonstrated</h3>
                      <ul className="space-y-2">
                        {summary.strengths.map((strength: string, index: number) => (
                          <li key={index} className="flex items-start gap-2">
                            <span className="text-green-600 font-bold mt-0.5">+</span>
                            <span className="text-green-800">{strength}</span>
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
          <p className="text-gray-500">Generate smart analysis to see summaries here...</p>
        </div>
      )}
    </div>
  )
}

