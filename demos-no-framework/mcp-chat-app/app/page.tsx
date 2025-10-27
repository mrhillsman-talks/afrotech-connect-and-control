'use client'

import { useState } from 'react'
import Chat from '@/components/Chat'
import UserList from '@/components/UserList'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'users'>('chat')

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Tabs Header */}
      <div className="border-b bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-3 border-b-2 transition-colors font-medium ${
                activeTab === 'chat'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              💬 Chat
            </button>
            <button
              onClick={() => setActiveTab('users')}
              className={`px-4 py-3 border-b-2 transition-colors font-medium ${
                activeTab === 'users'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              👥 Users
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto">
        {activeTab === 'chat' ? <Chat /> : <UserList />}
      </div>
    </main>
  )
}
