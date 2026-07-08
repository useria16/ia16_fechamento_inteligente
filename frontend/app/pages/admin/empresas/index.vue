<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-slate-900">Empresas</h1>
        <p class="mt-1 text-sm text-slate-500">Cadastre e gerencie as empresas disponíveis para conciliação.</p>
      </div>

      <NuxtLink
        to="/admin/empresas/nova"
        class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
      >
        Nova empresa
      </NuxtLink>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white">
      <div v-if="carregando" class="p-6 text-sm text-slate-500">Carregando empresas...</div>

      <div v-else-if="erro" class="p-6 text-sm text-red-600">
        {{ erro }}
      </div>

      <div v-else-if="empresas.length === 0" class="p-6">
        <p class="text-sm font-medium text-slate-800">Nenhuma empresa cadastrada.</p>
        <p class="mt-1 text-sm text-slate-500">Cadastre a primeira empresa para iniciar uma nova conciliação.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-100">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Empresa</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">CNPJ</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Status</th>
              <th class="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="empresa in empresas" :key="empresa.id" class="hover:bg-slate-50">
              <td class="px-6 py-4 text-sm font-medium text-slate-900">{{ empresa.nome }}</td>
              <td class="px-6 py-4 text-sm text-slate-600">{{ formatarCnpj(empresa.cnpj) }}</td>
              <td class="px-6 py-4">
                <span
                  class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
                  :class="empresa.status === 'ativa'
                    ? 'bg-green-50 text-green-700'
                    : 'bg-slate-100 text-slate-500'"
                >
                  {{ empresa.status === 'ativa' ? 'Ativa' : 'Inativa' }}
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <NuxtLink :to="`/admin/empresas/${empresa.id}`" class="text-sm font-semibold text-blue-600 hover:text-blue-700">
                  Editar
                </NuxtLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default', middleware: 'auth' })

const { empresas, carregando, erro, carregar } = useEmpresas()

onMounted(() => {
  carregar()
})

function formatarCnpj(valor: string) {
  const numeros = valor.replace(/\D/g, '')
  if (numeros.length !== 14) return valor
  return numeros.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}
</script>
