'use client'

import { Lightbulb, Target, CheckCircle, Smile, Meh, Frown } from 'lucide-react'

export default function CoachingPanel({ insights, vibe, context }: { insights: any, vibe: any, context: string }) {
  if ((!insights || Object.keys(insights).length === 0 || insights.error) && (!vibe || Object.keys(vibe).length === 0)) {
    return null; // Don't render if no data for either section
  }

  const VibeIcon = () => {
    if (!vibe || !vibe.vibe) return <Meh size={20} />;
    switch (vibe.vibe.toLowerCase()) {
      case 'engaged': return <Smile size={20} className="text-green-600" />;
      case 'neutral': return <Meh size={20} className="text-gray-600" />;
      case 'disinterested': return <Frown size={20} className="text-red-600" />;
      default: return <Meh size={20} />;
    }
  };

  const renderVibeCheck = () => (
    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
      <h4 className="font-semibold text-purple-900 mb-3 flex items-center gap-2">
        <VibeIcon /> Vibe Check
      </h4>
      <p className="text-gray-700 mb-2">
        The interviewer's/professional's sentiment appears to be: <strong className="text-purple-800">{vibe.vibe || 'Unknown'}</strong>
      </p>
      {vibe.evidence && vibe.evidence.length > 0 && (
        <div>
          <p className="text-sm font-semibold text-gray-600 mb-1">Evidence:</p>
          <ul className="space-y-1 text-sm list-disc list-inside">
            {vibe.evidence.map((item: string, index: number) => (
              <li key={index} className="text-gray-600 italic">"{item}"</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderInterviewFeedback = () => (
    <div>
      <h3 className="text-xl font-bold text-gray-800 mb-4">Interview Feedback</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="font-semibold text-green-900 mb-3 flex items-center gap-2"><CheckCircle size={20} /> Strengths</h4>
          <ul className="space-y-2">
            {insights.strengths?.map((item: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-green-600 font-bold mt-0.5">+</span>
                <span className="text-gray-700">{item}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-semibold text-yellow-900 mb-3 flex items-center gap-2"><Target size={20} /> Areas for Improvement</h4>
          <ul className="space-y-3">
            {insights.areas_for_improvement?.map((item: any, index: number) => (
              <li key={index}>
                <p className="text-gray-700 italic">"{item.quote}"</p>
                <p className="text-yellow-800 mt-1"><span className="font-semibold">Suggestion:</span> {item.suggestion}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );

  const renderCoffeeChatTips = () => (
    <div>
      <h3 className="text-xl font-bold text-gray-800 mb-4">Coffee Chat Takeaways</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2"><Lightbulb size={20} /> Key Career Tips</h4>
          <ul className="space-y-2">
            {insights.key_tips?.map((item: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">•</span>
                <span className="text-gray-700">{item}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
          <h4 className="font-semibold text-indigo-900 mb-3 flex items-center gap-2"><Target size={20} /> Recommended Follow-Ups</h4>
          <ul className="space-y-2">
            {insights.follow_ups?.map((item: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-indigo-600 font-bold mt-0.5">→</span>
                <span className="text-gray-700">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );

  return (
    <div className="card my-6">
      {context === 'interview' && renderInterviewFeedback()}
      {context === 'coffee_chat' && renderCoffeeChatTips()}
      {vibe && Object.keys(vibe).length > 0 && (context === 'interview' || context === 'coffee_chat') && renderVibeCheck()}
    </div>
  );
}
