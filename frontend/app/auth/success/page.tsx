'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function GoogleAuthSuccess() {
  const router = useRouter()

  useEffect(() => {
    try {
      const params = new URLSearchParams(window.location.search)
      const accessToken = params.get('access_token') || ''
      const refreshToken = params.get('refresh_token') || ''
      if (accessToken) {
        localStorage.setItem('google_access_token', accessToken)
      }
      if (refreshToken) {
        localStorage.setItem('google_refresh_token', refreshToken)
      }
    } catch {}
    // return to home after saving
    router.replace('/')
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-700">Google Calendar connected. Redirecting…</p>
    </div>
  )
}


