interface CallInfoProps {
  roomName: string
  duration: string
  isRecording: boolean
}

export default function CallInfo({ roomName, duration, isRecording }: CallInfoProps) {
  return (
    <div className="fixed z-10 portrait:top-4 portrait:left-4 landscape:top-6 landscape:left-6 transition-all duration-300">
      <div className="flex items-center gap-2 sm:gap-4 py-1.5 sm:py-2 px-3 sm:px-4 bg-black/20 backdrop-blur-lg rounded-full border border-white/10 shadow-lg text-xs sm:text-sm text-white">
        {/* Room name */}
        <h1 className="font-semibold">Ornina Call</h1>

        {/* Duration */}
        <span className="text-gray-300">{duration}</span>

        {/* Recording indicator */}
        {isRecording && (
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="font-medium text-red-400">REC</span>
          </div>
        )}
      </div>
    </div>
  )
}
