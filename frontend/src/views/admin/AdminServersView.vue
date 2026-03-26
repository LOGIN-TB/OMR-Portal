<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAdminStore } from '../../stores/admin'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import AdminLayout from '../../components/admin/AdminLayout.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Tag from 'primevue/tag'

const { t } = useI18n()
const adminStore = useAdminStore()
const toast = useToast()
const confirm = useConfirm()

const showDialog = ref(false)
const editMode = ref(false)
const form = ref({ id: '', name: '', admin_url: '', api_key: '' })

onMounted(() => adminStore.fetchServers())

function openCreate() {
  editMode.value = false
  form.value = { id: '', name: '', admin_url: '', api_key: '' }
  showDialog.value = true
}

function openEdit(server: any) {
  editMode.value = true
  form.value = { id: server.id, name: server.name, admin_url: server.admin_url, api_key: '' }
  showDialog.value = true
}

async function saveServer() {
  try {
    if (editMode.value) {
      const data: any = { name: form.value.name, admin_url: form.value.admin_url }
      if (form.value.api_key) data.api_key = form.value.api_key
      await adminStore.updateServer(form.value.id, data)
    } else {
      await adminStore.createServer(form.value)
    }
    showDialog.value = false
    toast.add({ severity: 'success', summary: t('admin.save_success'), life: 2000 })
  } catch {
    toast.add({ severity: 'error', summary: t('common.error'), life: 3000 })
  }
}

function deleteServer(id: string) {
  confirm.require({
    header: t('admin.delete_confirm'),
    message: t('admin.delete_confirm'),
    accept: async () => {
      await adminStore.deleteServer(id)
    },
  })
}

async function testServer(id: string) {
  const result = await adminStore.testServer(id)
  if (result.status === 'ok') {
    toast.add({ severity: 'success', summary: t('admin.servers_test_success'), life: 3000 })
  } else {
    toast.add({ severity: 'error', summary: t('admin.servers_test_fail'), detail: result.error, life: 5000 })
  }
}
</script>

<template>
  <AdminLayout>
    <div class="header-row">
      <h1>{{ t('admin.servers_title') }}</h1>
      <Button :label="t('admin.servers_add')" icon="pi pi-plus" @click="openCreate" />
    </div>

    <DataTable :value="adminStore.servers" stripedRows>
      <Column field="id" :header="t('admin.server_id')" />
      <Column field="name" :header="t('admin.server_name')" />
      <Column field="admin_url" :header="t('admin.server_admin_url')" />
      <Column field="api_key_masked" :header="t('admin.server_api_key')" />
      <Column field="is_active" header="Status">
        <template #body="{ data }">
          <Tag :severity="data.is_active ? 'success' : 'danger'" :value="data.is_active ? 'Aktiv' : 'Inaktiv'" />
        </template>
      </Column>
      <Column header="">
        <template #body="{ data }">
          <div class="action-buttons">
            <Button icon="pi pi-play" text size="small" @click="testServer(data.id)" v-tooltip="t('admin.servers_test')" />
            <Button icon="pi pi-pencil" text size="small" @click="openEdit(data)" />
            <Button icon="pi pi-trash" text severity="danger" size="small" @click="deleteServer(data.id)" />
          </div>
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="showDialog" :header="editMode ? 'Server bearbeiten' : t('admin.servers_add')" modal style="width: 500px">
      <div class="form-grid">
        <label>{{ t('admin.server_id') }}</label>
        <InputText v-model="form.id" :disabled="editMode" class="w-full" />
        <label>{{ t('admin.server_name') }}</label>
        <InputText v-model="form.name" class="w-full" />
        <label>{{ t('admin.server_admin_url') }}</label>
        <InputText v-model="form.admin_url" class="w-full" />
        <label>{{ t('admin.server_api_key') }}</label>
        <InputText v-model="form.api_key" class="w-full" :placeholder="editMode ? '(unveraendert)' : ''" />
      </div>
      <template #footer>
        <Button :label="t('common.cancel')" text @click="showDialog = false" />
        <Button :label="t('common.save')" @click="saveServer" />
      </template>
    </Dialog>
  </AdminLayout>
</template>

<style scoped>
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.action-buttons { display: flex; gap: 0.25rem; }
.form-grid { display: flex; flex-direction: column; gap: 0.5rem; }
.form-grid label { font-weight: 600; font-size: 0.9rem; margin-top: 0.5rem; }
.w-full { width: 100%; }
</style>
