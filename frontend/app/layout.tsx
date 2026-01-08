import type { Metadata } from 'next'
import './globals.css'
import { Toaster } from 'sonner'
import Navbar from '@/components/Navbar'
import { SpeedInsights } from "@vercel/speed-insights/next"

export const metadata: Metadata = {
  title: 'FlowTask - Premium Todo Platform',
  description: 'Secure, premium full-stack todo application with Premium Midnight theme',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Navbar />
        {children}
        <SpeedInsights />
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: 'rgba(15, 23, 42, 0.9)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#FFFFFF',
            },
            className: 'glass-toast',
          }}
        />
      </body>
    </html>
  )
}
