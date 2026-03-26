<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import type { AccountOverview } from '../stores/accounts'
import QuotaBar from './QuotaBar.vue'

const { t } = useI18n()
defineProps<{ account: AccountOverview }>()
</script>

<template>
  <div class="account-card" :class="{ 'server-error': account.server_error }">
    <div class="card-header">
      <div>
        <h3>{{ account.username }}</h3>
        <p class="server-name">{{ account.server_name }}</p>
      </div>
      <Tag v-if="account.server_error" severity="warn" :value="t('dashboard.server_unreachable')" />
      <Tag v-else-if="account.is_active" severity="success" value="Aktiv" />
      <Tag v-else severity="danger" value="Inaktiv" />
    </div>
    <p v-if="account.company" class="company">{{ account.company }}</p>
    <p v-if="account.mail_domain" class="domain">{{ account.mail_domain }}</p>
    <div v-if="!account.server_error" class="card-stats">
      <span>{{ t('account.stats_sent') }}: <strong>{{ account.today_sent }}</strong></span>
      <span>{{ t('account.stats_bounced') }}: <strong>{{ account.today_bounced }}</strong></span>
    </div>
    <QuotaBar v-if="!account.server_error" :quota="{ percentage: account.quota_percentage, package: account.quota_package, limit_day: account.quota_limit, used_today: account.quota_used }" compact />
  </div>
</template>

<style scoped>
.account-card {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: box-shadow 0.2s;
}
.account-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.account-card.server-error { opacity: 0.6; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; }
.card-header h3 { margin: 0; }
.server-name { color: #888; font-size: 0.85rem; margin: 0.25rem 0 0; }
.company, .domain { color: #666; font-size: 0.9rem; margin: 0.25rem 0; }
.card-stats { display: flex; gap: 1.5rem; margin: 0.75rem 0 0.5rem; font-size: 0.9rem; }
</style>
