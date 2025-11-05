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
  return (
    <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20">
      <div className="flex items-center justify-center gap-3 px-4 py-3 bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 shadow-2xl">
        {/* Microphone button */}
        <button
          onClick={onToggleMute}
          aria-label={isMuted ? 'Unmute microphone' : 'Mute microphone'}
          className={`p-3 rounded-full text-white transition-all duration-200 ${
            isMuted
              ? 'bg-red-500/80 hover:bg-red-500'
              : 'bg-white/10 hover:bg-white/25'
          }`}
        >
          <span className="material-symbols-outlined">
            {isMuted ? 'mic_off' : 'mic'}
          </span>
        </button>

        {/* Camera button */}
        <button
          onClick={onToggleVideo}
          aria-label={isVideoOff ? 'Turn on camera' : 'Turn off camera'}
          className={`p-3 rounded-full text-white transition-all duration-200 ${
            isVideoOff
              ? 'bg-red-500/80 hover:bg-red-500'
              : 'bg-white/10 hover:bg-white/25'
          }`}
        >
          <span className="material-symbols-outlined">
            {isVideoOff ? 'videocam_off' : 'videocam'}
          </span>
        </button>

        {/* Chat button */}
        <button
          onClick={onToggleChat}
          aria-label="Toggle chat"
          className={`p-3 rounded-full text-white transition-all duration-200 ${
            isChatOpen
              ? 'bg-primary/20 ring-1 ring-primary/80'
              : 'bg-white/10 hover:bg-white/25'
          }`}
        >
          <span className={`material-symbols-outlined ${isChatOpen ? 'text-primary' : ''}`}>
            chat_bubble
          </span>
        </button>

        {/* Settings button */}
        <button
          aria-label="Settings"
          className="p-3 bg-white/10 hover:bg-white/25 rounded-full text-white transition-all duration-200"
        >
          <span className="material-symbols-outlined">settings</span>
        </button>

        {/* Divider */}
        <div className="w-px h-8 bg-white/20 mx-2"></div>

        {/* End call button */}
        <button
          onClick={onEndCall}
          aria-label="End call"
          className="p-3 bg-red-500/80 hover:bg-red-500 rounded-full text-white transition-all duration-200"
        >
          <span className="material-symbols-outlined">call_end</span>
        </button>
      </div>
    </div>
  )
}
