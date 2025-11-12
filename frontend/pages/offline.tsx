import Head from 'next/head'

export default function Offline() {
  return (
    <>
      <Head>
        <title>Offline - Ornina AI Avatar</title>
      </Head>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          {/* Glassmorphism card */}
          <div className="relative backdrop-blur-xl bg-white/5 rounded-3xl shadow-2xl border border-white/10 p-8 overflow-hidden">
            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none"></div>
            
            {/* Content */}
            <div className="relative">
              {/* Icon with glass effect */}
              <div className="mb-8 inline-block p-4 rounded-2xl bg-gradient-to-br from-red-500/20 to-orange-500/20 backdrop-blur-sm border border-white/20">
                <svg
                  className="w-16 h-16 text-red-400 drop-shadow-lg"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414"
                  />
                </svg>
              </div>
              
              <h1 className="text-4xl font-bold text-white mb-4 drop-shadow-md">
                أنت غير متصل بالإنترنت
              </h1>
              <p className="text-lg text-white/90 mb-4 drop-shadow">
                يبدو أنك فقدت الاتصال بالإنترنت. يرجى التحقق من اتصالك والمحاولة مرة أخرى.
              </p>
              <p className="text-base text-white/70 mb-8 drop-shadow">
                You are offline. Please check your internet connection and try again.
              </p>
              
              <button
                onClick={() => window.location.reload()}
                className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-8 py-3.5 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 backdrop-blur-sm"
              >
                إعادة المحاولة / Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
