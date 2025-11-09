'use client'

import './globals.css'
import { useEffect, useState, createContext, useContext } from 'react'

type ThemeContextType = {
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType>({
  theme: 'light',
  toggleTheme: () => { },
})

export function useTheme() {
  return useContext(ThemeContext)
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    // On mount, initialize from localStorage or system preference
    const saved = localStorage.getItem('theme') as 'light' | 'dark' | null
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

    const initialTheme = saved ?? (prefersDark ? 'dark' : 'light')
    setTheme(initialTheme)
    document.documentElement.classList.toggle('dark', initialTheme === 'dark')
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)

    // ✅ This is crucial: toggle the 'dark' class on <html>
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  return (
    <html lang="en">
      <head>
        <title>EVE - Everyday Virtual Executive</title>
        <meta name="description" content="AI Productivity Companion" />
        <link rel="icon" type="image/png" href="/icon.png" />
        <link rel="shortcut icon" href="/icon.png" />
      </head>
      <body className="bg-gray-50 dark:bg-gray-900 transition-colors duration-500">
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
          {children}
        </ThemeContext.Provider>
      </body>
    </html>
  )
}
