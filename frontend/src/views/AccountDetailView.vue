<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAccountsStore } from '../stores/accounts'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'
import StatsCard from '../components/StatsCard.vue'
import StatsChart from '../components/StatsChart.vue'
import QuotaBar from '../components/QuotaBar.vue'
import DnsStatusPanel from '../components/DnsStatusPanel.vue'
import PasswordReset from '../components/PasswordReset.vue'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const accountsStore = useAccountsStore()

const serverId = route.params.serverId as string
const smtpUserId = Number(route.params.smtpUserId)

const stats = ref<any>(null)
const dns = ref<any>(null)
const loading = ref(true)
const dnsLoading = ref(false)

onMounted(async () => {
  try {
    stats.value = await accountsStore.fetchStats(serverId, smtpUserId)
  } catch { /* handled in template */ }
  loading.value = false
})

async function loadDns() {
  dnsLoading.value = true
  try {
    dns.value = await accountsStore.fetchDns(serverId, smtpUserId)
  } catch { /* handled in template */ }
  dnsLoading.value = false
}

function downloadPdf() {
  accountsStore.downloadConfigPdf(serverId, smtpUserId)
}
</script>

<template>
  <div class="account-detail">
    <header class="detail-header">
      <div class="header-left">
        <Button icon="pi pi-arrow-left" text rounded @click="router.push({ name: 'dashboard' })" />
        <h1>{{ t('account.title') }}</h1>
      </div>
      <LanguageSwitcher />
    </header>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <template v-else-if="stats">
      <Tabs value="0">
        <TabList>
          <Tab value="0">{{ t('account.tab_stats') }}</Tab>
          <Tab value="1" @click="!dns && loadDns()">{{ t('account.tab_dns') }}</Tab>
          <Tab value="2">{{ t('account.tab_password') }}</Tab>
          <Tab value="3">{{ t('account.tab_config') }}</Tab>
        </TabList>
        <TabPanels>
          <TabPanel value="0">
            <div class="stats-cards">
              <StatsCard :label="t('account.stats_sent')" :value="stats.today.sent" icon="pi pi-send" color="#3b82f6" />
              <StatsCard :label="t('account.stats_deferred')" :value="stats.today.deferred" icon="pi pi-clock" color="#f59e0b" />
              <StatsCard :label="t('account.stats_bounced')" :value="stats.today.bounced" icon="pi pi-times-circle" color="#ef4444" />
              <StatsCard :label="t('account.stats_rejected')" :value="stats.today.rejected" icon="pi pi-ban" color="#6b7280" />
              <StatsCard :label="t('account.stats_success_rate')" :value="`${stats.today.success_rate}%`" icon="pi pi-check-circle" color="#10b981" />
            </div>
            <StatsChart :history24h="stats.history_24h" :history30d="stats.history_30d" />
            <QuotaBar :quota="stats.quota" />
          </TabPanel>
          <TabPanel value="1">
            <DnsStatusPanel :dns="dns" :loading="dnsLoading" @recheck="loadDns" />
          </TabPanel>
          <TabPanel value="2">
            <PasswordReset :server-id="serverId" :smtp-user-id="smtpUserId" :username="stats.username" />
          </TabPanel>
          <TabPanel value="3">
            <div class="config-section">
              <h3>{{ t('account.config_title') }}</h3>
              <table class="config-table">
                <tr>
                  <td>{{ t('account.config_server') }}</td>
                  <td>{{ serverId }}</td>
                </tr>
                <tr>
                  <td>{{ t('account.config_port') }}</td>
                  <td>587</td>
                </tr>
                <tr>
                  <td>{{ t('account.config_encryption') }}</td>
                  <td>{{ t('account.config_starttls') }}</td>
                </tr>
              </table>
              <Button :label="t('account.config_download_pdf')" icon="pi pi-download" @click="downloadPdf" class="mt-3" />
            </div>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </template>
  </div>
</template>

<style scoped>
.account-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.5rem;
}
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.config-section { padding: 1rem 0; }
.config-table { width: 100%; border-collapse: collapse; }
.config-table td { padding: 0.5rem; border-bottom: 1px solid #eee; }
.config-table td:first-child { font-weight: 600; width: 40%; }
.mt-3 { margin-top: 0.75rem; }
.loading { text-align: center; padding: 3rem; color: #666; }
</style>
