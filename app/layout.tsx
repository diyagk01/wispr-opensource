import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Voice Transcription - Glass',
  description: 'AI-powered voice transcription with glass morphism design',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="font-light" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
        {children}
      </body>
    </html>
  )
} 