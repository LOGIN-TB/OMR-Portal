<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'

const { t } = useI18n()
const toast = useToast()

defineProps<{
  dns: any
  loading: boolean
}>()

const emit = defineEmits<{ recheck: [] }>()

function severityFor(status: string) {
  if (status === 'ok') return 'success'
  if (status === 'warning') return 'warn'
  return 'danger'
}

function copyText(text: string) {
  navigator.clipboard.writeText(text)
  toast.add({ severity: 'info', summary: t('common.copied'), life: 2000 })
}
</script>

<template>
  <div class="dns-panel">
    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <template v-else-if="dns">
      <div v-for="type in ['spf', 'dkim', 'dmarc']" :key="type" class="dns-row">
        <div class="dns-label">
          <Tag :severity="severityFor(dns[type].status)" :value="t(`account.dns_${type}`)" />
          <span class="dns-status">{{ dns[type].status }}</span>
        </div>
        <div class="dns-record" v-if="dns[type].record || dns[type].record_found !== undefined">
          <code>{{ dns[type].record || (dns[type].record_found ? 'Found' : 'Not found') }}</code>
        </div>
        <div v-if="dns[type].suggestion" class="dns-suggestion">
          <strong>{{ t('account.dns_suggestion') }}:</strong> {{ dns[type].suggestion }}
          <Button :label="t('account.dns_copy')" icon="pi pi-copy" text size="small" @click="copyText(dns[type].suggestion)" />
        </div>
      </div>
      <Button :label="t('account.dns_recheck')" icon="pi pi-refresh" outlined class="mt-3" @click="emit('recheck')" />
    </template>
    <div v-else>
      <Button :label="t('account.dns_recheck')" icon="pi pi-refresh" @click="emit('recheck')" />
    </div>
  </div>
</template>

<style scoped>
.dns-panel { padding: 1rem 0; }
.dns-row { padding: 0.75rem 0; border-bottom: 1px solid #f0f0f0; }
.dns-label { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem; }
.dns-status { color: #666; font-size: 0.9rem; }
.dns-record code { background: #f5f5f5; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem; word-break: break-all; }
.dns-suggestion { margin-top: 0.5rem; font-size: 0.9rem; color: #e67e22; }
.mt-3 { margin-top: 0.75rem; }
.loading { padding: 2rem; text-align: center; color: #666; }
</style>
