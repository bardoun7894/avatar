import React, { useState, useRef, useEffect } from 'react';

// Custom SVG components with glass UI theme
const MicIcon = ({ width = 24, height = 24, className = "" }: { width?: number; height?: number; className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} fill="none" className={className} viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
  </svg>
);

const MicDisabledIcon = ({ width = 24, height = 24, className = "" }: { width?: number; height?: number; className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} fill="none" className={className} viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3.75L17.25 14.25" />
  </svg>
);

const CameraIcon = ({ width = 24, height = 24, className = "" }: { width?: number; height?: number; className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} fill="none" className={className} viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
  </svg>
);

const CameraDisabledIcon = ({ width = 24, height = 24, className = "" }: { width?: number; height?: number; className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} fill="none" className={className} viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 6.75L17.25 17.25" />
  </svg>
);

const ChatIcon = ({ width = 24, height = 24, className = "" }: { width?: number; height?: number; className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} fill="none" className={className} viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const GearIcon = ({ width = 24, height = 24, className = "" }: { width?: number; height?: number; className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} fill="none" className={className} viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75" />
  </svg>
);

const LeaveIcon = ({ width = 24, height = 24, className = "" }: { width?: number; height?: number; className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} fill="none" className={className} viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h7.5" />
  </svg>
);

interface ControlBarProps {
  isMuted: boolean
  isVideoOff: boolean
  isChatOpen: boolean
  onToggleMute: () => void
  onToggleVideo: () => void
  onToggleChat: () => void
  onEndCall: () => void
}

export default function ControlBar({
  isMuted,
  isVideoOff,
  isChatOpen,
  onToggleMute,
  onToggleVideo,
  onToggleChat,
  onEndCall,
}: ControlBarProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [isInitialized, setIsInitialized] = useState(false)
  const controlBarRef = useRef<HTMLDivElement>(null)

  // Initialize position to center bottom on mount
  useEffect(() => {
    if (controlBarRef.current && !isInitialized) {
      const rect = controlBarRef.current.getBoundingClientRect()
      const centerX = (window.innerWidth - rect.width) / 2
      const bottomY = window.innerHeight - rect.height - 32 // 32px from bottom (2rem)
      setPosition({ x: centerX, y: bottomY })
      setIsInitialized(true)
    }
  }, [isInitialized])

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (controlBarRef.current) {
        const rect = controlBarRef.current.getBoundingClientRect()
        setPosition(prev => {
          // Keep within bounds
          const maxX = window.innerWidth - rect.width
          const maxY = window.innerHeight - rect.height
          return {
            x: Math.min(Math.max(0, prev.x), maxX),
            y: Math.min(Math.max(0, prev.y), maxY)
          }
        })
      }
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const handleMouseDown = (e: React.MouseEvent) => {
    // Only allow dragging from the container background, not from buttons
    if (e.target === controlBarRef.current || (e.target as HTMLElement).classList.contains('drag-handle')) {
      if (controlBarRef.current) {
        const rect = controlBarRef.current.getBoundingClientRect()
        setDragOffset({
          x: e.clientX - rect.left,
          y: e.clientY - rect.top
        })
        setIsDragging(true)
        e.preventDefault()
      }
    }
  }

  const handleTouchStart = (e: React.TouchEvent) => {
    // Only allow dragging from the container background, not from buttons
    if (e.target === controlBarRef.current || (e.target as HTMLElement).classList.contains('drag-handle')) {
      if (controlBarRef.current && e.touches.length === 1) {
        const rect = controlBarRef.current.getBoundingClientRect()
        const touch = e.touches[0]
        setDragOffset({
          x: touch.clientX - rect.left,
          y: touch.clientY - rect.top
        })
        setIsDragging(true)
        e.preventDefault()
      }
    }
  }

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging && controlBarRef.current) {
        const rect = controlBarRef.current.getBoundingClientRect()
        const newX = e.clientX - dragOffset.x
        const newY = e.clientY - dragOffset.y

        // Keep within bounds
        const maxX = window.innerWidth - rect.width
        const maxY = window.innerHeight - rect.height

        setPosition({
          x: Math.min(Math.max(0, newX), maxX),
          y: Math.min(Math.max(0, newY), maxY)
        })
      }
    }

    const handleTouchMove = (e: TouchEvent) => {
      if (isDragging && controlBarRef.current && e.touches.length === 1) {
        const rect = controlBarRef.current.getBoundingClientRect()
        const touch = e.touches[0]
        const newX = touch.clientX - dragOffset.x
        const newY = touch.clientY - dragOffset.y

        // Keep within bounds
        const maxX = window.innerWidth - rect.width
        const maxY = window.innerHeight - rect.height

        setPosition({
          x: Math.min(Math.max(0, newX), maxX),
          y: Math.min(Math.max(0, newY), maxY)
        })
      }
    }

    const handleMouseUp = () => {
      setIsDragging(false)
    }

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.addEventListener('touchmove', handleTouchMove)
      document.addEventListener('touchend', handleMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.removeEventListener('touchmove', handleTouchMove)
      document.removeEventListener('touchend', handleMouseUp)
    }
  }, [isDragging, dragOffset])

  return (
    <div
      ref={controlBarRef}
      className="fixed flex flex-col items-center gap-1 bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 shadow-2xl z-20"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        userSelect: 'none'
      }}
      data-label-id="0"
      data-metatip="true"
    >
      {/* Drag Handle */}
      <div
        className={`drag-handle w-full py-1 flex items-center justify-center ${
          isDragging ? 'cursor-grabbing' : 'cursor-grab'
        }`}
        onMouseDown={handleMouseDown}
        onTouchStart={handleTouchStart}
        style={{ touchAction: 'none' }}
      >
        <div className="w-8 h-1 bg-white/30 rounded-full"></div>
      </div>

      {/* Control Buttons */}
      <div className="flex items-center justify-center gap-2 sm:gap-3 px-3 sm:px-4 pb-2 sm:pb-3">
      {/* Microphone button */}
      <button
        onClick={onToggleMute}
        aria-label={isMuted ? 'Unmute microphone' : 'Mute microphone'}
        className={`p-2 sm:p-3 rounded-full text-white transition-all duration-200 ${
          isMuted
            ? 'bg-red-500/80 hover:bg-red-500'
            : 'bg-white/10 hover:bg-white/25'
        }`}
      >
        {isMuted ? (
          <MicDisabledIcon width={20} height={20} className="sm:w-6 sm:h-6" />
        ) : (
          <MicIcon width={20} height={20} className="sm:w-6 sm:h-6" />
        )}
      </button>

      {/* Camera button */}
      <button
        onClick={onToggleVideo}
        aria-label={isVideoOff ? 'Turn on camera' : 'Turn off camera'}
        className={`p-2 sm:p-3 rounded-full text-white transition-all duration-200 ${
          isVideoOff
            ? 'bg-red-500/80 hover:bg-red-500'
            : 'bg-white/10 hover:bg-white/25'
        }`}
      >
        {isVideoOff ? (
          <CameraDisabledIcon width={20} height={20} className="sm:w-6 sm:h-6" />
        ) : (
          <CameraIcon width={20} height={20} className="sm:w-6 sm:h-6" />
        )}
      </button>

      {/* Chat button */}
      <button
        onClick={onToggleChat}
        aria-label="Toggle chat"
        className={`p-2 sm:p-3 rounded-full text-white transition-all duration-200 ${
          isChatOpen
            ? 'bg-primary/20 ring-1 ring-primary/80'
            : 'bg-white/10 hover:bg-white/25'
        }`}
      >
        <ChatIcon
          width={20}
          height={20}
          className={`${isChatOpen ? 'text-primary' : ''} sm:w-6 sm:h-6`}
        />
      </button>

      {/* Settings button */}
      <button
        aria-label="Settings"
        className="p-2 sm:p-3 bg-white/10 hover:bg-white/25 rounded-full text-white transition-all duration-200"
      >
        <GearIcon width={20} height={20} className="sm:w-6 sm:h-6" />
      </button>

      {/* Divider */}
      <div className="w-px h-6 sm:h-8 bg-white/20 mx-1 sm:mx-2"></div>

      {/* End call button */}
      <button
        onClick={onEndCall}
        aria-label="End call"
        className="p-2 sm:p-3 bg-red-500/80 hover:bg-red-500 rounded-full text-white transition-all duration-200"
      >
        <LeaveIcon width={20} height={20} className="sm:w-6 sm:h-6" />
      </button>
      </div>
    </div>
  )
}
