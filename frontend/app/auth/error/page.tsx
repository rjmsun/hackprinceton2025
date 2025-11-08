'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function GoogleAuthError() {
  const router = useRouter()
  useEffect(() => {
    const timer = setTimeout(() => router.replace('/'), 1500)
    return () => clearTimeout(timer)
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-red-600">Google Calendar connection failed. Returning…</p>
    </div>
  )
}


