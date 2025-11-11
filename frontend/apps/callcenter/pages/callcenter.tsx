import Head from 'next/head'
import { useState } from 'react'
import { useRouter } from 'next/router'
import { motion } from 'framer-motion'

export default function CallCenter() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  const handleStartCall = async () => {
    setLoading(true)
    const roomId = `callcenter-${Date.now()}`
    const userName = 'Customer'

    console.log('🎙️ Starting audio call...')
    console.log(`Room ID: ${roomId}`)
    console.log(`User: ${userName}`)

    try {
      await router.push({
        pathname: '/callcenter/call-with-audio',
        query: {
          room: roomId,
          user: userName,
        },
      })
      console.log('✅ Successfully routed to audio call page')
    } catch (error) {
      console.error('❌ Error starting call:', error)
      setLoading(false)
      alert('Failed to start call. Please try again.')
    }
  }

  const handleAgentDashboard = async () => {
    setLoading(true)
    console.log('👥 Opening agent dashboard...')
    try {
      await router.push('/callcenter/agent-dashboard')
      console.log('✅ Successfully opened agent dashboard')
    } catch (error) {
      console.error('❌ Error opening agent dashboard:', error)
      setLoading(false)
      alert('Failed to open agent dashboard. Please try again.')
    }
  }

  const handleCrmDashboard = async () => {
    setLoading(true)
    console.log('📊 Opening CRM dashboard...')
    try {
      await router.push('/callcenter/crm-dashboard')
      console.log('✅ Successfully opened CRM dashboard')
    } catch (error) {
      console.error('❌ Error opening CRM dashboard:', error)
      setLoading(false)
      alert('Failed to open CRM dashboard. Please try again.')
    }
  }

  return (
    <>
      <Head>
        <title>Call Center - AI Powered System</title>
        <meta name="description" content="Intelligent call center with IVR, CRM, and agent dashboard" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="relative flex min-h-screen flex-col items-center justify-center bg-gray-900 overflow-hidden">
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
          className="relative z-10 w-full max-w-2xl px-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {/* Header */}
          <motion.div
            className="mb-12 text-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Call Center System
            </h1>
            <p className="text-gray-300 text-lg">
              Intelligent IVR, Agent Dashboard & CRM Management
            </p>
          </motion.div>

          {/* Mode Selection Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Customer Call Card */}
            <motion.div
              className="relative group cursor-pointer"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
              onClick={handleStartCall}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-300"></div>
              <div className="relative px-6 py-8 bg-black/20 rounded-2xl border border-white/20 backdrop-blur-lg hover:border-white/40 transition-all">
                <div className="text-4xl mb-4">📞</div>
                <h3 className="text-xl font-semibold text-white mb-2">Start Call</h3>
                <p className="text-gray-300 text-sm">
                  Begin a new customer call with IVR system
                </p>
              </div>
            </motion.div>

            {/* Agent Dashboard Card */}
            <motion.div
              className="relative group cursor-pointer"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
              onClick={handleAgentDashboard}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-300"></div>
              <div className="relative px-6 py-8 bg-black/20 rounded-2xl border border-white/20 backdrop-blur-lg hover:border-white/40 transition-all">
                <div className="text-4xl mb-4">👥</div>
                <h3 className="text-xl font-semibold text-white mb-2">Agent Dashboard</h3>
                <p className="text-gray-300 text-sm">
                  Monitor calls and manage agent activities
                </p>
              </div>
            </motion.div>

            {/* CRM Dashboard Card */}
            <motion.div
              className="relative group cursor-pointer"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
              onClick={handleCrmDashboard}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-300"></div>
              <div className="relative px-6 py-8 bg-black/20 rounded-2xl border border-white/20 backdrop-blur-lg hover:border-white/40 transition-all">
                <div className="text-4xl mb-4">📊</div>
                <h3 className="text-xl font-semibold text-white mb-2">CRM Dashboard</h3>
                <p className="text-gray-300 text-sm">
                  Manage customers and support tickets
                </p>
              </div>
            </motion.div>
          </div>

          {/* Loading indicator */}
          {loading && (
            <motion.div
              className="flex justify-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="flex items-center gap-3 px-6 py-3 bg-white/10 rounded-full border border-white/20 backdrop-blur-lg">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                <span className="text-white text-sm">Loading...</span>
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </>
  )
}
