'use client'

import { useState } from 'react'
import { CheckCircle2, Circle, Calendar, User, AlertCircle } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function TasksPanel({ tasks, onTasksUpdate }: any) {
  const [selectedTasks, setSelectedTasks] = useState<string[]>([])
  const [isScheduling, setIsScheduling] = useState(false)

  const toggleTask = (taskId: string) => {
    setSelectedTasks(prev => 
      prev.includes(taskId) 
        ? prev.filter(id => id !== taskId)
        : [...prev, taskId]
    )
  }

  const scheduleSelected = async () => {
    if (selectedTasks.length === 0) {
      alert('Please select at least one task to schedule')
      return
    }

    // For demo: just show alert that calendar integration needs OAuth
    alert(
      'Calendar Integration:\n\n' +
      'To create real calendar events, you need to:\n' +
      '1. Set up Google OAuth credentials\n' +
      '2. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env\n' +
      '3. Implement OAuth flow in frontend\n\n' +
      'For now, this demo shows the extracted tasks ready to be scheduled.'
    )

    // In production, you would:
    // const tasksToSchedule = tasks.filter((t: any) => selectedTasks.includes(t.id))
    // await axios.post(`${API_URL}/calendar/schedule`, {
    //   tasks: tasksToSchedule,
    //   access_token: 'YOUR_GOOGLE_ACCESS_TOKEN'
    // })
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50'
      case 'medium': return 'text-yellow-600 bg-yellow-50'
      case 'low': return 'text-green-600 bg-green-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Extracted Tasks</h2>
        {tasks.length > 0 && (
          <button
            onClick={scheduleSelected}
            disabled={selectedTasks.length === 0 || isScheduling}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Schedule Selected ({selectedTasks.length})
          </button>
        )}
      </div>

      {tasks.length === 0 ? (
        <div className="text-center py-12">
          <AlertCircle className="mx-auto mb-4 text-gray-400" size={48} />
          <p className="text-gray-500">No tasks yet. Record or upload audio to extract tasks.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task: any) => (
            <div
              key={task.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => toggleTask(task.id)}
            >
              <div className="flex items-start gap-3">
                <div className="mt-1">
                  {selectedTasks.includes(task.id) ? (
                    <CheckCircle2 className="text-primary" size={24} />
                  ) : (
                    <Circle className="text-gray-300" size={24} />
                  )}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{task.action}</h3>
                    <span className={`px-2 py-1 text-xs rounded-full font-medium ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{task.context}</p>
                  
                  <div className="flex flex-wrap gap-3 text-sm">
                    {task.due && (
                      <div className="flex items-center gap-1 text-gray-700">
                        <Calendar size={16} />
                        <span>{new Date(task.due).toLocaleString()}</span>
                      </div>
                    )}
                    {task.date_hint && !task.due && (
                      <div className="flex items-center gap-1 text-gray-500">
                        <Calendar size={16} />
                        <span>{task.date_hint}</span>
                      </div>
                    )}
                    {task.owner && (
                      <div className="flex items-center gap-1 text-gray-700">
                        <User size={16} />
                        <span>{task.owner}</span>
                      </div>
                    )}
                    <div className="text-gray-500">
                      Confidence: {(task.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  {task.source_section && (
                    <div className="mt-2 text-xs text-gray-500">
                      From: {task.source_section}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

