<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAdminStore } from '../../stores/admin'
import { useToast } from 'primevue/usetoast'
import AdminLayout from '../../components/admin/AdminLayout.vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'

const { t } = useI18n()
const adminStore = useAdminStore()
const toast = useToast()
const localSettings = ref<Record<string, string>>({})

const smtpKeys = ['smtp_sender', 'smtp_sender_name', 'smtp_server_id', 'smtp_username', 'smtp_password', 'smtp_port']
const thresholdKeys = ['warning_quota_threshold', 'warning_quota_critical_threshold', 'warning_bounce_rate_threshold', 'warning_throttle_hours']
const schedulerKeys = ['scheduler_quota_interval_hours', 'scheduler_dns_interval_hours', 'scheduler_bounce_check_hour']
const portalKeys = ['magic_link_lifetime_minutes', 'session_lifetime_days', 'portal_maintenance_mode', 'portal_maintenance_message_de', 'portal_maintenance_message_en']

onMounted(async () => {
  await adminStore.fetchSettings()
  localSettings.value = { ...adminStore.settings }
})

async function saveSettings() {
  try {
    await adminStore.updateSettings(localSettings.value)
    toast.add({ severity: 'success', summary: t('admin.save_success'), life: 2000 })
  } catch {
    toast.add({ severity: 'error', summary: t('common.error'), life: 3000 })
  }
}

async function doTestSmtp() {
  const result = await adminStore.testSmtp()
  if (result.status === 'ok') {
    toast.add({ severity: 'success', summary: t('admin.settings_test_smtp_ok'), life: 3000 })
  } else {
    toast.add({ severity: 'error', summary: t('admin.settings_test_smtp_fail'), detail: result.error, life: 5000 })
  }
}
</script>

<template>
  <AdminLayout>
    <h1>{{ t('admin.settings_title') }}</h1>

    <div class="settings-section">
      <h2>{{ t('admin.settings_smtp') }}</h2>
      <div class="settings-grid">
        <template v-for="key in smtpKeys" :key="key">
          <label>{{ key }}</label>
          <InputText v-model="localSettings[key]" class="w-full" :type="key.includes('password') ? 'password' : 'text'" />
        </template>
      </div>
      <div class="button-row">
        <Button :label="t('admin.settings_test_smtp')" icon="pi pi-envelope" outlined @click="doTestSmtp" />
      </div>
    </div>

    <div class="settings-section">
      <h2>{{ t('admin.settings_thresholds') }}</h2>
      <div class="settings-grid">
        <template v-for="key in thresholdKeys" :key="key">
          <label>{{ key }}</label>
          <InputText v-model="localSettings[key]" class="w-full" />
        </template>
      </div>
    </div>

    <div class="settings-section">
      <h2>{{ t('admin.settings_scheduler') }}</h2>
      <div class="settings-grid">
        <template v-for="key in schedulerKeys" :key="key">
          <label>{{ key }}</label>
          <InputText v-model="localSettings[key]" class="w-full" />
        </template>
      </div>
    </div>

    <div class="settings-section">
      <h2>{{ t('admin.settings_portal') }}</h2>
      <div class="settings-grid">
        <template v-for="key in portalKeys" :key="key">
          <label>{{ key }}</label>
          <InputText v-model="localSettings[key]" class="w-full" />
        </template>
      </div>
    </div>

    <div class="save-bar">
      <Button :label="t('common.save')" icon="pi pi-check" @click="saveSettings" />
    </div>
  </AdminLayout>
</template>

<style scoped>
.settings-section { background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.settings-section h2 { margin-top: 0; font-size: 1.1rem; }
.settings-grid { display: grid; grid-template-columns: 250px 1fr; gap: 0.5rem; align-items: center; }
.settings-grid label { font-size: 0.85rem; color: #555; }
.w-full { width: 100%; }
.button-row { margin-top: 1rem; }
.save-bar { margin-top: 1rem; }
</style>
