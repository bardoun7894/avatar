import Head from 'next/head'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { motion } from 'framer-motion'
import { KeyIcon, ArrowRightOnRectangleIcon, ArrowLeftOnRectangleIcon } from '@heroicons/react/24/outline'

export default function Home() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [password, setPassword] = useState('')
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  // Check if user is already logged in on component mount
  useEffect(() => {
    const savedPassword = localStorage.getItem('ornina_password')
    if (savedPassword === 'Tarek1234') {
      setIsLoggedIn(true)
    }
  }, [])

  const handleJoinCall = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()

    // If already logged in, skip password check
    if (!isLoggedIn) {
      // Check if password is correct
      const enteredPassword = password.trim()
      console.log('Password entered:', enteredPassword)

      if (enteredPassword === 'Tarek1234') {
        // Save password to localStorage
        localStorage.setItem('ornina_password', enteredPassword)
        setIsLoggedIn(true)
        console.log('Password saved to localStorage')
      } else {
        alert('Incorrect password. Please try again.')
        return
      }
    }

    setLoading(true)

    try {
      // Navigate to call page with default parameters
      await router.push({
        pathname: '/call',
        query: {
          room: `ornina-${Date.now()}`,
          user: 'Guest',
        },
      })
    } catch (error) {
      console.error('Error joining call:', error)
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('ornina_password')
    setIsLoggedIn(false)
    setPassword('')
    alert('You have been logged out')
    console.log('User logged out, password cleared from localStorage:', !!localStorage.getItem('ornina_password'))
  }

  return (
    <>
      <Head>
        <title>Ornina AI Avatar - Interactive Call Center</title>
        <meta name="description" content="Professional AI-powered call center with video avatars" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="relative flex min-h-screen flex-col items-center justify-center bg-gray-900 overflow-hidden">
        {/* Logout Button - Bottom Left */}
        {isLoggedIn && (
          <motion.button
            onClick={handleLogout}
            className="fixed bottom-4 left-4 z-20 p-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full shadow-lg transition-all duration-300"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title="Logout"
          >
            <ArrowLeftOnRectangleIcon className="h-5 w-5" />
          </motion.button>
        )}

        {/* Background gradient effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-purple-600/20 to-pink-600/20"></div>

        {/* Animated background blobs */}
        <motion.div 
          className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/30 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            repeatType: "reverse",
          }}
        ></motion.div>
        <motion.div 
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            repeatType: "reverse",
            delay: 1,
          }}
        ></motion.div>

        {/* Main content */}
        <motion.div 
          className="relative z-10 w-full max-w-md px-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {/* Logo/Brand */}
          <motion.div 
            className="mb-8 text-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <motion.h1 
              className="text-5xl font-bold text-white mb-2"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              Ornina
            </motion.h1>
            <motion.p 
              className="text-xl text-gray-300"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              AI Avatar System
            </motion.p>
            <motion.p 
              className="text-sm text-gray-400 mt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              شركة أورنينا للذكاء الاصطناعي
            </motion.p>
          </motion.div>

          {/* Login Form - Glass morphism effect */}
          {!isLoggedIn && (
            <motion.div 
              className="bg-white/5 backdrop-blur-md border-white/10 rounded-2xl p-8 shadow-2xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
              whileHover={{ 
                boxShadow: "0 25px 50px -12px rgba(255, 255, 255, 0.05)",
                backgroundColor: "rgba(255, 255, 255, 0.05)"
              }}
            >
              <motion.h2 
                className="text-2xl font-semibold text-white mb-6 text-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 1 }}
              >
                
              </motion.h2>

              <form onSubmit={handleJoinCall} className="space-y-4">
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <motion.input
                    type="password"
                    placeholder="Enter PIN"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full py-3 px-6 bg-white/5 backdrop-blur-md border-white/10 text-white placeholder-white/50 font-semibold rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-white/30"
                    whileFocus={{ 
                      backgroundColor: "rgba(255, 255, 255, 0.05)",
                      borderColor: "rgba(255, 255, 255, 0.2)"
                    }}
                  />
                </motion.div>
                
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <motion.button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3 px-6 bg-green-600/20 backdrop-blur-md border-green-600/30 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 hover:bg-green-600/30 hover:shadow-xl hover:shadow-green-600/10 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg relative overflow-hidden group"
                    whileHover={{ 
                      backgroundColor: "rgba(34, 197, 94, 0.3)",
                      boxShadow: "0 10px 25px -5px rgba(34, 197, 94, 0.3)"
                    }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {loading ? (
                      <span className="flex items-center justify-center">
                        <motion.div 
                          className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full mr-3"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        ></motion.div>
                        جارٍ الاتصال...
                      </span>
                    ) : (
                      <motion.span
                        initial={{ opacity: 0.8 }}
                        whileHover={{ opacity: 1 }}
                        transition={{ duration: 0.2 }}
                        className="flex items-center justify-center"
                      >
                        <ArrowRightOnRectangleIcon className="h-5 w-5 mr-2" />
                        ابدأ المحادثة / Start Call
                      </motion.span>
                    )}
                    <motion.div 
                      className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-green-600/20 to-transparent"
                      animate={{ translateX: loading ? "100%" : "-100%" }}
                      transition={{ 
                        duration: 1.5, 
                        repeat: loading ? Infinity : 0,
                        ease: "easeInOut"
                      }}
                    ></motion.div>
                  </motion.button>
                </motion.div>
              </form>
            </motion.div>
          )}

          {/* Logged In State */}
          {isLoggedIn && (
            <motion.div 
              className="bg-white/5 backdrop-blur-md border-white/10 rounded-2xl p-8 shadow-2xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
              whileHover={{ 
                boxShadow: "0 25px 50px -12px rgba(255, 255, 255, 0.05)",
                backgroundColor: "rgba(255, 255, 255, 0.05)"
              }}
            >
              <motion.div 
                className="text-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 1 }}
              >
                <div className="w-16 h-16 bg-green-500/30 rounded-full flex items-center justify-center mb-4 mx-auto">
                  <KeyIcon className="h-8 w-8 text-green-400" />
                </div>
                <h2 className="text-2xl font-semibold text-white mb-4">
                  Welcome Back!
                </h2>
                <p className="text-gray-300 mb-6">
                  You are logged in and can start a call
                </p>
                
                <motion.button
                  onClick={handleJoinCall}
                  disabled={loading}
                  className="w-full py-3 px-6 bg-green-500/30 backdrop-blur-md border-green-600/30 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 hover:bg-green-600/30 hover:shadow-xl hover:shadow-green-600/10 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg relative overflow-hidden group"
                  whileHover={{ 
                    backgroundColor: "rgba(34, 197, 94, 0.3)",
                    boxShadow: "0 10px 25px -5px rgba(34, 197, 94, 0.3)"
                  }}
                  whileTap={{ scale: 0.98 }}
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <motion.div 
                        className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full mr-3"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        ></motion.div>
                        جارٍ الاتصال...
                      </span>
                    ) : (
                      <motion.span
                        initial={{ opacity: 0.8 }}
                        whileHover={{ opacity: 1 }}
                        transition={{ duration: 0.2 }}
                        className="flex items-center justify-center"
                      >
                        <ArrowRightOnRectangleIcon className="h-5 w-5 mr-2" />
                        ابدأ المحادثة / Start Call
                      </motion.span>
                    )}
                    <motion.div 
                      className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-green-600/30 to-transparent"
                      animate={{ translateX: loading ? "100%" : "-100%" }}
                      transition={{ 
                        duration: 1.5, 
                        repeat: loading ? Infinity : 0,
                        ease: "easeInOut"
                      }}
                    ></motion.div>
                </motion.button>
              </motion.div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </>
  )
}
