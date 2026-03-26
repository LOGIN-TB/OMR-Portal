<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { useAccountsStore } from '../stores/accounts'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'

const { t } = useI18n()
const confirm = useConfirm()
const toast = useToast()
const accountsStore = useAccountsStore()

const props = defineProps<{
  serverId: string
  smtpUserId: number
  username: string
}>()

const newPassword = ref('')
const loading = ref(false)

function doReset() {
  confirm.require({
    header: t('account.password_confirm_title'),
    message: t('account.password_confirm_message'),
    acceptLabel: t('common.confirm'),
    rejectLabel: t('common.cancel'),
    accept: async () => {
      loading.value = true
      try {
        const result = await accountsStore.resetPassword(props.serverId, props.smtpUserId)
        newPassword.value = result.new_password
      } catch {
        toast.add({ severity: 'error', summary: t('common.error'), life: 3000 })
      } finally {
        loading.value = false
      }
    },
  })
}

function copyPassword() {
  navigator.clipboard.writeText(newPassword.value)
  toast.add({ severity: 'info', summary: t('account.password_copied'), life: 2000 })
}
</script>

<template>
  <div class="password-reset">
    <div class="field">
      <label>{{ t('account.password_username') }}</label>
      <InputText :modelValue="username" readonly class="w-full" />
    </div>
    <Button
      :label="t('account.password_reset')"
      icon="pi pi-refresh"
      :loading="loading"
      @click="doReset"
      severity="warn"
    />
    <div v-if="newPassword" class="new-password">
      <label>{{ t('account.password_new') }}</label>
      <div class="password-display">
        <InputText :modelValue="newPassword" readonly class="w-full" />
        <Button icon="pi pi-copy" @click="copyPassword" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.password-reset { padding: 1rem 0; }
.field { margin-bottom: 1rem; }
.field label { display: block; margin-bottom: 0.25rem; font-weight: 600; }
.w-full { width: 100%; }
.new-password { margin-top: 1.5rem; padding: 1rem; background: #f0fdf4; border-radius: 8px; }
.new-password label { display: block; margin-bottom: 0.25rem; font-weight: 600; }
.password-display { display: flex; gap: 0.5rem; }
</style>
