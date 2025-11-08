'use client'

import { BarChart, Calendar, MessageSquare } from 'lucide-react'

export default function Dashboard({ tasksCount, transcript }: any) {
  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Analytics Dashboard</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <MessageSquare className="text-blue-600" size={32} />
            <span className="text-3xl font-bold text-blue-700">1</span>
          </div>
          <p className="text-sm text-blue-800 font-medium">Sessions Today</p>
        </div>
        
        <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <Calendar className="text-green-600" size={32} />
            <span className="text-3xl font-bold text-green-700">{tasksCount}</span>
          </div>
          <p className="text-sm text-green-800 font-medium">Tasks Extracted</p>
        </div>
        
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <BarChart className="text-purple-600" size={32} />
            <span className="text-3xl font-bold text-purple-700">
              {transcript ? Math.floor(transcript.split(' ').length / 150) : 0}
            </span>
          </div>
          <p className="text-sm text-purple-800 font-medium">Minutes Processed</p>
        </div>
      </div>

      <div className="mt-8 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200">
        <p className="text-sm text-gray-700 text-center">
          💡 <strong>Pro tip:</strong> EVE learns from your conversations to provide better insights over time
        </p>
      </div>
    </div>
  )
}

