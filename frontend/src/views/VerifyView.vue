<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import Button from 'primevue/button'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const error = ref(false)
const loading = ref(true)

onMounted(async () => {
  const token = route.query.token as string
  if (!token) {
    error.value = true
    loading.value = false
    return
  }
  try {
    const res = await fetch(`/api/auth/verify?token=${encodeURIComponent(token)}`, {
      credentials: 'include',
      redirect: 'manual',
    })
    if (res.ok || res.status === 0) {
      await auth.fetchMe()
      router.push({ name: 'dashboard' })
    } else {
      error.value = true
    }
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="verify-page">
    <div class="verify-card">
      <template v-if="loading">
        <p>{{ t('verify.verifying') }}</p>
      </template>
      <template v-else-if="error">
        <h2>{{ t('verify.error_title') }}</h2>
        <p>{{ t('verify.error_message') }}</p>
        <Button :label="t('verify.back_to_login')" @click="router.push({ name: 'login' })" />
      </template>
    </div>
  </div>
</template>

<style scoped>
.verify-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}
.verify-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 400px;
}
</style>
