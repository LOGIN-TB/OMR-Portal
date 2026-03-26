<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'

const { t } = useI18n()
const email = ref('')
const sent = ref(false)
const error = ref(false)
const loading = ref(false)

async function requestLink() {
  loading.value = true
  error.value = false
  try {
    const res = await fetch('/api/auth/request-magic-link', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value }),
    })
    if (res.ok) {
      sent.value = true
    } else {
      error.value = true
    }
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-header">
      <LanguageSwitcher />
    </div>
    <div class="login-card">
      <h1>{{ t('app.title') }}</h1>
      <template v-if="!sent">
        <h2>{{ t('login.title') }}</h2>
        <form @submit.prevent="requestLink">
          <label>{{ t('login.email_label') }}</label>
          <InputText
            v-model="email"
            type="email"
            :placeholder="t('login.email_placeholder')"
            class="w-full"
            required
          />
          <Button
            type="submit"
            :label="t('login.submit')"
            :loading="loading"
            class="w-full mt-3"
          />
        </form>
        <p v-if="error" class="error-msg">{{ t('login.error') }}</p>
      </template>
      <template v-else>
        <h2>{{ t('login.success_title') }}</h2>
        <p>{{ t('login.success_message') }}</p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}
.login-header {
  position: absolute;
  top: 1rem;
  right: 1rem;
}
.login-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  max-width: 400px;
  width: 100%;
}
.login-card h1 {
  text-align: center;
  margin-bottom: 0.5rem;
}
.login-card h2 {
  text-align: center;
  font-size: 1.2rem;
  color: #666;
}
.login-card form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.w-full { width: 100%; }
.mt-3 { margin-top: 0.75rem; }
.error-msg { color: #e74c3c; text-align: center; }
</style>
