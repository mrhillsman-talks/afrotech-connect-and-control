'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import type { User } from '@/types'

export default function UserList() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getUsers()
      setUsers(data.users)
    } catch (err) {
      console.error('Failed to load users:', err)
      setError('Failed to load users. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const createRandomUser = async () => {
    try {
      setCreating(true)
      await api.callTool('create-random-user', {})
      await loadUsers() // Refresh list
    } catch (err) {
      console.error('Failed to create user:', err)
      setError('Failed to create random user. Please try again.')
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <p className="text-gray-600">Loading users...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
          <button
            onClick={loadUsers}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-900">
          Users ({users.length})
        </h2>
        <button
          onClick={createRandomUser}
          disabled={creating}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          {creating ? (
            <>
              <span className="inline-block animate-spin">⚙️</span>
              Creating...
            </>
          ) : (
            <>
              <span>➕</span>
              Add Random User
            </>
          )}
        </button>
      </div>

      {users.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-600 mb-4">No users yet</p>
          <button
            onClick={createRandomUser}
            disabled={creating}
            className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 transition-colors"
          >
            Create Your First User
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {users.map((user) => (
            <div
              key={user.id}
              className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow bg-white"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-gray-900">{user.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{user.email}</p>
                </div>
                <span className="text-gray-400 text-sm">#{user.id}</span>
              </div>
              <div className="mt-3 text-sm text-gray-600 space-y-1">
                <p className="flex items-start gap-2">
                  <span className="text-lg">📍</span>
                  <span className="flex-1">{user.address}</span>
                </p>
                <p className="flex items-center gap-2">
                  <span className="text-lg">📞</span>
                  <span>{user.phone}</span>
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 text-center">
        <button
          onClick={loadUsers}
          className="text-sm text-blue-600 hover:text-blue-700 underline"
        >
          Refresh List
        </button>
      </div>
    </div>
  )
}
