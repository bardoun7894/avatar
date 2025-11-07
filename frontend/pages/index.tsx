import Head from 'next/head'
import { useState } from 'react'
import { useRouter } from 'next/router'

export default function Home() {
  const router = useRouter()
  const [roomName, setRoomName] = useState('')
  const [userName, setUserName] = useState('')
  const [loading, setLoading] = useState(false)

  const handleJoinCall = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Navigate to call page with parameters
      await router.push({
        pathname: '/call',
        query: {
          room: roomName || `ornina-${Date.now()}`,
          user: userName || 'Guest',
        },
      })
    } catch (error) {
      console.error('Error joining call:', error)
      setLoading(false)
    }
  }

  return (
    <>
      <Head>
        <title>Ornina AI Avatar - Interactive Call Center</title>
        <meta name="description" content="Professional AI-powered call center with video avatars" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="relative flex min-h-screen flex-col items-center justify-center bg-gray-900 overflow-hidden">
        {/* Background gradient effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-purple-600/20 to-pink-600/20"></div>

        {/* Animated background blobs */}
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>

        {/* Main content */}
        <div className="relative z-10 w-full max-w-md px-6">
          {/* Logo/Brand */}
          <div className="mb-8 text-center">
            <h1 className="text-5xl font-bold text-white mb-2">Ornina</h1>
            <p className="text-xl text-gray-300">AI Avatar System</p>
            <p className="text-sm text-gray-400 mt-2">شركة أورنينا للذكاء الاصطناعي</p>
          </div>

          {/* Join Call Form */}
          <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 shadow-2xl">
            <h2 className="text-2xl font-semibold text-white mb-6 text-center">
              انضم للمحادثة
            </h2>

            <form onSubmit={handleJoinCall} className="space-y-4">
              <div>
                <label htmlFor="userName" className="block text-sm font-medium text-gray-200 mb-2">
                  الاسم / Name
                </label>
                <input
                  type="text"
                  id="userName"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  placeholder="أدخل اسمك"
                  className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent transition-all"
                />
              </div>

              <div>
                <label htmlFor="roomName" className="block text-sm font-medium text-gray-200 mb-2">
                  رمز الغرفة / Room Code (Optional)
                </label>
                <input
                  type="text"
                  id="roomName"
                  value={roomName}
                  onChange={(e) => setRoomName(e.target.value)}
                  placeholder="اتركه فارغاً لغرفة جديدة"
                  className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent transition-all"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-6 bg-white/10 backdrop-blur-lg border border-white/20 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 hover:bg-white/20 hover:shadow-xl hover:shadow-white/10 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg relative overflow-hidden group animate-pulse"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    جارٍ الاتصال...
                  </span>
                ) : (
                  <>
                    'ابدأ المحادثة / Start Call'
                    <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent group-hover:translate-x-full transition-transform duration-1000"></span>
                  </>
                )}
              </button>
            </form>

            {/* Info */}
            <div className="mt-6 text-center text-sm text-gray-400">
              <p>اتصل بنا: 3349028</p>
              <p className="mt-1">دمشق - المزرعة - مقابل وزارة التربية</p>
            </div>
          </div>

        </div>
      </div>
    </>
  )
}
