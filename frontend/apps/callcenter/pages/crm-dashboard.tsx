import Head from 'next/head'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/router'

interface Ticket {
  id: string
  customerName: string
  customerPhone: string
  subject: string
  status: 'open' | 'in_progress' | 'pending' | 'resolved'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  createdAt: Date
  assignedTo?: string
}

interface Customer {
  id: string
  name: string
  phone: string
  totalCalls: number
  totalTickets: number
  lastInteraction?: Date
}

interface CRMStats {
  totalCustomers: number
  openTickets: number
  resolvedTickets: number
  avgResolutionTime: number
}

export default function CRMDashboard() {
  const router = useRouter()
  const [selectedTab, setSelectedTab] = useState<'tickets' | 'customers'>('tickets')

  const [tickets] = useState<Ticket[]>([
    {
      id: 'TKT-20241101-001',
      customerName: 'أحمد محمد',
      customerPhone: '+966501234567',
      subject: 'مشكلة في التسليم',
      status: 'open',
      priority: 'high',
      createdAt: new Date(Date.now() - 3600000),
      assignedTo: 'علي محمود',
    },
    {
      id: 'TKT-20241101-002',
      customerName: 'فاطمة علي',
      customerPhone: '+966509876543',
      subject: 'استفسار عن السعر',
      status: 'in_progress',
      priority: 'medium',
      createdAt: new Date(Date.now() - 7200000),
      assignedTo: 'سارة أحمد',
    },
    {
      id: 'TKT-20241101-003',
      customerName: 'محمد حسن',
      customerPhone: '+966505555555',
      subject: 'تقديم شكوى رسمية',
      status: 'pending',
      priority: 'urgent',
      createdAt: new Date(Date.now() - 1800000),
    },
    {
      id: 'TKT-20241101-004',
      customerName: 'خديجة سالم',
      customerPhone: '+966504444444',
      subject: 'طلب تتبع الطلب',
      status: 'resolved',
      priority: 'low',
      createdAt: new Date(Date.now() - 14400000),
      assignedTo: 'محمود علي',
    },
  ])

  const [customers] = useState<Customer[]>([
    {
      id: 'CUST-001',
      name: 'أحمد محمد',
      phone: '+966501234567',
      totalCalls: 5,
      totalTickets: 2,
      lastInteraction: new Date(Date.now() - 3600000),
    },
    {
      id: 'CUST-002',
      name: 'فاطمة علي',
      phone: '+966509876543',
      totalCalls: 3,
      totalTickets: 1,
      lastInteraction: new Date(Date.now() - 7200000),
    },
    {
      id: 'CUST-003',
      name: 'محمد حسن',
      phone: '+966505555555',
      totalCalls: 8,
      totalTickets: 4,
      lastInteraction: new Date(Date.now() - 1800000),
    },
  ])

  const [stats] = useState<CRMStats>({
    totalCustomers: customers.length,
    openTickets: tickets.filter((t) => ['open', 'in_progress'].includes(t.status)).length,
    resolvedTickets: tickets.filter((t) => t.status === 'resolved').length,
    avgResolutionTime: 240,
  })

  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'bg-red-500/20 border-red-400/50 text-red-200'
      case 'in_progress':
        return 'bg-yellow-500/20 border-yellow-400/50 text-yellow-200'
      case 'pending':
        return 'bg-blue-500/20 border-blue-400/50 text-blue-200'
      case 'resolved':
        return 'bg-green-500/20 border-green-400/50 text-green-200'
      default:
        return 'bg-gray-500/20 border-gray-400/50 text-gray-200'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'text-red-400'
      case 'high':
        return 'text-orange-400'
      case 'medium':
        return 'text-yellow-400'
      default:
        return 'text-green-400'
    }
  }

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('ar-SA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <>
      <Head>
        <title>CRM Dashboard - Call Center</title>
        <meta name="description" content="CRM and ticket management dashboard" />
      </Head>

      <div className="min-h-screen bg-gray-900 p-6">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">CRM Dashboard</h1>
            <p className="text-gray-400">Manage customers and support tickets</p>
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
            { label: 'Total Customers', value: stats.totalCustomers.toString(), icon: '👥' },
            { label: 'Open Tickets', value: stats.openTickets.toString(), icon: '📂' },
            { label: 'Resolved', value: stats.resolvedTickets.toString(), icon: '✓' },
            { label: 'Avg Resolution', value: `${stats.avgResolutionTime}m`, icon: '⏱️' },
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

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-white/10">
          {(['tickets', 'customers'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setSelectedTab(tab)}
              className={`pb-3 px-4 font-medium transition-all ${
                selectedTab === tab
                  ? 'text-white border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              {tab === 'tickets' ? 'Tickets' : 'Customers'}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main List */}
          <div className="lg:col-span-2">
            <div className="bg-black/20 rounded-2xl border border-white/20 backdrop-blur-lg overflow-hidden">
              <div className="max-h-96 overflow-y-auto">
                {selectedTab === 'tickets' ? (
                  <div className="divide-y divide-white/10">
                    {tickets.map((ticket) => (
                      <motion.div
                        key={ticket.id}
                        className="p-4 hover:bg-white/5 cursor-pointer transition-all"
                        whileHover={{ scale: 1.01 }}
                        onClick={() => setSelectedTicket(ticket)}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <p className="text-white font-medium mb-1">{ticket.subject}</p>
                            <p className="text-gray-400 text-sm">{ticket.customerName}</p>
                            <p className="text-gray-500 text-xs font-mono">{ticket.customerPhone}</p>
                          </div>
                          <div className="text-right">
                            <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status)} mb-2`}>
                              {ticket.status.toUpperCase()}
                            </span>
                            <div className={`text-xs font-bold ${getPriorityColor(ticket.priority)}`}>
                              {ticket.priority.toUpperCase()}
                            </div>
                          </div>
                        </div>
                        <p className="text-gray-500 text-xs">{ticket.id}</p>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="divide-y divide-white/10">
                    {customers.map((customer) => (
                      <motion.div
                        key={customer.id}
                        className="p-4 hover:bg-white/5 cursor-pointer transition-all"
                        whileHover={{ scale: 1.01 }}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="text-white font-medium mb-1">{customer.name}</p>
                            <p className="text-gray-400 text-sm font-mono">{customer.phone}</p>
                          </div>
                          <div className="text-right">
                            <div className="flex gap-4">
                              <div>
                                <p className="text-white font-bold text-lg">{customer.totalCalls}</p>
                                <p className="text-gray-400 text-xs">Calls</p>
                              </div>
                              <div>
                                <p className="text-white font-bold text-lg">{customer.totalTickets}</p>
                                <p className="text-gray-400 text-xs">Tickets</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Details Panel */}
          <div className="bg-black/20 rounded-2xl border border-white/20 backdrop-blur-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-white/10">
              <h2 className="text-lg font-semibold text-white">
                {selectedTab === 'tickets'
                  ? selectedTicket
                    ? 'Ticket Details'
                    : 'Select a Ticket'
                  : 'Customer Details'}
              </h2>
            </div>
            {selectedTicket && selectedTab === 'tickets' ? (
              <div className="p-6 space-y-4">
                <div>
                  <p className="text-gray-400 text-xs mb-1">TICKET ID</p>
                  <p className="text-white font-mono">{selectedTicket.id}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs mb-1">CUSTOMER</p>
                  <p className="text-white">{selectedTicket.customerName}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs mb-1">PHONE</p>
                  <p className="text-white font-mono">{selectedTicket.customerPhone}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs mb-1">SUBJECT</p>
                  <p className="text-white">{selectedTicket.subject}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-gray-400 text-xs mb-1">STATUS</p>
                    <span className={`inline-block px-3 py-1 rounded text-xs font-medium ${getStatusColor(selectedTicket.status)}`}>
                      {selectedTicket.status.toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="text-gray-400 text-xs mb-1">PRIORITY</p>
                    <p className={`text-sm font-bold ${getPriorityColor(selectedTicket.priority)}`}>
                      {selectedTicket.priority.toUpperCase()}
                    </p>
                  </div>
                </div>
                <div>
                  <p className="text-gray-400 text-xs mb-1">CREATED</p>
                  <p className="text-white text-sm">{formatDate(selectedTicket.createdAt)}</p>
                </div>
                {selectedTicket.assignedTo && (
                  <div>
                    <p className="text-gray-400 text-xs mb-1">ASSIGNED TO</p>
                    <p className="text-white">{selectedTicket.assignedTo}</p>
                  </div>
                )}
                <div className="pt-4 space-y-2">
                  <button className="w-full px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/50 text-blue-200 rounded-lg transition-all text-sm">
                    Edit Ticket
                  </button>
                  <button className="w-full px-4 py-2 bg-green-500/20 hover:bg-green-500/30 border border-green-400/50 text-green-200 rounded-lg transition-all text-sm">
                    Mark as Resolved
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-6 text-center text-gray-400 text-sm">
                <p>
                  {selectedTab === 'tickets'
                    ? 'Click on a ticket to view details'
                    : 'Select a customer to view details'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
