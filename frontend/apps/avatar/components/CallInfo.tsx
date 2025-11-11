interface CallInfoProps {
  roomName: string
  duration: string
  isRecording: boolean
}

export default function CallInfo({ roomName, duration, isRecording }: CallInfoProps) {
  return (
    <div className="absolute top-6 left-6 z-10">
      <div className="flex items-center gap-4 py-2 px-4 bg-black/20 backdrop-blur-lg rounded-full border border-white/10 shadow-lg text-sm text-white">
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
