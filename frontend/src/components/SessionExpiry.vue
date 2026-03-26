<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import Message from 'primevue/message'

const { t } = useI18n()
const auth = useAuthStore()

const daysUntilExpiry = computed(() => {
  if (!auth.user?.session_expires) return null
  const expires = new Date(auth.user.session_expires)
  const now = new Date()
  return Math.ceil((expires.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
})

const showWarning = computed(() => {
  return daysUntilExpiry.value !== null && daysUntilExpiry.value <= 3 && daysUntilExpiry.value > 0
})
</script>

<template>
  <div v-if="showWarning" class="session-expiry">
    <Message severity="warn" :closable="false">
      {{ t('session.expiry_warning') }}
    </Message>
  </div>
</template>

<style scoped>
.session-expiry {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}
</style>
