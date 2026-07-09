<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-sm bg-white rounded-lg shadow p-8">
      <h1 class="text-xl font-semibold text-gray-900 mb-6">iA16 Fechamento Inteligente</h1>

      <form @submit.prevent="submeter" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
          <input
            v-model="email"
            type="email"
            required
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Senha</label>
          <input
            v-model="senha"
            type="password"
            required
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <p v-if="auth.erro" class="text-sm text-red-600">{{ auth.erro }}</p>

        <button
          type="submit"
          :disabled="auth.carregando"
          class="w-full bg-blue-600 text-white py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {{ auth.carregando ? "Entrando..." : "Entrar" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const auth = useAuthStore()
const email = ref("")
const senha = ref("")

async function submeter() {
  await auth.entrar(email.value, senha.value)
  if (auth.autenticado) {
    navigateTo(auth.trocaSenhaObrigatoria ? "/alterar-senha" : "/dashboard")
  }
}
</script>
