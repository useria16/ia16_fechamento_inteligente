<template>
  <aside class="flex flex-col w-56 bg-white text-slate-700 shrink-0 rounded-xl overflow-hidden">

    <!-- Botão de ação principal -->
    <div class="px-3 pt-4 pb-2">
      <NuxtLink
        to="/conciliacoes/nova"
        class="flex items-center gap-2 w-full px-4 py-2.5 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-800 text-sm font-semibold transition-colors"
      >
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        Conciliação
      </NuxtLink>
    </div>

    <!-- Navegação filtrada por perfil -->
    <nav class="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
      <LayoutAppSidebarLink
        v-for="item in itensFiltrados"
        :key="item.to"
        :to="item.to"
        :icon="item.icon"
        :disabled="item.disabled"
      >
        {{ item.label }}
      </LayoutAppSidebarLink>
    </nav>

    <!-- Rodapé -->
    <footer class="px-3 py-4 border-t border-slate-100">
      <button
        class="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition-colors"
        @click="auth.sair()"
      >
        <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6A2.25 2.25 0 005.25 5.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M18 15l3-3m0 0l-3-3m3 3H9" />
        </svg>
        Sair
      </button>
    </footer>

  </aside>
</template>

<script setup lang="ts">
const auth = useAuthStore()

type NavItem = {
  to: string
  icon: string
  label: string
  perfis?: string[]
  disabled?: boolean
}

const todosItens: NavItem[] = [
  { to: '/dashboard',                 icon: 'dashboard',    label: 'Dashboard' },
  { to: '/admin/empresas',            icon: 'empresas',     label: 'Empresas',     perfis: ['admin_ia16'],                        disabled: true },
  { to: '/admin/usuarios',            icon: 'usuarios',     label: 'Usuários',     perfis: ['admin_ia16'],                        disabled: true },
  { to: '/conciliacoes',              icon: 'conciliacoes', label: 'Conciliações' },
  { to: '/arquivos',                  icon: 'arquivos',     label: 'Arquivos',                                                    disabled: true },
  { to: '/divergencias',              icon: 'divergencias', label: 'Divergências',                                                disabled: true },
  { to: '/relatorios',                icon: 'relatorios',   label: 'Relatórios' },
  { to: '/configuracoes-conciliacao', icon: 'configuracoes',label: 'Configurações', perfis: ['admin_ia16', 'cliente_admin'],      disabled: true },
  { to: '/logs',                      icon: 'logs',         label: 'Logs',          perfis: ['admin_ia16'],                       disabled: true },
]

const itensFiltrados = computed(() => {
  const p = auth.perfil
  // sem perfil carregado: exibe tudo (safe default enquanto carrega)
  if (!p || p === 'admin_ia16') return todosItens
  return todosItens.filter(item => !item.perfis || item.perfis.includes(p))
})
</script>
