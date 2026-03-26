<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAdminAuthStore } from '../../stores/adminAuth'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'

const { t } = useI18n()
const router = useRouter()
const adminAuth = useAdminAuthStore()

const username = ref('')
const password = ref('')
const error = ref(false)
const loading = ref(false)

async function doLogin() {
  loading.value = true
  error.value = false
  const ok = await adminAuth.login(username.value, password.value)
  loading.value = false
  if (ok) {
    router.push({ name: 'admin-dashboard' })
  } else {
    error.value = true
  }
}
</script>

<template>
  <div class="admin-login-page">
    <div class="admin-login-card">
      <h1>{{ t('admin.login_title') }}</h1>
      <form @submit.prevent="doLogin">
        <label>{{ t('admin.username') }}</label>
        <InputText v-model="username" class="w-full" required />
        <label>{{ t('admin.password') }}</label>
        <Password v-model="password" :feedback="false" toggleMask class="w-full" inputClass="w-full" required />
        <Button type="submit" :label="t('login.submit')" :loading="loading" class="w-full mt-3" />
      </form>
      <p v-if="error" class="error-msg">{{ t('admin.login_error') }}</p>
    </div>
  </div>
</template>

<style scoped>
.admin-login-page {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; background: #1e293b;
}
.admin-login-card {
  background: white; padding: 2rem; border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3); max-width: 380px; width: 100%;
}
.admin-login-card h1 { text-align: center; margin-bottom: 1.5rem; }
.admin-login-card form { display: flex; flex-direction: column; gap: 0.5rem; }
.admin-login-card label { font-weight: 600; font-size: 0.9rem; }
.w-full { width: 100%; }
.mt-3 { margin-top: 0.75rem; }
.error-msg { color: #e74c3c; text-align: center; margin-top: 0.5rem; }
</style>
