import { defineStore } from 'pinia'
import { ref } from 'vue'

interface AdminInfo {
  id: number
  username: string
}

export const useAdminAuthStore = defineStore('adminAuth', () => {
  const admin = ref<AdminInfo | null>(null)

  async function login(username: string, password: string): Promise<boolean> {
    const res = await fetch('/api/admin/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password }),
    })
    if (res.ok) {
      await fetchMe()
      return true
    }
    return false
  }

  async function fetchMe() {
    try {
      const res = await fetch('/api/admin/auth/me', { credentials: 'include' })
      if (res.ok) {
        admin.value = await res.json()
      } else {
        admin.value = null
      }
    } catch {
      admin.value = null
    }
  }

  async function logout() {
    await fetch('/api/admin/auth/logout', { method: 'POST', credentials: 'include' })
    admin.value = null
  }

  return { admin, login, fetchMe, logout }
})
