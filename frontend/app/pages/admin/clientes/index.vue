<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-slate-900">Clientes</h1>
        <p class="mt-1 text-sm text-slate-500">Grupos que utilizam a plataforma iA16.</p>
      </div>
      <NuxtLink
        to="/admin/clientes/novo"
        class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        Novo cliente
      </NuxtLink>
    </div>

    <div v-if="carregando" class="py-12 text-center text-sm text-slate-500">Carregando...</div>

    <div v-else-if="erro" class="rounded-lg border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-600">
      {{ erro }}
    </div>

    <div v-else-if="clientes.length === 0" class="py-12 text-center text-sm text-slate-500">
      Nenhum cliente cadastrado.
    </div>

    <div v-else class="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-slate-100 bg-slate-50">
            <th class="px-4 py-3 text-left font-semibold text-slate-600">Nome</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600">Status</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600">Criado em</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="c in clientes" :key="c.id" class="hover:bg-slate-50">
            <td class="px-4 py-3 font-medium text-slate-900">{{ c.nome }}</td>
            <td class="px-4 py-3">
              <span
                class="inline-flex rounded-full px-2 py-0.5 text-xs font-semibold"
                :class="c.ativo ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'"
              >
                {{ c.ativo ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-4 py-3 text-slate-500">{{ formatarData(c.criado_em) }}</td>
            <td class="px-4 py-3 text-right">
              <NuxtLink
                :to="`/admin/clientes/${c.id}`"
                class="text-xs font-medium text-blue-600 hover:underline"
              >
                Editar
              </NuxtLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default', middleware: 'auth' })

const { clientes, carregando, erro, carregar } = useClientes()

function formatarData(iso: string) {
  return new Date(iso).toLocaleDateString('pt-BR')
}

onMounted(carregar)
</script>
