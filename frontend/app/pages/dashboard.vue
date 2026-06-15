<template>
  <div class="p-6">

    <!-- Título -->
    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-slate-800">Dashboard</h1>
      <p class="text-sm text-slate-500 mt-1">Bem-vindo, {{ auth.sessao?.user?.email }}</p>
    </div>

    <!-- KPIs -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div v-for="kpi in kpis" :key="kpi.label" class="bg-white rounded-xl border border-slate-200 p-5">
        <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">{{ kpi.label }}</p>
        <p class="text-3xl font-bold mt-2" :class="kpi.cor">{{ kpi.valor }}</p>
        <p class="text-xs text-slate-400 mt-1">{{ kpi.descricao }}</p>
      </div>
    </div>

    <!-- Fechamentos recentes -->
    <div class="bg-white rounded-xl border border-slate-200 mb-6">
      <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100">
        <h2 class="text-sm font-semibold text-slate-700">Conciliações recentes</h2>
        <span class="text-xs text-blue-600 cursor-pointer hover:underline">Ver todos</span>
      </div>
      <table class="w-full text-sm">
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
            v-for="f in fechamentos"
            :key="f.id"
            class="border-b border-slate-50 hover:bg-slate-50 transition-colors"
          >
            <td class="px-5 py-3 text-slate-700 font-medium">{{ f.empresa }}</td>
            <td class="px-5 py-3 text-slate-500">{{ f.tipo }}</td>
            <td class="px-5 py-3 text-slate-500">{{ f.periodo }}</td>
            <td class="px-5 py-3">
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium" :class="statusClass(f.status)">
                {{ labelStatus(f.status) }}
              </span>
            </td>
            <td class="px-5 py-3 text-right" :class="f.divergencias > 0 ? 'text-red-500 font-semibold' : 'text-slate-400'">
              {{ f.divergencias }}
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

const kpis = [
  { label: "Conciliações", valor: "12", descricao: "no mês atual", cor: "text-slate-800" },
  { label: "Aprovados", valor: "8", descricao: "sem divergências", cor: "text-green-600" },
  { label: "Divergências", valor: "34", descricao: "aguardando revisão", cor: "text-red-500" },
  { label: "Em processamento", valor: "2", descricao: "em andamento", cor: "text-blue-600" },
]

const fechamentos = [
  { id: 1,  empresa: "Daxx Omnimedia", tipo: "Bancária",   periodo: "Mai/2026", status: "aprovado",         divergencias: 0 },
  { id: 2,  empresa: "Daxx Omnimedia", tipo: "Bancária",   periodo: "Abr/2026", status: "com_divergencias", divergencias: 12 },
  { id: 3,  empresa: "Cliente B",      tipo: "Caixa",      periodo: "Mai/2026", status: "em_processamento", divergencias: 0 },
  { id: 4,  empresa: "Cliente B",      tipo: "Recebíveis", periodo: "Mai/2026", status: "rascunho",         divergencias: 0 },
  { id: 5,  empresa: "Daxx Omnimedia", tipo: "Bancária",   periodo: "Mar/2026", status: "aprovado",         divergencias: 0 },
  { id: 6,  empresa: "Cliente B",      tipo: "Caixa",      periodo: "Abr/2026", status: "aprovado",         divergencias: 0 },
  { id: 7,  empresa: "Daxx Omnimedia", tipo: "Bancária",   periodo: "Fev/2026", status: "aprovado",         divergencias: 0 },
  { id: 8,  empresa: "Cliente C",      tipo: "Adquirentes",periodo: "Mai/2026", status: "com_divergencias", divergencias: 7 },
  { id: 9,  empresa: "Cliente C",      tipo: "Adquirentes",periodo: "Abr/2026", status: "aprovado",         divergencias: 0 },
  { id: 10, empresa: "Daxx Omnimedia", tipo: "Bancária",   periodo: "Jan/2026", status: "cancelado",        divergencias: 0 },
  { id: 11, empresa: "Cliente B",      tipo: "Recebíveis", periodo: "Abr/2026", status: "processado",       divergencias: 0 },
  { id: 12, empresa: "Cliente C",      tipo: "Vendas",     periodo: "Mai/2026", status: "em_processamento", divergencias: 0 },
  { id: 13, empresa: "Daxx Omnimedia", tipo: "Bancária",   periodo: "Dez/2025", status: "aprovado",         divergencias: 0 },
  { id: 14, empresa: "Cliente B",      tipo: "Caixa",      periodo: "Mar/2026", status: "com_divergencias", divergencias: 3 },
  { id: 15, empresa: "Cliente C",      tipo: "Adquirentes",periodo: "Mar/2026", status: "aprovado",         divergencias: 0 },
]

function statusClass(status: string) {
  const map: Record<string, string> = {
    aprovado:          "bg-green-100 text-green-700",
    com_divergencias:  "bg-red-100 text-red-600",
    em_processamento:  "bg-blue-100 text-blue-600",
    rascunho:          "bg-slate-100 text-slate-500",
    processado:        "bg-teal-100 text-teal-600",
    erro:              "bg-red-100 text-red-600",
    cancelado:         "bg-slate-100 text-slate-400",
  }
  return map[status] ?? "bg-slate-100 text-slate-500"
}

</script>
