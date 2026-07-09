<template>
  <div class="max-w-2xl space-y-6">
    <div class="flex items-center gap-3">
      <NuxtLink to="/admin/clientes" class="text-sm font-medium text-slate-500 hover:text-slate-800">Voltar</NuxtLink>
      <div>
        <h1 class="text-3xl font-bold text-slate-900">Editar cliente</h1>
      </div>
    </div>

    <div v-if="carregando" class="py-12 text-center text-sm text-slate-500">Carregando...</div>

    <form v-else class="rounded-xl border border-slate-200 bg-white p-6 space-y-5" @submit.prevent="submeter">
      <div class="space-y-1">
        <label class="block text-sm font-semibold text-slate-700">Nome do cliente <span class="text-red-500">*</span></label>
        <input
          v-model="form.nome"
          type="text"
          class="w-full rounded-lg border px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="erros.nome ? 'border-red-400' : 'border-slate-200'"
        />
        <p v-if="erros.nome" class="text-xs text-red-500">{{ erros.nome }}</p>
      </div>

      <div class="flex items-center gap-2">
        <input id="ativo" v-model="form.ativo" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-blue-600" />
        <label for="ativo" class="text-sm font-medium text-slate-700">Cliente ativo</label>
      </div>

      <p v-if="erro" class="rounded-lg border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-600">{{ erro }}</p>

      <div class="flex flex-col gap-3 pt-2 sm:flex-row sm:justify-end">
        <NuxtLink
          to="/admin/clientes"
          class="inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100"
        >
          Cancelar
        </NuxtLink>
        <button
          type="submit"
          :disabled="salvando"
          class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
        >
          {{ salvando ? 'Salvando...' : 'Salvar alterações' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { clientePatchSchema } from '~/schemas/cliente.schema'
import type { ClientePatchForm } from '~/schemas/cliente.schema'

definePageMeta({ layout: 'default', middleware: 'auth' })

const route = useRoute()
const clienteId = route.params.id as string

const { obter, atualizar, salvando, erro } = useClientes()
const carregando = ref(true)

const form = reactive<ClientePatchForm & { ativo: boolean }>({ nome: '', ativo: true })
const erros = reactive<Partial<Record<keyof ClientePatchForm, string>>>({})

onMounted(async () => {
  try {
    const dados = await obter(clienteId)
    form.nome = dados.nome
    form.ativo = dados.ativo
  } catch {
    // erro será exibido pelo composable
  } finally {
    carregando.value = false
  }
})

function validar() {
  Object.keys(erros).forEach(k => delete (erros as any)[k])
  const resultado = clientePatchSchema.safeParse(form)
  if (!resultado.success) {
    for (const issue of resultado.error.issues) {
      const campo = issue.path[0] as keyof ClientePatchForm
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
    await atualizar(clienteId, { ...dados, ativo: form.ativo })
    await navigateTo('/admin/clientes')
  } catch {
    // erro já tratado no composable
  }
}
</script>
