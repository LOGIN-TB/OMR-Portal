import { defineStore } from 'pinia'
import { ref } from 'vue'

interface UserInfo {
  id: string
  email: string
  language: string
  session_expires: string
  accounts_count: number
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)

  async function fetchMe() {
    try {
      const res = await fetch('/api/auth/me', { credentials: 'include' })
      if (res.ok) {
        user.value = await res.json()
      } else {
        user.value = null
      }
    } catch {
      user.value = null
    }
  }

  async function logout() {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
    user.value = null
  }

  return { user, fetchMe, logout }
})
