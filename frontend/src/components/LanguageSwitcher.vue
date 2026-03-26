<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import SelectButton from 'primevue/selectbutton'

const { locale } = useI18n()

const options = [
  { label: 'DE', value: 'de' },
  { label: 'EN', value: 'en' },
]

async function switchLang(lang: string) {
  locale.value = lang
  try {
    await fetch('/api/preferences/language', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ language: lang }),
    })
  } catch { /* ignore if not logged in */ }
}
</script>

<template>
  <SelectButton
    :modelValue="locale"
    :options="options"
    optionLabel="label"
    optionValue="value"
    @update:modelValue="switchLang"
    :allowEmpty="false"
  />
</template>
