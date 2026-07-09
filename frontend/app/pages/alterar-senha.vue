<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="w-full max-w-md bg-white rounded-xl shadow-sm border border-slate-200 p-8">
      <h1 class="text-xl font-semibold text-gray-900">Alterar senha</h1>
      <p class="mt-2 text-sm text-slate-500">
        Para continuar usando o iA16, defina uma nova senha.
      </p>

      <form class="mt-6 space-y-4" @submit.prevent="submeter">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nova senha</label>
          <input
            v-model="novaSenha"
            type="password"
            required
            minlength="8"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar nova senha</label>
          <input
            v-model="confirmacao"
            type="password"
            required
            minlength="8"
            class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <p v-if="erroLocal" class="text-sm text-red-600">{{ erroLocal }}</p>
        <p v-else-if="auth.erro" class="text-sm text-red-600">{{ auth.erro }}</p>

        <button
          type="submit"
          :disabled="auth.carregando"
          class="w-full bg-blue-600 text-white py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {{ auth.carregando ? "Salvando..." : "Salvar nova senha" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false, middleware: "auth" })

const auth = useAuthStore()
const novaSenha = ref("")
const confirmacao = ref("")
const erroLocal = ref<string | null>(null)

async function submeter() {
  erroLocal.value = null
  if (novaSenha.value.length < 8) {
    erroLocal.value = "A senha deve ter pelo menos 8 caracteres."
    return
  }
  if (novaSenha.value !== confirmacao.value) {
    erroLocal.value = "As senhas não conferem."
    return
  }

  try {
    await auth.trocarSenha(novaSenha.value)
    await navigateTo("/dashboard")
  } catch {
    // auth.erro já foi preenchido no store
  }
}
</script>
