'use client'

import { useEffect, useState } from 'react'
import { CheckCircle2, Circle, Calendar, User, AlertCircle } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function TasksPanel({ tasks, onTasksUpdate }: any) {
  const [selectedTasks, setSelectedTasks] = useState<string[]>([])
  const [isScheduling, setIsScheduling] = useState(false)
  const [calendarToken, setCalendarToken] = useState<string | null>(null)

  useEffect(() => {
    try {
      const token = localStorage.getItem('google_access_token');
      setCalendarToken(token);
      // If we have a refresh token, we could implement token refresh here
    } catch (error) {
      console.error('Error accessing localStorage:', error);
    }
  }, [])

  const toggleTask = (taskId: string) => {
    setSelectedTasks(prev => 
      prev.includes(taskId) 
        ? prev.filter(id => id !== taskId)
        : [...prev, taskId]
    )
  }

  const connectCalendar = async () => {
    try {
      const resp = await axios.get(`${API_URL}/calendar/auth`)
      const url = resp.data?.auth_url
      if (url) window.location.href = url
    } catch (e) {
      alert('Failed to initiate Google OAuth. Check backend logs.')
    }
  }

  const scheduleSelected = async () => {
    if (selectedTasks.length === 0) {
      alert('Please select at least one task to schedule')
      return
    }

    if (!calendarToken) {
      const ok = confirm('Connect Google Calendar to create events?')
      if (ok) connectCalendar()
      return
    }

    try {
      setIsScheduling(true)
      const tasksToSchedule = tasks.filter((t: any) => selectedTasks.includes(t.id))
      await axios.post(`${API_URL}/calendar/schedule`, tasksToSchedule, {
        params: { access_token: calendarToken }
      })
      alert('Scheduled selected tasks!')
      setSelectedTasks([])
    } catch (e) {
      console.error(e)
      alert('Failed to schedule tasks. Check token and backend logs.')
    } finally {
      setIsScheduling(false)
    }
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

      {!calendarToken && (
        <div className="mb-4">
          <button onClick={connectCalendar} className="btn-secondary">Connect Google Calendar</button>
        </div>
      )}

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
                {task.due && calendarToken && (
                  <div className="mt-3">
                    <button
                      onClick={async (e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        try {
                          setIsScheduling(true)
                          await axios.post(`${API_URL}/calendar/schedule`, [task], {
                            params: { access_token: calendarToken }
                          })
                          alert('Event added to Google Calendar!')
                        } catch (err) {
                          console.error(err)
                          alert('Failed to add to Google Calendar.')
                        } finally {
                          setIsScheduling(false)
                        }
                      }}
                      className="px-3 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-md text-sm font-medium"
                    >
                      Add to Google Calendar
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

