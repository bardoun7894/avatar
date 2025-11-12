import { RefObject, useState, useEffect, useRef } from 'react'

interface ParticipantThumbnailProps {
  userName: string
  isMuted: boolean
  videoRef: RefObject<HTMLVideoElement>
}

// Custom hook for drag functionality
function useDraggable(initialPosition: { x: number; y: number }) {
  const [position, setPosition] = useState(initialPosition)
  const [isDragging, setIsDragging] = useState(false)
  const dragRef = useRef<{ startX: number; startY: number; initialX: number; initialY: number }>({
    startX: 0,
    startY: 0,
    initialX: 0,
    initialY: 0
  })

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    dragRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      initialX: position.x,
      initialY: position.y
    }
    e.preventDefault()
  }

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return

      const deltaX = e.clientX - dragRef.current.startX
      const deltaY = e.clientY - dragRef.current.startY

      setPosition({
        x: dragRef.current.initialX + deltaX,
        y: dragRef.current.initialY + deltaY
      })
    }

    const handleMouseUp = () => {
      setIsDragging(false)
    }

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging])

  return { position, isDragging, handleMouseDown }
}

export default function ParticipantThumbnail({ userName, isMuted, videoRef }: ParticipantThumbnailProps) {
  const [hasVideo, setHasVideo] = useState(false)
  
  // Initialize position based on screen orientation
  const getInitialPosition = () => {
    if (typeof window !== 'undefined') {
      const isPortrait = window.innerHeight > window.innerWidth
      return isPortrait 
        ? { x: window.innerWidth - 140, y: 20 }  // portrait: top-right
        : { x: window.innerWidth - 200, y: 30 } // landscape: top-right
    }
    return { x: 0, y: 0 }
  }
  
  const { position, isDragging, handleMouseDown } = useDraggable(getInitialPosition())

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
    <div 
      className={`fixed z-10 portrait:w-32 landscape:w-48 tall:w-36 rounded-xl overflow-hidden shadow-2xl border border-white/20 bg-black/20 backdrop-blur-md aspect-video transition-all duration-300 ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        transform: 'translate(0, 0)',
      }}
      onMouseDown={handleMouseDown}
    >
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
