import Head from 'next/head'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/router'

interface ActiveCall {
  id: string
  customerName: string
  customerPhone: string
  department: 'reception' | 'sales' | 'complaints'
  duration: number
  status: 'in_queue' | 'in_progress' | 'transferred'
}

interface QueueCall {
  id: string
  customerPhone: string
  serviceType: string
  waitTime: number
  priority: 'normal' | 'high' | 'urgent'
}

interface AgentStats {
  totalCalls: number
  avgDuration: number
  avgWaitTime: number
  ticketsCreated: number
}

export default function AgentDashboard() {
  const router = useRouter()
  const [activeCalls, setActiveCalls] = useState<ActiveCall[]>([
    {
      id: 'CALL-001',
      customerName: 'أحمد محمد',
      customerPhone: '+966501234567',
      department: 'complaints',
      duration: 45,
      status: 'in_progress',
    },
    {
      id: 'CALL-002',
      customerName: 'فاطمة علي',
      customerPhone: '+966509876543',
      department: 'sales',
      duration: 23,
      status: 'in_progress',
    },
  ])

  const [queueCalls, setQueueCalls] = useState<QueueCall[]>([
    {
      id: 'QUEUE-001',
      customerPhone: '+966505555555',
      serviceType: 'Billing Question',
      waitTime: 120,
      priority: 'normal',
    },
    {
      id: 'QUEUE-002',
      customerPhone: '+966504444444',
      serviceType: 'Complaint',
      waitTime: 300,
      priority: 'high',
    },
  ])

  const [stats] = useState<AgentStats>({
    totalCalls: 24,
    avgDuration: 320,
    avgWaitTime: 85,
    ticketsCreated: 8,
  })

  const [selectedCall, setSelectedCall] = useState<ActiveCall | null>(null)

  // Update call durations
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveCalls((prev) =>
        prev.map((call) => ({
          ...call,
          duration: call.duration + 1,
        }))
      )
      setQueueCalls((prev) =>
        prev.map((call) => ({
          ...call,
          waitTime: call.waitTime + 1,
        }))
      )
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getDepartmentColor = (dept: string) => {
    switch (dept) {
      case 'reception':
        return 'from-blue-600 to-blue-400'
      case 'sales':
        return 'from-green-600 to-green-400'
      case 'complaints':
        return 'from-red-600 to-red-400'
      default:
        return 'from-gray-600 to-gray-400'
    }
  }

  const getPriorityBadgeColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-500/20 border-red-400/50 text-red-200'
      case 'high':
        return 'bg-yellow-500/20 border-yellow-400/50 text-yellow-200'
      default:
        return 'bg-blue-500/20 border-blue-400/50 text-blue-200'
    }
  }

  return (
    <>
      <Head>
        <title>Agent Dashboard - Call Center</title>
        <meta name="description" content="Agent dashboard for call monitoring" />
      </Head>

      <div className="min-h-screen bg-gray-900 p-6">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Agent Dashboard</h1>
            <p className="text-gray-400">Real-time call monitoring and management</p>
          </div>
          <button
            onClick={() => router.push('/callcenter')}
            className="px-6 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-white transition-all"
          >
            ← Back
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Calls', value: stats.totalCalls.toString(), icon: '📞' },
            { label: 'Avg Duration', value: formatTime(stats.avgDuration), icon: '⏱️' },
            { label: 'Avg Wait Time', value: formatTime(stats.avgWaitTime), icon: '⏳' },
            { label: 'Tickets Created', value: stats.ticketsCreated.toString(), icon: '📋' },
          ].map((stat, idx) => (
            <motion.div
              key={idx}
              className="px-6 py-4 bg-black/20 rounded-xl border border-white/20 backdrop-blur-lg"
              whileHover={{ scale: 1.02 }}
            >
              <div className="text-2xl mb-2">{stat.icon}</div>
              <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
              <p className="text-2xl font-bold text-white">{stat.value}</p>
            </motion.div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Active Calls */}
          <div className="lg:col-span-2">
            <div className="bg-black/20 rounded-2xl border border-white/20 backdrop-blur-lg overflow-hidden">
              <div className="px-6 py-4 border-b border-white/10">
                <h2 className="text-lg font-semibold text-white">
                  Active Calls ({activeCalls.length})
                </h2>
              </div>
              <div className="p-4 max-h-96 overflow-y-auto space-y-3">
                {activeCalls.map((call) => (
                  <motion.div
                    key={call.id}
                    className="p-4 bg-white/5 border border-white/10 rounded-lg hover:border-white/20 cursor-pointer transition-all"
                    whileHover={{ scale: 1.01 }}
                    onClick={() => setSelectedCall(call)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <div className={`px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${getDepartmentColor(call.department)}`}>
                            {call.department.toUpperCase()}
                          </div>
                          <span className="text-white/60 text-xs">{call.id}</span>
                        </div>
                        <p className="text-white font-medium mb-1">{call.customerName}</p>
                        <p className="text-gray-400 text-sm font-mono">{call.customerPhone}</p>
                      </div>
                      <div className="text-right">
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse mb-2"></div>
                        <p className="text-white font-mono text-lg">{formatTime(call.duration)}</p>
                        <p className="text-gray-400 text-xs">In Progress</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Selected Call Details */}
          <div className="bg-black/20 rounded-2xl border border-white/20 backdrop-blur-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-white/10">
              <h2 className="text-lg font-semibold text-white">
                {selectedCall ? 'Call Details' : 'Select a Call'}
              </h2>
            </div>
            {selectedCall ? (
              <div className="p-6 space-y-4">
                <div>
                  <p className="text-gray-400 text-xs mb-1">CUSTOMER NAME</p>
                  <p className="text-white font-medium">{selectedCall.customerName}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs mb-1">PHONE NUMBER</p>
                  <p className="text-white font-mono">{selectedCall.customerPhone}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs mb-1">DEPARTMENT</p>
                  <p className="text-white capitalize">{selectedCall.department}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs mb-1">DURATION</p>
                  <p className="text-white font-mono text-lg">{formatTime(selectedCall.duration)}</p>
                </div>
                <div className="pt-4 space-y-2">
                  <button className="w-full px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/50 text-blue-200 rounded-lg transition-all">
                    Hold
                  </button>
                  <button className="w-full px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-400/50 text-purple-200 rounded-lg transition-all">
                    Transfer
                  </button>
                  <button className="w-full px-4 py-2 bg-red-500/20 hover:bg-red-500/30 border border-red-400/50 text-red-200 rounded-lg transition-all">
                    End Call
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-6 text-center text-gray-400">
                <p>Click on a call to view details and manage it</p>
              </div>
            )}
          </div>
        </div>

        {/* Queue Section */}
        <div className="mt-6 bg-black/20 rounded-2xl border border-white/20 backdrop-blur-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-white/10">
            <h2 className="text-lg font-semibold text-white">
              Call Queue ({queueCalls.length})
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-white/5 border-b border-white/10">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400">PHONE</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400">SERVICE TYPE</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400">WAIT TIME</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400">PRIORITY</th>
                </tr>
              </thead>
              <tbody>
                {queueCalls.map((call) => (
                  <tr key={call.id} className="border-b border-white/5 hover:bg-white/5">
                    <td className="px-6 py-4 text-sm text-white">{call.id}</td>
                    <td className="px-6 py-4 text-sm text-gray-300 font-mono">{call.customerPhone}</td>
                    <td className="px-6 py-4 text-sm text-gray-300">{call.serviceType}</td>
                    <td className="px-6 py-4 text-sm text-gray-300">{formatTime(call.waitTime)}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityBadgeColor(call.priority)}`}>
                        {call.priority.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  )
}
