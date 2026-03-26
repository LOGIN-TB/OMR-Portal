import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface RelayServer {
  id: string
  name: string
  admin_url: string
  api_key_masked: string
  is_active: boolean
  created_at: string | null
  updated_at: string | null
}

export const useAdminStore = defineStore('admin', () => {
  const servers = ref<RelayServer[]>([])
  const settings = ref<Record<string, string>>({})

  async function fetchServers() {
    const res = await fetch('/api/admin/servers', { credentials: 'include' })
    if (res.ok) servers.value = await res.json()
  }

  async function createServer(data: { id: string; name: string; admin_url: string; api_key: string }) {
    const res = await fetch('/api/admin/servers', {
      method: 'POST', credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to create server')
    await fetchServers()
  }

  async function updateServer(id: string, data: Record<string, any>) {
    const res = await fetch(`/api/admin/servers/${id}`, {
      method: 'PUT', credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to update server')
    await fetchServers()
  }

  async function deleteServer(id: string) {
    const res = await fetch(`/api/admin/servers/${id}`, { method: 'DELETE', credentials: 'include' })
    if (!res.ok) throw new Error('Failed to delete server')
    await fetchServers()
  }

  async function testServer(id: string) {
    const res = await fetch(`/api/admin/servers/${id}/test`, { method: 'POST', credentials: 'include' })
    return res.json()
  }

  async function fetchSettings() {
    const res = await fetch('/api/admin/settings', { credentials: 'include' })
    if (res.ok) settings.value = await res.json()
  }

  async function updateSettings(data: Record<string, string>) {
    const res = await fetch('/api/admin/settings', {
      method: 'PUT', credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ settings: data }),
    })
    if (!res.ok) throw new Error('Failed to update settings')
    await fetchSettings()
  }

  async function testSmtp() {
    const res = await fetch('/api/admin/settings/test-smtp', { method: 'POST', credentials: 'include' })
    return res.json()
  }

  return { servers, settings, fetchServers, createServer, updateServer, deleteServer, testServer, fetchSettings, updateSettings, testSmtp }
})
