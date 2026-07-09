<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-slate-900">Usuários</h1>
        <p class="mt-1 text-sm text-slate-500">Cadastre e gerencie quem pode acessar a ferramenta.</p>
      </div>

      <NuxtLink
        to="/admin/usuarios/novo"
        class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
      >
        Novo usuário
      </NuxtLink>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white">
      <div v-if="carregando" class="p-6 text-sm text-slate-500">Carregando usuários...</div>
      <div v-else-if="erro" class="p-6 text-sm text-red-600">{{ erro }}</div>
      <div v-else-if="usuarios.length === 0" class="p-6">
        <p class="text-sm font-medium text-slate-800">Nenhum usuário cadastrado.</p>
        <p class="mt-1 text-sm text-slate-500">Crie um usuário para liberar o acesso à aplicação.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-100">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Usuário</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Perfil</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Status</th>
              <th class="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="usuario in usuarios" :key="usuario.id" class="hover:bg-slate-50">
              <td class="px-6 py-4">
                <p class="text-sm font-medium text-slate-900">{{ usuario.nome }}</p>
                <p class="text-xs text-slate-500">{{ usuario.email }}</p>
              </td>
              <td class="px-6 py-4 text-sm text-slate-600">{{ labelPerfil(usuario.perfil) }}</td>
              <td class="px-6 py-4">
                <div class="flex flex-wrap gap-2">
                  <span
                    class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
                    :class="usuario.ativo ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'"
                  >
                    {{ usuario.ativo ? 'Ativo' : 'Inativo' }}
                  </span>
                  <span v-if="usuario.troca_senha_obrigatoria" class="inline-flex rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700">
                    Troca pendente
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 text-right">
                <button class="text-sm font-semibold text-blue-600 hover:text-blue-700" @click="abrirResetSenha(usuario)">
                  Resetar senha
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="usuarioReset" class="rounded-xl border border-slate-200 bg-white p-6">
      <h2 class="text-sm font-semibold text-slate-900">Resetar senha de {{ usuarioReset.nome }}</h2>
      <form class="mt-4 flex flex-col gap-3 sm:flex-row" @submit.prevent="confirmarResetSenha">
        <input
          v-model="senhaTemporaria"
          type="password"
          minlength="8"
          required
          placeholder="Nova senha temporária"
          class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          :disabled="salvando"
          class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ salvando ? 'Salvando...' : 'Confirmar' }}
        </button>
        <button type="button" class="rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100" @click="cancelarReset">
          Cancelar
        </button>
      </form>
      <p v-if="mensagem" class="mt-3 text-sm text-green-600">{{ mensagem }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UsuarioSistema } from '~/composables/useUsuarios'

definePageMeta({ layout: 'default', middleware: 'auth' })

const { usuarios, carregando, salvando, erro, carregar, resetarSenha } = useUsuarios()
const usuarioReset = ref<UsuarioSistema | null>(null)
const senhaTemporaria = ref('')
const mensagem = ref<string | null>(null)

onMounted(() => {
  carregar()
})

function labelPerfil(perfil: string) {
  const labels: Record<string, string> = {
    admin_ia16: 'Admin iA16',
    cliente_admin: 'Admin cliente',
    cliente_operador: 'Operador',
  }
  return labels[perfil] ?? perfil
}

function abrirResetSenha(usuario: UsuarioSistema) {
  usuarioReset.value = usuario
  senhaTemporaria.value = ''
  mensagem.value = null
}

function cancelarReset() {
  usuarioReset.value = null
  senhaTemporaria.value = ''
  mensagem.value = null
}

async function confirmarResetSenha() {
  if (!usuarioReset.value) return
  await resetarSenha(usuarioReset.value.id, senhaTemporaria.value)
  mensagem.value = 'Senha temporária atualizada. O usuário deverá trocar a senha no próximo acesso.'
  await carregar()
}
</script>
