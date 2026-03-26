<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminLayout from '../../components/admin/AdminLayout.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'

const { t } = useI18n()
const users = ref<any[]>([])
const search = ref('')

async function fetchUsers() {
  const params = search.value ? `?search=${encodeURIComponent(search.value)}` : ''
  const res = await fetch(`/api/admin/users${params}`, { credentials: 'include' })
  if (res.ok) users.value = await res.json()
}

onMounted(fetchUsers)
</script>

<template>
  <AdminLayout>
    <h1>{{ t('admin.users_title') }}</h1>
    <div class="search-bar">
      <InputText v-model="search" placeholder="E-Mail suchen" @keyup.enter="fetchUsers" />
    </div>
    <DataTable :value="users" stripedRows>
      <Column field="email" header="E-Mail" />
      <Column field="language" header="Sprache" />
      <Column field="accounts_count" header="Accounts" />
      <Column field="last_login" header="Letzter Login">
        <template #body="{ data }">
          {{ data.last_login ? new Date(data.last_login).toLocaleString() : '-' }}
        </template>
      </Column>
      <Column field="created_at" header="Erstellt">
        <template #body="{ data }">
          {{ data.created_at ? new Date(data.created_at).toLocaleDateString() : '-' }}
        </template>
      </Column>
    </DataTable>
  </AdminLayout>
</template>

<style scoped>
.search-bar { margin-bottom: 1rem; }
</style>
