<template>
  <div class="max-w-2xl space-y-6">
    <div class="flex items-center gap-3">
      <NuxtLink to="/admin/usuarios" class="text-sm font-medium text-slate-500 hover:text-slate-800">Voltar</NuxtLink>
      <div>
        <h1 class="text-3xl font-bold text-slate-900">Novo usuário</h1>
        <p class="mt-1 text-sm text-slate-500">Crie o acesso com senha temporária.</p>
      </div>
    </div>

    <form class="rounded-xl border border-slate-200 bg-white p-6 space-y-5" @submit.prevent="submeter">
      <div class="space-y-1">
        <label class="block text-sm font-semibold text-slate-700">Nome <span class="text-red-500">*</span></label>
        <input v-model="form.nome" type="text" class="campo" :class="erros.nome ? 'border-red-400' : 'border-slate-200'" />
        <p v-if="erros.nome" class="text-xs text-red-500">{{ erros.nome }}</p>
      </div>

      <div class="space-y-1">
        <label class="block text-sm font-semibold text-slate-700">E-mail <span class="text-red-500">*</span></label>
        <input v-model="form.email" type="email" class="campo" :class="erros.email ? 'border-red-400' : 'border-slate-200'" />
        <p v-if="erros.email" class="text-xs text-red-500">{{ erros.email }}</p>
      </div>

      <div class="space-y-1">
        <label class="block text-sm font-semibold text-slate-700">Perfil <span class="text-red-500">*</span></label>
        <select v-model="form.perfil" class="campo" :class="erros.perfil ? 'border-red-400' : 'border-slate-200'">
          <option v-if="auth.perfil === 'admin_ia16'" value="admin_ia16">Admin iA16</option>
          <option v-if="auth.perfil === 'admin_ia16'" value="cliente_admin">Admin cliente</option>
          <option value="cliente_operador">Operador</option>
        </select>
        <p v-if="erros.perfil" class="text-xs text-red-500">{{ erros.perfil }}</p>
      </div>

      <!-- Cliente/Grupo — visível para admin_ia16 ao criar usuário de cliente -->
      <div v-if="form.perfil !== 'admin_ia16' && auth.perfil === 'admin_ia16'" class="space-y-1">
        <label class="block text-sm font-semibold text-slate-700">Cliente/Grupo <span class="text-red-500">*</span></label>
        <select
          v-model="form.cliente_id"
          :disabled="carregandoClientes"
          class="campo disabled:cursor-not-allowed disabled:opacity-50"
          :class="erros.cliente_id ? 'border-red-400' : 'border-slate-200'"
        >
          <option value="">{{ carregandoClientes ? 'Carregando...' : 'Selecione o cliente/grupo' }}</option>
          <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.nome }}</option>
        </select>
        <p v-if="erros.cliente_id" class="text-xs text-red-500">{{ erros.cliente_id }}</p>
      </div>

      <div class="space-y-1">
        <label class="block text-sm font-semibold text-slate-700">Senha temporária <span class="text-red-500">*</span></label>
        <input
          v-model="form.senha_temporaria"
          type="password"
          class="campo"
          :class="erros.senha_temporaria ? 'border-red-400' : 'border-slate-200'"
        />
        <p v-if="erros.senha_temporaria" class="text-xs text-red-500">{{ erros.senha_temporaria }}</p>
        <p v-else class="text-xs text-slate-500">O usuário deverá trocar essa senha no primeiro acesso.</p>
      </div>

      <p v-if="erro" class="rounded-lg border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-600">{{ erro }}</p>

      <div class="flex flex-col gap-3 pt-2 sm:flex-row sm:justify-end">
        <NuxtLink to="/admin/usuarios" class="inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100">
          Cancelar
        </NuxtLink>
        <button
          type="submit"
          :disabled="salvando"
          class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ salvando ? 'Salvando...' : 'Salvar usuário' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { usuarioCreateSchema } from '~/schemas/usuario.schema'
import type { UsuarioCreateForm } from '~/schemas/usuario.schema'

definePageMeta({ layout: 'default', middleware: 'auth' })

const auth = useAuthStore()
const { criar, salvando, erro } = useUsuarios()
const { clientes, carregando: carregandoClientes, carregar: carregarClientes } = useClientes()

const form = reactive<UsuarioCreateForm>({
  nome: '',
  email: '',
  perfil: 'cliente_operador',
  cliente_id: '',
  senha_temporaria: '',
})
const erros = reactive<Partial<Record<keyof UsuarioCreateForm, string>>>({})

onMounted(async () => {
  if (auth.perfil === 'admin_ia16') {
    await carregarClientes()
    if (clientes.value.length === 1) {
      form.cliente_id = clientes.value[0].id
    }
  } else {
    // cliente_admin: vincula automaticamente ao próprio cliente
    form.cliente_id = auth.clienteId ?? ''
  }
})

watch(() => form.perfil, perfil => {
  if (perfil === 'admin_ia16') form.cliente_id = ''
})

function validar() {
  Object.keys(erros).forEach(k => delete (erros as any)[k])
  const resultado = usuarioCreateSchema.safeParse(form)
  if (!resultado.success) {
    for (const issue of resultado.error.issues) {
      const campo = issue.path[0] as keyof UsuarioCreateForm
      if (campo && !erros[campo]) erros[campo] = issue.message
    }
    return null
  }
  return resultado.data
}

async function submeter() {
  const dados = validar()
  if (!dados) return

  const clienteIdFinal = dados.perfil === 'admin_ia16'
    ? null
    : (dados.cliente_id || auth.clienteId || null)

  await criar({
    nome: dados.nome,
    email: dados.email,
    perfil: dados.perfil,
    cliente_id: clienteIdFinal,
    senha_temporaria: dados.senha_temporaria,
  })
  await navigateTo('/admin/usuarios')
}
</script>

<style scoped>
.campo {
  @apply w-full rounded-lg border px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500;
}
</style>
