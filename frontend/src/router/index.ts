import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  if (to.meta.public) return true

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
