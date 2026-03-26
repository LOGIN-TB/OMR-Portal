<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '../../components/admin/AdminLayout.vue'

const { t } = useI18n()

const stats = ref<any>(null)
const health = ref<any[]>([])

onMounted(async () => {
  const [statsRes, healthRes] = await Promise.all([
    fetch('/api/admin/system/stats', { credentials: 'include' }),
    fetch('/api/admin/system/health', { credentials: 'include' }),
  ])
  if (statsRes.ok) stats.value = await statsRes.json()
  if (healthRes.ok) health.value = await healthRes.json()
})
</script>

<template>
  <AdminLayout>
    <h1>{{ t('admin.dashboard_title') }}</h1>

    <div v-if="stats" class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_users }}</div>
        <div class="stat-label">{{ t('admin.total_users') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_accounts }}</div>
        <div class="stat-label">{{ t('admin.total_accounts') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_servers }}</div>
        <div class="stat-label">{{ t('admin.servers_title') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.warnings_24h }}</div>
        <div class="stat-label">{{ t('admin.warnings_24h') }}</div>
      </div>
    </div>

    <h2>{{ t('admin.system_health') }}</h2>
    <div class="health-list">
      <div v-for="s in health" :key="s.server_id" class="health-item" :class="s.status === 'ok' ? 'ok' : 'error'">
        <i :class="s.status === 'ok' ? 'pi pi-check-circle' : 'pi pi-times-circle'"></i>
        <span>{{ s.name }}</span>
        <span class="health-status">{{ s.status }}</span>
        <span v-if="s.version" class="health-version">v{{ s.version }}</span>
      </div>
    </div>
  </AdminLayout>
</template>

<style scoped>
.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.stat-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); text-align: center; }
.stat-value { font-size: 2rem; font-weight: 700; color: #3b82f6; }
.stat-label { color: #666; font-size: 0.9rem; margin-top: 0.25rem; }
.health-list { display: flex; flex-direction: column; gap: 0.5rem; }
.health-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; background: white; border-radius: 6px; }
.health-item.ok i { color: #10b981; }
.health-item.error i { color: #ef4444; }
.health-status { margin-left: auto; font-weight: 600; }
.health-version { color: #888; font-size: 0.85rem; }
</style>
