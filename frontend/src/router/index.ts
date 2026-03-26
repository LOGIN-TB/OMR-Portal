import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useAdminAuthStore } from '../stores/adminAuth'
import LoginView from '../views/LoginView.vue'
import VerifyView from '../views/VerifyView.vue'
import DashboardView from '../views/DashboardView.vue'
import AccountDetailView from '../views/AccountDetailView.vue'
import PreferencesView from '../views/PreferencesView.vue'

const routes = [
  { path: '/', name: 'login', component: LoginView, meta: { public: true } },
  { path: '/auth/verify', name: 'verify', component: VerifyView, meta: { public: true } },
  { path: '/dashboard', name: 'dashboard', component: DashboardView },
  { path: '/account/:serverId/:smtpUserId', name: 'account-detail', component: AccountDetailView },
  { path: '/preferences', name: 'preferences', component: PreferencesView },

  // Admin routes (lazy-loaded)
  { path: '/admin/login', name: 'admin-login', component: () => import('../views/admin/AdminLoginView.vue'), meta: { public: true, admin: true } },
  { path: '/admin', name: 'admin-dashboard', component: () => import('../views/admin/AdminDashboardView.vue'), meta: { admin: true } },
  { path: '/admin/servers', name: 'admin-servers', component: () => import('../views/admin/AdminServersView.vue'), meta: { admin: true } },
  { path: '/admin/settings', name: 'admin-settings', component: () => import('../views/admin/AdminSettingsView.vue'), meta: { admin: true } },
  { path: '/admin/users', name: 'admin-users', component: () => import('../views/admin/AdminUsersView.vue'), meta: { admin: true } },
  { path: '/admin/admins', name: 'admin-admins', component: () => import('../views/admin/AdminAdminsView.vue'), meta: { admin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  if (to.meta.public) return true

  if (to.meta.admin) {
    const adminAuth = useAdminAuthStore()
    if (!adminAuth.admin) await adminAuth.fetchMe()
    if (!adminAuth.admin) return { name: 'admin-login' }
    return true
  }

  const auth = useAuthStore()
  if (!auth.user) {
    await auth.fetchMe()
  }
  if (!auth.user) {
    return { name: 'login' }
  }
  return true
})

export default router
