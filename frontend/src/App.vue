<script setup lang="ts">
import { RouterView } from 'vue-router'
import SessionExpiry from './components/SessionExpiry.vue'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
</script>

<template>
  <div>
    <Toast />
    <ConfirmDialog />
    <SessionExpiry />
    <RouterView />
  </div>
</template>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f8f9fa;
}
</style>
