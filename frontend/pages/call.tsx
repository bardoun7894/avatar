import Head from 'next/head'
import { useRouter } from 'next/router'
import { useEffect, useState, useRef } from 'react'
import VideoCallInterface from '@/components/VideoCallInterface'

export default function Call() {
  const router = useRouter()
  const { room, user } = router.query
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    // Wait for router to be ready
    if (router.isReady) {
      if (!room || !user) {
        router.push('/')
        return
      }
      setIsReady(true)
    }
  }, [router.isReady, room, user, router])

  if (!isReady) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white">جارٍ التحميل...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Ornina AI Call - {room}</title>
        <meta name="description" content="AI-powered video call" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      </Head>

      <VideoCallInterface
        roomName={room as string}
        userName={user as string}
      />
    </>
  )
}
