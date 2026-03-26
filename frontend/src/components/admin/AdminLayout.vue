<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAdminAuthStore } from '../../stores/adminAuth'
import Button from 'primevue/button'

const { t } = useI18n()
const router = useRouter()
const adminAuth = useAdminAuthStore()

const navItems = [
  { label: 'admin.dashboard_title', icon: 'pi pi-home', route: 'admin-dashboard' },
  { label: 'admin.servers_title', icon: 'pi pi-server', route: 'admin-servers' },
  { label: 'admin.settings_title', icon: 'pi pi-cog', route: 'admin-settings' },
  { label: 'admin.users_title', icon: 'pi pi-users', route: 'admin-users' },
  { label: 'admin.admins_title', icon: 'pi pi-shield', route: 'admin-admins' },
]

async function doLogout() {
  await adminAuth.logout()
  router.push({ name: 'admin-login' })
}
</script>

<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <h2 class="sidebar-title">Admin</h2>
      <nav>
        <div
          v-for="item in navItems"
          :key="item.route"
          class="nav-item"
          :class="{ active: $route.name === item.route }"
          @click="router.push({ name: item.route })"
        >
          <i :class="item.icon"></i>
          <span>{{ t(item.label) }}</span>
        </div>
      </nav>
      <div class="sidebar-footer">
        <span class="admin-name">{{ adminAuth.admin?.username }}</span>
        <Button icon="pi pi-sign-out" text size="small" @click="doLogout" />
      </div>
    </aside>
    <main class="admin-main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; }
.admin-sidebar {
  width: 220px;
  background: #1e293b;
  color: white;
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
}
.sidebar-title { padding: 0 1rem; margin: 0 0 1.5rem; font-size: 1.3rem; }
.nav-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
  transition: background 0.15s;
}
.nav-item:hover { background: #334155; }
.nav-item.active { background: #3b82f6; }
.nav-item i { font-size: 1rem; }
.sidebar-footer {
  margin-top: auto;
  padding: 1rem;
  border-top: 1px solid #334155;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.admin-name { font-size: 0.85rem; color: #94a3b8; }
.admin-main { flex: 1; padding: 1.5rem; overflow-y: auto; }
</style>
