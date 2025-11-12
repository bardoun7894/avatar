import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import InstallAlertBanner from '@/components/InstallAlertBanner'
import { useEffect } from 'react'

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    // Register service worker update handler
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then((registration) => {
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New service worker available, prompt user to refresh
                if (confirm('تحديث جديد متاح! هل تريد إعادة تحميل الصفحة?\nNew update available! Reload to update?')) {
                  window.location.reload()
                }
              }
            })
          }
        })
      })
    }
  }, [])

  return (
    <>
      <Component {...pageProps} />
      <InstallAlertBanner />
    </>
  )
}
