<script setup lang="ts">
import { RouterView } from 'vue-router'
import SessionExpiry from './components/SessionExpiry.vue'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
</script>

<template>
  <Toast />
  <ConfirmDialog />
  <SessionExpiry />
  <RouterView />
</template>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f8f9fa;
}
</style>
