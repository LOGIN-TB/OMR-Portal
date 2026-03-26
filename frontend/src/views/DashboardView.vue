<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAccountsStore } from '../stores/accounts'
import AccountCard from '../components/AccountCard.vue'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import Button from 'primevue/button'

const { t } = useI18n()
const router = useRouter()
const accountsStore = useAccountsStore()

onMounted(() => {
  accountsStore.fetchOverview()
})

watch(() => accountsStore.accounts, (accs) => {
  if (accs.length === 1) {
    router.push({
      name: 'account-detail',
      params: { serverId: accs[0].server_id, smtpUserId: String(accs[0].smtp_user_id) },
    })
  }
})

function goToAccount(serverId: string, smtpUserId: number) {
  router.push({ name: 'account-detail', params: { serverId, smtpUserId: String(smtpUserId) } })
}
</script>

<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>{{ t('dashboard.title') }}</h1>
      <div class="header-actions">
        <LanguageSwitcher />
        <Button
          icon="pi pi-cog"
          text
          rounded
          @click="router.push({ name: 'preferences' })"
        />
      </div>
    </header>
    <div v-if="accountsStore.loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="accountsStore.accounts.length === 0" class="empty">
      {{ t('dashboard.no_accounts') }}
    </div>
    <div v-else class="accounts-grid">
      <AccountCard
        v-for="acc in accountsStore.accounts"
        :key="`${acc.server_id}-${acc.smtp_user_id}`"
        :account="acc"
        @click="goToAccount(acc.server_id, acc.smtp_user_id)"
      />
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.accounts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1rem;
}
.loading, .empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}
</style>
