<template>
  <div class="p-6">

    <!-- Título -->
    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-slate-800">Dashboard</h1>
      <p class="text-sm text-slate-500 mt-1">Bem-vindo, {{ auth.sessao?.user?.email }}</p>
    </div>

    <!-- KPIs -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div v-if="carregandoResumo" v-for="n in 4" :key="n"
        class="bg-white rounded-xl border border-slate-200 p-5 animate-pulse">
        <div class="h-3 bg-slate-200 rounded w-24 mb-3" />
        <div class="h-8 bg-slate-200 rounded w-12 mb-2" />
        <div class="h-3 bg-slate-200 rounded w-32" />
      </div>
      <template v-else>
        <div class="bg-white rounded-xl border border-slate-200 p-5">
          <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Conciliações</p>
          <p class="text-3xl font-bold mt-2 text-slate-800">{{ resumo?.total ?? 0 }}</p>
          <p class="text-xs text-slate-400 mt-1">total cadastradas</p>
        </div>
        <div class="bg-white rounded-xl border border-slate-200 p-5">
          <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Aprovadas</p>
          <p class="text-3xl font-bold mt-2 text-green-600">{{ resumo?.aprovadas ?? 0 }}</p>
          <p class="text-xs text-slate-400 mt-1">sem divergências</p>
        </div>
        <div class="bg-white rounded-xl border border-slate-200 p-5">
          <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Divergências</p>
          <p class="text-3xl font-bold mt-2 text-red-500">{{ resumo?.com_divergencias ?? 0 }}</p>
          <p class="text-xs text-slate-400 mt-1">aguardando revisão</p>
        </div>
        <div class="bg-white rounded-xl border border-slate-200 p-5">
          <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Em processamento</p>
          <p class="text-3xl font-bold mt-2 text-blue-600">{{ resumo?.em_processamento ?? 0 }}</p>
          <p class="text-xs text-slate-400 mt-1">em andamento</p>
        </div>
      </template>
    </div>

    <!-- Conciliações recentes -->
    <div class="bg-white rounded-xl border border-slate-200 mb-6">
      <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100">
        <h2 class="text-sm font-semibold text-slate-700">Conciliações recentes</h2>
        <NuxtLink to="/conciliacoes" class="text-xs text-blue-600 hover:underline">Ver todos</NuxtLink>
      </div>

      <!-- Carregando -->
      <div v-if="carregandoLista" class="px-5 py-8 text-sm text-slate-400 text-center">
        Carregando...
      </div>

      <!-- Erro -->
      <div v-else-if="erro" class="px-5 py-6 text-sm text-red-500">
        {{ erro }}
      </div>

      <!-- Vazio -->
      <div v-else-if="conciliacoes.length === 0" class="px-5 py-10 text-sm text-slate-400 text-center">
        Nenhuma conciliação encontrada.
      </div>

      <!-- Tabela -->
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="text-xs text-slate-400 uppercase tracking-wide border-b border-slate-100">
            <th class="text-left px-5 py-3 font-medium">Empresa</th>
            <th class="text-left px-5 py-3 font-medium">Tipo</th>
            <th class="text-left px-5 py-3 font-medium">Período</th>
            <th class="text-left px-5 py-3 font-medium">Status</th>
            <th class="text-right px-5 py-3 font-medium">Divergências</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="f in conciliacoes"
            :key="String(f.id)"
            class="border-b border-slate-50 hover:bg-slate-50 transition-colors cursor-pointer"
            @click="navigateTo(`/conciliacoes/${f.id}`)"
          >
            <td class="px-5 py-3 text-slate-700 font-medium">{{ f.empresa_nome }}</td>
            <td class="px-5 py-3 text-slate-500">{{ labelTipo(f.tipo_conciliacao) }}</td>
            <td class="px-5 py-3 text-slate-500">{{ labelPeriodo(f.periodo_inicio) }}</td>
            <td class="px-5 py-3">
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium" :class="statusClass(f.status)">
                {{ labelStatus(f.status) }}
              </span>
            </td>
            <td class="px-5 py-3 text-right" :class="f.quantidade_divergencias > 0 ? 'text-red-500 font-semibold' : 'text-slate-400'">
              {{ f.quantidade_divergencias }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "default", middleware: "auth" })

const auth = useAuthStore()
const api  = useApi()

// ── Resumo (KPIs) ─────────────────────────────────────────────────────────────

interface Resumo { total: number; em_processamento: number; com_divergencias: number; aprovadas: number }
const resumo          = ref<Resumo | null>(null)
const carregandoResumo = ref(true)

// ── Lista de conciliações recentes ────────────────────────────────────────────

interface Conciliacao {
  id: string
  empresa_nome: string
  tipo_conciliacao: string
  periodo_inicio: string
  status: string
  quantidade_divergencias: number
}
const conciliacoes    = ref<Conciliacao[]>([])
const carregandoLista = ref(true)
const erro            = ref<string | null>(null)

onMounted(async () => {
  await Promise.all([carregarResumo(), carregarLista()])
})

async function carregarResumo() {
  carregandoResumo.value = true
  try {
    const r = await api.get<{ sucesso: boolean; dados: Resumo }>('/api/v1/conciliacoes/resumo')
    resumo.value = r.dados
  } catch {
    // KPIs ficam zerados silenciosamente
  } finally {
    carregandoResumo.value = false
  }
}

async function carregarLista() {
  carregandoLista.value = true
  erro.value = null
  try {
    const r = await api.get<{ sucesso: boolean; dados: Conciliacao[] }>('/api/v1/conciliacoes?limite=15&pagina=1')
    conciliacoes.value = r.dados ?? []
  } catch (e: any) {
    erro.value = e.message ?? 'Não foi possível carregar as conciliações.'
  } finally {
    carregandoLista.value = false
  }
}

// ── Helpers de formatação ─────────────────────────────────────────────────────

function labelPeriodo(data: string): string {
  if (!data) return '—'
  const meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
  const d = new Date(data + 'T00:00:00')
  return `${meses[d.getMonth()]}/${d.getFullYear()}`
}

function labelTipo(tipo: string): string {
  const map: Record<string, string> = {
    bancaria:             'Bancária',
    caixa:                'Caixa',
    recebiveis:           'Recebíveis',
    caixa_recebiveis:     'Caixa + Recebíveis',
    vendas_recebimentos:  'Vendas',
    adquirentes:          'Adquirentes',
    extrato_anotado:      'Extrato Anotado',
    outro:                'Outro',
  }
  return map[tipo] ?? tipo
}

function labelStatus(status: string): string {
  const map: Record<string, string> = {
    rascunho:          'Rascunho',
    arquivos_enviados: 'Arquivos enviados',
    em_processamento:  'Em processamento',
    processado:        'Processado',
    com_divergencias:  'Com divergências',
    aprovado:          'Aprovado',
    reaberto:          'Reaberto',
    erro:              'Erro',
    cancelado:         'Cancelado',
  }
  return map[status] ?? status
}

function statusClass(status: string): string {
  const map: Record<string, string> = {
    aprovado:          'bg-green-100 text-green-700',
    com_divergencias:  'bg-red-100 text-red-600',
    em_processamento:  'bg-blue-100 text-blue-600',
    rascunho:          'bg-slate-100 text-slate-500',
    processado:        'bg-teal-100 text-teal-600',
    reaberto:          'bg-amber-100 text-amber-600',
    erro:              'bg-red-100 text-red-600',
    cancelado:         'bg-slate-100 text-slate-400',
  }
  return map[status] ?? 'bg-slate-100 text-slate-500'
}
</script>
