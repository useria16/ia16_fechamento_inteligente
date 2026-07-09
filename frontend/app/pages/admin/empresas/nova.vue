<template>
  <div class="max-w-2xl space-y-6">
    <div class="flex items-center gap-3">
      <NuxtLink to="/admin/empresas" class="text-sm font-medium text-slate-500 hover:text-slate-800">Voltar</NuxtLink>
      <div>
        <h1 class="text-3xl font-bold text-slate-900">Nova empresa</h1>
        <p class="mt-1 text-sm text-slate-500">Cadastre a empresa para liberar novas conciliações.</p>
      </div>
    </div>

    <form class="rounded-xl border border-slate-200 bg-white p-6 space-y-5" @submit.prevent="submeter">
      <div class="space-y-1">
        <label class="block text-sm font-semibold text-slate-700">Cliente <span class="text-red-500">*</span></label>
        <select
          v-model="form.cliente_id"
          class="w-full rounded-lg border px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="erros.cliente_id ? 'border-red-400' : 'border-slate-200'"
        >
          <option value="" disabled>Selecione o cliente</option>
          <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.nome }}</option>
        </select>
        <p v-if="erros.cliente_id" class="text-xs text-red-500">{{ erros.cliente_id }}</p>
      </div>

      <div class="space-y-1">
        <label class="block text-sm font-semibold text-slate-700">Nome da empresa <span class="text-red-500">*</span></label>
        <input
          v-model="form.nome"
          type="text"
          autocomplete="organization"
          class="w-full rounded-lg border px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="erros.nome ? 'border-red-400' : 'border-slate-200'"
          placeholder="DAXX MIDIA LTDA"
        />
        <p v-if="erros.nome" class="text-xs text-red-500">{{ erros.nome }}</p>
      </div>

      <div class="space-y-1">
        <label class="block text-sm font-semibold text-slate-700">CNPJ <span class="text-red-500">*</span></label>
        <input
          v-model="form.cnpj"
          type="text"
          inputmode="numeric"
          autocomplete="off"
          class="w-full rounded-lg border px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="erros.cnpj ? 'border-red-400' : 'border-slate-200'"
          placeholder="11.775.820/0001-71"
        />
        <p v-if="erros.cnpj" class="text-xs text-red-500">{{ erros.cnpj }}</p>
      </div>

      <p v-if="erro" class="rounded-lg border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-600">{{ erro }}</p>

      <div class="flex flex-col gap-3 pt-2 sm:flex-row sm:justify-end">
        <NuxtLink
          to="/admin/empresas"
          class="inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100"
        >
          Cancelar
        </NuxtLink>
        <button
          type="submit"
          :disabled="salvando"
          class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
        >
          {{ salvando ? 'Salvando...' : 'Salvar empresa' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { empresaCreateSchema } from '~/schemas/empresa.schema'
import type { EmpresaCreateForm } from '~/schemas/empresa.schema'

definePageMeta({ layout: 'default', middleware: 'auth' })

const { criar, salvando, erro } = useEmpresas()
const { clientes, carregar: carregarClientes } = useClientes()

const form = reactive<EmpresaCreateForm>({
  cliente_id: '',
  nome: '',
  cnpj: '',
})
const erros = reactive<Partial<Record<keyof EmpresaCreateForm, string>>>({})

onMounted(carregarClientes)

function validar() {
  Object.keys(erros).forEach(k => delete (erros as any)[k])

  const resultado = empresaCreateSchema.safeParse(form)
  if (!resultado.success) {
    for (const issue of resultado.error.issues) {
      const campo = issue.path[0] as keyof EmpresaCreateForm
      if (campo && !erros[campo]) erros[campo] = issue.message
    }
    return null
  }

  return resultado.data
}

async function submeter() {
  const dados = validar()
  if (!dados) return

  try {
    await criar(dados)
    await navigateTo('/admin/empresas')
  } catch {
    // erro já é tratado no composable
  }
}
</script>
