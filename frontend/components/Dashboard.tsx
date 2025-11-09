'use client'

import { BarChart, Calendar, MessageSquare } from 'lucide-react'

export default function Dashboard({ tasksCount, transcript }: any) {
  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Analytics Dashboard</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-blue-50 dark:bg-gray-700 p-6 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <MessageSquare className="text-blue-600" size={32} />
            <span className="text-3xl font-bold text-blue-700">1</span>
          </div>
          <p className="text-sm text-blue-800 font-medium">Sessions Today</p>
        </div>
        
        <div className="bg-green-50 dark:bg-gray-700 p-6 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <Calendar className="text-green-600" size={32} />
            <span className="text-3xl font-bold text-green-700">{tasksCount}</span>
          </div>
          <p className="text-sm text-green-800 font-medium">Tasks Extracted</p>
        </div>
        
        <div className="bg-purple-50 dark:bg-gray-700 p-6 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <BarChart className="text-purple-600" size={32} />
            <span className="text-3xl font-bold text-purple-700">
              {transcript ? Math.floor(transcript.split(' ').length / 150) : 0}
            </span>
          </div>
          <p className="text-sm text-purple-800 font-medium">Minutes Processed</p>
        </div>
      </div>

      <div className="mt-8 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
        <p className="text-sm text-gray-700 text-center">
          💡 <strong>Pro tip:</strong> EVE learns from your conversations to provide better insights over time
        </p>
      </div>
    </div>
  )
}

