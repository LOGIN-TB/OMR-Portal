<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ProgressBar from 'primevue/progressbar'

const { t } = useI18n()

const props = defineProps<{
  quota: { percentage: number; package: string; limit_day: number; used_today: number }
  compact?: boolean
}>()

const barColor = computed(() => {
  if (props.quota.percentage > 90) return '#ef4444'
  if (props.quota.percentage > 75) return '#f59e0b'
  return '#10b981'
})

</script>

<template>
  <div class="quota-bar" :class="{ compact }">
    <div v-if="!compact" class="quota-header">
      <span>{{ t('account.quota_title') }}: {{ quota.package }}</span>
      <span>{{ quota.used_today }} / {{ quota.limit_day }}</span>
    </div>
    <ProgressBar :value="Math.min(quota.percentage, 100)" :showValue="!compact" :style="{ '--p-progressbar-value-background': barColor }">
      <template #default>{{ quota.percentage.toFixed(1) }}%</template>
    </ProgressBar>
  </div>
</template>

<style scoped>
.quota-bar { margin-top: 0.5rem; }
.quota-bar.compact :deep(.p-progressbar) { height: 6px; }
.quota-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}
</style>
