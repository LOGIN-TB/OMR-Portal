import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface AccountOverview {
  server_id: string
  server_name: string
  smtp_user_id: number
  username: string
  company: string | null
  mail_domain: string | null
  is_active: boolean
  today_sent: number
  today_bounced: number
  quota_percentage: number
  quota_package: string
  quota_limit: number
  quota_used: number
  server_error: boolean
}

export const useAccountsStore = defineStore('accounts', () => {
  const accounts = ref<AccountOverview[]>([])
  const loading = ref(false)

  async function fetchOverview() {
    loading.value = true
    try {
      const res = await fetch('/api/dashboard/overview', { credentials: 'include' })
      if (res.ok) {
        const data = await res.json()
        accounts.value = data.accounts
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchStats(serverId: string, smtpUserId: number) {
    const res = await fetch(`/api/accounts/${serverId}/${smtpUserId}/stats`, { credentials: 'include' })
    if (!res.ok) throw new Error('Failed to fetch stats')
    return res.json()
  }

  async function fetchDns(serverId: string, smtpUserId: number) {
    const res = await fetch(`/api/accounts/${serverId}/${smtpUserId}/dns`, { credentials: 'include' })
    if (!res.ok) throw new Error('Failed to fetch DNS')
    return res.json()
  }

  async function resetPassword(serverId: string, smtpUserId: number) {
    const res = await fetch(`/api/accounts/${serverId}/${smtpUserId}/reset-password`, {
      method: 'POST',
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to reset password')
    return res.json()
  }

  async function downloadConfigPdf(serverId: string, smtpUserId: number) {
    const res = await fetch(`/api/accounts/${serverId}/${smtpUserId}/config-pdf`, { credentials: 'include' })
    if (!res.ok) throw new Error('Failed to download PDF')
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'smtp-config.pdf'
    a.click()
    URL.revokeObjectURL(url)
  }

  return { accounts, loading, fetchOverview, fetchStats, fetchDns, resetPassword, downloadConfigPdf }
})
