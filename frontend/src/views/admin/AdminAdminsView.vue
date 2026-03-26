<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import AdminLayout from '../../components/admin/AdminLayout.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Tag from 'primevue/tag'

const { t } = useI18n()
const toast = useToast()
const confirm = useConfirm()
const admins = ref<any[]>([])
const showDialog = ref(false)
const form = ref({ username: '', password: '' })

async function fetchAdmins() {
  const res = await fetch('/api/admin/admins', { credentials: 'include' })
  if (res.ok) admins.value = await res.json()
}

onMounted(fetchAdmins)

function openCreate() {
  form.value = { username: '', password: '' }
  showDialog.value = true
}

async function createAdmin() {
  const res = await fetch('/api/admin/admins', {
    method: 'POST', credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value),
  })
  if (res.ok) {
    showDialog.value = false
    await fetchAdmins()
    toast.add({ severity: 'success', summary: t('admin.save_success'), life: 2000 })
  } else {
    const err = await res.json()
    toast.add({ severity: 'error', summary: err.detail || t('common.error'), life: 3000 })
  }
}

async function toggleActive(admin: any) {
  await fetch(`/api/admin/admins/${admin.id}`, {
    method: 'PUT', credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_active: !admin.is_active }),
  })
  await fetchAdmins()
}

function deleteAdmin(admin: any) {
  confirm.require({
    header: t('admin.delete_confirm'),
    message: `${admin.username} loeschen?`,
    accept: async () => {
      const res = await fetch(`/api/admin/admins/${admin.id}`, { method: 'DELETE', credentials: 'include' })
      if (res.ok) {
        await fetchAdmins()
      } else {
        const err = await res.json()
        toast.add({ severity: 'error', summary: err.detail || t('common.error'), life: 3000 })
      }
    },
  })
}
</script>

<template>
  <AdminLayout>
    <div class="header-row">
      <h1>{{ t('admin.admins_title') }}</h1>
      <Button :label="t('admin.admins_add')" icon="pi pi-plus" @click="openCreate" />
    </div>

    <DataTable :value="admins" stripedRows>
      <Column field="username" header="Benutzername" />
      <Column field="is_active" header="Status">
        <template #body="{ data }">
          <Tag :severity="data.is_active ? 'success' : 'danger'" :value="data.is_active ? 'Aktiv' : 'Inaktiv'" style="cursor:pointer" @click="toggleActive(data)" />
        </template>
      </Column>
      <Column field="last_login" header="Letzter Login">
        <template #body="{ data }">
          {{ data.last_login ? new Date(data.last_login).toLocaleString() : '-' }}
        </template>
      </Column>
      <Column header="">
        <template #body="{ data }">
          <Button icon="pi pi-trash" text severity="danger" size="small" @click="deleteAdmin(data)" />
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="showDialog" :header="t('admin.admins_add')" modal style="width: 400px">
      <div class="form-col">
        <label>{{ t('admin.username') }}</label>
        <InputText v-model="form.username" class="w-full" />
        <label>{{ t('admin.password') }}</label>
        <Password v-model="form.password" :feedback="false" toggleMask class="w-full" inputClass="w-full" />
      </div>
      <template #footer>
        <Button :label="t('common.cancel')" text @click="showDialog = false" />
        <Button :label="t('common.save')" @click="createAdmin" />
      </template>
    </Dialog>
  </AdminLayout>
</template>

<style scoped>
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.form-col { display: flex; flex-direction: column; gap: 0.5rem; }
.form-col label { font-weight: 600; margin-top: 0.5rem; }
.w-full { width: 100%; }
</style>
