<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import SelectButton from 'primevue/selectbutton'
import ToggleSwitch from 'primevue/toggleswitch'
import Button from 'primevue/button'

const { t, locale } = useI18n()
const router = useRouter()
const auth = useAuthStore()

const WARNING_TYPES = ['quota_warning', 'quota_critical', 'dns_problem', 'rbl_listing', 'high_bounce']
const langOptions = [
  { label: 'Deutsch', value: 'de' },
  { label: 'English', value: 'en' },
]

const notifications = ref<Record<string, boolean>>({})
const selectedLang = ref(locale.value)

onMounted(async () => {
  const res = await fetch('/api/preferences/notifications', { credentials: 'include' })
  if (res.ok) {
    const data: Array<{ warning_type: string; enabled: boolean }> = await res.json()
    for (const pref of data) {
      notifications.value[pref.warning_type] = pref.enabled
    }
    for (const wt of WARNING_TYPES) {
      if (!(wt in notifications.value)) {
        notifications.value[wt] = true
      }
    }
  }
})

async function updateLanguage(lang: string) {
  selectedLang.value = lang
  locale.value = lang
  await fetch('/api/preferences/language', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ language: lang }),
  })
}

async function toggleNotification(warningType: string, enabled: boolean) {
  notifications.value[warningType] = enabled
  await fetch('/api/preferences/notifications', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ warning_type: warningType, enabled }),
  })
}

async function doLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="preferences">
    <header class="pref-header">
      <Button icon="pi pi-arrow-left" text rounded @click="router.push({ name: 'dashboard' })" />
      <h1>{{ t('preferences.title') }}</h1>
    </header>

    <section class="pref-section">
      <h2>{{ t('preferences.language') }}</h2>
      <SelectButton
        :modelValue="selectedLang"
        :options="langOptions"
        optionLabel="label"
        optionValue="value"
        @update:modelValue="updateLanguage"
      />
    </section>

    <section class="pref-section">
      <h2>{{ t('preferences.notifications_title') }}</h2>
      <div v-for="wt in WARNING_TYPES" :key="wt" class="notification-row">
        <span>{{ t(`preferences.notify_${wt}`) }}</span>
        <ToggleSwitch
          :modelValue="notifications[wt] ?? true"
          @update:modelValue="(v: boolean) => toggleNotification(wt, v)"
        />
      </div>
    </section>

    <section class="pref-section">
      <h2>{{ t('preferences.session_title') }}</h2>
      <p v-if="auth.user">{{ t('preferences.session_expires') }}: {{ new Date(auth.user.session_expires).toLocaleString() }}</p>
      <Button :label="t('preferences.logout')" severity="danger" @click="doLogout" />
    </section>
  </div>
</template>

<style scoped>
.preferences {
  max-width: 600px;
  margin: 0 auto;
  padding: 1.5rem;
}
.pref-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.pref-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.pref-section h2 {
  margin-top: 0;
  font-size: 1.1rem;
}
.notification-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}
.notification-row:last-child { border-bottom: none; }
</style>
