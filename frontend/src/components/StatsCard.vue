<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  icon: string
  color: string
}>()
</script>

<template>
  <div class="stats-card">
    <div class="card-icon" :style="{ color }">
      <i :class="icon"></i>
    </div>
    <div class="card-content">
      <div class="card-value">{{ value }}</div>
      <div class="card-label">{{ label }}</div>
    </div>
  </div>
</template>

<style scoped>
.stats-card {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  gap: 1rem;
}
.card-icon { font-size: 1.5rem; }
.card-value { font-size: 1.5rem; font-weight: 700; }
.card-label { color: #888; font-size: 0.85rem; }
</style>
