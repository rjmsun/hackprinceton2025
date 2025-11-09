'use client'

import { useState } from 'react'
import { Video, Eye, MessageSquare, Image, Clock, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react'

interface VideoAnalysisProps {
  videoAnalysis: any
  isProcessing: boolean
}

export default function VideoAnalysisPanel({ videoAnalysis, isProcessing }: VideoAnalysisProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>('summary')

  if (isProcessing) {
    return (
      <div className="card bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600">
        <div className="flex items-center gap-3 mb-4">
          <Video className="text-purple-600 animate-pulse" size={28} />
          <h2 className="text-2xl font-bold text-gray-800">Video Analysis</h2>
        </div>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing video frames with AI vision...</p>
          <p className="text-sm text-gray-500 mt-2">This may take a minute</p>
        </div>
      </div>
    )
  }

  if (!videoAnalysis) {
    return null
  }

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <div className="card bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600">
      <div className="flex items-center gap-3 mb-6">
        <Video className="text-purple-600" size={32} />
        <div>
          <h2 className="text-2xl font-bold text-gray-800">📹 Video Analysis</h2>
          <p className="text-sm text-gray-600">AI-powered visual insights</p>
        </div>
      </div>

      {/* Narrative Summary */}
      <div className="mb-6">
        <button
          onClick={() => toggleSection('summary')}
          className="w-full flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-all"
        >
          <div className="flex items-center gap-3">
            <MessageSquare className="text-blue-600" size={24} />
            <div className="text-left">
              <h3 className="font-bold text-gray-800">Narrative Summary</h3>
              <p className="text-sm text-gray-600">AI-generated overview of video content</p>
            </div>
          </div>
          {expandedSection === 'summary' ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>
        
        {expandedSection === 'summary' && (
          <div className="mt-3 p-4 bg-white rounded-lg border border-gray-200">
            <p className="text-gray-800 leading-relaxed">
              {videoAnalysis.narrative || videoAnalysis.summary || "No narrative summary available"}
            </p>
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div className="bg-blue-50 p-3 rounded">
                <div className="text-blue-800 font-semibold">Duration</div>
                <div className="text-lg font-bold text-blue-600">
                  {videoAnalysis.video_duration_seconds?.toFixed(1) || 0}s
                </div>
              </div>
              <div className="bg-green-50 p-3 rounded">
                <div className="text-green-800 font-semibold">Frames</div>
                <div className="text-lg font-bold text-green-600">
                  {videoAnalysis.total_frames_analyzed || 0}
                </div>
              </div>
              <div className="bg-purple-50 p-3 rounded">
                <div className="text-purple-800 font-semibold">Key Scenes</div>
                <div className="text-lg font-bold text-purple-600">
                  {videoAnalysis.key_scenes?.length || 0}
                </div>
              </div>
              <div className="bg-orange-50 p-3 rounded">
                <div className="text-orange-800 font-semibold">Slides</div>
                <div className="text-lg font-bold text-orange-600">
                  {videoAnalysis.slide_changes?.length || 0}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Key Scenes */}
      {videoAnalysis.key_scenes && videoAnalysis.key_scenes.length > 0 && (
        <div className="mb-6">
          <button
            onClick={() => toggleSection('scenes')}
            className="w-full flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-all"
          >
            <div className="flex items-center gap-3">
              <Eye className="text-purple-600" size={24} />
              <div className="text-left">
                <h3 className="font-bold text-gray-800">Key Scenes ({videoAnalysis.key_scenes.length})</h3>
                <p className="text-sm text-gray-600">Important moments detected by AI</p>
              </div>
            </div>
            {expandedSection === 'scenes' ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          
          {expandedSection === 'scenes' && (
            <div className="mt-3 space-y-3">
              {videoAnalysis.key_scenes.slice(0, 5).map((scene: any, index: number) => (
                <div key={index} className="p-4 bg-white rounded-lg border border-gray-200">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Clock className="text-gray-500" size={16} />
                      <span className="font-semibold text-gray-800">
                        {scene.timestamp?.toFixed(1)}s
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      {[...Array(Math.min(scene.importance || 0, 5))].map((_, i) => (
                        <span key={i} className="text-yellow-500">⭐</span>
                      ))}
                    </div>
                  </div>
                  <p className="text-gray-700 mb-2">{scene.description}</p>
                  {scene.details && (
                    <div className="text-xs text-gray-600 space-y-1">
                      {scene.details.faces > 0 && (
                        <div>👥 {scene.details.faces} person(s) visible</div>
                      )}
                      {scene.details.objects && scene.details.objects.length > 0 && (
                        <div>🏷️ Objects: {scene.details.objects.join(', ')}</div>
                      )}
                      {scene.details.text_preview && (
                        <div className="mt-2 p-2 bg-gray-50 rounded italic">
                          "{scene.details.text_preview}"
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Slide Changes (OCR) */}
      {videoAnalysis.slide_changes && videoAnalysis.slide_changes.length > 0 && (
        <div className="mb-6">
          <button
            onClick={() => toggleSection('slides')}
            className="w-full flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-all"
          >
            <div className="flex items-center gap-3">
              <Image className="text-orange-600" size={24} />
              <div className="text-left">
                <h3 className="font-bold text-gray-800">Slide Content ({videoAnalysis.slide_changes.length})</h3>
                <p className="text-sm text-gray-600">Text extracted via OCR</p>
              </div>
            </div>
            {expandedSection === 'slides' ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          
          {expandedSection === 'slides' && (
            <div className="mt-3 space-y-3">
              {videoAnalysis.slide_changes.map((slide: any, index: number) => (
                <div key={index} className="p-4 bg-white rounded-lg border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="text-gray-500" size={16} />
                    <span className="font-semibold text-gray-800">
                      Slide #{index + 1} at {slide.timestamp?.toFixed(1)}s
                    </span>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <p className="text-gray-700 text-sm whitespace-pre-wrap">
                      {slide.text || slide.full_text}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Emotions Timeline */}
      {videoAnalysis.emotions_timeline && videoAnalysis.emotions_timeline.length > 0 && (
        <div className="mb-6">
          <button
            onClick={() => toggleSection('emotions')}
            className="w-full flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-all"
          >
            <div className="flex items-center gap-3">
              <TrendingUp className="text-green-600" size={24} />
              <div className="text-left">
                <h3 className="font-bold text-gray-800">Emotions Timeline</h3>
                <p className="text-sm text-gray-600">Facial expression analysis</p>
              </div>
            </div>
            {expandedSection === 'emotions' ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          
          {expandedSection === 'emotions' && (
            <div className="mt-3 p-4 bg-white rounded-lg border border-gray-200">
              <div className="space-y-2">
                {videoAnalysis.emotions_timeline.slice(0, 10).map((emotion: any, index: number) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                      {emotion.timestamp?.toFixed(1)}s
                    </span>
                    <span className="font-semibold text-gray-800 capitalize">
                      {emotion.dominant_emotion || 'neutral'} 
                      {emotion.dominant_emotion === 'happy' && ' 😊'}
                      {emotion.dominant_emotion === 'surprised' && ' 😮'}
                      {emotion.dominant_emotion === 'neutral' && ' 😐'}
                      {emotion.dominant_emotion === 'sad' && ' 😔'}
                      {emotion.dominant_emotion === 'angry' && ' 😠'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Insights */}
      <div className="bg-blue-600 text-white p-4 rounded-lg">
        <h4 className="font-semibold mb-2 flex items-center gap-2">
          <span>💡</span> Video Insights
        </h4>
        <ul className="space-y-1 text-sm">
          {videoAnalysis.has_slides && (
            <li>✓ Presentation detected - {videoAnalysis.slide_changes?.length} slides with OCR</li>
          )}
          {videoAnalysis.has_faces && (
            <li>✓ People visible - emotion tracking enabled</li>
          )}
          {videoAnalysis.key_scenes && videoAnalysis.key_scenes.length > 0 && (
            <li>✓ {videoAnalysis.key_scenes.length} key moments identified</li>
          )}
          {!videoAnalysis.has_slides && !videoAnalysis.has_faces && (
            <li>ℹ️ Video analyzed - see key scenes above</li>
          )}
        </ul>
      </div>
    </div>
  )
}

