<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import SelectButton from 'primevue/selectbutton'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

const { t } = useI18n()

const props = defineProps<{
  history24h: Array<{ hour: string; sent: number; deferred: number; bounced: number; rejected: number }>
  history30d: Array<{ date: string; sent: number; deferred: number; bounced: number; rejected: number }>
}>()

const viewOptions = computed(() => [
  { label: t('account.stats_24h'), value: '24h' },
  { label: t('account.stats_30d'), value: '30d' },
])
const view = ref('24h')

const chartData = computed(() => {
  const is24h = view.value === '24h'
  const data = is24h ? props.history24h : props.history30d
  const labels = data.map(d => {
    if (is24h) {
      return new Date((d as any).hour).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    return new Date((d as any).date).toLocaleDateString([], { day: '2-digit', month: '2-digit' })
  })
  return {
    labels,
    datasets: [
      { label: t('account.stats_sent'), data: data.map(d => d.sent), borderColor: '#3b82f6', fill: false, tension: 0.3 },
      { label: t('account.stats_bounced'), data: data.map(d => d.bounced), borderColor: '#ef4444', fill: false, tension: 0.3 },
      { label: t('account.stats_deferred'), data: data.map(d => d.deferred), borderColor: '#f59e0b', fill: false, tension: 0.3 },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' as const } },
}
</script>

<template>
  <div class="stats-chart">
    <div class="chart-header">
      <SelectButton v-model="view" :options="viewOptions" optionLabel="label" optionValue="value" />
    </div>
    <div class="chart-container">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
.stats-chart {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.chart-header { margin-bottom: 1rem; }
.chart-container { height: 300px; }
</style>
