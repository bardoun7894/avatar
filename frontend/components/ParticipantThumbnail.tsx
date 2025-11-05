import { RefObject, useState, useEffect } from 'react'

interface ParticipantThumbnailProps {
  userName: string
  isMuted: boolean
  videoRef: RefObject<HTMLVideoElement>
}

export default function ParticipantThumbnail({ userName, isMuted, videoRef }: ParticipantThumbnailProps) {
  const [hasVideo, setHasVideo] = useState(false)

  useEffect(() => {
    const checkVideoStream = () => {
      if (videoRef.current && videoRef.current.srcObject) {
        setHasVideo(true)
      }
    }

    // Check periodically for video stream
    const interval = setInterval(checkVideoStream, 500)
    return () => clearInterval(interval)
  }, [videoRef])

  return (
    <div className="absolute top-6 right-6 z-10 w-48 rounded-xl overflow-hidden shadow-2xl border border-white/20 bg-black/20 backdrop-blur-md aspect-video">
      {/* Video element */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="absolute inset-0 w-full h-full object-cover z-10"
      />

      {/* Placeholder when no video - only show if no video stream */}
      {!hasVideo && (
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/40 to-purple-600/40 flex items-center justify-center z-0">
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center mx-auto mb-2">
              <span className="text-3xl">👤</span>
            </div>
            <p className="text-xs text-white/80">{userName}</p>
          </div>
        </div>
      )}

      {/* User name overlay */}
      <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/60 to-transparent z-20">
        <p className="text-white text-sm font-semibold leading-tight line-clamp-1">
          {userName}
        </p>
      </div>

      {/* Mute indicator */}
      {isMuted && (
        <div className="absolute top-2 right-2 p-1 bg-black/40 backdrop-blur-sm rounded-full text-white z-20">
          <span className="material-symbols-outlined filled text-sm">mic_off</span>
        </div>
      )}
    </div>
  )
}
